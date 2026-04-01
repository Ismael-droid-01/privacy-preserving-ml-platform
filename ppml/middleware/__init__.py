import ppml.services as S
from xolo.client import XoloClient
from typing import Annotated, Optional
from fastapi import Depends,Header,HTTPException
from ppml.repositories import UsersProfilesRepository
from fastapi.security import OAuth2PasswordBearer
import ppml.config as Cfg
import ppml.dtos as DTO


L = Log(
    name = __name__,
    path = Cfg.JUB_LOG_PATH
)



def get_xolo_client()->XoloClient:
    return XoloClient(
        api_url= Cfg.XOLO_API_URL,
        secret= Cfg.XOLO_SECRET_KEY
    )


def get_users_service(xolo_client:S.XoloClient = Depends(get_xolo_client))->S.UsersService:
    repository = UsersProfilesRepository()
    return S.UsersService(repository=repository, xolo=xolo_client)



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def __get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], 
    temporal_secret_key: Annotated[Optional[str], Header(alias="Temporal-Secret-Key")] = None,
    users_profiles_service: S.UsersService = Depends(get_users_service),
    xolo_client: XoloClient = Depends(get_xolo_client)
):

    try:
        user_result =  xolo_client.get_current_user(
            token = token, 
            temporal_secret = temporal_secret_key
        )
        if user_result.is_err:
            e = user_result.unwrap_err() 
            L.error({
                "msg": f"Error getting user from Xolo: {e.detail.msg}",
                "code": e.code,
                "raw_error": e.detail.raw_error
            })
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        user_dto            = user_result.unwrap()
        user_profile_result = await users_profiles_service.get_user_profile_by_username(username = user_dto.username)
        # print("User profile result:", user_profile_result)
        if user_profile_result.is_err:
            e = user_profile_result.unwrap_err()
            L.error({
                "msg": f"Error getting user profile: {e.detail}",
            })
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        user_profile    = user_profile_result.unwrap()

        return DTO.UserProfileDTO(
            username   = user_profile.username,
            user_id    = user_profile.user_id,
            email      = user_profile.email,
            is_disabled= user_profile.disabled,
            first_name = user_profile.first_name,
            last_name  = user_profile.last_name,
            fullname   = user_profile.fullname,
            settings   = DTO.UserPreferencesDTO.from_model(user_profile.settings),
            created_at = user_profile.created_at.isoformat(),
            updated_at = user_profile.updated_at.isoformat(),
        )
        # user_profile = 

    except Exception as e:
        L.error(f"Error in __get_current_user: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

async def get_current_user(
    current_user: Annotated[DTO.UserProfileDTO, Depends(__get_current_user)]
):
    if current_user.is_disabled:
        raise HTTPException(
            status_code=403,
            detail=f"User {current_user.user_id} is disabled."
        )
    return current_user
