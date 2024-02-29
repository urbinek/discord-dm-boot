# Discord Bot with ChatGPT Integration

This project is a Discord Bot integrated with OpenAI's ChatGPT, enabling interactions with Discord users via chat.

## Requirements

### Required Libraries

- discord.py
- openai

```bash
pip install -r requirements.txt
```

### Required Data

1. Discord Token (`DISCORD_TOKEN`)
2. OpenAI API Key (`OPENAI_API_KEY`)
3. Assistant Configuration File (`assistant.json`)

## Configuration

1. Set the required environment variables:
   - `DISCORD_TOKEN`: Your Discord token.
   - `OPENAI_API_KEY`: Your OpenAI API key.
```bash
export DISCORD_TOKEN=" ... "
export OPENAI_API_KEY=" .. "
```

2. Customize the assistant configuration in the `assistant.json` file.
```json
{
    "name": "Game Master",
    "instructions": "You are the Game Master of Dungeons'n'Dragons, you will guide the fates of a group of heroes. Each of them is an individual and will address you according to the pattern '$name: $message'. Respond like an old innkeeper who was once a traveler.",
    "tools": [{"type": "retrieval"}],
    "model": "gpt-3.5-turbo"
}
```

Remmber that data provided by `user` wil lbe formated as `'$name: $message'` in ChatGPT input
## Running

Run the `disco_dm.py` script to activate the Discord bot.

```bash
python disco_dm.py [--thread-id THREAD_ID] [--assistant-id ASSISTANT_ID] [--previous]
```

### Command Line Options:

- `--thread-id THREAD_ID`: ID of the thread to use (generat if not provided).
- `--assistant-id ASSISTANT_ID`: ID of the assistant to use (generat if not provided).
- `--previous`: Load the previous session if available.

## Example Sessions and Session Log

### Sample Session Log (`session_log.json`)

Stores the history of user interactions with the bot along with assistant responses.

```json
[
    {
        "timestamp": "2024-02-28 21:02:21.379229",
        "user": "User1",
        "msg": "Sample user message",
        "assistant": "AssistantName#1234",
        "response": "Sample assistant response"
    },
    {
        "timestamp": "2024-02-28 21:04:45.888624",
        "user": "User2",
        "msg": "Another sample message",
        "assistant": "AssistantName#1234",
        "response": "Another sample assistant response"
    }
]
```

### Sample Session (`session.json`)

Stores information about recent sessions, including assistant and thread IDs.

```json
[
    {
        "last_used": "2024-02-28 21:04:28.636313",
        "assistant_id": "asst_123456789",
        "thread_id": "thread_987654321"
    },
    {
        "last_used": "2024-02-28 19:02:40.248348",
        "assistant_id": "asst_987654321",
        "thread_id": "thread_123456789"
    }
]
```
