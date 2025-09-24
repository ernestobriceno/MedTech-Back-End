# meditech/app/__init__.py
import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session

db = SQLAlchemy()
migrate = Migrate()

def _register_auth_blueprint(app: Flask) -> None:
    """
    Intenta registrar el blueprint `auth` desde varios lugares comunes:
    - meditech.auth (si __init__.py exporta `auth`)
    - meditech.auth.routes (si el blueprint vive en routes.py)
    """
    tried = []
    for modpath in ("meditech.auth", "meditech.auth.routes"):
        try:
            mod = __import__(modpath, fromlist=["auth"])
            bp = getattr(mod, "auth", None)
            if bp is not None:
                app.register_blueprint(bp)
                app.logger.info(f"✅ Blueprint 'auth' registrado desde {modpath}")
                return
            tried.append(f"{modpath} (sin atributo 'auth')")
        except Exception as e:
            tried.append(f"{modpath} ({e!r})")
    app.logger.warning("⚠️ No se pudo registrar blueprint 'auth'. Intentos: " + " | ".join(tried))

def create_app() -> Flask:
    app = Flask(__name__)

    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret"),
        SQLALCHEMY_DATABASE_URI=os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///meditech.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_TYPE=os.getenv("SESSION_TYPE", "filesystem"),
    )

    db.init_app(app)
    migrate.init_app(app, db)
    Session(app)
    CORS(
        app,
        resources={r"/*": {"origins": os.getenv("CORS_ORIGIN", "*").split(",")}},
        supports_credentials=True,
    )

    # Registrar auth
    _register_auth_blueprint(app)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Mostrar mapa de rutas en logs para depurar
    with app.app_context():
        try:
            app.logger.info("📍 URL Map:\n" + "\n".join(sorted(str(r) for r in app.url_map.iter_rules())))
        except Exception as e:
            app.logger.debug(f"No se pudo listar url_map: {e!r}")

    return app
