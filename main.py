from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from openai import OpenAI
import fitz
import json
import os

from app.database import init_db, save_extraction, get_extraction
from app.auth import require_api_key

app = FastAPI(title="Contract Intelligence API")
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../prompts/extract.txt")


@app.on_event("startup")
def startup():
    init_db()


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = "\n".join(page.get_text() for page in doc)
        if not text.strip():
            raise HTTPException(
                status_code=422,
                detail="PDF appears to be scanned or empty — no text could be extracted."
            )
        return text
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to read PDF: {str(e)}")


def analyze_with_llm(text: str) -> dict:
    with open(PROMPT_PATH, "r") as f:
        system_prompt = f.read()
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text[:12000]},
            ],
        )
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="LLM returned invalid JSON.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")


@app.post("/extract")
async def extract(
    file: UploadFile = File(...),
    api_key: str = Depends(require_api_key),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    pdf_bytes = await file.read()
    text = extract_text_from_pdf(pdf_bytes)
    result = analyze_with_llm(text)
    extraction_id = save_extraction(file.filename, result)

    return {"id": extraction_id, "result": result}


@app.get("/result/{extraction_id}")
def get_result(
    extraction_id: str,
    api_key: str = Depends(require_api_key),
):
    data = get_extraction(extraction_id)
    if not data:
        raise HTTPException(status_code=404, detail="Extraction not found.")
    return data


@app.get("/health")
def health():
    return {"status": "ok"}
