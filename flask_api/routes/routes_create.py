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


bp_routes_create = Blueprint('routes_create', __name__)



@bp_routes_create.route("/viagem")
def forms_viagem():
    return render_template("forms/forms_viagem.html")

@bp_routes_create.route("/motorista/create")
def forms_motorista():
    return render_template("forms/forms.html")



# -------------------- CREATE ROUTES --------------------

# -------------------- CRIAR MOTORISTA --------------------
@bp_routes_create.route("/criar_motorista", methods=["POST"])
def criar_motorista():

    try:
        
        # ---------------- Pegar dados do formulário -----------------
        
        raw_data = {
            "nome": request.form.get("nome"),
            "cpf": request.form.get("cpf"),
            "cat_cnh": request.form.get("cnh"),
            "exp_anos": int(request.form.get("experiencia")),
            "disponibilidade": request.form.get("disponibilidade"),
            "cnh_valido_ate": request.form.get("cnh_valido_ate")
        }

        # ----------Validar com Pydantic Model ------------------
        
        pydantic_data = Motorista_create(**raw_data)

        # --------- Validação adicional: CPF duplicado -------------

        if cpf_existe(pydantic_data.cpf):
            flash("❌ Este CPF já está cadastrado.")
            return redirect("/motorista/create")


        # ---------- Converter data string → date (para evitar qualquer erro de tipagem) ---------


        if isinstance(pydantic_data.cnh_valido_ate, str):
            pydantic_data.cnh_valido_ate = datetime.strptime(
                pydantic_data.cnh_valido_ate, "%Y-%m-%d"
            ).date()

        
        # ------------- 5) Criar objeto de domínio (Motorista) ---------------

        motorista = Motorista(
            id=None,  # será gerado pelo BD
            nome=pydantic_data.nome,
            cpf=pydantic_data.cpf,
            cat_cnh=pydantic_data.cat_cnh,
            exp_anos=pydantic_data.exp_anos,
            disponibilidade=pydantic_data.disponibilidade.value,  # ENUM → string
            cnh_valido_ate=pydantic_data.cnh_valido_ate
        )
        # ----------------- Persistir no Banco de Dados -----------------

        inserir_motorista(motorista)
        flash("✅ Motorista cadastrado com sucesso!")

        return redirect(url_for("routes_index.index"))

    except ValueError as e:
        # ----- erros vindos do domínio (ex: CNH vencida) ----------
        flash(f"❌ Erro de validação: {e}")
        return redirect("/motorista/create")

    except Exception as e:
        print("Erro inesperado:", str(e))
        flash("❌ Ocorreu um erro inesperado.")
        return redirect("/motorista/create")

#---------------------------- CRIAR VEICULO ----------------------------
@bp_routes_create.route("/veiculo/create")
def forms_veiculo():
    return render_template("forms/forms_veiculo.html")


@bp_routes_create.route("/criar_veiculo", methods=["POST"])
def criar_veiculo():
    
    # ------------------- VALIDAÇÃO PLACA -------------------
    placa = request.form.get("placa")

    if not placa:
        flash("❌ Placa não informada.")
        return redirect(url_for("routes_create.forms_veiculo"))
    if validar_placa_mercosul(placa) == False:
        flash("❌ Placa inválida. Use o padrão Mercosul (LLLNLNNN).")
        return redirect(url_for('routes_create.forms_veiculo'))
    if placa_existe(placa):
        flash("❌ Já há um veiculo com essa placa no sistema!")
        return redirect(url_for('routes_create.forms_veiculo'))

    # ------------------- BUSCA ÚNICA DO MODELO -------------------
    try:
        id_modelo = int(request.form.get("modelo_fk"))
    except (ValueError, TypeError):
        flash("❌ ID do Modelo inválido.")
        return redirect(url_for("routes_create.forms_veiculo"))

    # CHAMA A FUNÇÃO ÚNICA
    dados_modelo = buscar_dados_modelo(id_modelo) 
    
    if dados_modelo is None:
        flash("❌ Modelo não encontrado no banco de dados.")
        return redirect(url_for("routes_create.forms_veiculo"))
    
    # Desempacota os dados buscados para a variável 'raw_data'
    # Os dados buscados (tipo_veiculo, qtd_litros, consumo_medio, tipo_combustivel) 
    # sobrescrevem qualquer valor potencial do formulário, garantindo a integridade.
    
    # ------------------- MONTAR OBJETO Pydantic -------------------
    raw_data = {
        'placa': placa,
        'modelo_fk': id_modelo,
        'ano': int(request.form.get("ano")),
        'quilometragem': float(request.form.get("quilometragem")),
        'status': request.form.get("disponibilidade", Veiculo_status.ATIVO.value),
        
        # ------- Dados obtidos do banco (substituem as 4 buscas individuais) --------
        **dados_modelo
    }
    
    if raw_data["quilometragem"] < 0:
        flash("❌ Quilometragem Inválida")
        return redirect(url_for("routes_create.forms_veiculo"))
        

    try:
        data = Veiculo_create(**raw_data)
    except Exception as e:
        flash(f"❌ Erro de validação de dados: {e}")
        return redirect(url_for("routes_create.forms_veiculo"))

    # ------------------- INSERT NO BANCO -------------------
    inserir_veiculo(data)

    flash("✅ Veículo cadastrado com sucesso!")
    return redirect(url_for("routes_index.index"))





