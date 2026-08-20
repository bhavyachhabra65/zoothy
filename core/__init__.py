from flask import Flask, redirect, url_for
from pathlib import Path

from core.settings import Config
from core.extensions import db, login_manager, migrate

from apps.auth.models import User

from apps.cover.routes import cover_bp
from apps.dashboard.routes import dashboard_bp
from apps.cheque.routes import cheque_bp
from apps.invoice.routes import invoice_bp
from apps.auth.routes import auth_bp

from core.routes.health import health_bp


BASE_DIR = Path(__file__).resolve().parent.parent

def create_app():
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static")
    )
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    app.register_blueprint(cover_bp)

    app.register_blueprint(dashboard_bp)

    app.register_blueprint(cheque_bp)

    app.register_blueprint(invoice_bp)

    app.register_blueprint(health_bp)
    
    app.register_blueprint(auth_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.route("/")
    def home():
        return redirect(url_for("cover.index"))
    return app