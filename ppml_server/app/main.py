from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import tenseal as ts

class HomomorphicLogisticRegression:
    def __init__(self, context_bytes: bytes):
        self.context = ts.context_from(context_bytes)
        self.w = None
        self.b = None

    def train(self, enc_X_bytes: List[bytes], enc_y_bytes: List[bytes], lr: float = 0.05):
        pass

app = FastAPI(
    title="privacy-preserving-ml-platform",
    version="1.0",
    description="API for a machine learning platform that preserves data privacy.",

)

# Request schema
class TrainingTask(BaseModel):
    X: List[List[float]]
    y: List[int]

# Endpoints
@app.get("/")
def root():
    return {
        "service": app.title,
        "status": "running",
        "version": app.version
    }

@app.post("/train")
def run_training_job(request: TrainingTask):
    

    return {
        "message": "Everything is gonna be ok!"
    }