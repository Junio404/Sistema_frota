from flask import render_template, Blueprint, request, redirect, url_for, flash, jsonify
from flask_api.models.model_motorista import Motorista_create
from flask_api.models.model_veiculo import Veiculo_create
from flask_api.models.model_viagem import *
from flask_api.repositories.motorista_repo.motorista__repo import *
from flask_api.repositories.veiculo_repo.veiculo_repo import *
from flask_api.models.enums import *
import sqlite3
from config import Config
from flask_api.repositories.viagem_repo.viagem_repo import *
from flask_api.repositories.abastecimento_repo.abastecimento_repo import *
from pydantic import ValidationError
from flask_api.models.model_viagem import ViagemCreate
from flask_api.models.model_abastecimento import Abastecimento_create
from flask_api.domain_classes.dc_veiculo import Veiculo


bp = Blueprint('routes', __name__)



#------------------------------ PAGINA INICIAL ------------------------------------
@bp.route("/")
def index():
    return render_template("index.html")

#------------------------------- OPTIONS HTML -------------------------------------
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

@bp.route("/motorista/create")
def forms_motorista():
    return render_template("forms.html")



# -------------------- CREATE ROUTES --------------------

# -------------------- CRIAR MOTORISTA --------------------
@bp.route("/criar_motorista", methods=["POST"])
def criar_motorista():

    try:
        # ---------------------------
        # 1) Pegar dados do formulário
        # ---------------------------
        raw_data = {
            "nome": request.form.get("nome"),
            "cpf": request.form.get("cpf"),
            "cat_cnh": request.form.get("cnh"),
            "exp_anos": int(request.form.get("experiencia")),
            "disponibilidade": request.form.get("disponibilidade"),
            "cnh_valido_ate": request.form.get("cnh_valido_ate")
        }

        # ---------------------------
        # 2) Validar com Pydantic Model
        # ---------------------------
        pydantic_data = Motorista_create(**raw_data)

        # ---------------------------
        # 3) Validação adicional: CPF duplicado
        # ---------------------------
        if cpf_existe(pydantic_data.cpf):
            flash("❌ Este CPF já está cadastrado.")
            return redirect("/motorista/create")

        # ---------------------------
        # 4) Converter data string → date
        # Pydantic já aceita date, mas se vier string precisamos converter
        # ---------------------------
        if isinstance(pydantic_data.cnh_valido_ate, str):
            pydantic_data.cnh_valido_ate = datetime.strptime(
                pydantic_data.cnh_valido_ate, "%Y-%m-%d"
            ).date()

        # ---------------------------
        # 5) Criar objeto de domínio (Motorista)
        # ---------------------------
        motorista = Motorista(
            id=None,  # será gerado pelo BD
            nome=pydantic_data.nome,
            cpf=pydantic_data.cpf,
            cat_cnh=pydantic_data.cat_cnh,
            exp_anos=pydantic_data.exp_anos,
            disponibilidade=pydantic_data.disponibilidade.value,  # ENUM → string
            cnh_valido_ate=pydantic_data.cnh_valido_ate
        )

        # ---------------------------
        # 6) Persistir no repositório
        # ---------------------------
        inserir_motorista(motorista)
        flash("✅ Motorista cadastrado com sucesso!")

        return redirect(url_for("routes.index"))

    except ValueError as e:
        # erros vindos do domínio (ex: CNH vencida)
        flash(f"❌ Erro de validação: {e}")
        return redirect("/motorista/create")

    except Exception as e:
        print("Erro inesperado:", str(e))
        flash("❌ Ocorreu um erro inesperado.")
        return redirect("/motorista/create")

@bp.route("/veiculo/read")
def tabela_veiculos():
    return render_template("ver_modelos.html")

#---------------------------- CRIAR VEICULO ----------------------------
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
    if validar_placa_mercosul(placa) == False:
        flash("❌ Placa inválida. Use o padrão Mercosul (LLLNLNNN).")
        return redirect(url_for('routes.forms_veiculo'))

    # ------------------- BUSCA ÚNICA DO MODELO -------------------
    try:
        id_modelo = int(request.form.get("modelo_fk"))
    except (ValueError, TypeError):
        flash("❌ ID do Modelo inválido.")
        return redirect(url_for("routes.forms_veiculo"))

    # CHAMA A FUNÇÃO ÚNICA
    dados_modelo = buscar_dados_modelo(id_modelo) 
    
    if dados_modelo is None:
        flash("❌ Modelo não encontrado no banco de dados.")
        return redirect(url_for("routes.forms_veiculo"))
    
    # Desempacota os dados buscados para a variável 'raw_data'
    # Os dados buscados (tipo_veiculo, qtd_litros, consumo_medio, tipo_combustivel) 
    # sobrescrevem qualquer valor potencial do formulário, garantindo a integridade.
    
    # ------------------- MONTAR OBJETO Pydantic -------------------
    raw_data = {
        'placa': placa,
        'modelo_fk': id_modelo,
        'ano': int(request.form.get("ano")),
        'quilometragem': float(request.form.get("quilometragem")),
        'status': request.form.get("disponibilidade", Veiculo_status.ATIVO.value), # Use .value para o Pydantic, se for um Enum
        
        # Dados obtidos do banco (substituem as 4 buscas individuais)
        **dados_modelo
    }

    try:
        data = Veiculo_create(**raw_data)
    except Exception as e:
        flash(f"❌ Erro de validação de dados: {e}")
        return redirect(url_for("routes.forms_veiculo"))

    # ------------------- INSERT NO BANCO -------------------
    inserir_veiculo(data)

    flash("✅ Veículo cadastrado com sucesso!")
    return redirect(url_for("routes.index"))





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
        #Criação do objeto Pydantic (Validação de tipo e formato de dados)
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
    
    
@bp.route("/veiculo/abastecimento")
def forms_abastecimento():
    return render_template("forms_abastecimento.html")
    
