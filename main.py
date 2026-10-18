import time
import uuid

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

EMAIL = "23f3003379@ds.study.iitm.ac.in"
ALLOWED_ORIGIN = "https://dash-16xgtq.example.com"

app = FastAPI()

# 1) CORS added FIRST
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],      # exact origin only, no "*"
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=False,
    expose_headers=["X-Request-ID", "X-Process-Time"],
)

# 2) Header middleware added LAST, so it is the outermost layer and also
#    wraps the CORS preflight responses (every response must carry the headers)
@app.middleware("http")
async def add_request_headers(request: Request, call_next):
    start = time.perf_counter()
    request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.6f}"
    return response


@app.get("/")
def health():
    return {"status": "ok"}


@app.get("/stats")
def stats(values: str = Query(...)):
    try:
        nums = [int(x.strip()) for x in values.split(",") if x.strip() != ""]
    except ValueError:
        raise HTTPException(status_code=400, detail="values must be comma-separated integers")
    if not nums:
        raise HTTPException(status_code=400, detail="no values provided")

    total = sum(nums)
    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": total,
        "min": min(nums),
        "max": max(nums),
        "mean": total / len(nums),
    }
