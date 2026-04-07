import asyncio
import os
from dotenv import load_dotenv
import pytest
from tortoise import Tortoise

from ppml.dtos import TaskCreateFormDTO, UserProfileDTO
from ppml.models import Task, UserProfile, Algorithm, NumericParameter, StringParameter, Result as ResultModel
from ppml.repositories import AlgorithmsRepository, TasksRepository, UsersProfilesRepository

def pytest_configure(config):
    if os.path.exists(".env.test"):
        load_dotenv(dotenv_path=".env.test")

TEST_DB_URL = "mysql://samuel_user:samuel_password@localhost:3306/ppml_database" 
@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True, scope="session")
async def initialize_tests():
    # Setup: Initialize Tortoise with your models
    await Tortoise.init(
        db_url=TEST_DB_URL,
        modules={'models': ['ppml.models']}
    )
    await Tortoise.generate_schemas()
    
    yield # Tests run here
    
    # Teardown: Clean up
    await Tortoise.close_connections()

@pytest.fixture(autouse=True)
async def clean_database():
    await _clean()
    yield
    await _clean()

async def _clean():
    await ResultModel.all().delete()
    await Task.all().delete()         
    await NumericParameter.all().delete()
    await StringParameter.all().delete()
    await Algorithm.all().delete()    
    await UserProfile.all().delete()

def mock_current_user(user_id: str, username: str):
    """Genera un override de get_current_user para simular autenticación."""
    async def _mock():
        return UserProfileDTO(
            user_id    = user_id,
            username   = username,
            email      = f"{username}@test.com",
            first_name = "Test",
            last_name  = "User",
            is_disabled= False,
            created_at = "2024-01-01T00:00:00",
            updated_at = "2024-01-01T00:00:00",
        )
    return _mock

async def create_test_user(suffix: str = ""):
    repo = UsersProfilesRepository()
    result = await repo.create(
        user_id    = f"test-user-id-{suffix}",
        username   = f"testuser{suffix}",
        email      = f"testuser{suffix}@example.com",
        first_name = f"TestFirstName{suffix}",
        last_name  = f"TestLastName{suffix}"
    )
    return result.unwrap()

async def create_test_algorithm(name: str = "TestAlgo"):
    repo = AlgorithmsRepository()
    result = await repo.create(name=name, type="classification")
    return result.unwrap()

async def create_test_task(user_id: str, algorithm_id: int):
    repo = TasksRepository()
    dto = TaskCreateFormDTO(algorithm_id=algorithm_id, response_time=1.23)
    result = await repo.create(user_id=user_id, algorithm_id=algorithm_id, response_time=dto.response_time)
    return result.unwrap()