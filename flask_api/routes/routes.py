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

@bp.route("/modelo/read")
def tabela_modelo():
    return render_template("ver_modelos.html")

@bp.route("/motorista/read")
def tabela_motorista():
    return render_template("ver_motorista.html")

@bp.route("/veiculo/read")
def tabela_veiculo():
    return render_template("ver_veiculo.html")

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
    if placa_existe(placa):
        flash("❌ Já há um veiculo com essa placa no sistema!")
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
    
    if raw_data["quilometragem"] < 0:
        flash("❌ Quilometragem Inválida")
        return redirect(url_for("routes.forms_veiculo"))
        

    try:
        data = Veiculo_create(**raw_data)
    except Exception as e:
        flash(f"❌ Erro de validação de dados: {e}")
        return redirect(url_for("routes.forms_veiculo"))

    # ------------------- INSERT NO BANCO -------------------
    inserir_veiculo(data)

    flash("✅ Veículo cadastrado com sucesso!")
    return redirect(url_for("routes.index"))





@bp.route("/criar_viagem", methods=["POST"])
def criar_viagem_route():

    # 1. Dados do formulário
    dados = request.form
    placa_fk = dados.get("placa_fk")
    cpf_fk = dados.get("cpf_fk")
    origem = dados.get("origem")
    destino = dados.get("destino")
    distancia_str = dados.get("distancia_km")
    data_chegada = dados.get("data_chegada")

    # 2. Validação básica
    try:
        if not placa_fk or not cpf_fk or not origem or not destino or not distancia_str or not data_chegada:
            raise ValueError("Todos os campos são obrigatórios.")

        distancia_km = float(distancia_str)

    except ValueError as e:
        flash(f"❌ Erro: {str(e)}")
        return redirect(url_for("routes.forms_viagem"))

    # 3. Buscar entidades
    veiculo = repo_get_veiculo(placa_fk)
    if not veiculo:
        flash("❌ Veículo não encontrado.")
        return redirect(url_for("routes.forms_viagem"))

    motorista = repo_get_motorista(cpf_fk)
    if not motorista:
        flash("❌ Motorista não encontrado.")
        return redirect(url_for("routes.forms_viagem"))

    # 4. Modelo Pydantic
    try:
        viagem = ViagemCreate(
            placa_fk=placa_fk,
            cpf_fk=cpf_fk,
            origem=origem,
            destino=destino,
            distancia_km=distancia_km,
            data_chegada=data_chegada,
        )
    except Exception as e:
        flash(f"❌ Erro nos dados da viagem: {str(e)}")
        return redirect(url_for("routes.forms_viagem"))

    # 5. REGRAS DE NEGÓCIO — usando dados que seu repo oferece

    # Status do motorista
    if motorista["DISPONIBILIDADE"] != Status_motorista.ATIVO.value:
        flash("❌ Motorista não está disponível.")
        return redirect(url_for("routes.forms_viagem"))

    # Status do veículo
    if veiculo["STATUS"] != Veiculo_status.ATIVO.value:
        flash("❌ Veículo não está disponível.")
        return redirect(url_for("routes.forms_viagem"))

    # Hodômetro atual
    hodometro_atual = repo_get_quilometragem(placa_fk)
    if hodometro_atual is None:
        flash("❌ Erro ao obter quilometragem do veículo.")
        return redirect(url_for("routes.forms_viagem"))

    hodometro_final = hodometro_atual + distancia_km

    # Consumo e combustível atual
    consumo_medio, litros_atual = repo_get_consumo(placa_fk)
    litros_necessarios = distancia_km / consumo_medio

    if litros_necessarios > litros_atual:
        flash("❌ Combustível insuficiente para realizar a viagem.")
        return redirect(url_for("routes.forms_viagem"))

    novo_nivel_combustivel = litros_atual - litros_necessarios

    # 6. Persistência — todas as operações dentro da mesma transação
    try:
        with conectar() as conn:
            # Inserir viagem
            repo_insert_viagem(
                conn,
                viagem,
                hodometro_atual,
                hodometro_final
            )

            # Inserir histórico
            repo_insert_evento_viagem(conn, viagem)

            # Atualizar veículo
            repo_update_veiculo_viagem(
                conn,
                placa_fk,
                hodometro_final
            )

            # Atualizar combustível
            repo_update_combustivel(
                conn,
                placa_fk,
                novo_nivel_combustivel
            )

            # Atualizar motorista
            repo_update_motorista_viagem(
                conn,
                cpf_fk
            )

            conn.commit()

        flash("🚗💨 Viagem registrada com sucesso!")
        return redirect(url_for("routes.index"))

    except Exception as e:
        flash(f"❌ Erro ao registrar viagem: {str(e)}")
        return redirect(url_for("routes.forms_viagem"))

    
