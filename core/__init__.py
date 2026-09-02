from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, redirect, request, session, url_for
from flask_login import current_user, logout_user

from core.settings import Config
from core.extensions import db, login_manager, migrate

from apps.auth.models import User

from apps.cover.routes import cover_bp
from apps.dashboard.routes import dashboard_bp
from apps.cheque.routes import cheque_bp
from apps.invoice.routes import invoice_bp
from apps.auth.routes import auth_bp
from apps.settings.routes import settings_bp
from apps.customers.routes import customers_bp
from apps.suppliers.routes import suppliers_bp


from core.routes.health import health_bp


BASE_DIR = Path(__file__).resolve().parent.parent


def create_app():

    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static")
    )

    app.config.from_object(Config)

    # ==========================================================
    # EXTENSIONS
    # ==========================================================

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # ==========================================================
    # SESSION TIMEOUT
    # ==========================================================

    @app.before_request
    def check_idle_timeout():

        if not current_user.is_authenticated:
            return

        now = datetime.now(timezone.utc)

        last_activity = session.get("last_activity")

        if last_activity:

            last_activity = datetime.fromisoformat(last_activity)

            idle_seconds = (
                now - last_activity
            ).total_seconds()

            # 30 minutes
            if idle_seconds >= 1800:

                logout_user()
                session.clear()

                return redirect(
                    url_for(
                        "auth.login",
                        next=request.path
                    )
                )

        session["last_activity"] = now.isoformat()

    # ==========================================================
    # BLUEPRINTS
    # ==========================================================

    app.register_blueprint(cover_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(cheque_bp)
    app.register_blueprint(invoice_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(suppliers_bp)

    # ==========================================================
    # LOGIN MANAGER
    # ==========================================================

    @login_manager.user_loader
    def load_user(user_id):

        return db.session.get(
            User,
            int(user_id)
        )

    # ==========================================================
    # HOME
    # ==========================================================

    @app.route("/")
    def home():
        
        return redirect(
            url_for("cover.index")
        )

    return app