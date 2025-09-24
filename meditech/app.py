# meditech/app.py
import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from flask_login import LoginManager
from flask_cors import CORS

# Exportados a nivel de módulo (otros módulos usan: from meditech.app import db)
db = SQLAlchemy()
login_manager = LoginManager()

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")

def create_app():
    app = Flask(__name__)

    # ===== Config para Render (usa variables de entorno) =====
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI", "")
    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        # Evita usar localhost en Render por accidente
        raise RuntimeError("Falta SQLALCHEMY_DATABASE_URI en Environment de Render.")

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me")
    app.config["SESSION_TYPE"] = os.getenv("SESSION_TYPE", "filesystem")
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_USE_SIGNER"] = True
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    # CORS (admite lista separada por comas)
    cors_origins = os.getenv("CORS_ORIGIN", "*")
    origins_list = [o.strip() for o in cors_origins.split(",")]
    CORS(app, resources={r"/*": {"origins": origins_list}}, supports_credentials=True)

    # ===== Extensiones =====
    db.init_app(app)
    Migrate(app, db)
    Session(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # evita import circular
        from .users.models import User
        return User.query.get(user_id)

    # ===== Blueprints =====
    # IMPORTANTE: los blueprints NO deben tener url_prefix dentro; se lo damos aquí.
    from .appointments.routes import appointments
    from .auth.routes import auth
    from .doctors.routes import doctors
    from .hospitals.routes import hospitals
    from .insurances.routes import insurances
    from .subscriptions.routes import subscriptions
    from .medications.routes import medications
    from .examinations.routes import examinations
    from .users.routes import users

    app.register_blueprint(appointments,  url_prefix="/appointments")
    app.register_blueprint(auth,          url_prefix="/auth")
    app.register_blueprint(doctors,       url_prefix="/doctors")
    app.register_blueprint(hospitals,     url_prefix="/hospitals")
    app.register_blueprint(insurances,    url_prefix="/insurances")
    app.register_blueprint(subscriptions, url_prefix="/subscriptions")
    app.register_blueprint(medications,   url_prefix="/medications")
    app.register_blueprint(examinations,  url_prefix="/examinations")
    app.register_blueprint(users,         url_prefix="/users")

    # ===== Utilidad =====
    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Endpoint de depuración: lista TODAS las rutas (bórralo luego si quieres)
    @app.get("/__routes")
    def list_routes():
        rules = []
        for r in app.url_map.iter_rules():
            if r.endpoint != "static":
                methods = sorted(m for m in r.methods if m not in {"HEAD", "OPTIONS"})
                rules.append({"rule": str(r), "methods": methods})
        return jsonify(sorted(rules, key=lambda x: x["rule"]))

    return app
