from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder="./static/")
app.config.from_object('src.config')
app.secret_key = "randiodnaknldaiad;kdnaa345"
db = SQLAlchemy(app)

from .models import employee
import src.views