@bp.route("/veiculo/abastecimento")
def forms_abastecimento():
    return render_template("forms_abastecimento.html")
    

@bp.route("/criar_abastecimento", methods=["POST"])
def criar_abastecimento():
    try:
        placa_fk = request.form.get("placa_fk").upper()
        litros = float(request.form.get("litros"))
        hodometro = get_quilometragem_atual_abastecimento(placa_fk)

        # ---------------------------------------------
        # 1 — VALIDAR SE A PLACA EXISTE
        # ---------------------------------------------
        if not placa_existe(placa_fk):
            flash("❌ Placa não cadastrada.")
            return redirect(url_for("routes.forms_abastecimento"))

        # ---------------------------------------------
        # 2 — BUSCAR TIPO DE COMBUSTÍVEL DO VEÍCULO
        # ---------------------------------------------
        tipo_combustivel = buscar_tipo_combustivel(placa_fk)
        if tipo_combustivel is None:
            flash("❌ Tipo de combustível do veículo não encontrado.")
            return redirect(url_for("routes.forms_abastecimento"))

        # ---------------------------------------------
        # 3 — VALIDAR QUANTIDADE DE LITROS
        # ---------------------------------------------
        qtd_litros_max = get_qtd_litros_abastecimento(placa_fk)

        try:
            validar_litros_qtd_combustivel(litros, qtd_litros_max)
        except ValueError as e:
            flash(f"❌ {str(e)}")
            return redirect(url_for("routes.forms_abastecimento"))

        # ---------------------------------------------
        # 4 — CALCULAR VALOR A PAGAR
        # ---------------------------------------------
        try:
            valor_pago = valor_a_pagar(tipo_combustivel, litros)
        except ValueError as e:
            flash(f"❌ {str(e)}")
            return redirect(url_for("routes.forms_abastecimento"))

        # ---------------------------------------------
        # 5 — VALIDAR COM Pydantic ANTES DE CRIAR OBJETO
        # ---------------------------------------------
        try:
            dados_validados = Abastecimento_create(
                placa_fk=placa_fk,
                tipo_combustivel=tipo_combustivel,
                data=date.today(),
                litros=litros,
                valor_pago=valor_pago,
                hodometro=hodometro
            )
        except ValidationError as e:
            flash(f"❌ Dados inválidos: {e.errors()}")
            return redirect(url_for("routes.forms_abastecimento"))

        # ---------------------------------------------
        # 6 — CRIAR OBJETO ABASTECIMENTO
        # ---------------------------------------------
        abastecimento = Abastecimento(
            id=None,
            placa_fk=dados_validados.placa_fk,
            tipo_combustivel=dados_validados.tipo_combustivel.value
                if hasattr(dados_validados.tipo_combustivel, "value")
                else dados_validados.tipo_combustivel,
            data=dados_validados.data,
            litros=dados_validados.litros,
            valor_pago=dados_validados.valor_pago,
            hodometro=dados_validados.hodometro
        )

        # ---------------------------------------------
        # 7 — INSERIR NO BANCO
        # ---------------------------------------------
        inserir_abastecimento(abastecimento)
        insert_evento_abastecimento(abastecimento)
        atualizar_litros_combustivel_abastecimento(litros, qtd_litros_max, placa_fk)

        flash("⛽ Abastecimento registrado com sucesso!")
        return redirect(url_for("routes.index"))

    except Exception as e:
        print("Erro ao cadastrar abastecimento:", e)
        flash("❌ Erro inesperado ao registrar abastecimento.")
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



@bp.route("/api/veiculos")
def api_veiculos():

    with sqlite3.connect(Config.DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

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

            "modelo": {
                "id": r["modelo_id"],
                "nome_modelo": r["NOME_MODELO"],
                "tipo_veiculo": r["modelo_tipo_veiculo"],
                "tipo_combustivel": r["modelo_tipo_combustivel"],
                "qtd_litros": r["modelo_qtd_litros"],
                "consumo_medio_km_l": r["modelo_consumo"]
            },

            "marca": {
                "id": r["marca_id"],
                "nome": r["marca_nome"]
            }
        })

    return jsonify(veiculos)



@bp.route("/api/motoristas")
def api_motoristas():

    with sqlite3.connect(Config.DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

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

    return jsonify(motoristas)


