import os 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import calpulli.config as Cfg
from calpulli.controllers import calpulli_routers,users_profile_router, algorithms_router, numeric_parameters_router, string_parameters_router, tasks_router, results_router, datasets_router
from tortoise.contrib.fastapi import register_tortoise
from contextlib import asynccontextmanager

from calpulli.core.worker.consumer import TaskConsumer

from calpulli.log import Log
import calpulli.config as Cfg

L= Log(
    name= __name__,
    path= Cfg.CALPULLI_LOG_PATH
)




@asynccontextmanager
async def lifespan(app: FastAPI):
    L.debug("Starting lifespan context manager")
    
    task_consumer = TaskConsumer(n_workers=Cfg.CALPULLI_WORKERS_COUNT, max_queue_size=Cfg.CALPULLI_WORKER_QUEUE_SIZE)
    app.state.task_consumer = task_consumer
    L.debug("Starting TaskConsumer")
    await app.state.task_consumer.start()
    # Create dataset sink directory if it doesn't exist
    try:
        if not os.path.exists(Cfg.CALPULLI_DATASET_SINK_PATH):
            os.makedirs(Cfg.CALPULLI_DATASET_SINK_PATH,exist_ok=True)
            L.debug(f"Created dataset sink path: {Cfg.CALPULLI_DATASET_SINK_PATH}")
        else:
            L.debug(f"Dataset sink path already exists: {Cfg.CALPULLI_DATASET_SINK_PATH}")
    except Exception as e:
        L.error(f"Error creating dataset sink at {Cfg.CALPULLI_DATASET_SINK_PATH}: {e}")
        # raise e

    yield
    L.debug("Stopping lifespan context manager")
    await app.state.task_consumer.stop()





app = FastAPI(
    title   = Cfg.CALPULLI_APP_TITLE,
    version = Cfg.CALPULLI_APP_VERSION,
    lifespan=lifespan
)
register_tortoise(
    app,
    db_url=Cfg.CALPULLI_DB_URL,
    modules={"models": ["calpulli.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = Cfg.CALPULLI_APP_ORIGINS,
    allow_credentials = Cfg.CALPULLI_APP_CREDENTIALS,
    allow_methods     = Cfg.CALPULLI_APP_METHODS,
    allow_headers     = Cfg.CALPULLI_APP_HEADERS,
)

app.include_router(calpulli_routers,tags=["calpulli"])
app.include_router(users_profile_router,tags=["users_profile"])
app.include_router(algorithms_router,tags=["algorithms"])
app.include_router(numeric_parameters_router,tags=["numeric_parameters"])
app.include_router(string_parameters_router, tags=["string_parameters"])
app.include_router(tasks_router, tags=["tasks"])
app.include_router(results_router, tags=["results"])
app.include_router(datasets_router, tags=["datasets"])