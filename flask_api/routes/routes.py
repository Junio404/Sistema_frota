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


bp = Blueprint('routes', __name__)



#------------------------------ PAGINA INICIAL ------------------------------------
@bp.route("/")
def index():
    return render_template("index.html")

#------------------------------- OPTIONS HTML -------------------------------------
@bp.route("/veiculo")
def veiculo_options():
    return render_template("options/veiculo_options.html")

@bp.route("/motorista")
def motorista_options():
    return render_template("options/motorista_options.html")

@bp.route("/relatórios")
def relatorio_options():
    return render_template("options/relatorio_options.html")



@bp.route("/viagem")
def forms_viagem():
    return render_template("forms/forms_viagem.html")

@bp.route("/motorista/create")
def forms_motorista():
    return render_template("forms/forms.html")



# -------------------- CREATE ROUTES --------------------

# -------------------- CRIAR MOTORISTA --------------------
@bp.route("/criar_motorista", methods=["POST"])
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

        return redirect(url_for("routes.index"))

    except ValueError as e:
        # ----- erros vindos do domínio (ex: CNH vencida) ----------
        flash(f"❌ Erro de validação: {e}")
        return redirect("/motorista/create")

    except Exception as e:
        print("Erro inesperado:", str(e))
        flash("❌ Ocorreu um erro inesperado.")
        return redirect("/motorista/create")

@bp.route("/modelo/read")
def tabela_modelo():
    return render_template("read/ver_modelos.html")

@bp.route("/motorista/read")
def tabela_motorista():
    return render_template("read/ver_motorista.html")

@bp.route("/veiculo/read")
def tabela_veiculo():
    return render_template("read/ver_veiculo.html")

@bp.route("/historico_veiculo/read")
def tabela_historico():
    return render_template("read/ver_historico_veiculo.html")


@bp.route("/relatorio/ranking_eficiencia")
def relatorio_eficiencia():
    return render_template("relatorio/relatorio_eficiencia.html")

@bp.route("/relatorio/quilometragem_media")
def relatorio_quilometragem():
    return render_template("relatorio/relatorio_km.html")

@bp.route("/relatorio/total_viagens")
def relatorio_total_viagens():
    return render_template("relatorio/relatorio_total_viagens.html")

@bp.route("/relatorio/custo_manutenções")
def relatorio_manutencao():
    return render_template("relatorio/relatorio_manutencao.html")
#---------------------------- CRIAR VEICULO ----------------------------
@bp.route("/veiculo/create")
def forms_veiculo():
    return render_template("forms/forms_veiculo.html")


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
        'status': request.form.get("disponibilidade", Veiculo_status.ATIVO.value),
        
        # ------- Dados obtidos do banco (substituem as 4 buscas individuais) --------
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
        return redirect(url_for("routes.forms_viagem"))

    # -------------- Buscar entidades -------------
    veiculo = repo_get_veiculo(placa_fk)
    if not veiculo:
        flash("❌ Veículo não encontrado.")
        return redirect(url_for("routes.forms_viagem"))

    motorista = repo_get_motorista(cpf_fk)
    if not motorista:
        flash("❌ Motorista não encontrado.")
        return redirect(url_for("routes.forms_viagem"))

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
        return redirect(url_for("routes.forms_viagem"))

    # ------- REGRAS DE NEGÓCIO — usando dados que seu repo oferece --------------

    # ----------------- Status do motorista ---------------------
    if motorista["DISPONIBILIDADE"] != Status_motorista.ATIVO.value:
        flash("❌ Motorista não está disponível.")
        return redirect(url_for("routes.forms_viagem"))

    # -------------- Status do veículo ----------------
    if veiculo["STATUS"] != Veiculo_status.ATIVO.value:
        flash("❌ Veículo não está disponível.")
        return redirect(url_for("routes.forms_viagem"))
    
    if veiculo["STATUS"] == Veiculo_status.PREVENTIVA_URGENTE.value:
        flash("❌ Veiculo precisa de uma revisão preventiva urgente! ")

    # ------------- Hodômetro atual -------------
    hodometro_atual = repo_get_quilometragem(placa_fk)
    if hodometro_atual is None:
        flash("❌ Erro ao obter quilometragem do veículo.")
        return redirect(url_for("routes.forms_viagem"))

    hodometro_final = hodometro_atual + distancia_km

    #--------- Consumo e combustível atual -----------
    consumo_medio, litros_atual = repo_get_consumo(placa_fk)
    litros_necessarios = distancia_km / consumo_medio

    if litros_necessarios > litros_atual:
        flash("❌ Combustível insuficiente para realizar a viagem.")
        return redirect(url_for("routes.forms_viagem"))

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
        return redirect(url_for("routes.index"))

    except Exception as e:
        flash(f"❌ Erro ao registrar viagem: {str(e)}")
        return redirect(url_for("routes.forms_viagem"))

    
