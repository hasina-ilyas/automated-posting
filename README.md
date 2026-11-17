# Automated Multi-Platform Posting System

FastAPI service that validates a short CTA message and publishes it across **five** third-party platforms through their official APIs.

| Detail | Value |
|---|---|
| Stack | Python 3.x, FastAPI, Uvicorn, Pydantic, HTTPX |
| Endpoint | `POST /posting` |
| Port | `4000` |
| Docs | http://localhost:4000/docs |

## Platforms

| Platform | Official docs | Auth |
|---|---|---|
| **Telegram** | [Bot API – sendMessage](https://core.telegram.org/bots/api#sendmessage) | Bot token + chat ID |
| **Discord** | [Execute Webhook](https://discord.com/developers/docs/resources/webhook#execute-webhook) | Incoming webhook URL |
| **Mastodon** | [Create status](https://docs.joinmastodon.org/methods/statuses/#create) | Access token |
| **Dev.to** | [Create article](https://developers.forem.com/api/v1#tag/articles/operation/createArticle) | API key |
| **Bluesky** | [createSession](https://docs.bsky.app/docs/api/com-atproto-server-create-session) / [createRecord](https://docs.bsky.app/docs/api/com-atproto-repo-create-record) | Handle + app password |

Each platform is isolated: if one fails, the remaining platforms still receive the message.

## Project structure

```text
automated-posting/
├── app/
│   ├── main.py
│   ├── schemas.py
│   ├── config.py
│   ├── platforms/
│   │   ├── base.py
│   │   ├── telegram.py
│   │   ├── discord.py
│   │   ├── mastodon.py
│   │   ├── devto.py
│   │   └── bluesky.py
│   └── services/
│       └── posting_service.py
├── tests/
│   └── test_posting.py
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

```bash
cd automated-posting
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in the credentials you want to use in `.env`. Platforms without credentials return a clear `failed` result and do not block the others.

## Run

```bash
uvicorn app.main:app --host 0.0.0.0 --port 4000
```

Open interactive docs: http://localhost:4000/docs

## API

### Request

```http
POST http://localhost:4000/posting
Content-Type: application/json
```

```json
{
  "message": "Check out our latest business platform and grow your online visibility. https://example.com"
}
```

### Validation rules

- Message length ≤ 200 characters
- Exactly **one** CTA link (`http://` or `https://`)
- URL must be syntactically valid

### Sample success response

```json
{
  "success": true,
  "results": [
    {
      "platform": "Telegram",
      "status": "success",
      "posted_url": "https://t.me/mychannel/42",
      "public_access": true,
      "date": "2026-11-15",
      "time": "10:30:00",
      "error": null
    },
    {
      "platform": "Discord",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": null,
      "time": null,
      "error": "Missing DISCORD_WEBHOOK_URL"
    }
  ]
}
```

`success` is `true` when **at least one** platform posts successfully.

### Sample validation error (HTTP 422)

```bash
curl -s -X POST http://localhost:4000/posting \
  -H "Content-Type: application/json" \
  -d '{"message":"hello without a link"}'
```

## Quick curl example

```bash
curl -s -X POST http://localhost:4000/posting \
  -H "Content-Type: application/json" \
  -d '{"message":"Check out our latest business platform and grow your online visibility. https://example.com"}' \
  | python3 -m json.tool
```

## Tests

```bash
pytest -q
```

## Credential notes (no secrets committed)

| Variable | Where to get it |
|---|---|
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` | [@BotFather](https://t.me/BotFather) + chat/channel ID |
| `DISCORD_WEBHOOK_URL` | Discord channel → Integrations → Webhooks |
| `MASTODON_ACCESS_TOKEN` | Mastodon Preferences → Development |
| `DEVTO_API_KEY` | [dev.to/settings/extensions](https://dev.to/settings/extensions) |
| `BLUESKY_HANDLE` / `BLUESKY_APP_PASSWORD` | Bluesky Settings → App Passwords |

Never commit `.env`. Only `.env.example` is tracked.
