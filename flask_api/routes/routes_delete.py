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


bp_routes_delete = Blueprint('routes_delete', __name__)
#--------------------- DELETE ROUTES -------------------------------

@bp_routes_delete.route("/motorista/deletar")
def delete_motorista():
    return render_template("delete/deletar_motorista.html")


@bp_routes_delete.route("/deletar_motorista", methods=["POST"])
def deletar_motorista_route():
    try:
        cpf = request.form.get("cpf")
        # Recebe o cpf do formulário e valida se ele existe no Banco de Dados
        if not cpf_existe(cpf):
            flash("❌ Insira um CPF válido para deletar.")
            return redirect("/motorista/deletar")
        
        with sqlite3.connect(Config.DATABASE) as conn:
            cur = conn.cursor()
            
            cur.execute("""
            SELECT DISPONIBILIDADE
            FROM MOTORISTA
            WHERE CPF = ?                        
                        """, (cpf,))
            cpf_status = cur.fetchone()
        
        if cpf_status != Veiculo_status.ATIVO.value or cpf_status != Veiculo_status.INATIVO.value:
            flash("❌ Delete o Motorista apenas se ele não estiver em Viagem")
            return redirect("/motorista/deletar")


# ------------ DELETAR ------------
        motorista_deletado = deletar_motorista(cpf)
        flash("✅ Motorista Deletado com sucesso!")
        return redirect(url_for('routes_index.index'))
        
    except ValueError as e:
        flash(f"❌ Erro de validação: {e}")
        return redirect("/motorista/deletar")

    except Exception as e:
        print(f"Erro inesperado ao deletar motorista: {e}")
        flash("❌ Erro inesperado no sistema.")
        return redirect("/motorista/deletar")
    
@bp_routes_delete.route("/veiculo/deletar")  
def delete_veiculo():
    return render_template("delete/deletar_veiculo.html")

@bp_routes_delete.route("/deletar_veiculo", methods=["POST"])
def deletar_veiculo_route():
    try:
        placa = request.form.get("placa")
        
        if not placa_existe(placa):
            flash("❌ Insira uma PLACA válida para deletar.")
            return redirect("/veiculo/deletar")
        
        with sqlite3.connect(Config.DATABASE) as conn:
            cur = conn.cursor()
            
            cur.execute("""
            SELECT STATUS
            FROM VEICULO
            WHERE PLACA = ?                        
                        """, (placa,))
            placa_status = cur.fetchone()
        
        if placa_status != Status_motorista.ATIVO.value or placa_status != Status_motorista.INATIVO.value:
            flash("❌ Delete o Veiculo apenas se ele não estiver em Viagem ou em Manutenção")
            return redirect("/veiculo/deletar")        
        
        veiculo_deletado = deletar_veiculo(placa)
        flash("✅ Veiculo Deletado com sucesso!")
        return redirect(url_for('routes_index.index'))
        
    except ValueError as e:
        flash(f"❌ Erro de validação: {e}")
        return redirect("/veiculo/deletar")

    except Exception as e:
        print(f"Erro inesperado ao deletar veiculo: {e}")
        flash("❌ Erro inesperado no sistema.")
        return redirect("/veiculo/deletar")
    