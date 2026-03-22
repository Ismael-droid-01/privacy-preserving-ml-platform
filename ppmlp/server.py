from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import ppmlp.config as Cfg
from ppmlp.controllers import ppml_router
app = FastAPI(
    title   = Cfg.APP_TITLE,
    version = Cfg.APP_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = Cfg.APP_ORIGINS,
    allow_credentials = Cfg.APP_CREDENTIALS,
    allow_methods     = Cfg.APP_METHODS,
    allow_headers     = Cfg.APP_HEADERS,
)

app.include_router(ppml_router,tags=["ppml"])