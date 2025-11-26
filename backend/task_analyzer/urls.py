from pathlib import Path

from django.contrib import admin
from django.http import Http404, HttpResponse
from django.urls import path, include


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"


def serve_index(request):
    """Serve the frontend index.html at the root URL (/)."""
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.is_file():
        raise Http404("index.html not found in frontend folder.")
    with open(index_path, "rb") as f:
        return HttpResponse(f.read(), content_type="text/html")


def serve_frontend_asset(request, filename: str):
    """Serve frontend CSS/JS without Django static setup (DEBUG-only use)."""
    asset_path = FRONTEND_DIR / filename

    if not asset_path.is_file():
        raise Http404("Asset not found")

    if filename.endswith(".css"):
        content_type = "text/css"
    elif filename.endswith(".js"):
        content_type = "application/javascript"
    else:
        content_type = "application/octet-stream"

    with open(asset_path, "rb") as f:
        return HttpResponse(f.read(), content_type=content_type)


urlpatterns = [
    # Frontend routes
    path("", serve_index, name="frontend_index"),
    path("styles.css", lambda request, fn="styles.css": serve_frontend_asset(request, fn)),
    path("script.js", lambda request, fn="script.js": serve_frontend_asset(request, fn)),

    # Backend API + admin
    path("admin/", admin.site.urls),
    path("api/tasks/", include("tasks.urls")),
]
