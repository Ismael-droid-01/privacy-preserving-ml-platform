import os
from fastapi import APIRouter as Router, Depends, File, HTTPException, UploadFile
import calpulli.middleware as MX
import calpulli.services as S
import calpulli.dtos as DTO

from calpulli.log import Log
import calpulli.config as Cfg

L= Log(
    name= __name__,
    path= Cfg.CALPULLI_LOG_PATH
)

router = Router(prefix="/datasets")

@router.post("")
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: DTO.UserProfileDTO = Depends(MX.get_current_user),
    service: S.DatasetsService = Depends(MX.get_datasets_service)
):
    raw_filename = file.filename or ""
    sanitized_filename = os.path.basename(raw_filename)

    if not sanitized_filename:
        raise HTTPException(status_code=400, detail="File must have a valid name")

    name, ext = os.path.splitext(sanitized_filename)
    
    normalized_name = name.strip()
    extension = ext.lstrip(".")

    if not normalized_name or not extension:
        raise HTTPException(status_code=400, detail="The file must have a valid name and extension")
    
    writing_result = await service.write_dataset_file(filename=sanitized_filename, file_data=file.file)
    if writing_result.is_err:
        L.error(f"Error writing dataset file: {writing_result.unwrap_err()}")
        raise HTTPException(status_code=500, detail="Error saving dataset file")
    L.info(f"Dataset file written successfully: {sanitized_filename}")

    result = await service.register(
        user_id=current_user.user_id,
        name=normalized_name,
        extension=extension
    )
    
    if result.is_err:
        L.error(f"Error registering dataset: {result.unwrap_err()}")
        raise HTTPException(status_code=500, detail=str(result.unwrap_err()))
    
    # dataset_id = result.unwrap().dataset_id
    # dest_path =f"{Cfg.CALPULLI_DATASET_SINK_PATH}/{normalized_name}"

    L.info(f"Dataset registered successfully: {result.unwrap().dataset_id}")
    return result.unwrap()

@router.get("", response_model=list[DTO.DatasetDTO])
async def get_users_datasets(
    current_user: DTO.UserProfileDTO = Depends(MX.get_current_user),
    service: S.DatasetsService = Depends(MX.get_datasets_service)
):
    result = await service.get_by_user_id(user_id=current_user.user_id)
    if result.is_ok:
        return result.unwrap()
    raise HTTPException(status_code=500, detail=str(result.unwrap_err()))

@router.delete("/{dataset_id}")
async def delete_dataset(
    dataset_id: int,
    current_user: DTO.UserProfileDTO = Depends(MX.get_current_user),
    service: S.DatasetsService = Depends(MX.get_datasets_service)
):
    result = await service.delete(user_id=current_user.user_id, dataset_id=dataset_id)
    if result.is_ok:
        return {"message": "Dataset deleted successfully"}
    
    error = result.unwrap_err()
    error_detail = str(error)
    if "not found" in error_detail.lower():
        raise HTTPException(status_code=404, detail=error_detail)
    
    raise HTTPException(status_code=500, detail=error_detail)