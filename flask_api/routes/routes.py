from flask import render_template, Blueprint, request, redirect, url_for, flash
from flask_api.models.model_motorista import Motorista_create
from flask_api.models.model_veiculo import Veiculo_create
from flask_api.models.model_viagem import *
from flask_api.repositories.motorista_repo.motorista__repo import *
from flask_api.repositories.veiculo_repo.veiculo_repo import *
from flask_api.models.enums import *
import sqlite3
from config import Config
from flask_api.repositories.viagem_repo.viagem_repo import *
bp = Blueprint('routes', __name__)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/motorista/create")
def forms_motorista():
    return render_template("forms.html")

# -------------------- CRIAR MOTORISTA --------------------
@bp.route("/criar_motorista", methods=["POST"])
def criar_motorista():
    raw_data = {
        'nome': request.form.get("nome"),
        'cpf': request.form.get("cpf"),
        'cat_cnh': request.form.get("cnh"),
        'exp_anos': int(request.form.get("experiencia")),   # converte para int
        'disponibilidade': request.form.get("disponibilidade"),
        'cnh_valido_ate': request.form.get("cnh_valido_ate")
    }
    
    data = Motorista_create(**raw_data)
    
    if validar_cpf(data.cpf) == False:
        flash("❌ Insira um CPF válido com 11 digitos")
        return redirect("/motorista/create")
    
    if cpf_existe(data.cpf) == True:
        flash("❌ Este CPF já está cadastrado")
        return redirect("/motorista/create")


    inserir_motorista(data)
    flash("✅ motorista cadastrado com sucesso!")
    
    return redirect(url_for("routes.index"))

@bp.route("/veiculo/create")
def forms_veiculo():
    return render_template("forms_veiculo.html")

@bp.route("/criar_veiculo", methods=["POST"])
def criar_veiculo():

    # ------------------- VALIDAÇÃO PLACA -------------------
    placa = request.form.get("placa")

    if not placa:
        flash("❌ Placa não informada.")
        return redirect(url_for("routes.forms_veiculo"))
    if not validar_placa_mercosul(placa):
        flash("❌ Placa inválida. Use o padrão Mercosul (LLLNLNNN).")
        return redirect(url_for('routes.forms_veiculo'))

    # ------------------- BUSCAR TIPO DO MODELO -------------------
    id_modelo = int(request.form.get("modelo_fk"))
    tipo_veiculo = buscar_tipo_modelo(id_modelo)
    
    # ------------------- BUSCAR TIPO DO MODELO -------------------

    qtd_litros = buscar_qtd_litros(id_modelo)
    
    # ------------------- BUSCAR TIPO DO MODELO -------------------

    consumo_medio = buscar_consumo_medio(id_modelo)

    if tipo_veiculo is None:
        flash("❌ Modelo não encontrado no banco de dados.")
        return redirect(url_for("routes.forms_veiculo"))

    # ------------------- MONTAR OBJETO Pydantic -------------------
    raw_data = {
        'placa': placa,
        'modelo_fk': id_modelo,
        'ano': int(request.form.get("ano")),
        'tipo_veiculo': tipo_veiculo,
        'quilometragem': float(request.form.get("quilometragem")),
        'consumo_medio_km_l': consumo_medio,
        'qtd_litros': qtd_litros,
        'status': request.form.get("disponibilidade", Veiculo_status.ATIVO)
    }

    data = Veiculo_create(**raw_data)

    # ------------------- INSERT NO BANCO -------------------
    inserir_veiculo(data)

    flash("✅ Veículo cadastrado com sucesso!")
    return redirect(url_for("routes.index"))
        

# @bp.errorhandler(Exception)
# def handle_exception(e):
#     return render_template("erro.html", erro=str(e)), 500


@bp.route("/api/marcas_modelos")
def api_marcas_modelos():
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # pega todas as marcas
        cur.execute("SELECT ID, NOME FROM MARCA ORDER BY NOME")
        marcas = cur.fetchall()

        resultado = []

        for marca in marcas:
            marca_id = marca["ID"]

            # pega todos os modelos dessa marca (AGORA COMPLETO)
            cur.execute("""
                SELECT 
                    ID,
                    NOME_MODELO,
                    TIPO_VEICULO,
                    CAT_MIN_CNH,
                    QTD_LITROS,
                    CONSUMO_MEDIO_KM_L
                FROM MODELO
                WHERE MARCA_FK = ?
                ORDER BY NOME_MODELO
            """, (marca_id,))
            
            modelos = [dict(m) for m in cur.fetchall()]

            resultado.append({
                "marca": marca["NOME"],
                "modelos": modelos
            })

    return resultado   # Flask converte automaticamente para JSON


