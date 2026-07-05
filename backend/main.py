from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import generate, review

app = FastAPI(title="契合 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate.router)
app.include_router(review.router)


@app.get("/")
async def health_check():
    return {"status": "ok", "service": "qihe-backend"}
