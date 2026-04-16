# Contract Intelligence API

Extract structured data from legal contracts in seconds.

Upload a PDF → get back JSON with parties, dates, amounts, and flagged risk clauses.

## Example response

```json
{
  "parties": ["Acme s.r.o.", "Beta a.s."],
  "contract_value": "1 200 000 CZK",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "payment_terms": "Net 30 days",
  "governing_law": "Czech Republic",
  "risk_flags": [
    "Unlimited liability clause — §12.3",
    "Automatic renewal without notice — §8.1"
  ]
}
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/extract` | Upload PDF, returns extracted JSON |
| GET | `/health` | Health check |

## Run locally

```bash
cp .env.example .env
# Add your OPENAI_API_KEY to .env

pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Run with Docker

```bash
docker build -t contract-api .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key contract-api
```

## Test with curl

```bash
curl -X POST http://localhost:8000/extract \
  -F "file=@your_contract.pdf"
```

## Known limitations

- Scanned PDFs (image-based) are not supported — text layer required.
- First 12 000 characters of the contract are analyzed (covers most standard contracts).

## Stack

- [FastAPI](https://fastapi.tiangolo.com/)
- [PyMuPDF](https://pymupdf.readthedocs.io/)
- [OpenAI GPT-4o](https://platform.openai.com/docs/)
- Docker + Render
