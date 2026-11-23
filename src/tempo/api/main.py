from fastapi import FastAPI

app = FastAPI(title="Tempo")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
