from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.middleware import CorrelationIdMiddleware


def test_correlation_id_middleware_generates_new_id():
    app = FastAPI()
    app.add_middleware(CorrelationIdMiddleware)

    @app.get("/")
    async def index():
        return {"hello": "world"}

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "x-request-id" in response.headers
    x_id = response.headers["x-request-id"]
    assert x_id.startswith("req-")
    assert len(x_id) == 12  # "req-" (4) + 8-char hex (8) = 12 characters
    assert "x-response-time-ms" in response.headers


def test_correlation_id_middleware_preserves_existing_id():
    app = FastAPI()
    app.add_middleware(CorrelationIdMiddleware)

    @app.get("/")
    async def index():
        return {"hello": "world"}

    client = TestClient(app)
    response = client.get("/", headers={"x-request-id": "custom-id-123"})
    assert response.status_code == 200
    assert "x-request-id" in response.headers
    assert response.headers["x-request-id"] == "custom-id-123"
    assert "x-response-time-ms" in response.headers
