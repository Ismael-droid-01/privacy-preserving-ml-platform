from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

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