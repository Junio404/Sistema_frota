import sqlite3
from datetime import date
from typing import Optional, Dict

# Assumindo que você tem um arquivo de configuração ou usa um path fixo.
# Se você usa 'Config.DATABASE', mude o valor default abaixo.
DB_PATH = "meu_banco.db" 

from flask_api.models.enums import (
    Status_motorista,
    Veiculo_status,
    Status_viagem,
    Tipo_evento
)
from flask_api.models.model_viagem import ViagemCreate # Assumindo que este é o nome do seu arquivo

# =============================================================
# MAPEAMENTO DE CATEGORIAS MÍNIMAS PARA CNH
# (Este dicionário é fixo, mas poderia ser obtido da tabela TIPO_VEICULO_CNH)
# =============================================================
Tipo_veiculo_cnh = {
    "MOTO": "A",
    "CARRO": "B",
    "CAMINHAO": "C"
}

# =============================================================
# CONEXÃO COM O BANCO
# =============================================================
def conectar(db_path: str = DB_PATH):
    """Cria e retorna uma nova conexão com o banco de dados."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


# =============================================================
# REPOSITÓRIO: BUSCAS SIMPLES (USADAS PELA ROTA)
# =============================================================

def repo_buscar_veiculo_por_placa(placa: str, db_path: str = DB_PATH) -> Optional[Dict]:
    """Busca dados de um veículo por placa."""
    with conectar(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                PLACA, MODELO_FK, TIPO_VEICULO, ANO,
                QUILOMETRAGEM, QTD_LITROS, CONSUMO_MEDIO_KM_L, STATUS
            FROM VEICULO
            WHERE PLACA = ?
        """, (placa,))
        row = cur.fetchone()
        return dict(row) if row else None


