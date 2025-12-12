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


bp_routes_api = Blueprint('routes_api', __name__)


# ----------------------------- API / JSON DO BANCO ------------------------------------

@bp_routes_api.route("/api/marcas_modelos")
def api_marcas_modelos():
    
    # ---------- Abre conexão com SQLite e habilita Row para acessar colunas por nome ----------
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # ---------- Consulta JOIN única para trazer marcas + modelos + categoria mínima de CNH ----------
        cur.execute("""
            SELECT 
                M.ID AS marca_id, 
                M.NOME AS marca_nome,
                MO.ID AS modelo_id,
                MO.NOME_MODELO,
                MO.TIPO_VEICULO,
                TVC.CAT_MIN_CNH,
                MO.QTD_LITROS,
                MO.CONSUMO_MEDIO_KM_L,
                MO.TIPO_COMBUSTIVEL
            FROM MARCA M
            LEFT JOIN MODELO MO ON M.ID = MO.MARCA_FK
            LEFT JOIN TIPO_VEICULO_CNH TVC ON MO.TIPO_VEICULO = TVC.TIPO_VEICULO
            ORDER BY M.NOME, MO.NOME_MODELO
        """)
        
        todos_modelos = cur.fetchall()
        
    # ---------- Estrutura que agrupa modelos dentro das marcas ----------
    resultado_agrupado = {}

    for row in todos_modelos:
        marca_nome = row['marca_nome']
        
        # ---------- Cria entrada da marca caso ainda não exista ----------
        if marca_nome not in resultado_agrupado:
            resultado_agrupado[marca_nome] = {
                "marca": marca_nome,
                "modelos": []
            }
        
        # ---------- Se existe um modelo, adiciona ele dentro da marca ----------
        if row['modelo_id'] is not None:
            modelo_data = {
                "id": row['modelo_id'],
                "nome_modelo": row['NOME_MODELO'],
                "tipo_veiculo": row['TIPO_VEICULO'],
                "cat_min_cnh": row['CAT_MIN_CNH'],
                "qtd_litros": row['QTD_LITROS'],
                "consumo_medio_km_l": row['CONSUMO_MEDIO_KM_L'],
                "tipo_combustivel": row['TIPO_COMBUSTIVEL']
            }
            resultado_agrupado[marca_nome]['modelos'].append(modelo_data)

    # ---------- Converte o dict em lista obrigatória no padrão JSON ----------
    resultado_final = list(resultado_agrupado.values())

    # ---------- Retorna JSON final ----------
    return jsonify(resultado_final)


@bp_routes_api.route("/api/veiculos")
def api_veiculos():

    # ---------- Conexão com banco e ativação do acesso por nome ----------
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # ---------- Busca completa de veículos, modelos e marcas ----------
        cur.execute("""
            SELECT 
                V.PLACA,
                V.ANO,
                V.TIPO_VEICULO,
                V.QUILOMETRAGEM,
                V.QTD_LITROS,
                V.CONSUMO_MEDIO_KM_L,
                V.TIPO_COMBUSTIVEL,
                V.STATUS,

                MO.ID AS modelo_id,
                MO.NOME_MODELO,
                MO.TIPO_VEICULO AS modelo_tipo_veiculo,
                MO.TIPO_COMBUSTIVEL AS modelo_tipo_combustivel,
                MO.QTD_LITROS AS modelo_qtd_litros,
                MO.CONSUMO_MEDIO_KM_L AS modelo_consumo,
                
                M.ID AS marca_id,
                M.NOME AS marca_nome

            FROM VEICULO V
            JOIN MODELO MO ON V.MODELO_FK = MO.ID
            JOIN MARCA M ON M.ID = MO.MARCA_FK
            ORDER BY M.NOME, MO.NOME_MODELO, V.PLACA
        """)

        rows = cur.fetchall()

    # ---------- Monta lista final para JSON ----------
    veiculos = []

    for r in rows:
        veiculos.append({
            "placa": r["PLACA"],
            "ano": r["ANO"],
            "quilometragem": r["QUILOMETRAGEM"],
            "tipo_veiculo": r["TIPO_VEICULO"],
            "qtd_litros": r["QTD_LITROS"],
            "consumo_medio_km_l": r["CONSUMO_MEDIO_KM_L"],
            "tipo_combustivel": r["TIPO_COMBUSTIVEL"],
            "status": r["STATUS"],

            # ---------- Dados do modelo ----------
            "modelo": {
                "id": r["modelo_id"],
                "nome_modelo": r["NOME_MODELO"],
                "tipo_veiculo": r["modelo_tipo_veiculo"],
                "tipo_combustivel": r["modelo_tipo_combustivel"],
                "qtd_litros": r["modelo_qtd_litros"],
                "consumo_medio_km_l": r["modelo_consumo"]
            },

            # ---------- Dados da marca ----------
            "marca": {
                "id": r["marca_id"],
                "nome": r["marca_nome"]
            }
        })

    # ---------- Retorna JSON ----------
    return jsonify(veiculos)



