from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="URL Shrotner App", debug=True)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True)


@app.get("/")
async def root():
    return {"message": "URL Shortner App", "docs": "/docs"}