@bp_routes_create.route("/criar_viagem", methods=["POST"])
def criar_viagem_route():

    # ---------- Dados do formulário ----------------
    dados = request.form
    placa_fk = dados.get("placa_fk")
    cpf_fk = dados.get("cpf_fk")
    origem = dados.get("origem")
    destino = dados.get("destino")
    distancia_str = dados.get("distancia_km")
    data_chegada = dados.get("data_chegada")

    # ---------------- Validação básica ---------------
    try:
        if not placa_fk or not cpf_fk or not origem or not destino or not distancia_str or not data_chegada:
            raise ValueError("Todos os campos são obrigatórios.")

        distancia_km = float(distancia_str)

    except ValueError as e:
        flash(f"❌ Erro: {str(e)}")
        return redirect(url_for("routes_create.forms_viagem"))

    # -------------- Buscar entidades -------------
    veiculo = repo_get_veiculo(placa_fk)
    if not veiculo:
        flash("❌ Veículo não encontrado.")
        return redirect(url_for("routes_create.forms_viagem"))

    motorista = repo_get_motorista(cpf_fk)
    if not motorista:
        flash("❌ Motorista não encontrado.")
        return redirect(url_for("routes_create.forms_viagem"))

    # -------- Modelo Pydantic ------------
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
        return redirect(url_for("routes_create.forms_viagem"))

    # ------- REGRAS DE NEGÓCIO --------------

    # ----------------- Status do motorista ---------------------
    if motorista["DISPONIBILIDADE"] != Status_motorista.ATIVO.value:
        flash("❌ Motorista não está disponível.")
        return redirect(url_for("routes_create.forms_viagem"))

    # -------------- Status do veículo ----------------
    if veiculo["STATUS"] != Veiculo_status.ATIVO.value:
        flash("❌ Veículo não está disponível.")
        return redirect(url_for("routes_create.forms_viagem"))
    
    if veiculo["STATUS"] == Veiculo_status.PREVENTIVA_URGENTE.value:
        flash("❌ Veiculo precisa de uma revisão preventiva urgente! ")

    # ------------- Hodômetro atual -------------
    hodometro_atual = repo_get_quilometragem(placa_fk)
    if hodometro_atual is None:
        flash("❌ Erro ao obter quilometragem do veículo.")
        return redirect(url_for("routes_create.forms_viagem"))

    hodometro_final = hodometro_atual + distancia_km

    #--------- Consumo e combustível atual -----------
    consumo_medio, litros_atual = repo_get_consumo(placa_fk)
    litros_necessarios = distancia_km / consumo_medio

    if litros_necessarios > litros_atual:
        flash("❌ Combustível insuficiente para realizar a viagem.")
        return redirect(url_for("routes_create.forms_viagem"))

    novo_nivel_combustivel = litros_atual - litros_necessarios

    #-----------Persistência — todas as operações dentro da mesma transação ------------- 
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
        return redirect(url_for("routes_index.index"))

    except Exception as e:
        flash(f"❌ Erro ao registrar viagem: {str(e)}")
        return redirect(url_for("routes_create.forms_viagem"))

    
@bp_routes_create.route("/veiculo/abastecimento")
def forms_abastecimento():
    return render_template("forms/forms_abastecimento.html")
    

