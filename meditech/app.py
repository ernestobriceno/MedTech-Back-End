import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from flask_login import LoginManager
from flask_cors import CORS

db = SQLAlchemy()
login_manager = LoginManager()

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

def _normalize_db_url(raw_url: str) -> str:
    """
    - Usa psycopg3: postgresql+psycopg://
    - Si viene con postgres:// lo normaliza
    - Asegura sslmode=require cuando se despliega (Render ya lo soporta)
    """
    url = raw_url or ""
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://") and "+psycopg" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    if "sslmode=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"
    return url

def create_app():
    app = Flask(__name__)

    # Permitir tu frontend en Netlify (ajusta el dominio si cambia)
    frontend_origin = os.getenv("FRONTEND_ORIGIN", )
    CORS(app, resources={r"/*": {"origins": [frontend_origin, ]}}, supports_credentials=True)

    # Lee DATABASE_URL de Render; si no existe, usa SQLite local para dev
    raw_db_url = os.getenv("DATABASE_URL", "sqlite:///meditech.db")
    app.config['SQLALCHEMY_DATABASE_URI'] = _normalize_db_url(raw_db_url)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SESSION_TYPE'] = os.getenv('SESSION_TYPE', 'filesystem')
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    db.init_app(app)
    Migrate(app, db)
    Session(app)
    login_manager.init_app(app)

    from .appointments.routes import appointments
    from .auth.routes import auth
    from .doctors.routes import doctors
    from .hospitals.routes import hospitals
    from .insurances.routes import insurances
    from .subscriptions.routes import subscriptions
    from .medications.routes import medications
    from .examinations.routes import examinations
    from .users.routes import users

    app.register_blueprint(appointments, url_prefix='/appointments')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(doctors, url_prefix='/doctors')
    app.register_blueprint(hospitals, url_prefix='/hospitals')
    app.register_blueprint(insurances, url_prefix='/insurances')
    app.register_blueprint(subscriptions, url_prefix='/subscriptions')
    app.register_blueprint(medications, url_prefix='/medications')
    app.register_blueprint(examinations, url_prefix='/examinations')
    app.register_blueprint(users, url_prefix='/users')

    @login_manager.user_loader
    def load_user(user_id):
        from .users.models import User
        return User.query.get(user_id)

    return app
