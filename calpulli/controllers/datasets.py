import os
from fastapi import APIRouter as Router, Depends, HTTPException, UploadFile
import calpulli.middleware as MX
import calpulli.services as S
import calpulli.dtos as DTO

router = Router(prefix="/datasets")

@router.post("")
async def upload_dataset(
    file: UploadFile,
    current_user: DTO.UserProfileDTO = Depends(MX.get_current_user),
    service: S.DatasetsService = Depends(MX.get_datasets_service)
):
    name, ext = os.path.splitext(file.filename)
    extension = ext.lstrip(".")

    result = await service.register(
        user_id=current_user.user_id,
        name=name,
        extension=extension
    )
    if result.is_ok:
        return result.unwrap()
    raise HTTPException(status_code=500, detail=str(result.unwrap_err()))

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
    raise HTTPException(status_code=500, detail=str(result.unwrap_err()))