@bp.route("/veiculo/abastecimento")
def forms_abastecimento():
    return render_template("forms/forms_abastecimento.html")
    

@bp.route("/criar_abastecimento", methods=["POST"])
def criar_abastecimento():
    try:
        placa_fk = request.form.get("placa_fk").upper()
        litros = float(request.form.get("litros"))
        hodometro = get_quilometragem_atual_abastecimento(placa_fk)

        #----------- Valida se Placa Existe ------------- 
        if not placa_existe(placa_fk):
            flash("❌ Placa não cadastrada.")
            return redirect(url_for("routes.forms_abastecimento"))

        #----------- Valida o Tipo de Combustivel do Veiculo ------------- 
        tipo_combustivel = buscar_tipo_combustivel(placa_fk)
        if tipo_combustivel is None:
            flash("❌ Tipo de combustível do veículo não encontrado.")
            return redirect(url_for("routes.forms_abastecimento"))

        #----------- Valida a Quantidade de Litros ------------- 
        qtd_litros_max = get_qtd_litros_abastecimento(placa_fk)

        try:
            validar_litros_qtd_combustivel(litros, qtd_litros_max)
        except ValueError as e:
            flash(f"❌ {str(e)}")
            return redirect(url_for("routes.forms_abastecimento"))

        #----------- Calcula o valor a Pagar ------------- 
        try:
            valor_pago = valor_a_pagar(tipo_combustivel, litros)
        except ValueError as e:
            flash(f"❌ {str(e)}")
            return redirect(url_for("routes.forms_abastecimento"))

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
            return redirect(url_for("routes.forms_abastecimento"))

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
        return redirect(url_for("routes.index"))

    except Exception as e:
        print("Erro ao cadastrar abastecimento:", e)
        flash("❌ Erro inesperado ao registrar abastecimento.")
        return redirect(url_for("routes.forms_abastecimento"))
    
    
    
@bp.route("/veiculo/manutencao")
def forms_manutencao():
    return render_template("forms/forms_manutencao.html")
    
CUSTOS_PREVENTIVA = {
    "MOTO": 150.00,
    "CARRO": 350.00,
    "CAMINHAO": 900.00
}
@bp.route("/criar_manutencao", methods=["POST"])
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
            return redirect(url_for("routes.forms_manutencao"))

        veiculo = repo_get_veiculo(placa_fk)
        #----------- Valida o Tipo de Manutenção -------------

        try:
            tipo_manutencao = Tipo_manutencao(tipo_str)
        except ValueError:
            flash("❌ Tipo de manutenção inválido.")
            return redirect(url_for("routes.forms_manutencao"))
        
                
        if veiculo["STATUS"] not in (
            Veiculo_status.ATIVO.value,
            Veiculo_status.INATIVO.value,
            Veiculo_status.PREVENTIVA_URGENTE.value
        ):
            flash("❌ Veículo não pode fazer manutenção agora.")
            return redirect(url_for("routes.forms_viagem"))


        # ----------- CASO SEJA CORRETIVA → validar campos obrigatórios -----------

        if tipo_manutencao == Tipo_manutencao.CORRETIVA:
            if not custo or not descricao:
                flash("❌ Para manutenção corretiva, custo e descrição são obrigatórios.")
                return redirect(url_for("routes.forms_manutencao"))

            try:
                custo = float(custo)
            except:
                flash("❌ Custo inválido.")
                return redirect(url_for("routes.forms_manutencao"))


        # --------- VALIDAR DATA DE CONCLUSÃO (corretiva opcional) -----------

        if data_conclusao:
            try:
                data_conclusao = date.fromisoformat(data_conclusao)
            except:
                flash("❌ Data de conclusão inválida.")
                return redirect(url_for("routes.forms_manutencao"))


        #----------- Validação com o MODELS -------------

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
            return redirect(url_for("routes.forms_manutencao"))


        #----------- Inserção no DB (Verifica se é preventiva ou corretiva) -------------

        print(dados_validados)
        manutencao = inserir_manutencao(dados_validados)
        atualizar_status_veiculo_manutencao(placa_fk)
        historico = repo_insert_evento_manutencao(manutencao)
        flash("🔧 Manutenção registrada com sucesso!")

        
        return redirect(url_for("routes.index"))

    except Exception as e:
        print("Erro ao cadastrar manutenção:", e)
        flash("❌ Erro inesperado ao registrar manutenção.")
        return redirect(url_for("routes.forms_manutencao"))
    
        
    
