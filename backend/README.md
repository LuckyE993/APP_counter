# Beancount Accounting Agent - Backend

FastAPI backend for intelligent accounting with VLM-powered bill recognition.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run development server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- `POST /api/parse/image` - Parse bill screenshot
- `POST /api/parse/text` - Parse natural language text
- `POST /api/transaction` - Save transaction to Beancount
- `GET /api/balance` - Get account balances
- `GET /api/accounts` - Get account list

## Docker

```bash
docker-compose up --build
```

## Configuration

See `.env.example` for available configuration options.
