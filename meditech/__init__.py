# meditech/app/__init__.py
import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app() -> Flask:
    app = Flask(__name__)

    # Config desde variables de entorno (Render)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret"),
        SQLALCHEMY_DATABASE_URI=os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///meditech.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_TYPE=os.getenv("SESSION_TYPE", "filesystem"),
    )

    # Extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    Session(app)
    login_manager.init_app(app)
    CORS(
        app,
        resources={r"/*": {"origins": os.getenv("CORS_ORIGIN", "*").split(",")}},
        supports_credentials=True,
    )

    # Blueprints
    try:
        # si auth/__init__.py exporta `auth`, esto funciona
        from meditech.auth import auth as auth_bp
        app.register_blueprint(auth_bp)
        app.logger.info("✅ Blueprint 'auth' registrado desde meditech.auth")
    except Exception as e:
        try:
            # alternativa si vive en auth/routes.py
            from meditech.auth.routes import auth as auth_bp
            app.register_blueprint(auth_bp)
            app.logger.info("✅ Blueprint 'auth' registrado desde meditech.auth.routes")
        except Exception as e2:
            app.logger.warning(f"⚠️ No se pudo registrar blueprint 'auth': {e!r} | {e2!r}")

    # Ruta de salud
    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Log del mapa de rutas para verificar que /auth/login exista
    with app.app_context():
        try:
            url_map = "\n".join(sorted(str(r) for r in app.url_map.iter_rules()))
            app.logger.info("📍 URL Map:\n" + url_map)
        except Exception:
            pass

    return app
