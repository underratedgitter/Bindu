from types import SimpleNamespace

from starlette.testclient import TestClient
from slowapi.middleware import SlowAPIMiddleware

from bindu.server.applications import BinduApplication


def _make_minimal_manifest():
    return SimpleNamespace(
        capabilities={"extensions": []},
        url="http://localhost:3773",
        name="test_agent",
    )


def _make_dummy_task_manager():
    return SimpleNamespace(is_running=True)


def test_rate_limiting_middleware_is_registered():
    app = BinduApplication(manifest=_make_minimal_manifest(), debug=True)

    middleware_classes = [m.cls for m in app.user_middleware]
    assert SlowAPIMiddleware in middleware_classes
    assert hasattr(app.state, "limiter")


def test_health_endpoint_is_rate_limited():
    app = BinduApplication(manifest=_make_minimal_manifest(), debug=True)
    app.task_manager = _make_dummy_task_manager()

    client = TestClient(app)

    last_response = None
    for _ in range(6):
        last_response = client.get("/health")

    assert last_response is not None
    assert last_response.status_code == 429
    assert last_response.json()["error"] == "rate_limit_exceeded"
    assert "Retry-After" in last_response.headers
