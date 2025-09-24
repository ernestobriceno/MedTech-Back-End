# meditech/app/__init__.py
import os
from flask import Flask, jsonify
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

    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret"),
        SQLALCHEMY_DATABASE_URI=os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///meditech.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_TYPE=os.getenv("SESSION_TYPE", "filesystem"),
    )

    db.init_app(app)
    migrate.init_app(app, db)
    Session(app)
    login_manager.init_app(app)
    CORS(
        app,
        resources={r"/*": {"origins": os.getenv("CORS_ORIGIN", "*").split(",")}},
        supports_credentials=True,
    )

    # —— REGISTRO DEL BLUEPRINT (sin try/except, si falla veremos el error) ——
    from meditech.auth import auth as auth_bp   # <- usa lo exportado en auth/__init__.py
    app.register_blueprint(auth_bp)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Endpoint de diagnóstico para ver TODAS las rutas
    @app.get("/__routes")
    def __routes():
        rules = []
        for r in app.url_map.iter_rules():
            methods = ",".join(sorted(m for m in r.methods if m in {"GET","POST","PUT","PATCH","DELETE"}))
            rules.append({"rule": str(r), "methods": methods})
        # ordenamos por path
        rules.sort(key=lambda x: x["rule"])
        return jsonify(rules)

    return app
