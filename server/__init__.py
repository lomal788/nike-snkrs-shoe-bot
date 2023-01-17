from flask import Blueprint
server = Blueprint('server', __name__)
from .app import *
from .healthcheck import *
