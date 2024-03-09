# -*- coding: utf-8 -*-
import discord
import openai
import argparse
import os
import logging
import time
import json
from datetime import datetime

# Define global variables
discord_client = None
openai_client = None
assistant_id = None
thread_id = None

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description="Discord bot with ChatGPT integration")
    parser.add_argument("--thread-id", help="ID of the thread to use, e.g.: thread_...", default=None)
    parser.add_argument("--assistant-id", help="ID of the assistant to use, e.g.: asst_...", default=None)
    parser.add_argument("--previous", action="store_true", help="Load previous session if available")
    return parser.parse_args()

def load_session():
    if os.path.exists("session.json"):
        with open("session.json", "r") as f:
            return json.load(f)
    else:
        return []

def save_session(session_data):
    with open("session.json", "w") as f:
        json.dump(session_data, f, indent=4, ensure_ascii=False   )

def update_session(assistant_id, thread_id):
    session_data = load_session()
    for session in session_data:
        if session["assistant_id"] == assistant_id and session["thread_id"] == thread_id:
            session["last_used"] = f"{datetime.now()}"
            break
    else:
        session_data.append({
            "timestamp": f"{datetime.now()}",
            "last_used": f"{datetime.now()}",
            "assistant_id": assistant_id,
            "thread_id": thread_id
        })
    save_session(session_data)

def load_previous_session():
    session_data = load_session()
    if session_data:
        last_session = max(session_data, key=lambda x: x["last_used"])
        return last_session["assistant_id"], last_session["thread_id"]
    else:
        return None, None

def load_assistant_config_from_json(file_path):
    with open(file_path, "r") as f:
        config = json.load(f)
    return config

def create_gpt_assistant(client, config):
    return client.beta.assistants.create(
        name=config["name"],
        instructions=config["instructions"],
        tools=config["tools"],
        model=config["model"]
    )

def create_gpt_thread(client):
    return client.beta.threads.create()

def disco_dm():
    global discord_client, openai_client, assistant_id, thread_id

    # Load tokens from environment variables
    DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    # Initialize OpenAI client
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

    # Initialize Discord client
    intents = discord.Intents.default()
    intents.message_content = True
    discord_client = discord.Client(intents=intents, fetch_offline_members=True)

    args = parse_args()
    thread_id = args.thread_id
    assistant_id = args.assistant_id

    if args.previous:
        assistant_id, thread_id = load_previous_session()

    if not thread_id and not assistant_id:
        assistant_config = load_assistant_config_from_json("assistant.json")
        assistant = create_gpt_assistant(client=openai_client, config=assistant_config)
        thread = create_gpt_thread(client=openai_client)
        thread_id = thread.id
        assistant_id = assistant.id

    update_session(assistant_id, thread_id)

    @discord_client.event
    async def on_ready():
        logger.info(f'Running discord bot as {discord_client.user.name}')

    @discord_client.event
    async def on_message(message):
        if message.author == discord_client.user:
            return

        if message.content.startswith("/dm_beta "):
            user = f"{message.author}"
            msg = message.content[len('/dm_beta '):]
            question_msg = json.dumps({"timestamp": f"{datetime.now()}", "user": f"{message.author}", "msg": msg}, ensure_ascii=False)
            logger.info(question_msg)

            async with message.channel.typing():
                response = await ask_gpt(openai_client, assistant_id, thread_id, f"{user}: {msg}")

            response_msg = json.dumps({"timestamp": f"{datetime.now()}", "assistant": f"{discord_client.user}", "response": response}, ensure_ascii=False)
            logger.info(response_msg)
            await message.channel.send(f"{message.author.mention}```\n{response}\n```")

            # Save conversation log
            create_session_log(user, msg, response)

    discord_client.run(DISCORD_TOKEN, log_handler=None)

async def ask_gpt(client, assistant, thread, message):
    message = client.beta.threads.messages.create(
        thread_id=thread,
        role="user",
        content=message
    )

    run = client.beta.threads.runs.create(
        thread_id=thread,
        assistant_id=assistant
    )

    assistant_response = None
    for attempt in range(1, 10):
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread,
            run_id=run.id
        )
        logger.info(f"Response status: {run.status}")
        if run.status == "completed":
            messages = client.beta.threads.messages.list(
                thread_id=thread
            )
            for message in messages:
                if message.role == "assistant":
                    assistant_response = message.content
                    break
            break
        time.sleep(4)
    else:
        logger.error("Failed to execute the task within the specified time!")

    if assistant_response:
        response_text = assistant_response[0].text.value
        return response_text
    else:
        logger.error("No response from the assistant found.")
        return "No response found from the assistant!"

def create_session_log(user, message, assistant_response):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    log_entry = {
        "timestamp": timestamp,
        "user": user,
        "msg": message,
        "assistant": f"{discord_client.user}",
        "response": assistant_response
    }

    session_log = load_session_log()
    session_log.append(log_entry)

    with open("session_log.json", "w") as f:
        json.dump(session_log, f, indent=4, ensure_ascii=False)

def load_session_log():
    try:
        with open("session_log.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.decoder.JSONDecodeError:
        return []

if __name__ == "__main__":
    disco_dm()
