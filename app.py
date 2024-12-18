import os
from flask import Flask
from flask_cors import CORS
from routes.feedbacks.feedbacks_routes import bp as feedback_bp
from routes.users.users_route import bp as users_bp
from routes.transcripts.transcripts_routes import bp as transcripts_bp
from routes.mocks.mocks_routes import bp as mocks_bp
from routes.stations.stations_routes import bp as stations_bp
from flask_jwt_extended import (
    JWTManager,
)
from routes.messages.messages_routes import bp as messages_bp
from config.helpers import mail

LOCAL_FRONT_END_URL = "http://localhost:3000"
FRONT_END_URLS = [LOCAL_FRONT_END_URL]


SECRET_KEY = os.getenv("JWT_SECRET_KEY")
GMAIL_USERNAME = os.environ.get("GMAIL_USERNAME")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")
GMAIL_DEFAULT_SENDER = os.environ.get("GMAIL_DEFAULT_SENDER")


app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": FRONT_END_URLS}})

app.register_blueprint(feedback_bp)
app.register_blueprint(users_bp)
app.register_blueprint(transcripts_bp)
app.register_blueprint(mocks_bp)
app.register_blueprint(stations_bp)
app.register_blueprint(messages_bp)
app.config["JWT_SECRET_KEY"] = SECRET_KEY
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

# Gmail setup
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = GMAIL_USERNAME
app.config["MAIL_PASSWORD"] = GMAIL_PASSWORD
app.config["MAIL_DEFAULT_SENDER"] = GMAIL_DEFAULT_SENDER


jwt = JWTManager(app)
mail.init_app(app)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
