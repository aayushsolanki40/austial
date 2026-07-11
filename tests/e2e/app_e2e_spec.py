"""End-to-end test -- mirrors a Nest ``*.e2e-spec.ts`` test: spin up a real
(in-process) app via ``austial.testing`` + ``httpx``'s ASGI transport, and hit
routes exactly like a client would, no mocking of the HTTP layer at all.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from austial.testing import Test
from src.app_controller import AppController
from src.app_service import AppService
from src.modules.cats.cats_module import CatsModule
from src.modules.health.health_module import HealthModule


async def _make_client(app):
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


@pytest.mark.asyncio
async def test_root_and_health_endpoints():
    module = await Test.create_testing_module(
        imports=[HealthModule],
        controllers=[AppController],
        providers=[AppService],
    ).compile()
    app = module.create_austial_application()
    await app.init()

    async with await _make_client(app) as client:
        root_response = await client.get("/")
        assert root_response.status_code == 200
        assert "message" in root_response.json()

        health_response = await client.get("/health")
        assert health_response.status_code == 200
        body = health_response.json()
        assert body["status"] == "ok"
        assert "memory_heap" in body["info"]

        protected_denied = await client.get("/health/protected")
        assert protected_denied.status_code == 403

        protected_allowed = await client.get("/health/protected", headers={"x-api-key": "changeme"})
        assert protected_allowed.status_code == 200


@pytest.mark.asyncio
async def test_cats_crud_flow():
    module = await Test.create_testing_module(imports=[CatsModule]).compile()
    app = module.create_austial_application()
    await app.init()

    async with await _make_client(app) as client:
        create_response = await client.post("/cats", json={"name": "Whiskers"})
        assert create_response.status_code == 201
        created = create_response.json()
        cat_id = created["id"]
        assert created["name"] == "Whiskers"

        list_response = await client.get("/cats")
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1

        get_response = await client.get(f"/cats/{cat_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Whiskers"

        update_response = await client.patch(f"/cats/{cat_id}", json={"name": "Mittens"})
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "Mittens"

        delete_response = await client.delete(f"/cats/{cat_id}")
        assert delete_response.status_code == 200
        assert delete_response.json() == {"deleted": True}

        final_list = await client.get("/cats")
        assert final_list.json() == []


@pytest.mark.asyncio
async def test_not_found_returns_nest_shaped_error():
    module = await Test.create_testing_module(imports=[CatsModule]).compile()
    app = module.create_austial_application()
    await app.init()

    async with await _make_client(app) as client:
        response = await client.get("/cats/999")
        assert response.status_code == 404
        body = response.json()
        assert body["statusCode"] == 404
        assert "timestamp" in body
        assert body["path"] == "/cats/999"
