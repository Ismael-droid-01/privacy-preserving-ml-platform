import pytest
from ppml.services import TasksService
from ppml.repositories import TasksRepository, UsersProfilesRepository, AlgorithmsRepository
from ppml.dtos import TaskCreateFormDTO

async def create_test_user(suffix: str = ""):
    repo = UsersProfilesRepository()
    result = await repo.create(
        user_id    = f"test-user-id-{suffix}",
        username   = f"testuser{suffix}",
        email      = f"testuser{suffix}@test.com",
        first_name = "Test",
        last_name  = "User",
    )
    return result.unwrap()

async def create_test_algorithm(name: str = "TestAlgo"):
    repo = AlgorithmsRepository()
    result = await repo.create(name=name, type="classification")
    return result.unwrap()


@pytest.mark.asyncio
async def test_create_task_service():
    user      = await create_test_user(suffix="create")
    algorithm = await create_test_algorithm(name="AlgoCreate")
    
    service = TasksService(repository=TasksRepository())
    dto     = TaskCreateFormDTO(algorithm_id=algorithm.algorithm_id, response_time=1.23)
    result  = await service.create_task(user_id=user.user_id, dto=dto)

    assert result.is_ok
    task = result.unwrap()
    assert task.user_id      == user.user_id
    assert task.algorithm_id == algorithm.algorithm_id
    assert task.response_time == 1.23
    assert task.task_id is not None


@pytest.mark.asyncio
async def test_create_task_user_not_found_service():
    algorithm = await create_test_algorithm(name="AlgoUserNotFound")
    
    service = TasksService(repository=TasksRepository())
    dto     = TaskCreateFormDTO(algorithm_id=algorithm.algorithm_id, response_time=0.5)
    result  = await service.create_task(user_id="nonexistent-user-id", dto=dto)

    assert result.is_err


@pytest.mark.asyncio
async def test_create_task_algorithm_not_found_service():
    user = await create_test_user(suffix="algonotfound")

    service = TasksService(repository=TasksRepository())
    dto     = TaskCreateFormDTO(algorithm_id=999999, response_time=0.5)
    result  = await service.create_task(user_id=user.user_id, dto=dto)

    assert result.is_err


@pytest.mark.asyncio
async def test_get_tasks_by_user_service():
    user      = await create_test_user(suffix="getbyuser")
    algorithm = await create_test_algorithm(name="AlgoGetByUser")

    service = TasksService(repository=TasksRepository())
    dto     = TaskCreateFormDTO(algorithm_id=algorithm.algorithm_id, response_time=2.0)

    await service.create_task(user_id=user.user_id, dto=dto)
    await service.create_task(user_id=user.user_id, dto=dto)

    result = await service.get_tasks_by_user(user_id=user.user_id)

    assert result.is_ok
    tasks = result.unwrap()
    assert isinstance(tasks, list)
    assert len(tasks) >= 2
    assert all(t.user_id == user.user_id for t in tasks)

@pytest.mark.asyncio
async def test_get_tasks_by_user_not_found_service():
    service = TasksService(repository=TasksRepository())
    result  = await service.get_tasks_by_user(user_id="nonexistent-user-id")

    assert result.is_err


@pytest.mark.asyncio
async def test_get_tasks_by_user_empty_service():
    user = await create_test_user(suffix="empty")

    service = TasksService(repository=TasksRepository())
    result  = await service.get_tasks_by_user(user_id=user.user_id)

    if result.is_ok:
        assert result.unwrap() == []
    else:
        assert result.is_err