@bp.route("/veiculo/abastecimento", methods=["POST"])
def criar_abastecimento():
    dados = request.form
    

    #-------------- Obtenção + pré-validação -----------------

    placa_fk = dados.get("placa_fk", "").upper()
    litros_str = dados.get("litros")

    try:
        if not placa_fk or not litros_str:
            raise ValueError("Todos os campos do formulário são obrigatórios.")
        
        litros = float(litros_str)

    except (TypeError, ValueError) as e:
        flash(f"❌ Erro de formulário: Campo 'litros' inválido. ({e})")
        return redirect(url_for("routes.forms_abastecimento"))

    # ----------------Validações de existência no sistema ---------------

    if not placa_existe(placa_fk):
        flash("❌ Placa não está cadastrada no sistema.")
        return redirect(url_for("routes.forms_abastecimento"))
    
    tipo_combustivel = buscar_tipo_combustivel(placa_fk)

    if not tipo_combustivel:
        flash("❌ Esse veículo não possui tipo de combustível cadastrado.")
        return redirect(url_for("routes.forms_abastecimento"))

    # ----------------Calculo do Valor---------------

    try:
        valor = valor_a_pagar(tipo_combustivel, litros)

    except ValueError as e:
        flash(f"❌ Erro de Validação: {str(e)}")
        return redirect(url_for("routes.forms_abastecimento"))

    except Exception as e:
        flash(f"❌ Erro inesperado no cálculo: {str(e)}")
        return redirect(url_for("routes.forms_abastecimento"))

    # ----------------Validação com PYDANTIC ---------------

    try:
        raw_data = {
            "placa_fk": placa_fk,
            "tipo_combustivel": tipo_combustivel,
            "data": date.today().isoformat(),
            "litros": litros,
            "valor_pago": valor,
            "hodometro": get_quilometragem_atual(placa_fk)
        }

        data = Abastecimento_create(**raw_data)

    except ValidationError as e:
        flash(f"❌ Erro no formato dos dados (Pydantic): {e.errors()[0].get('msg', 'Erro desconhecido')}")
        return redirect(url_for("routes.forms_abastecimento"))

    except Exception as e:
        flash(f"❌ Erro inesperado ao validar dados: {str(e)}")
        return redirect(url_for("routes.forms_abastecimento"))

    # ----------------Adicionar ao Banco de Dados ---------------
    
    try:
        resultado = inserir_abastecimento(data)
        flash("⛽ Abastecimento registrado com sucesso!")
        return redirect(url_for("routes.index"))

    except ValueError as e:
        flash(f"❌ Erro ao salvar abastecimento: {str(e)}")
        return redirect(url_for("routes.forms_abastecimento"))

    except Exception as e:
        flash(f"❌ Erro inesperado ao salvar no banco de dados: {str(e)}")
        return redirect(url_for("routes.forms_abastecimento"))
    
    
    
    
        
    
        

# @bp.errorhandler(Exception)
# def handle_exception(e):
#     return render_template("erro.html", erro=str(e)), 500
















#------------------------ API / JSON DO BANCO ------------------------------------

@bp.route("/api/marcas_modelos")
def api_marcas_modelos():
    
    # Usando uma busca centralizada para todos os modelos com JOIN
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # 1. Pega todas as marcas e seus modelos em UMA ÚNICA consulta JOIN
        # Isso é mais eficiente do que o loop original que fazia N consultas.
        cur.execute("""
            SELECT 
                M.ID AS marca_id, 
                M.NOME AS marca_nome,
                MO.ID AS modelo_id,
                MO.NOME_MODELO,
                MO.TIPO_VEICULO,
                TVC.CAT_MIN_CNH,                 -- BUSCADO DO JOIN
                MO.QTD_LITROS,
                MO.CONSUMO_MEDIO_KM_L,
                MO.TIPO_COMBUSTIVEL              -- Adicionado para completar o modelo
            FROM MARCA M
            LEFT JOIN MODELO MO ON M.ID = MO.MARCA_FK
            LEFT JOIN TIPO_VEICULO_CNH TVC ON MO.TIPO_VEICULO = TVC.TIPO_VEICULO
            ORDER BY M.NOME, MO.NOME_MODELO
        """)
        
        todos_modelos = cur.fetchall()
        
    # 2. Processamento dos dados para estruturar o JSON
    resultado_agrupado = {}

    for row in todos_modelos:
        marca_nome = row['marca_nome']
        
        # Inicializa a lista de modelos para a marca se ainda não existir
        if marca_nome not in resultado_agrupado:
            resultado_agrupado[marca_nome] = {
                "marca": marca_nome,
                "modelos": []
            }
        
        # Adiciona os detalhes do modelo (se houver)
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

    # Converte o dicionário de agrupamento em uma lista de valores para o formato final
    resultado_final = list(resultado_agrupado.values())

    # 3. Retorna o resultado usando jsonify do Flask
    return jsonify(resultado_final)









