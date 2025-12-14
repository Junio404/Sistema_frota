import sqlite3
from config import Config
import random # Importação realocada para o escopo global do init_db

def init_db():

    with sqlite3.connect(Config.DATABASE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()

        # ---------------------------------------------------------
        # ENUMS
        # ---------------------------------------------------------

        cur.execute("""
        CREATE TABLE IF NOT EXISTS ENUM_VEICULO_STATUS (
            STATUS TEXT PRIMARY KEY
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS ENUM_TIPO_MANUTENCAO (
            TIPO TEXT PRIMARY KEY
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS ENUM_TIPO_COMBUSTIVEL (
            TIPO TEXT PRIMARY KEY
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS ENUM_STATUS_MOTORISTA (
            STATUS TEXT PRIMARY KEY
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS ENUM_STATUS_VIAGEM (
            STATUS TEXT PRIMARY KEY
        );
        """)
        
        cur.execute("""
        CREATE TABLE IF NOT EXISTS ENUM_QTD_COMBUSTIVEL (
            TIPO_VEICULO TEXT,
            QTD_LITROS INTEGER PRIMARY KEY,
            FOREIGN KEY (TIPO_VEICULO) REFERENCES TIPO_VEICULO_CNH(TIPO_VEICULO)
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS ENUM_TIPO_EVENTO (
            TIPO_EVENTO TEXT PRIMARY KEY
        )
        """)
        # ---------------------------------------------------------
# ENUMS (NOVA ADIÇÃO)
# ---------------------------------------------------------
        cur.execute("""
        CREATE TABLE IF NOT EXISTS ENUM_STATUS_MANUTENCAO (
            STATUS TEXT PRIMARY KEY
        );
        """)

        # ---------------------------------------------------------
        # SUPERCLASSE PESSOA (NOVA)
        # ---------------------------------------------------------

        cur.execute("""
        CREATE TABLE IF NOT EXISTS PESSOA (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CPF TEXT UNIQUE,
            NOME TEXT NOT NULL
        );
        """)

        # ---------------------------------------------------------
        # TABELAS DE REFERÊNCIA
        # ---------------------------------------------------------

        cur.execute("""
        CREATE TABLE IF NOT EXISTS MARCA (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NOME TEXT UNIQUE NOT NULL 
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS TIPO_VEICULO_CNH (
            TIPO_VEICULO TEXT PRIMARY KEY,
            CAT_MIN_CNH TEXT UNIQUE NOT NULL
        );
        """)

        # ---------------------------------------------------------
        # TABELA MODELO CORRIGIDA
        # A coluna CAT_MIN_CNH foi removida para eliminar redundância e erro de FK.
        # ---------------------------------------------------------

        cur.execute("""
        CREATE TABLE IF NOT EXISTS MODELO (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NOME_MODELO TEXT NOT NULL,
            MARCA_FK INTEGER NOT NULL,
            TIPO_VEICULO TEXT NOT NULL,
            TIPO_COMBUSTIVEL TEXT NOT NULL,
            QTD_LITROS INTEGER NOT NULL,
            CONSUMO_MEDIO_KM_L REAL NOT NULL,
            
            FOREIGN KEY (TIPO_COMBUSTIVEL) REFERENCES ENUM_TIPO_COMBUSTIVEL(TIPO),
            FOREIGN KEY (TIPO_VEICULO) REFERENCES TIPO_VEICULO_CNH(TIPO_VEICULO),
            
            UNIQUE (NOME_MODELO, MARCA_FK),
            FOREIGN KEY (MARCA_FK) REFERENCES MARCA(ID)
        );
        """)


        # ---------------------------------------------------------
        # VEICULO
        # ---------------------------------------------------------

        cur.execute("""
        CREATE TABLE IF NOT EXISTS VEICULO (
            PLACA TEXT PRIMARY KEY,
            MODELO_FK INTEGER NOT NULL,
            TIPO_VEICULO TEXT NOT NULL,
            ANO INTEGER NOT NULL,
            QUILOMETRAGEM REAL NOT NULL,
            QTD_LITROS INTEGER NOT NULL,
            CONSUMO_MEDIO_KM_L REAL NOT NULL,
            TIPO_COMBUSTIVEL TEXT NOT NULL,
            STATUS TEXT NOT NULL,
            FOREIGN KEY (MODELO_FK) REFERENCES MODELO(ID),
            FOREIGN KEY (TIPO_COMBUSTIVEL) REFERENCES ENUM_TIPO_COMBUSTIVEL(TIPO),
            FOREIGN KEY (TIPO_VEICULO) REFERENCES TIPO_VEICULO_CNH(TIPO_VEICULO),
            FOREIGN KEY (STATUS) REFERENCES ENUM_VEICULO_STATUS(STATUS)
        );
        """)

        # ---------------------------------------------------------
        # MOTORISTA (HERDA DE PESSOA)
        # ---------------------------------------------------------

        cur.execute("""
        CREATE TABLE IF NOT EXISTS MOTORISTA (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CPF TEXT UNIQUE,
            CAT_CNH TEXT NOT NULL,
            EXP_ANOS INTEGER NOT NULL,
            DISPONIBILIDADE TEXT NOT NULL,
            CNH_VALIDO_ATE DATE NOT NULL,
            FOREIGN KEY (CPF) REFERENCES PESSOA(CPF),
            FOREIGN KEY (DISPONIBILIDADE) REFERENCES ENUM_STATUS_MOTORISTA(STATUS)
        );
        """)

        # ---------------------------------------------------------
        # MANUTENÇÃO
        # ---------------------------------------------------------
        cur.execute("""
                CREATE TABLE IF NOT EXISTS MANUTENCAO (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    PLACA_FK TEXT NOT NULL,
                    TIPO_MANUTENCAO TEXT NOT NULL,
                    DATA_INICIO DATE NOT NULL,
                    DATA_CONCLUSAO DATE, 		 
                    CUSTO REAL, 				 
                    DESCRICAO TEXT, 			 
                    STATUS_MANUTENCAO TEXT NOT NULL,
                    FOREIGN KEY (PLACA_FK) REFERENCES VEICULO(PLACA),
                    FOREIGN KEY (TIPO_MANUTENCAO) REFERENCES ENUM_TIPO_MANUTENCAO(TIPO),
                    FOREIGN KEY (STATUS_MANUTENCAO) REFERENCES ENUM_STATUS_MANUTENCAO(STATUS)
                );
                """)

        # ---------------------------------------------------------
        # ABASTECIMENTO
        # ---------------------------------------------------------

        cur.execute("""
        CREATE TABLE IF NOT EXISTS ABASTECIMENTO (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            PLACA_FK TEXT NOT NULL,
            TIPO_COMBUSTIVEL TEXT NOT NULL,
            DATA DATE NOT NULL,
            LITROS REAL NOT NULL,
            VALOR_PAGO REAL NOT NULL,
            HODOMETRO REAL NOT NULL,
            FOREIGN KEY (PLACA_FK) REFERENCES VEICULO(PLACA),
            FOREIGN KEY (TIPO_COMBUSTIVEL) REFERENCES ENUM_TIPO_COMBUSTIVEL(TIPO)
        );
        """)

        # ---------------------------------------------------------
        # VIAGEM
        # ---------------------------------------------------------

        cur.execute("""
        CREATE TABLE IF NOT EXISTS VIAGEM (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            PLACA_FK TEXT NOT NULL,
            CPF_FK TEXT NOT NULL,
            ORIGEM TEXT NOT NULL,
            DESTINO TEXT NOT NULL,
            DISTANCIA_KM REAL,
            DATA_SAIDA DATE NOT NULL,
            DATA_CHEGADA DATE,
            HODOMETRO_SAIDA REAL NOT NULL,
            HODOMETRO_CHEGADA REAL,
            STATUS TEXT NOT NULL,
            FOREIGN KEY (STATUS) REFERENCES ENUM_STATUS_VIAGEM(STATUS),
            FOREIGN KEY (PLACA_FK) REFERENCES VEICULO(PLACA),
            FOREIGN KEY (CPF_FK) REFERENCES MOTORISTA(CPF)
        );
        """)

        # ---------------------------------------------------------
        # HISTÓRICO EVENTOS DE VEÍCULO
        # ---------------------------------------------------------

        cur.execute("""
        CREATE TABLE IF NOT EXISTS HISTORICO_EVENTO_VEICULO (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            PLACA_FK TEXT NOT NULL,
            TIPO_EVENTO TEXT NOT NULL,
            DATA_EVENTO DATE NOT NULL,
            RESUMO TEXT,
            VALOR_ASSOCIADO REAL,
            OBSERVACAO TEXT,
            FOREIGN KEY (PLACA_FK) REFERENCES VEICULO(PLACA),
            FOREIGN KEY (TIPO_EVENTO) REFERENCES ENUM_TIPO_EVENTO(TIPO_EVENTO)
        );
        """)

        # ---------------------------------------------------------
        # CONFIGURAÇÃO
        # ---------------------------------------------------------

        cur.execute("""
        CREATE TABLE IF NOT EXISTS CONFIGURACAO (
            CHAVE TEXT PRIMARY KEY,
            VALOR TEXT NOT NULL,
            DESCRICAO TEXT
        );
        """)

        # ---------------------------------------------------------
        # INSERINDO ENUMS
        # ---------------------------------------------------------

        cur.executemany("INSERT OR IGNORE INTO ENUM_VEICULO_STATUS VALUES (?)",
            [("ATIVO",), ("INATIVO",), ("MANUTENCAO",), ("EM_VIAGEM",), ("PREVENTIVA_URGENTE",)])

        cur.executemany("INSERT OR IGNORE INTO ENUM_TIPO_MANUTENCAO VALUES (?)",
            [("PREVENTIVA",), ("CORRETIVA",)])

        cur.executemany("INSERT OR IGNORE INTO ENUM_TIPO_COMBUSTIVEL VALUES (?)",
            [("GASOLINA",), ("DIESEL",), ("ETANOL",)])

        cur.executemany("INSERT OR IGNORE INTO ENUM_STATUS_MOTORISTA VALUES (?)",
            [("ATIVO",), ("INATIVO",), ("EM_VIAGEM",)])
        cur.executemany("INSERT OR IGNORE INTO ENUM_TIPO_EVENTO VALUES (?)",
            [("VIAGEM",), ("MANUTENÇÃO",), ("ABASTECIMENTO",)])

        cur.executemany("INSERT OR IGNORE INTO ENUM_STATUS_VIAGEM VALUES (?)",
            [("EM_ANDAMENTO",), ("CONCLUIDA",)])

        cur.executemany("INSERT OR IGNORE INTO TIPO_VEICULO_CNH (TIPO_VEICULO, CAT_MIN_CNH) VALUES (?, ?)",
            [("CAMINHAO", "C"), ("CARRO", "B"), ("MOTO", "A")])

        cur.executemany("INSERT OR IGNORE INTO ENUM_QTD_COMBUSTIVEL (TIPO_VEICULO, QTD_LITROS) VALUES (?, ?)",
                        [("CARRO", 60), ("MOTO", 15), ("CAMINHAO", 700)])
        cur.executemany("INSERT OR IGNORE INTO ENUM_STATUS_MANUTENCAO VALUES (?)",
            [("PENDENTE",), ("EM_ANDAMENTO",), ("CONCLUIDA",), ("CANCELADA",)])

        # ---------------------------------------------------------
        # INSERIR MARCAS
        # ---------------------------------------------------------
        marcas = [
            ('Honda',), ('Yamaha',), ('Suzuki',), ('Kawasaki',), ('Dafra',),
            ('Toyota',), ('Volkswagen',), ('Ford',), ('Chevrolet',), ('Hyundai',),
            ('Volvo',), ('Mercedes-Benz',), ('Scania',), ('Iveco',), ('DAF',)
        ]

        cur.executemany("INSERT OR IGNORE INTO MARCA (NOME) VALUES (?)", marcas)
        conn.commit()

        # Recuperar IDs das marcas
        cur.execute("SELECT ID, NOME FROM MARCA")
        marcas_ids = {nome: id for (id, nome) in cur.fetchall()}


        # ---------------------------------------------------------
        # MODELOS ORIGINAIS (sem mudanças)
        # ---------------------------------------------------------

        moto_modelos = {
            "Honda": [
                ("CG 160", 38.5),
                ("Biz 125", 42.2),
                ("XRE 300", 30.1),
                ("CB 500F", 28.7),
                ("Hornet 600", 17.5),
            ],
            "Yamaha": [
                ("Factor 150", 40.3),
                ("Fazer 250", 33.1),
                ("MT-03", 22.4),
                ("R3", 24.8),
                ("Lander 250", 32.2),
            ],
            "Suzuki": [
                ("Yes 125", 41.0),
                ("V-Strom 650", 22.1),
                ("Burgman 125", 37.4),
                ("GSX-S750", 20.2),
                ("Hayabusa", 14.3),
            ],
            "Kawasaki": [
                ("Ninja 300", 26.4),
                ("Z400", 27.3),
                ("Versys 650", 21.8),
                ("Z900", 17.1),
                ("Ninja ZX-6R", 15.5),
            ],
            "Dafra": [
                ("Citycom 300", 28.2),
                ("Apache 200", 37.8),
                ("Next 250", 30.5),
                ("Horizon 250", 27.9),
                ("Cruiser 150", 36.0),
            ]
        }

        carro_modelos = {
            "Toyota": [
                ("Corolla", 12.3),
                ("Etios", 13.0),
                ("Yaris", 12.8),
                ("Hilux", 9.5), # Diesel
                ("SW4", 8.7), # Diesel
            ],
            "Volkswagen": [
                ("Gol", 12.1),
                ("Polo", 12.8),
                ("Virtus", 13.2),
                ("T-Cross", 11.7),
                ("Golf", 12.5),
            ],
            "Ford": [
                ("Ka", 13.5),
                ("Fiesta", 12.7),
                ("Focus", 11.5),
                ("Ranger", 9.0),# Diesel
                ("Ecosport", 11.4),
            ],
            "Chevrolet": [
                ("Onix", 13.9),
                ("Prisma", 12.8),
                ("Cruze", 11.2),
                ("S10", 9.4),# Diesel
                ("Tracker", 11.9),
            ],
            "Hyundai": [
                ("HB20", 13.7),
                ("Creta", 11.0),
                ("i30", 9.8),
                ("Tucson", 8.9),
                ("Azera", 7.2),
            ]
        }

        caminhao_modelos = {
            "Volvo": [
                ("FH 540", 2.6),
                ("FMX 440", 2.4),
                ("VM 270", 3.1),
                ("FH 460", 2.8),
                ("FM 330", 3.0),
            ],
            "Mercedes-Benz": [
                ("Actros 2651", 2.7),
                ("Atego 2430", 3.4),
                ("Accelo 1016", 4.5),
                ("Axor 2544", 2.9),
                ("Atego 1719", 4.1),
            ],
            "Scania": [
                ("R450", 2.8),
                ("G410", 3.0),
                ("P340", 3.5),
                ("R500", 2.6),
                ("S620", 2.4),
            ],
            "Iveco": [
                ("Hi-Way 480", 2.7),
                ("Tector 240", 3.8),
                ("Daily 70C17", 5.2),
                ("Stralis 460", 2.9),
                ("Vertis 90V18", 4.6),
            ],
            "DAF": [
                ("XF105", 2.7),
                ("CF85", 2.9),
                ("XF95", 2.6),
                ("LF55", 3.8),
                ("CF75", 3.6),
            ]
        }

        # ---------------------------------------------------------
        # FUNÇÃO AUXILIAR – agora com combustível
        # ---------------------------------------------------------

        def distribuir_combustivel(tipo):
            """
            Seleção realista:
            - MOTO      → GASOLINA / ETANOL
            - CARRO     → GASOLINA / ETANOL / DIESEL (SUVs e pick-ups diesel)
            - CAMINHÃO  → DIESEL
            """
            # random já foi importado no escopo do init_db

            if tipo == "MOTO":
                return random.choice(["GASOLINA", "ETANOL"])

            if tipo == "CARRO":
                # SUVs e picapes que são diesel na vida real
                diesel_excecoes = ["Hilux", "SW4", "Ranger", "S10"]

                return "DIESEL" if modelo_atual in diesel_excecoes else random.choice(["GASOLINA", "ETANOL"])

            if tipo == "CAMINHAO":
                return "DIESEL"


        modelos = []

        def add_modelos(dic, tipo, cnh, litros_padrao):
            global modelo_atual
            
            for marca, lista in dic.items():
                marca_id = marcas_ids.get(marca)
                if not marca_id:
                    continue

                for (modelo, consumo) in lista:
                    modelo_atual = modelo
                    combustivel = distribuir_combustivel(tipo)
                    
                    # CORREÇÃO: Removido 'cnh' da tupla
                    modelos.append((
                        modelo,
                        marca_id,
                        tipo,
                        combustivel, # A CNH já foi removida
                        litros_padrao,
                        consumo
                    ))

        # Usando a função
        add_modelos(moto_modelos, "MOTO", "A", 15)
        add_modelos(carro_modelos, "CARRO", "B", 60)
        add_modelos(caminhao_modelos, "CAMINHAO", "C", 700)

        # ---------------------------------------------------------
        # Inserção final CORRIGIDA (Removido CAT_MIN_CNH)
        # ---------------------------------------------------------
        cur.executemany("""
            INSERT OR IGNORE INTO MODELO 
            (NOME_MODELO, MARCA_FK, TIPO_VEICULO, TIPO_COMBUSTIVEL, QTD_LITROS, CONSUMO_MEDIO_KM_L)
            VALUES (?, ?, ?, ?, ?, ?)
        """, modelos)

        conn.commit()

        print("✔ Modelos inseridos com combustíveis corretos, realistas e variados!")
        
        cur.execute("PRAGMA foreign_key_check")


    print("Banco de dados criado com sucesso utilizando contexto!")


    print("Banco de dados criado com sucesso utilizando contexto!")
    # executar apenas uma vez
    # preencher_dados_fixos()

# import sqlite3
# from config import Config

# def delete_db():
#     with sqlite3.connect(Config.DATABASE) as conn:
#         conn.execute("PRAGMA foreign_keys = ON")
#         c = conn.cursor()
#         c.execute("DROP TABLE IF EXISTS veiculos")
#         c.execute("DROP TABLE IF EXISTS motoristas")
#         c.execute("DROP TABLE IF EXISTS tipo_veiculo")
#         conn.commit()
        
# delete_db()


        