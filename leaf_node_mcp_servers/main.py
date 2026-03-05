from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from file_service_mcp import mcp as file_service_mcp_server
from transform_service_mcp import mcp as transform_service_mcp_server
from analysis_service_mcp import mcp as analysis_service_mcp_server
from compute_service_mcp import mcp as compute_service_mcp_server
import contextlib
import uvicorn

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
  async with contextlib.AsyncExitStack() as stack:
    await stack.enter_async_context(file_service_mcp_server.session_manager.run())
    await stack.enter_async_context(transform_service_mcp_server.session_manager.run())
    await stack.enter_async_context(analysis_service_mcp_server.session_manager.run())
    await stack.enter_async_context(compute_service_mcp_server.session_manager.run())
    yield

app = FastAPI(lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

app.mount("/file-service-mcp", file_service_mcp_server.streamable_http_app())
app.mount("/transform-service-mcp", transform_service_mcp_server.streamable_http_app())
app.mount("/analysis-service-mcp", analysis_service_mcp_server.streamable_http_app())
app.mount("/compute-service-mcp", compute_service_mcp_server.streamable_http_app())
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=10000, log_level="debug")