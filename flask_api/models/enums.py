from enum import Enum

# -------------------- ENUMS VEÍCULO --------------------

class Veiculo_status(str, Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    MANUTENCAO = "MANUTENÇÃO"
    
# -------------------- ENUMS MOTORISTA --------------------

class Motorista_status(str, Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    
# -------------------- ENUMS MANUTENÇÃO --------------------

class Tipo_manutencao(str, Enum):
    PREVENTIVA = "Preventiva"
    CORRETIVA = "Corretiva"


# -------------------- ENUM COMBUSTÍVEL --------------------

class Tipo_combustivel(str, Enum):
    GASOLINA = "GASOLINA"
    DIESEL = "DIESEL"
    ETANOL = "ETANOL"


# -------------------- ENUM MOTORISTA --------------------

class Status_motorista(str, Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"


# -------------------- ENUM VIAGEM --------------------

class Status_viagem(str, Enum):
    EM_ANDAMENTO = "EM_ANDAMENTO"
    CONCLUIDA = "CONCLUIDA"