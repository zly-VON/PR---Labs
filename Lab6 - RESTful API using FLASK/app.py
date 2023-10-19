# app.py
from flask import Flask, jsonify
import json
from flask_sqlalchemy import SQLAlchemy
from models.database import db
from models.electro_scooter import ElectroScooter
from flask_swagger_ui import get_swaggerui_blueprint

def create_app():
    app = Flask(__name__)

    # Configure SQLAlchemy to use SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pr:1234@localhost:5432/pr6'
    db.init_app(app)
    return app


if __name__ == "__main__":
    app = create_app()
    import routes

    # Create a Swagger UI blueprint
    SWAGGER_URL = '/api/docs'  # URL for the Swagger documentation
    API_URL = 'http://127.0.0.1:5000/swagger.json'  # Path to Swagger JSON file

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Electro Scooter API"
        }
    )

    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    @app.route('/swagger.json')
    def swagger():
        with open('swagger.json', 'r') as f:
            return jsonify(json.load(f))

    app.run()