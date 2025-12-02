from enum import Enum

# -------------------- ENUMS VEÍCULO --------------------

class Veiculo_status(str, Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    MANUTENCAO = "MANUTENÇÃO"
    EM_VIAGEM = "EM_VIAGEM"
        
# -------------------- ENUMS MOTORISTA --------------------

class Motorista_status(str, Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    
# -------------------- ENUMS MANUTENÇÃO --------------------

class Tipo_manutencao(str, Enum):
    PREVENTIVA = "PREVENTIVA"
    CORRETIVA = "CORRETIVA"


# -------------------- ENUM COMBUSTÍVEL --------------------

class Tipo_combustivel(str, Enum):
    GASOLINA = "GASOLINA"
    DIESEL = "DIESEL"
    ETANOL = "ETANOL"


# -------------------- ENUM MOTORISTA --------------------

class Status_motorista(str, Enum):
    ATIVO = "ATIVO"
    EM_VIAGEM = "EM_VIAGEM"
    INATIVO = "INATIVO"


# -------------------- ENUM VIAGEM --------------------

class Status_viagem(str, Enum):
    EM_ANDAMENTO = "EM_ANDAMENTO"
    CONCLUIDA = "CONCLUIDA"
    

# -------------------- ENUM QTD COMBUSTIVEL --------------------

class Qtd_combustivel_litro(int, Enum):
    CARRO = 60
    MOTO = 15
    CAMINHAO = 700


# -------------------- ENUM TIPO EVENTO --------------------

class Tipo_evento(str, Enum):
    VIAGEM = "VIAGEM"
    ABASTECIMENTO = "ABASTECIMENTO"
    MANUTENCAO = "MANUTENÇÃO"
