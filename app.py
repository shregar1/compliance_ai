import os
import uvicorn

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from controllers.apis import router as APIRouter

from middlewares.request_context import RequestContextMiddleware

app = FastAPI()

load_dotenv()
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    response_payload: dict = {
        "transaction_urn": request.state.urn,
        "response_message": "Bad or missing input.",
        "response_key": "error_bad_input",
        "errors": exc.errors()
    }
    return JSONResponse(
        status_code=400,
        content=response_payload,
    )

app.add_middleware(
    middleware_class=TrustedHostMiddleware, 
    allowed_hosts=["*"]
)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.debug("Initialising middleware stack")
app.add_middleware(RequestContextMiddleware)
logger.debug("Initialised middleware stack")

logger.debug("Initialising routers")
app.include_router(APIRouter)
logger.debug("Initialised routers")

if __name__ == '__main__':
    uvicorn.run("app:app", port=PORT, host=HOST, reload=True)