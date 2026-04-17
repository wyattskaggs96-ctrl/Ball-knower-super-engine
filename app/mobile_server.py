from __future__ import annotations

import os
from pathlib import Path

from app.pipelines.mobile_command_center import refresh_mobile_command_center

try:
    from flask import Flask, Response, jsonify, send_file
except ModuleNotFoundError as exc:  # pragma: no cover - depends on environment
    Flask = None
    Response = object
    jsonify = None
    send_file = None
    _FLASK_IMPORT_ERROR = exc
else:
    _FLASK_IMPORT_ERROR = None


PAGE_PATH = Path("data/exports/mobile_command_center.html")
DATA_PATH = Path("data/exports/mobile_command_center.json")
app = Flask(__name__) if Flask else None


if app:

    @app.get("/")
    def index() -> Response:
        if not PAGE_PATH.exists():
            return Response(f"Missing file: {PAGE_PATH}", status=404)
        return send_file(PAGE_PATH, mimetype="text/html")


    @app.get("/mobile_command_center.json")
    def mobile_command_center_data() -> Response:
        if not DATA_PATH.exists():
            return Response(f"Missing file: {DATA_PATH}", status=404)
        return send_file(DATA_PATH, mimetype="application/json")


    @app.post("/run-engine")
    def run_engine() -> Response:
        result = refresh_mobile_command_center(run_engine=True)
        return jsonify(result)


def serve_mobile_command_center(host: str = "0.0.0.0", port: int | None = None) -> None:
    if app is None:
        raise RuntimeError("Flask is required to run mobile server. Install dependencies from requirements.txt") from _FLASK_IMPORT_ERROR

    resolved_port = port if port is not None else int(os.environ.get("PORT", 8000))
    app.run(host=host, port=resolved_port)


if __name__ == "__main__":
    serve_mobile_command_center(host="0.0.0.0")
