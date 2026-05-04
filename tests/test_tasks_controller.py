import pytest
from calpulli.dtos import TaskCreateFormDTO
from calpulli.server import app
from calpulli.models import Algorithm, NumericParameter,NumericParameterType,AlgorithmType
import calpulli.dtos as DTO

@pytest.mark.asyncio
async def test_create_task_service(prepare_with_user_algorithm_client):
    user,algorithm,client = prepare_with_user_algorithm_client
    headers ={"Authorization": f"Bearer {user.access_token}", "Temporal-Secret-Key": user.temporal_secret}

    dto = TaskCreateFormDTO(algorithm_id=algorithm.algorithm_id, response_time=1.23)
    response = await client.post("/tasks",json=dto.model_dump(),headers = headers) 
    assert response.status_code == 200  # Validación de campos faltantes
   

@pytest.mark.asyncio
async def test_create_new_task_integration(get_user_clean_and_get_client):
    user,client =  get_user_clean_and_get_client
    
    # A. Preparar los datos reales en la base de datos en memoria
    
    algo = await Algorithm.create(name="Kmeans", type=AlgorithmType.UNSUPERVISED)
    
    param = await NumericParameter.create(
        algorithm     = algo,
        name          = "k",
        type          = NumericParameterType.INTEGER,
        default_value = 2,
        max_value     = 100
    )

    payload = DTO.TaskCreateAggregateDTO(
        algorithm_id   = algo.algorithm_id,
        numeric_values = [],
        string_values  = [],
        # user_id        = user.
    )
    
    # C. Ejecutar la petición HTTP
    headers = {"Authorization": f"Bearer {user.access_token}", "Temporal-Secret-Key": user.temporal_secret}
    response = await client.post("/tasks/run", json=payload.model_dump(),headers=headers)
    
    # D. Validaciones HTTP
    print("Response status code:", response)
    assert response.status_code == 200



@pytest.mark.asyncio
async def test_get_my_tasks_endpoint(prepare_with_user_algorithm_task_client):
    user,_,task,client = prepare_with_user_algorithm_task_client
    headers = {"Authorization": f"Bearer {user.access_token}", "Temporal-Secret-Key": user.temporal_secret}
    response = await client.get("/tasks/my-tasks",headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # assert all(t["user_id"] == user.user_id for t in data)


@pytest.mark.asyncio
async def test_get_task_by_id_endpoint(prepare_with_user_algorithm_task_client):
    user,_,tasks,client = prepare_with_user_algorithm_task_client
    headers = {"Authorization": f"Bearer {user.access_token}", "Temporal-Secret-Key": user.temporal_secret}
    task = tasks[0]
    response = await client.get(f"/tasks/{task.task_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"]  == task.task_id
    assert data["algorithm_id"]  == task.algorithm_id


@pytest.mark.asyncio
async def test_get_task_by_id_not_found_endpoint(prepare_with_user_algorithm_task_client):
    user,_,_,client = prepare_with_user_algorithm_task_client
    headers = {"Authorization": f"Bearer {user.access_token}", "Temporal-Secret-Key": user.temporal_secret}
    response = await client.get("/tasks/999999", headers=headers)

    app.dependency_overrides.clear()

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_task_unauthorized_endpoint(prepare_with_user_algorithm_task_client):
    user, algorithm, tasks, client = prepare_with_user_algorithm_task_client
    task = tasks[0]
    headers = {"Authorization": f"Bearer {user.access_token}", "Temporal-Secret-Key": "invalid-temporal-secret"}
    response = await client.get(f"/tasks/{task.task_id}", headers=headers)
    assert response.status_code == 401