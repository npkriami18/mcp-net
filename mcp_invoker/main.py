from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcp_invoker import mcp as mcp_invoker_server
import contextlib
import uvicorn


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):

    async with contextlib.AsyncExitStack() as stack:

        await stack.enter_async_context(
            mcp_invoker_server.session_manager.run()
        )

        yield


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/mcp-invoker", mcp_invoker_server.streamable_http_app())


if __name__ == "__main__":

    uvicorn.run(
        app,
        host="localhost",
        port=30001,
        log_level="debug"
    )