# -------------------- UPDATE ROUTES --------------------------------

@bp.route("/motorista/update")
def update_motorista():
    return render_template("atualizar/atualizar_motorista.html")

@bp.route("/atualizar_motorista", methods=["POST"])
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
        return redirect(url_for("routes.index"))

    except ValueError as e:
        flash(f"❌ Erro de validação: {e}")
        return redirect("/motorista/update")

    except Exception as e:
        print(f"Erro inesperado ao atualizar motorista: {e}")
        flash("❌ Erro inesperado no sistema.")
        return redirect("/motorista/update")


@bp.route("/veiculo/update")
def update_veiculo():
    return render_template("atualizar/atualizar_veiculo.html")

@bp.route("/atualizar_veiculo", methods=["POST"])
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
        return redirect(url_for("routes.index"))

    except Exception as e:
        print("Erro inesperado:", e)
        flash("❌ Ocorreu um erro ao atualizar o veículo.")
        return redirect("/veiculo/update")

#--------------------- DELETE ROUTES -------------------------------

@bp.route("/motorista/deletar")
def delete_motorista():
    return render_template("delete\deletar_motorista.html")


@bp.route("/deletar_motorista", methods=["POST"])
def deletar_motorista_route():
    try:
        cpf = request.form.get("cpf")
        # Recebe o cpf do formulário e valida se ele existe no Banco de Dados
        if not cpf_existe(cpf):
            flash("❌ Insira um CPF válido para deletar.")
            return redirect("/motorista/deletar")


# ------------ DELETAR ------------
        motorista_deletado = deletar_motorista(cpf)
        flash("✅ Motorista Deletado com sucesso!")
        return redirect(url_for('routes.index'))
        
    except ValueError as e:
        flash(f"❌ Erro de validação: {e}")
        return redirect("/motorista/deletar")

    except Exception as e:
        print(f"Erro inesperado ao deletar motorista: {e}")
        flash("❌ Erro inesperado no sistema.")
        return redirect("/motorista/deletar")
    
@bp.route("/veiculo/deletar")  
def delete_veiculo():
    return render_template("delete/deletar_veiculo.html")

@bp.route("/deletar_veiculo", methods=["POST"])
def deletar_veiculo_route():
    try:
        placa = request.form.get("placa")
        
        if not placa_existe(placa):
            flash("❌ Insira uma PLACA válida para deletar.")
            return redirect("/veiculo/deletar")
        
        veiculo_deletado = deletar_veiculo(placa)
        flash("✅ Veiculo Deletado com sucesso!")
        return redirect(url_for('routes.index'))
        
    except ValueError as e:
        flash(f"❌ Erro de validação: {e}")
        return redirect("/veiculo/deletar")

    except Exception as e:
        print(f"Erro inesperado ao deletar veiculo: {e}")
        flash("❌ Erro inesperado no sistema.")
        return redirect("/veiculo/deletar")
    

    
# ----------------------------- API / JSON DO BANCO ------------------------------------

@bp.route("/api/marcas_modelos")
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


@bp.route("/api/veiculos")
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



@bp.route("/api/motoristas")
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



@bp.route("/api/historico_veiculo")
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


@bp.route("/api/viagens")
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



@bp.route("/api/manutencoes")
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





# ------------------------ ERROR ROUTE ---------------------------
@bp.errorhandler(Exception)
def handle_exception(e):
    # Não deixa a api quebrar, em vez disso, renderiza uma tela de erro e permite o usuário voltar à tela principal.
    return render_template("erro.html", erro=str(e)), 500