@bp_routes_api.route("/api/motoristas")
def api_motoristas():

    # ---------- Conexão com banco e leitura por nome ----------
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # ---------- Consulta Motorista + Pessoa ----------
        cur.execute("""
            SELECT 
                MT.CPF,
                MT.CAT_CNH,
                MT.EXP_ANOS,
                MT.DISPONIBILIDADE,
                MT.CNH_VALIDO_ATE,
                
                P.NOME AS pessoa_nome

            FROM MOTORISTA MT
            JOIN PESSOA P ON P.CPF = MT.CPF
            ORDER BY P.NOME
        """)

        rows = cur.fetchall()

    # ---------- Monta JSON final ----------
    motoristas = []

    for r in rows:
        motoristas.append({
            "cpf": r["CPF"],
            "nome": r["pessoa_nome"],
            "cat_cnh": r["CAT_CNH"],
            "experiencia_anos": r["EXP_ANOS"],
            "disponibilidade": r["DISPONIBILIDADE"],
            "cnh_valido_ate": r["CNH_VALIDO_ATE"]
        })

    # ---------- Retorno JSON ----------
    return jsonify(motoristas)



@bp_routes_api.route("/api/historico_veiculo")
def api_historico_veiculo():
    
    
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""
        SELECT 
        HV.ID,
        HV.PLACA_FK,
        HV.TIPO_EVENTO,
        HV.DATA_EVENTO,
        HV.RESUMO,
        HV.VALOR_ASSOCIADO,
        HV.OBSERVACAO
        
        FROM HISTORICO_EVENTO_VEICULO HV
        ORDER BY HV.ID
        
                    """)
        
        rows = cur.fetchall()
        
    historico_veiculo = []
    
    for r in rows:
        historico_veiculo.append({
            "id": r["ID"],
            "placa_fk": r["PLACA_FK"],
            "tipo_evento": r["TIPO_EVENTO"],
            "data_evento": r["DATA_EVENTO"],
            "resumo": r["RESUMO"],
            "valor_associado": r["VALOR_ASSOCIADO"],
            "observacao": r["OBSERVACAO"]
            
        })
        
    return jsonify(historico_veiculo)


@bp_routes_api.route("/api/viagens")
def api_viagens():
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""
            SELECT
                V.ID,
                V.PLACA_FK,
                V.CPF_FK,
                V.ORIGEM,
                V.DESTINO,
                V.DISTANCIA_KM,
                V.DATA_SAIDA,
                V.DATA_CHEGADA,
                V.HODOMETRO_SAIDA,
                V.HODOMETRO_CHEGADA,
                V.STATUS
            FROM VIAGEM V
            ORDER BY V.ID
        """)

        rows = cur.fetchall()

    viagens = []
    for r in rows:
        viagens.append({
            "id": r["ID"],
            "placa_fk": r["PLACA_FK"],
            "cpf_fk": r["CPF_FK"],
            "origem": r["ORIGEM"],
            "destino": r["DESTINO"],
            "distancia_km": r["DISTANCIA_KM"],
            "data_saida": r["DATA_SAIDA"],
            "data_chegada": r["DATA_CHEGADA"],
            "hodometro_saida": r["HODOMETRO_SAIDA"],
            "hodometro_chegada": r["HODOMETRO_CHEGADA"],
            "status": r["STATUS"]
        })

    return jsonify(viagens)



@bp_routes_api.route("/api/manutencoes")
def api_manutencoes():
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""
            SELECT
                M.ID,
                M.PLACA_FK,
                M.TIPO_MANUTENCAO,
                M.DATA_INICIO,
                M.DATA_CONCLUSAO,
                M.CUSTO,
                M.DESCRICAO,
                M.STATUS_MANUTENCAO
            FROM MANUTENCAO M
            ORDER BY M.ID
        """)

        rows = cur.fetchall()

    manutencoes = []
    for r in rows:
        manutencoes.append({
            "id": r["ID"],
            "placa_fk": r["PLACA_FK"],
            "tipo_manutencao": r["TIPO_MANUTENCAO"],
            "data_inicio": r["DATA_INICIO"],
            "data_conclusao": r["DATA_CONCLUSAO"],
            "custo": r["CUSTO"],
            "descricao": r["DESCRICAO"],
            "status_manutencao": r["STATUS_MANUTENCAO"]
        })

    return jsonify(manutencoes)

