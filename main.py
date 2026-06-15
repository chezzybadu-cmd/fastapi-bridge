from fastapi import FastAPI, HTTPException
from models import SignalPayload
from forwarder import forward_to_anything
import datetime

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.datetime.utcnow()}

@app.post("/signal")
async def receive_signal(payload: SignalPayload):
    try:
        forward_to_anything(payload.dict())
        return {"status": "forwarded", "data": payload}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/performance")
def get_performance():
    return {"message": "Anything.com will fetch performance from its own DB"}

@app.get("/backtest")
def get_backtest():
    return {"message": "Backtest results will be stored in Anything.com"}

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
