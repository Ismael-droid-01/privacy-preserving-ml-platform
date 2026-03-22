from fastapi import APIRouter, HTTPException, UploadFile, File
# from app.schemas.response import UploadResponse, DatasetPreviewResponse
from ppmlp.models import DatasetSplitRequest,DatasetValidationRequest,UploadResponse,DatasetPreviewMetaDataResponse,DatasetPreviewResponse
import requests
import pickle
import pandas as pd
from fastapi import HTTPException
from Pyfhel import Pyfhel, PyCtxt
import uuid
import numpy as np
import pickle
import os
import ppmlp.config as Cfg
from ppmlp.helpers import Helpers

# STORAGE_DIR = "storage"
# os.makedirs(STORAGE_DIR, exist_ok=True)

memory_storage = {}

def save_to_memory(df: pd.DataFrame, parent_id: str = None, tag: str = "original") -> str:
    try:
        dataset_id = f"{tag}_{uuid.uuid4().hex[:8]}" 
        # dataset_id = "estudiantes"
        memory_storage[dataset_id] = {
            "df": df,
            "parent_id": parent_id,
            "type": tag
        }
        return dataset_id
    except Exception as e:
        raise Exception(f"Error al guardar en memoria: {e}")


router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.post("/upload", response_model=UploadResponse)
def upload_dataset(file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)
        dataset_id = str(uuid.uuid4())

        file_path = os.path.join(Cfg.APP_SINK_DATA_PATH, f"{dataset_id}.bin")

        with open(file_path, "wb") as f:
            pickle.dump(df, f, protocol=pickle.HIGHEST_PROTOCOL)

        return UploadResponse(
            dataset_id=dataset_id,
            message="Dataset saved as binary"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    finally:
        file.file.close()

@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
def preview_dataset(dataset_id: str):
    try:
        df = Helpers.load_dataset(dataset_id)

        metadata = {
            "columns": df.columns.tolist(),
            "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "null_counts": df.isnull().sum().to_dict()
        }

        df_head = df.head(10)
        data_dict = df_head.to_dict(orient="records")

        return DatasetPreviewResponse(
            dataset_id=dataset_id,
            metadata=metadata,
            data=data_dict,
            message="Successfully generated preview"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing dataset: {str(e)}"
        )


@router.post("/{dataset_id}/submit")
def sumbit_dataset(dataset_id: str):
    initial_mem = Helpers.get_ram_usage()
    HE, cx, cy = Helpers.encrypt_dataset(dataset_id)
    peak_mem = Helpers.get_ram_usage()

    # Temporal: Debemos de ver la manera de obtener esto mas rapido
    file_path = os.path.join(Cfg.APP_SINK_DATA_PATH, f"{dataset_id}.bin")
    with open(file_path, "rb") as f:
        df = pickle.load(f)
    n_samples = df.shape[0]
    n_features = df.shape[1] - 1

    package = {
        "context": HE.to_bytes_context(),
        "pk": HE.to_bytes_public_key(),
        "rlk": HE.to_bytes_relin_key(), 
        "cx": cx.to_bytes(),
        "cy": cy.to_bytes(),
        "n_features": n_features,
        "n_samples": n_samples
    }
    
    response = requests.post(
        "http://localhost:8001/train", 
        data=pickle.dumps(package), 
        headers={'Content-Type': 'application/octet-stream'},
        timeout=300
    )

    if response.status_code == 200:
        result_package = pickle.loads(response.content)
        return {
            "training_time": f"{result_package.get('training_time', 0):.4f}s",
            "compute_ram": f"{result_package.get('compute_ram', 0)}mb",
            "encryption_ram": f"{peak_mem - initial_mem}mb",
            "message": "Homomorphic training correctly"
        }
    else:
        return {
            "training_time": "0s",
            "message": f"Server error: {response.text}"
        }