@bp.route("/veiculo")
def veiculo_options():
    return render_template("veiculo_options.html")

@bp.route("/motorista")
def motorista_options():
    return render_template("motorista_options.html")

@bp.route("/relatórios")
def relatorio_options():
    return render_template("relatorio_options.html")

@bp.route("/viagem")
def forms_viagem():
    return render_template("forms_viagem.html")

from pydantic import ValidationError # Importante para capturar erros do Pydantic


# Importações do repositório refatorado
from flask_api.models.model_viagem import ViagemCreate

# Define o caminho do banco de dados (deve ser consistente com o repo)
DB_PATH = "meu_banco.db"

@bp.route("/criar_viagem", methods=["POST"])
def criar_viagem_route():

    # 1. Obtenção dos dados brutos do formulário
    dados = request.form
    placa_fk = dados.get("placa_fk")
    cpf_fk = dados.get("cpf_fk")
    origem = dados.get("origem")
    destino = dados.get("destino")
    distancia_km_str = dados.get("distancia_km")
    data_chegada = dados.get("data_chegada")

    # 2. Pré-validação de campos obrigatórios/numéricos
    try:
        if not placa_fk or not cpf_fk or not origem or not destino or not distancia_km_str or not data_chegada:
             raise ValueError("Todos os campos do formulário são obrigatórios.")
             
        distancia_km = float(distancia_km_str)

    except (TypeError, ValueError) as e:
        flash(f"❌ Erro de formulário: O campo Distância (km) deve ser um número válido. ({e})")
        return redirect(url_for("routes.forms_viagem"))
    
    # 3. Validação de existência de entidades (Motorista/Veículo)
    if not repo_buscar_veiculo_por_placa(placa_fk, DB_PATH):
        flash("❌ Veículo não encontrado.")
        return redirect(url_for("routes.forms_viagem"))

    if not repo_buscar_motorista_por_cpf(cpf_fk, DB_PATH):
        flash("❌ Motorista não encontrado.")
        return redirect(url_for("routes.forms_viagem"))

    try:
        # 4. Criação do objeto Pydantic (Validação de tipo e formato de dados)
        # Se Pydantic falhar (ex: formato de data incorreto), lança ValidationError.
        dados_viagem = ViagemCreate(
            placa_fk=placa_fk,
            cpf_fk=cpf_fk,
            origem=origem,
            destino=destino,
            distancia_km=distancia_km,
            data_chegada=data_chegada
        )

        # 5. Chama o Orquestrador do Repositório (Validações de Negócio + Persistência)
        # O orquestrador 'criar_viagem' irá:
        # - Validar status do Motorista (ATIVO/EM_VIAGEM/INATIVO)
        # - Validar status do Veículo (ATIVO/EM_VIAGEM/MANUTENCAO)
        # - Validar compatibilidade CNH x Veículo
        # - Calcular hodômetro e consumo de combustível
        # - VALIDAR COMBUSTÍVEL SUFICIENTE
        # - Inserir Viagem e Histórico, e Atualizar status/KM/litros
        
        resultado = criar_viagem(dados_viagem)

        flash("🚗💨 Viagem registrada com sucesso!")
        return redirect(url_for("routes.index"))

    except ValidationError as e:
        # Captura erros de validação do modelo Pydantic (ex: data_chegada inválida)
        flash(f"❌ Erro no formato dos dados (Pydantic): {e.errors()[0].get('msg', 'Erro desconhecido')}")
        return redirect(url_for("routes.forms_viagem"))
        
    except ValueError as e:
        # Captura erros de validação de negócio (lançados por funções internas do repo)
        flash(f"❌ Erro de Validação: {str(e)}")
        return redirect(url_for("routes.forms_viagem"))
        
    except Exception as e:
        # Captura erros inesperados (DB, conexão, etc.)
        flash(f"❌ Erro inesperado ao criar a viagem: {str(e)}")
        return redirect(url_for("routes.forms_viagem"))




