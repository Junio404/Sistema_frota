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


bp_routes_read = Blueprint('routes_read', __name__)


@bp_routes_read.route("/modelo/read")
def tabela_modelo():
    return render_template("read/ver_modelos.html")

@bp_routes_read.route("/motorista/read")
def tabela_motorista():
    return render_template("read/ver_motorista.html")

@bp_routes_read.route("/veiculo/read")
def tabela_veiculo():
    return render_template("read/ver_veiculo.html")

@bp_routes_read.route("/historico_veiculo/read")
def tabela_historico():
    return render_template("read/ver_historico_veiculo.html")
