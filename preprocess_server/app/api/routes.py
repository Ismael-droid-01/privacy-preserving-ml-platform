from fastapi import APIRouter, HTTPException
from app.schemas.request import DatasetValidationRequest
from app.schemas.response import UploadResponse, DatasetPreviewResponse
from app.data.loader import load_csv_from_base64
from app.core.config import settings
from pathlib import Path
from app.logic.encryption import encrypt_dataset_ckks

import pandas as pd
import uuid
memory_storage = {}
def save_to_memory(df: pd.DataFrame) -> str:
    try:
        dataset_id = str(uuid.uuid4())
        memory_storage[dataset_id] = df
        return dataset_id
    except Exception as e:
        raise Exception(f"Error al guardar en memoria: {e}")



router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.post("/upload", response_model=UploadResponse)
def upload_dataset(request: DatasetValidationRequest):
    try:
        df = load_csv_from_base64(request.dataset_base64)
        dataset_id = save_to_memory(df)

        return UploadResponse(
            dataset_id=dataset_id,
            message="Dataset cargado correctamente"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al cargar: {str(e)}")


@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
def preview_dataset(dataset_id: str):
    try:
        df = memory_storage.get(dataset_id)

        if df is None:
            raise HTTPException(
                status_code=404, 
                detail="El dataset no existe en memoria. Es posible que el servidor se haya reiniciado."
            )
        
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
            message="Vista previa generada correctamente desde memoria"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al procesar el dataset en RAM: {str(e)}"
        )

@router.post("/{dataset_id}/encrypt")
def encrypt_dataset(dataset_id: str):
    try:
        # settings.PROCESSED_DATA_PATH
        file_path = Path(settings.RAW_DATA_PATH) / f"{dataset_id}.csv"
        print(file_path)
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404, 
                detail="Debes preprocesar el dataset antes de cifrarlo."
            )

        encrypted_dataset = encrypt_dataset_ckks(file_path)

        return {
            "dataset_id": dataset_id,
            "context": encrypted_dataset["context"],
            "encrypted_vector": encrypted_dataset["encrypted_vectors"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    