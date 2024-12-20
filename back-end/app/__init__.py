from flask import Flask, jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)
app.config.from_object('config')
db = SQLAlchemy(app)
ma = Marshmallow(app)


from .models import users, history
from .views import users, chat, helper
from .routes import routes

