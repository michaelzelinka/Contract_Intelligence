# Contract Intelligence API

Extract structured data from legal contracts in seconds.

Upload a PDF → get back JSON with parties, dates, amounts, and flagged risk clauses.

## Live demo

```bash
curl -X POST https://contract-intelligence-api-0j31.onrender.com/extract \
  -H "X-API-Key: your_api_key" \
  -F "file=@contract.pdf"
```

```json
{
  "id": "25ef69ef-19a3-4396-8fa5-88387cb60469",
  "result": {
    "parties": ["TITANS s.r.o.", "Mgr. Michael Zelinka, MBA"],
    "contract_value": null,
    "start_date": null,
    "end_date": null,
    "payment_terms": null,
    "governing_law": "Czech Republic",
    "risk_flags": [
      "Subdodavatel is liable for full responsibility for borrowed technical equipment (§3.7).",
      "Penalty clause: 2,500 Kč per day for failure to return equipment or comply with terms (§3.8, §5.3).",
      "Automatic transfer of IP rights to Objednatel (§6.1, §6.2).",
      "Missing dispute resolution mechanism."
    ]
  }
}
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/extract` | Upload PDF, returns extraction ID + result |
| `GET` | `/result/{id}` | Retrieve a past extraction by ID |
| `GET` | `/health` | Health check |

## Authentication

All endpoints require an API key passed as a header:

```
X-API-Key: your_api_key
```

## What gets extracted

| Field | Description |
|-------|-------------|
| `parties` | All named parties in the contract |
| `contract_value` | Total value with currency |
| `start_date` | Contract start date (YYYY-MM-DD) |
| `end_date` | Contract end date (YYYY-MM-DD) |
| `payment_terms` | Payment conditions |
| `governing_law` | Jurisdiction |
| `risk_flags` | Potentially risky or unusual clauses with section references |

## Run locally

```bash
cp .env.example .env
# Fill in OPENAI_API_KEY and DATABASE_URL

pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Run with Docker

```bash
docker build -t contract-api .
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e DATABASE_URL=your_db_url \
  contract-api
```

## Stack

- [FastAPI](https://fastapi.tiangolo.com/) — API framework
- [PyMuPDF](https://pymupdf.readthedocs.io/) — PDF text extraction
- [OpenAI GPT-4o](https://platform.openai.com/docs/) — LLM extraction
- [PostgreSQL / Neon](https://neon.tech/) — persistence
- [Docker](https://www.docker.com/) + [Render](https://render.com/) — deployment

## Known limitations

- Scanned PDFs (image-based) are not supported — text layer required.
- First 12,000 characters of the contract are analyzed.
- Framework contracts (rámcové smlouvy) may return null for value/dates — these are defined in appendices (objednávky), not in the main body.