def repo_buscar_motorista_por_cpf(cpf: str, db_path: str = DB_PATH) -> Optional[Dict]:
    """Busca dados de um motorista por CPF (incluindo dados de Pessoa)."""
    with conectar(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                M.ID, M.CPF, M.CAT_CNH, M.EXP_ANOS, M.DISPONIBILIDADE, M.CNH_VALIDO_ATE,
                P.NOME 
            FROM MOTORISTA M
            JOIN PESSOA P ON M.CPF = P.CPF
            WHERE M.CPF = ?
        """, (cpf,))
        row = cur.fetchone()
        return dict(row) if row else None


# =============================================================
# REPOSITÓRIO: VALIDAÇÕES DE NEGÓCIO (USADAS INTERNAMENTE)
# =============================================================

def validar_status_motorista(conn: sqlite3.Connection, cpf: str) -> str:
    """Verifica status e retorna a categoria CNH do motorista."""
    cur = conn.cursor()
    cur.execute("""
        SELECT DISPONIBILIDADE, CAT_CNH 
        FROM MOTORISTA 
        WHERE CPF = ?
    """, (cpf,))
    row = cur.fetchone()

    if not row:
        raise ValueError("Motorista não encontrado.")

    disponibilidade = row["DISPONIBILIDADE"]
    cat_cnh = row["CAT_CNH"]

    if disponibilidade == Status_motorista.INATIVO.value:
        raise ValueError("Motorista está INATIVO e não pode iniciar viagem.")

    if disponibilidade == Status_motorista.EM_VIAGEM.value:
        raise ValueError("Motorista já está em viagem.")

    return cat_cnh


def validar_status_veiculo(conn: sqlite3.Connection, placa: str) -> str:
    """Verifica status e retorna o tipo de veículo (MOTO/CARRO/CAMINHAO)."""
    cur = conn.cursor()

    # CORREÇÃO: M.ID em vez de M.ID_MODELO e M.TIPO_VEICULO em vez de M.TIPO
    cur.execute("""
        SELECT V.STATUS, M.TIPO_VEICULO
        FROM VEICULO V
        JOIN MODELO M ON M.ID = V.MODELO_FK
        WHERE V.PLACA = ?
    """, (placa,))
    
    row = cur.fetchone()

    if not row:
        raise ValueError("Veículo não encontrado.")

    status = row["STATUS"]
    tipo_veiculo = row["TIPO_VEICULO"]

    if status == Veiculo_status.INATIVO.value:
        raise ValueError("Veículo está INATIVO e não pode iniciar viagem.")

    if status == Veiculo_status.MANUTENCAO.value:
        raise ValueError("Veículo está em MANUTENÇÃO e não pode iniciar viagem.")

    if status == Veiculo_status.EM_VIAGEM.value:
        raise ValueError("Veículo já está em viagem.")

    return tipo_veiculo


def validar_cnh_motorista_para_veiculo(cat_cnh_motorista: str, tipo_veiculo: str):
    """Verifica se a CNH do motorista é compatível com o veículo."""
    categoria_minima = Tipo_veiculo_cnh.get(tipo_veiculo)

    if categoria_minima is None:
        raise ValueError(f"Tipo de veículo '{tipo_veiculo}' não possui categoria CNH mínima definida.")

    ordem = ["A", "B", "C", "D", "E"] # Assumindo ordem crescente de complexidade

    if ordem.index(cat_cnh_motorista) < ordem.index(categoria_minima):
        raise ValueError(
            f"CNH incompatível. Para dirigir {tipo_veiculo}, o mínimo é {categoria_minima}, "
            f"mas o motorista possui {cat_cnh_motorista}."
        )


# =============================================================
# REPOSITÓRIO: CÁLCULOS E ATUALIZAÇÕES
# =============================================================

def get_quilometragem_atual(conn: sqlite3.Connection, placa: str) -> float:
    """Obtém a quilometragem atual do veículo."""
    cur = conn.cursor()
    cur.execute("SELECT QUILOMETRAGEM FROM VEICULO WHERE PLACA = ?", (placa,))
    row = cur.fetchone()

    if not row:
        # Tecnicamente não deveria ocorrer se validar_status_veiculo passou
        raise ValueError("Veículo não encontrado.") 

    return float(row["QUILOMETRAGEM"])


def calcular_hodometro_chegada(quilometragem_atual: float, distancia_km: float) -> float:
    """Calcula o hodômetro final da viagem."""
    if distancia_km <= 0:
        raise ValueError("Distância da viagem deve ser maior que zero.")
        
    return quilometragem_atual + distancia_km


def get_consumo_e_combustivel(conn: sqlite3.Connection, placa: str) -> tuple[float, float]:
    """Obtém consumo médio e litros atuais do veículo."""
    cur = conn.cursor()
    cur.execute("""
        SELECT CONSUMO_MEDIO_KM_L, QTD_LITROS
        FROM VEICULO
        WHERE PLACA = ?
    """, (placa,))
    row = cur.fetchone()

    if not row:
         # Tecnicamente não deveria ocorrer se validar_status_veiculo passou
        raise ValueError("Veículo não encontrado.") 

    return float(row["CONSUMO_MEDIO_KM_L"]), float(row["QTD_LITROS"])


def calcular_novo_nivel_combustivel(distancia_km: float, consumo_medio_km_l: float, qtd_litros_atual: float) -> float:
    """Calcula o nível de combustível após a viagem e verifica se é suficiente."""
    if consumo_medio_km_l <= 0:
        raise ValueError("Consumo médio do veículo inválido.")

    litros_gastos = distancia_km / consumo_medio_km_l
    
    if litros_gastos > qtd_litros_atual:
        # Nova validação importante: evitar que o combustível fique negativo se a viagem for longa demais
        raise ValueError(f"Combustível insuficiente. Necessário {litros_gastos:.2f}L, disponível {qtd_litros_atual:.2f}L.")

    novo_nivel = qtd_litros_atual - litros_gastos
    
    # Garantindo que nunca retorne um valor negativo no banco (embora a validação acima ajude)
    return max(novo_nivel, 0) 


def atualizar_qtd_litros(conn: sqlite3.Connection, placa: str, novo_qtd_litros: float):
    """Atualiza a quantidade de litros no tanque do veículo."""
    cur = conn.cursor()
    cur.execute("""
        UPDATE VEICULO
        SET QTD_LITROS = ?
        WHERE PLACA = ?
    """, (novo_qtd_litros, placa))


def processar_consumo_veiculo(conn: sqlite3.Connection, placa: str, distancia_km: float) -> float:
    """Orquestra o cálculo e atualização do consumo de combustível."""
    consumo_medio, qtd_litros_atual = get_consumo_e_combustivel(conn, placa)

    novo_nivel = calcular_novo_nivel_combustivel(
        distancia_km,
        consumo_medio,
        qtd_litros_atual
    )

    atualizar_qtd_litros(conn, placa, novo_nivel)

    return novo_nivel


def inserir_viagem(conn: sqlite3.Connection, viagem: ViagemCreate, hodometro_atual: float, hodometro_chegada: float):
    """Insere o registro da nova viagem."""
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO VIAGEM 
        (PLACA_FK, CPF_FK, ORIGEM, DESTINO, DISTANCIA_KM,
         DATA_SAIDA, DATA_CHEGADA, HODOMETRO_SAIDA, HODOMETRO_CHEGADA, STATUS)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        viagem.placa_fk,
        viagem.cpf_fk,
        viagem.origem,
        viagem.destino,
        viagem.distancia_km,
        date.today().isoformat(), # DATA_SAIDA é sempre hoje
        viagem.data_chegada.isoformat(), # Converte a data de chegada do Pydantic para string ISO
        hodometro_atual,
        hodometro_chegada,
        Status_viagem.EM_ANDAMENTO.value
    ))


def atualizar_status_veiculo(conn: sqlite3.Connection, placa: str, novo_hodometro: float):
    """Atualiza o status e a quilometragem do veículo."""
    cur = conn.cursor()
    cur.execute("""
        UPDATE VEICULO 
        SET STATUS = ?, QUILOMETRAGEM = ?
        WHERE PLACA = ?
    """, (
        Veiculo_status.EM_VIAGEM.value,
        novo_hodometro,
        placa
    ))


def atualizar_status_motorista(conn: sqlite3.Connection, cpf: str):
    """Atualiza a disponibilidade do motorista."""
    cur = conn.cursor()
    cur.execute("""
        UPDATE MOTORISTA 
        SET DISPONIBILIDADE = ?
        WHERE CPF = ?
    """, (
        Status_motorista.EM_VIAGEM.value,
        cpf
    ))


def inserir_historico(conn: sqlite3.Connection, viagem: ViagemCreate):
    """Registra o evento de viagem no histórico do veículo."""
    cur = conn.cursor()

    resumo = f"Viagem de {viagem.origem} para {viagem.destino}"
    
    # VALOR_ASSOCIADO pode ser a DISTANCIA_KM
    valor_associado = viagem.distancia_km 
    observacao = f"Motorista CPF: {viagem.cpf_fk}" 

    cur.execute("""
        INSERT INTO HISTORICO_EVENTO_VEICULO
        (PLACA_FK, TIPO_EVENTO, DATA_EVENTO, RESUMO, VALOR_ASSOCIADO, OBSERVACAO)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        viagem.placa_fk,
        Tipo_evento.VIAGEM.value,
        date.today().isoformat(),
        resumo,
        valor_associado,
        observacao
    ))


