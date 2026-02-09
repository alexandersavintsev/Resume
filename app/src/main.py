from fastapi import FastAPI

app = FastAPI(title="ML Resume Matching Service")

@app.get("/health")
def health():
    return {"status": "ok"}
