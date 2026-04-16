from fastapi import FastAPI, UploadFile, File, HTTPException
from openai import OpenAI
import fitz  # pymupdf
import json
import os

app = FastAPI(title="Contract Intelligence API")
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../prompts/extract.txt")


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = "\n".join(page.get_text() for page in doc)
        if not text.strip():
            raise HTTPException(status_code=422, detail="PDF appears to be scanned or empty — no text could be extracted.")
        return text
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
async def extract(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    pdf_bytes = await file.read()
    text = extract_text_from_pdf(pdf_bytes)
    result = analyze_with_llm(text)
    return result


@app.get("/health")
def health():
    return {"status": "ok"}
