from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from data_domain_service_mcp import mcp as data_domain_mcp_server
from dev_domain_service_mcp import mcp as dev_domain_mcp_server
from utility_domain_service_mcp import mcp as utility_domain_mcp_server
import contextlib
import uvicorn

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
  async with contextlib.AsyncExitStack() as stack:
    await stack.enter_async_context(data_domain_mcp_server.session_manager.run())
    await stack.enter_async_context(dev_domain_mcp_server.session_manager.run())
    await stack.enter_async_context(utility_domain_mcp_server.session_manager.run())
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

app.mount("/data-domain-service-mcp", data_domain_mcp_server.streamable_http_app())
app.mount("/dev-domain-service-mcp", dev_domain_mcp_server.streamable_http_app())
app.mount("/utility-domain-service-mcp", utility_domain_mcp_server.streamable_http_app())
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=20000, log_level="debug")