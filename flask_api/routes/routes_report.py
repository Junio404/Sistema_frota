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


bp_routes_report = Blueprint('routes_report', __name__)

@bp_routes_report.route("/relatorio/ranking_eficiencia")
def relatorio_eficiencia():
    return render_template("relatorio/relatorio_eficiencia.html")

@bp_routes_report.route("/relatorio/quilometragem_media")
def relatorio_quilometragem():
    return render_template("relatorio/relatorio_km.html")

@bp_routes_report.route("/relatorio/total_viagens")
def relatorio_total_viagens():
    return render_template("relatorio/relatorio_total_viagens.html")

@bp_routes_report.route("/relatorio/custo_manutenções")
def relatorio_manutencao():
    return render_template("relatorio/relatorio_manutencao.html")