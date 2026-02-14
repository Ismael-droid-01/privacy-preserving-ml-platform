from fastapi import APIRouter, HTTPException
from app.schemas.request import DatasetValidationRequest
from app.schemas.response import DatasetPreviewMetaDataResponse, PreprocessResponse, UploadResponse, DatasetPreviewResponse
from app.data.loader import load_csv_from_base64
from app.data.validator import summarize_dataset
from app.data.storage import save_temp_dataset
from app.data.loader import get_dataset_head, get_dataset_metadata
from app.core.config import settings
from pathlib import Path
from app.logic.encryption import encrypt_dataset_ckks

router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.post("/upload", response_model=UploadResponse)
def upload_dataset(request: DatasetValidationRequest):
    try:
        df = load_csv_from_base64(request.dataset_base64)
        dataset_id = save_temp_dataset(df)

        return UploadResponse(
            dataset_id=dataset_id,
            message="Dataset cargado correctamente"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al cargar: {str(e)}")

@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
def preview_dataset(dataset_id: str):
    try:
        file_path = Path(settings.RAW_DATA_PATH) / f"{dataset_id}.csv"

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="El dataset no existe.")
        
        metadata = get_dataset_metadata(file_path)

        df_head = get_dataset_head(file_path)
        data_dict = df_head.to_dict(orient="records")

        return DatasetPreviewResponse(
            dataset_id=dataset_id,
            metadata=metadata,
            data=data_dict,
            message="Vista previa generada correctamente"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer el dataset: {str(e)}")

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
    
###############################################################################
@router.post(
    "/validate-and-summarize",
    response_model=PreprocessResponse
)
def validate_and_summarize(request: DatasetValidationRequest):
    try:
        # Cargar (En memoria)
        df = load_csv_from_base64(request.dataset_base64)

        # Guardar (Persistencia)
        dataset_id = save_temp_dataset(df)

        summary_data = summarize_dataset(df, request.target)
        summary_data["dataset_id"] = dataset_id
        
        return PreprocessResponse(
            summary=summary_data,
            isValid=True,
            message="Dataset procesado correctamente"
        )
    except Exception as e:
        return PreprocessResponse(
            summary=None,
            isValid=False,
            message=f"Error en validacion: {str(e)}"
        )

    