from contextlib import asynccontextmanager

from fastapi import FastAPI, BackgroundTasks
from starlette.responses import RedirectResponse

from server.couch_handlers import create_couch_entry
from server.handlers import execute_train, execute_infer
from server.middleware_handlers.connection import (
    server_startup,
)
from server.validation_schema import InferRequest, TrainRequest, CouchEntry


@asynccontextmanager
async def lifespan(app: FastAPI):
    server_startup()
    yield


generator = FastAPI(
    lifespan=lifespan,
    title="Generator APIary",
    description="""This is the core of the whole architecture where model blueprints \
                    (algorithms) resides. It exposes two endpoints to start a new training or inference \
                    process.
                    """,
)


@generator.post(
    "/train",
    responses={400: {"model": str}, 500: {"model": str}},
    response_model=CouchEntry,
    description="""
    This endpoint is used to start a new training process. \
    It returns a doc_id that can be used to retrieve the status of the training process. \
    The training process is executed in the background, updating the document \
    in CouchDB as soon as new results are available
    When a new model is trained, it is pushed to the middleware for storage.
    """,
)
async def train(request: TrainRequest, background_tasks: BackgroundTasks):
    """
    :param background_tasks: task to execute in background
    :param request: a request for train and infer
    :return:
    """
    couch_doc = create_couch_entry()
    background_tasks.add_task(execute_train, request, couch_doc)
    return CouchEntry(doc_id=couch_doc)


@generator.post(
    "/infer",
    responses={400: {"model": str}, 500: {"model": str}},
    response_model=CouchEntry,
    description="""
    This endpoint is used to start a new inference process. \
    Inference processes accept two kind of inputs: the first one include an example \
    dataset from which the generator will evaluate synthetic data.
    Alternatively, it is possible to uniquely send the data structure (included in model)
    It returns a doc_id that can be used to retrieve the status of the inference process. \
    The inference process is executed in the background, updating the document \
    in CouchDB as soon as new results are available
    """,
)
async def infer_data(request: InferRequest, background_tasks: BackgroundTasks):
    """
    :param background_tasks: task to execute in background
    :param request: a request for train and infer
    :return:
    """
    couch_doc = create_couch_entry()
    background_tasks.add_task(execute_infer, request, couch_doc)
    return CouchEntry(doc_id=couch_doc)


@generator.get("/", include_in_schema=False)
async def home_to_docs():
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(generator, host="0.0.0.0", port=8010)
