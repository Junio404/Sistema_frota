from flask import render_template, Blueprint, request, redirect, url_for, flash, jsonify
from flask_api.models.model_motorista import Motorista_create, Motorista_update
from flask_api.models.model_veiculo import Veiculo_create
from flask_api.models.model_viagem import *
from flask_api.repositories.motorista_repo.motorista_repo import *
from flask_api.repositories.manutencao_repo import *
from flask_api.repositories.veiculo_repo.veiculo_repo import *
from flask_api.models.enums import *
import sqlite3
from config import Config
from flask_api.repositories.viagem_repo.viagem_repo import *
from flask_api.repositories.abastecimento_repo.abastecimento_repo import *
from pydantic import ValidationError
from flask_api.models.model_viagem import ViagemCreate
from flask_api.models.model_abastecimento import Abastecimento_create
from flask_api.models.model_manutencao import Manutencao_create
from datetime import datetime
from datetime import date 


bp_routes_index_options = Blueprint('routes_index', __name__)


#------------------------------ PAGINA INICIAL ------------------------------------
@bp_routes_index_options.route("/")
def index():
    return render_template("index.html")

#------------------------------- OPTIONS HTML -------------------------------------
@bp_routes_index_options.route("/veiculo")
def veiculo_options():
    return render_template("options/veiculo_options.html")

@bp_routes_index_options.route("/motorista")
def motorista_options():
    return render_template("options/motorista_options.html")

@bp_routes_index_options.route("/relatórios")
def relatorio_options():
    return render_template("options/relatorio_options.html")