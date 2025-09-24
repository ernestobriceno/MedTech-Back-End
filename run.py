from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    
    CORS(
        app,
        resources={r"/*": {"origins": os.getenv("CORS_ORIGIN", "*").split(",")}},
        supports_credentials=True
    )

   
    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
