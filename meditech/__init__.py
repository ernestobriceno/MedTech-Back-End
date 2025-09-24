# meditech/app/__init__.py

import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session

# Exportamos db a nivel de módulo para que otros puedan hacer: from meditech.app import db
db = SQLAlchemy()
migrate = Migrate()

def create_app() -> Flask:
    app = Flask(__name__)

    # ---- Configuración base (lee de variables de entorno de Render) ----
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret"),
        SQLALCHEMY_DATABASE_URI=os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///meditech.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_TYPE=os.getenv("SESSION_TYPE", "filesystem"),
    )

    # ---- Inicializar extensiones ----
    db.init_app(app)
    migrate.init_app(app, db)
    Session(app)
    CORS(
        app,
        resources={r"/*": {"origins": os.getenv("CORS_ORIGIN", "*").split(",")}},
        supports_credentials=True,
    )

    # ---- Registrar blueprints ----
    # Auth (asegúrate de que tu blueprint 'auth' esté definido y exportado)
    try:
        # Si tu blueprint está en meditech/auth/__init__.py
        from meditech.auth import auth as auth_bp
        app.register_blueprint(auth_bp)
    except Exception:
        try:
            # Alternativa si lo tienes en meditech/auth/routes.py
            from meditech.auth.routes import auth as auth_bp
            app.register_blueprint(auth_bp)
        except Exception as e:
            app.logger.warning(f"No se pudo registrar el blueprint de auth: {e}")

    # (Opcionales) Si luego agregas otros blueprints, descomenta/ajusta este patrón:
    # for dotted in [
    #     "meditech.appointments.routes:appointments_bp",
    #     "meditech.doctors.routes:doctors_bp",
    #     "meditech.medications.routes:medications_bp",
    #     "meditech.hospitals.routes:hospitals_bp",
    #     "meditech.insurances.routes:insurances_bp",
    #     "meditech.subscriptions.routes:subscriptions_bp",
    #     "meditech.examinations.routes:examinations_bp",
    # ]:
    #     try:
    #         module, attr = dotted.split(":")
    #         mod = __import__(module, fromlist=[attr])
    #         app.register_blueprint(getattr(mod, attr))
    #     except Exception as e:
    #         app.logger.debug(f"Blueprint opcional {dotted} no registrado: {e}")

    # ---- Rutas de utilidad ----
    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
