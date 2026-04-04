import asyncio
import pytest
from tortoise import Tortoise
from ppml.dtos import AlgorithmCreateFormDTO
from ppml.repositories import AlgorithmsRepository
from ppml.services import AlgorithmsService

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

@pytest.mark.asyncio
async def test_create_algorithm_service():
    repo = AlgorithmsRepository()
    service = AlgorithmsService(repository=repo)

    result = await service.create_algorithm(AlgorithmCreateFormDTO(
        name="LinearRegression",
        type="regression"
    ))

    assert result.is_ok
    assert result.unwrap().name == "LinearRegression"


@pytest.mark.asyncio
async def test_create_algorithm_duplicate_service():
    repo = AlgorithmsRepository()
    service = AlgorithmsService(repository=repo)

    await service.create_algorithm(AlgorithmCreateFormDTO(
        name="SVM", type="classification"
    ))
    result = await service.create_algorithm(AlgorithmCreateFormDTO(
        name="SVM", type="classification"
    ))

    assert result.is_err

@pytest.mark.asyncio
async def test_get_algorithms_service():
    repo = AlgorithmsRepository()
    service = AlgorithmsService(repository=repo)

    await service.create_algorithm(AlgorithmCreateFormDTO(
        name="LinearRegression",
        type="regression"
    ))

    result = await service.get_algorithms()

    assert result.is_ok
    algorithms = result.unwrap()
    assert isinstance(algorithms, list)
    assert len(algorithms) > 0
    assert all(hasattr(alg, "algorithm_id") for alg in algorithms)
    assert all(hasattr(alg, "name") for alg in algorithms)
    assert all(hasattr(alg, "type") for alg in algorithms)


@pytest.mark.asyncio
async def test_get_algorithm_by_id_service():
    repo = AlgorithmsRepository()
    service = AlgorithmsService(repository=repo)

    create_result = await service.create_algorithm(AlgorithmCreateFormDTO(
        name="KMEANS",
        type="classification"
    ))
    assert create_result.is_ok
    algorithm_id = create_result.unwrap().algorithm_id

    result = await service.get_algorithm_by_id(algorithm_id=algorithm_id)

    assert result.is_ok
    algorithm = result.unwrap()
    assert algorithm.algorithm_id == algorithm_id
    assert algorithm.name == "KMEANS"


@pytest.mark.asyncio
async def test_get_algorithm_by_id_not_found_service():
    repo = AlgorithmsRepository()
    service = AlgorithmsService(repository=repo)

    result = await service.get_algorithm_by_id(algorithm_id=999999)

    assert result.is_err