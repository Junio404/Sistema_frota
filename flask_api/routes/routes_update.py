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


bp_routes_update = Blueprint('routes_update', __name__)

# -------------------- UPDATE ROUTES --------------------------------

@bp_routes_update.route("/motorista/update")
def update_motorista():
    return render_template("atualizar/atualizar_motorista.html")

@bp_routes_update.route("/atualizar_motorista", methods=["POST"])
def atualizar_motorista_route():
    try:
        # ------------ 1. Coletar CPF do formulário ------------
        cpf = request.form.get("cpf")

        if not cpf or not cpf_existe(cpf):
            flash("❌ CPF não fornecido ou não encontrado no sistema.")
            return redirect("/motorista/update")

        # ------------ 2. Buscar motorista original ------------
        with sqlite3.connect(Config.DATABASE) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT 
                    P.ID, P.NOME, P.CPF, M.CAT_CNH, M.EXP_ANOS, 
                    M.DISPONIBILIDADE, M.CNH_VALIDO_ATE
                FROM MOTORISTA M
                INNER JOIN PESSOA P ON P.ID = M.ID
                WHERE P.CPF = ?
                """,
                (cpf,)
            )
            row = cur.fetchone()

        motorista_original = row_to_motorista(row)
        
        print(motorista_original)

        if motorista_original is None:
            flash("❌ Motorista não encontrado após a busca inicial.")
            return redirect("/motorista/update")

        # ------------ Coletar dados e aplicar Fallback ------------

        raw_data = {
            "cat_cnh": request.form.get("cnh") or motorista_original.cat_cnh,
            "exp_anos": request.form.get("experiencia") or motorista_original.exp_anos,
            "disponibilidade": request.form.get("disponibilidade") or motorista_original.disponibilidade,
            "cnh_valido_ate": request.form.get("cnh_valido_ate") or motorista_original.cnh_valido_ate
        }
        

        # ------------ Validar e Converter com Pydantic ------------

        pydantic_data = Motorista_update(

            id=motorista_original.id, 
            cat_cnh=raw_data["cat_cnh"],
            exp_anos=int(raw_data["exp_anos"]), # Deve ser convertido para int antes de passar para Pydantic
            disponibilidade=raw_data["disponibilidade"],
            cnh_valido_ate=raw_data["cnh_valido_ate"]
        )

        # ------------ Preparar dados para o Repositório ------------
        
        # O repositório espera um dicionário de dados no formato do banco de dados (colunas)
        dados_para_db = {
            "CAT_CNH": pydantic_data.cat_cnh,

            "EXP_ANOS": pydantic_data.exp_anos,
            

            "DISPONIBILIDADE": pydantic_data.disponibilidade.value,
            
            
            "CNH_VALIDO_ATE": pydantic_data.cnh_valido_ate
        }

        # ------------ Persistir (Atualizar) ------------
        # Chama a função de atualização, passando o ID e o dicionário de dados
        atualizar_motorista(motorista_original.id, dados_para_db)

        flash("✅ Motorista atualizado com sucesso!")
        return redirect(url_for("routes_index.index"))

    except ValueError as e:
        flash(f"❌ Erro de validação: {e}")
        return redirect("/motorista/update")

    except Exception as e:
        print(f"Erro inesperado ao atualizar motorista: {e}")
        flash("❌ Erro inesperado no sistema.")
        return redirect("/motorista/update")


@bp_routes_update.route("/veiculo/update")
def update_veiculo():
    return render_template("atualizar/atualizar_veiculo.html")

@bp_routes_update.route("/atualizar_veiculo", methods=["POST"])
def atualizar_veiculo_route():
    try:
        placa = request.form.get("placa")

        if not placa_existe(placa):
            flash("❌ Placa não encontrada no sistema.")
            return redirect("/veiculo/update")

        dados_update = {}

        # ------------------------------------------
        # Consumo (opcional)
        # ------------------------------------------
        consumo = request.form.get("consumo_medio_km_l")
        if consumo:
            try:
                consumo_float = float(consumo)
                if consumo_float <= 0:
                    raise ValueError("Consumo médio inválido.")
                dados_update["CONSUMO_MEDIO_KM_L"] = consumo_float
            except:
                flash("❌ Consumo médio inválido.")
                return redirect("/veiculo/update")

        # ------------------------------------------
        # Status (opcional)
        # ------------------------------------------
        status = request.form.get("status")
        if status:
            try:
                Veiculo_status(status)  # valida enum
                dados_update["STATUS"] = status
            except:
                flash("❌ Status inválido.")
                return redirect("/veiculo/update")

        # Se nada foi enviado, não faz update
        if not dados_update:
            flash("ℹ Nenhum campo enviado para atualização.")
            return redirect("/veiculo/update")

        # ------------------------------------------
        # Persistir no banco
        # ------------------------------------------
        atualizar_veiculo(placa, dados_update)

        flash("✅ Veículo atualizado com sucesso!")
        return redirect(url_for("routes_index.index"))

    except Exception as e:
        print("Erro inesperado:", e)
        flash("❌ Ocorreu um erro ao atualizar o veículo.")
        return redirect("/veiculo/update")