@bp_routes_create.route("/criar_abastecimento", methods=["POST"])
def criar_abastecimento():
    try:
        placa_fk = request.form.get("placa_fk").upper()
        litros = float(request.form.get("litros"))
        hodometro = get_quilometragem_atual_abastecimento(placa_fk)

        #----------- Valida se Placa Existe ------------- 
        if not placa_existe(placa_fk):
            flash("❌ Placa não cadastrada.")
            return redirect(url_for("routes_create.forms_abastecimento"))

        #----------- Valida o Tipo de Combustivel do Veiculo ------------- 
        tipo_combustivel = buscar_tipo_combustivel(placa_fk)
        if tipo_combustivel is None:
            flash("❌ Tipo de combustível do veículo não encontrado.")
            return redirect(url_for("routes_create.forms_abastecimento"))

        #----------- Valida a Quantidade de Litros ------------- 
        qtd_litros_max = get_qtd_litros_abastecimento(placa_fk)

        try:
            validar_litros_qtd_combustivel(litros, qtd_litros_max)
        except ValueError as e:
            flash(f"❌ {str(e)}")
            return redirect(url_for("routes_create.forms_abastecimento"))

        #----------- Calcula o valor a Pagar ------------- 
        try:
            valor_pago = valor_a_pagar(tipo_combustivel, litros)
        except ValueError as e:
            flash(f"❌ {str(e)}")
            return redirect(url_for("routes_create.forms_abastecimento"))

        #----------- Validação com o Model antes de criar o objeto ------------- 
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
            return redirect(url_for("routes_create.forms_abastecimento"))

        #----------- Cria objeto abastecimento com a classe de domínio ------------- 
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

        #----------- Insert no Banco ------------- 
        inserir_abastecimento(abastecimento)
        insert_evento_abastecimento(abastecimento)
        atualizar_litros_combustivel_abastecimento(litros, qtd_litros_max, placa_fk)

        flash("⛽ Abastecimento registrado com sucesso!")
        return redirect(url_for("routes_index.index"))

    except Exception as e:
        print("Erro ao cadastrar abastecimento:", e)
        flash("❌ Erro inesperado ao registrar abastecimento.")
        return redirect(url_for("routes_create.forms_abastecimento"))
    
    
    
@bp_routes_create.route("/veiculo/manutencao")
def forms_manutencao():
    return render_template("forms/forms_manutencao.html")
    
CUSTOS_PREVENTIVA = {
    "MOTO": 150.00,
    "CARRO": 350.00,
    "CAMINHAO": 900.00
}
@bp_routes_create.route("/criar_manutencao", methods=["POST"])
def criar_manutencao_route():
    try:
        placa_fk = request.form.get("placa_fk", "").upper()
        tipo_str = request.form.get("tipo_manutencao", "")
        descricao = request.form.get("descricao")
        custo = request.form.get("custo")
        data_conclusao = request.form.get("data_conclusao")
        
        
        print(tipo_str)

        #----------- Valida se Placa Existe ------------- 
        if not placa_existe(placa_fk):
            flash("❌ Placa não cadastrada.")
            return redirect(url_for("routes_create.forms_manutencao"))

        veiculo = repo_get_veiculo(placa_fk)
        #----------- Valida o Tipo de Manutenção -------------

        try:
            tipo_manutencao = Tipo_manutencao(tipo_str)
        except ValueError:
            flash("❌ Tipo de manutenção inválido.")
            return redirect(url_for("routes_create.forms_manutencao"))
        
                
        if veiculo["STATUS"] not in (
            Veiculo_status.ATIVO.value,
            Veiculo_status.INATIVO.value,
            Veiculo_status.PREVENTIVA_URGENTE.value
        ):
            flash("❌ Veículo não pode fazer manutenção agora.")
            return redirect(url_for("routes_create.forms_viagem"))


        # ----------- CASO SEJA CORRETIVA → validar campos obrigatórios -----------

        if tipo_manutencao == Tipo_manutencao.CORRETIVA:
            if not custo or not descricao:
                flash("❌ Para manutenção corretiva, custo e descrição são obrigatórios.")
                return redirect(url_for("routes_create.forms_manutencao"))

            try:
                custo = float(custo)
            except:
                flash("❌ Custo inválido.")
                return redirect(url_for("routes_create.forms_manutencao"))


        # --------- VALIDAR DATA_create DE CONCLUSÃO (corretiva opcional) -----------

        if data_conclusao:
            try:
                data_conclusao = date.fromisoformat(data_conclusao)
            except:
                flash("❌ Data de conclusão inválida.")
                return redirect(url_for("routes_create.forms_manutencao"))


        #----------- Validação com o_create MODELS -------------

        try:
            dados_validados = Manutencao_create(
                placa_fk=placa_fk,
                tipo_manutencao=tipo_manutencao,
                data_conclusao=data_conclusao,
                descricao=descricao,
                custo=custo
            )
        except ValidationError as e:
            flash(f"❌ Dados inválidos: {e.errors()}")
            return redirect(url_for("routes_create.forms_manutencao"))


        #----------- Inserção no DB_create (Verifica se é preventiva ou corretiva) -------------

        print(dados_validados)
        manutencao = inserir_manutencao(dados_validados)
        atualizar_status_veiculo_manutencao(placa_fk)
        historico = repo_insert_evento_manutencao(manutencao)
        flash("🔧 Manutenção registrada com sucesso!")

        
        return redirect(url_for("routes_index.index"))

    except Exception as e:
        print("Erro ao cadastrar manutenção:", e)
        flash("❌ Erro inesperado_create ao registrar manutenção.")
        return redirect(url_for("routes_create.forms_manutencao"))
    