# =============================================================
# ORQUESTRADOR PRINCIPAL — CRIAR VIAGEM
# =============================================================

def criar_viagem(viagem: ViagemCreate, db_path: str = DB_PATH):
    """
    Orquestra todas as validações de regras de negócio e a persistência
    da nova viagem em uma transação.
    """
    # A transação começa aqui (with conecta)
    with conectar(db_path) as conn:
        try:
            # 1 — Validações de Status e Compatibilidade
            cat_cnh = validar_status_motorista(conn, viagem.cpf_fk)
            tipo_veiculo = validar_status_veiculo(conn, viagem.placa_fk)
            validar_cnh_motorista_para_veiculo(cat_cnh, tipo_veiculo)

            # 2 — Hodômetro
            hodometro_atual = get_quilometragem_atual(conn, viagem.placa_fk)
            hodometro_chegada = calcular_hodometro_chegada(hodometro_atual, viagem.distancia_km)

            # 3 — Combustível (inclui validação de suficiência)
            combustivel_restante = processar_consumo_veiculo(conn, viagem.placa_fk, viagem.distancia_km)

            # 4 — Persistência
            inserir_viagem(conn, viagem, hodometro_atual, hodometro_chegada)
            atualizar_status_veiculo(conn, viagem.placa_fk, hodometro_chegada)
            atualizar_status_motorista(conn, viagem.cpf_fk)
            inserir_historico(conn, viagem)

            # O commit é feito automaticamente pelo 'with conectar' se não houver erro

            return {
                "message": "Viagem criada com sucesso",
                "hodometro_chegada": hodometro_chegada,
                "combustivel_restante": combustivel_restante
            }
        
        except ValueError as e:
            # Se ocorrer um ValueError (erro de validação, CNH, status, combustível),
            # o with block fará um rollback implicitamente antes de propagar o erro.
            raise e
        
        except sqlite3.Error as e:
            # Erros de DB
            raise RuntimeError(f"Erro no banco de dados durante a criação da viagem: {e}")

    # A conexão é fechada automaticamente pelo 'with conectar'