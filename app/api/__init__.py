from flask import Blueprint

# Erstell ein Blueprint für das API

api = Blueprint('api', __name__)

# Importier die Views (API-Endpunkte) für das Blueprint
from . import views