import json
from string import Template
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, Response

well_known = APIRouter(prefix="/.well-known", tags=["well-known"])


def get_host(request: Request):
    host_header = request.headers.get("X-Forwarded-Host") or request.headers.get("Host")
    protocol = request.headers.get("X-Forwarded-Proto") or request.url.scheme
    return f"{protocol}://{host_header}"


def get_ai_plugin():
    with open("ai-plugin.json", encoding="utf-8") as file:
        return json.loads(file.read())


@well_known.get("/logo.png", include_in_schema=False)
async def logo():
    return FileResponse("logo.png", media_type="image/png")


@well_known.get("/ai-plugin.json", include_in_schema=False)
async def manifest(request: Request):
    ai_plugin = get_ai_plugin()
    return Response(
        content=Template(json.dumps(ai_plugin)).substitute(host=get_host(request)),
        media_type="application/json",
    )
