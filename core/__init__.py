from flask import Flask, redirect, url_for
from pathlib import Path

from core.settings import Config
from apps.cheque.routes import cheque_bp
from core.routes.health import health_bp


BASE_DIR = Path(__file__).resolve().parent.parent

def create_app():
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static")
    )
    app.config.from_object(Config)

    app.register_blueprint(cheque_bp)

    app.register_blueprint(health_bp)

    @app.route("/")
    def home():
        return redirect(url_for("cheque.index"))

    return app