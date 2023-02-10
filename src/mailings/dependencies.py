from src.config import get_settings
from src.mailings.endpoints import Endpoint, APIEndpoint, TestEndpoint


async def get_endpoint() -> Endpoint:
    endpoint_url = get_settings().endpoint_url
    endpoint = APIEndpoint(endpoint_url) if endpoint_url else TestEndpoint()
    return endpoint


async def get_endpoint_stub() -> None:
    raise NotImplementedError
