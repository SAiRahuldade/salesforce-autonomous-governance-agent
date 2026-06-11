from fastapi import FastAPI

app = FastAPI(title="Salesforce Autonomous Governance Agent")


@app.get("/health")
def health_check():
    return {"status": "ok"}
