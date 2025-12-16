# SISTEMA DE GERENCIAMENTO DE FROTA DE VEÍCULOS
Repositório para a cadeira de POO. Construção de um sistema de gerenciamento de frota de veículos utilizando programação orientada a objetos.

## 📝 Descrição do Projeto e Objetivo
O **Gerenciamento de frota** é uma API mínima desenvolvida com **Flask** e persistência em **SQlite** para gerenciar a frota de veículos e motoristas de uma transportadora. Seu objetivo é otimizar a eficiência operacional e controlar custos, garantindo a conformidade e fornecendo dados analíticos.

O sistema aplica conceitos avançados de POO, como o uso de um repositório desacoplado da lógica de negócio e regras de negócio configuráveis (lidas via config.py), o que torna a manutenção e a adaptação do projeto mais fáceis.

## Clonagem de Repositório, Dependências e Inicialização do Projeto

Este documento descreve, passo a passo, como clonar o repositório, configurar o ambiente virtual, instalar as dependências e executar a aplicação.

**Pré-requisito:**  
- Python já instalado na máquina  
- Git instalado
- Para visualização do banco: DB browser for Sqlite

---

## 1️⃣ Clonar o Repositório

Abra o terminal (Prompt de Comando, PowerShell ou Git Bash) e execute:

```bash
git clone https://github.com/Junio404/Sistema_frota.git
```
2️⃣ Entrar na Pasta do Projeto

Após o clone, acesse o diretório do projeto:

```bash
cd Sistema_frota
```

3️⃣ Criar o Ambiente Virtual (venv)

Dentro da pasta do projeto, crie o ambiente virtual:
```bash
python -m venv venv
```

4️⃣ Ativar o Ambiente Virtual
Windows (CMD ou PowerShell)
```bash
venv\Scripts\activate
```

Após a ativação, o terminal exibirá algo semelhante a:

(venv)

5️⃣ Instalar as Dependências

Com o ambiente virtual ativado, instale todas as dependências do projeto:
```bash
pip install -r .\requirements.txt
```

6️⃣ Executar a Aplicação

Após a instalação das dependências, execute o projeto:
```bash
python app.py
```

7️⃣ Aplicação em Execução

Se tudo estiver correto, o Flask iniciará o servidor e exibirá algo semelhante a:
```bash
 * Serving Flask app 'flask_api'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000 <- CTRL + Clique aqui
Press CTRL+C to quit
 * Restarting with stat
✔ Modelos inseridos com combustíveis corretos, realistas e variados!
Banco de dados criado com sucesso utilizando contexto!
Banco de dados criado com sucesso utilizando contexto!
 * Debugger is active!
 * Debugger PIN: 797-667-847
```
#### Segure o CRTL e clique no link http que aparece ao inicializar o localhost e se quiser fechar o localhost dê CRTL + C no terminal


Acesse o endereço acima no navegador para utilizar o sistema.

Resumo dos Comandos (Use-os na Ordem descrita)
```bash
git clone https://github.com/Junio404/Sistema_frota.git
```
```bash
cd Sistema_frota
```
```bash
python -m venv venv
```
```bash
venv\Scripts\activate
```
```bash
pip install -r .\requirements.txt
```
```bash
python app.py
```




# 🧱 Classes de Domínio (Domain Classes) — Especificação Atualizada

Este documento descreve a arquitetura de domínio, persistência, rotas e automações do sistema de gestão de frota, seguindo boas práticas de separação de responsabilidades, encapsulamento e consistência de dados.

---

## 📦 Classes de Domínio (`domain_classes`)

As classes de domínio definem o universo do negócio utilizando **dataclasses**, **properties** (para encapsulamento) e **validações internas**, garantindo regras de negócio próximas aos dados.

---

### 👤 Pessoa (Classe Base)

**Campos**
- `id`
- `nome`
- `cpf`

**Validações**
- Nome válido (conteúdo e formato)
- CPF válido (formato e dígitos verificadores)

---

### 🚗 Motorista (Herda de Pessoa)

**Campos**
- `cat_cnh` (A–E)
- `exp_anos`
- `disponibilidade`
- `cnh_valido_ate`

**Validações e Regras**
- Categoria da CNH válida
- Verificação de CNH vencida  
- Integração com o **APScheduler** para atualização automática de status

---

### 🚙 Veículo

**Campos**
- `placa` (validação padrão Mercosul)
- `modelo_fk`
- `tipo_veiculo` (MOTO / CARRO / CAMINHÃO)
- `ano`
- `quilometragem`
- `consumo_medio_km_l`
- `qtd_litros`
- `tipo_combustivel`
- `status`

**Regras**
- Propriedades com validação e normalização  
  - Exemplo: placa sempre em **uppercase**
- `status` utiliza Enum `Veiculo_status`

---

## 📊 Eventos e Histórico

### ⛽ Abastecimento

**Campos**
- `placa_fk`
- `tipo_combustivel`
- `data`
- `litros`
- `valor_pago`
- `hodometro`

**Validações**
- `litros > 0`
- `data` do tipo `date`
- Tipo de combustível válido

---

### 🛠️ Manutenção

**Campos**
- `id`
- `placa_fk`
- `tipo_manutencao` (PREVENTIVA / CORRETIVA)
- `data_inicio`
- `data_conclusao`
- `custo`
- `descricao`
- `status_manutencao`

**Uso**
- Cálculo de custo médio
- Alteração automática do status do veículo

---

### 🧭 Viagem

**Campos**
- `placa_fk`
- `cpf_fk`
- `origem`
- `destino`
- `distancia_km`
- `data_chegada`

**Validações**
- Motorista disponível
- Veículo disponível
- CNH compatível com o veículo

**Efeitos**
- Atualiza automaticamente a quilometragem do veículo

---

### 🗂️ Histórico do Veículo

**Historico_Veiculo**
- Agrega eventos:
  - Manutenções
  - Abastecimentos
  - Viagens
- Centraliza a linha do tempo operacional do veículo

---

## 🧾 Enums e Regras de Estado

Os Enums estão definidos em `enums.py` e evitam o uso de *strings mágicas*.

**Principais Enums**
- `Veiculo_status`
- `Motorista_status`
- `Tipo_combustivel`
- `Tipo_manutencao`

---

## ⚙️ Camada de Persistência e Infraestrutura

### 🗄️ Repositories (Repository Pattern)

Encapsulam o acesso ao banco **SQLite (`meu_banco.db`)**, expondo operações CRUD e consultas específicas.

**Repositórios Principais**
- `veiculo_repo`
  - CRUD de veículos
  - Validação de placa
  - Consultas por status e tipo
- `motorista_repo`
  - CRUD de motoristas
  - Verificação de CNH
  - Detecção de CNH vencida
- `abastecimento_repo`
  - Registro de abastecimentos
  - Cálculo de consumo (KM/L)
- `manutencao_repo`
  - Registro de manutenções
  - Marcação de veículos em manutenção
  - Cálculo de custo médio
- `viagem_repo`
  - Registro de viagens
  - Atualização automática de quilometragem
  - Validações de disponibilidade

---

## 🌐 Rotas (Flask)

As rotas são organizadas por responsabilidade:

- `routes_create.py`  
  Criação de motoristas, veículos, viagens, manutenções e abastecimentos
- `routes_read.py`  
  Listagem, detalhes e históricos
- `routes_update.py`  
  Atualização de motoristas e veículos
- `routes_delete.py`  
  Remoção de motoristas e veículos
- `routes_report.py`  
  Relatórios:
  - Eficiência
  - Quilometragem
  - Manutenção
  - Total de viagens
- `routes_index_options.py`  
  Opções de UI (menus e formulários)

---

## ⏱️ Agendador (APScheduler) — `app.py`

Tarefas executadas em **background**, com `trigger=interval` (24h), sem bloquear o servidor Flask.

**Tarefas Agendadas**
- `verificar_conclusao_manutencao`  
  Finaliza manutenções pendentes
- `verificar_cnh_vencida_motoristas`  
  Identifica CNHs expiradas e atualiza status
- `verificar_conclusao_viagem`  
  Marca viagens concluídas e ajusta estados
- `verificar_preventiva_urgente_veiculos`  
  Sinaliza veículos que necessitam manutenção preventiva

---

## 🧩 Vantagens e Boas Práticas Aplicadas

- Separação clara entre:
  - Domínio
  - Persistência
  - Rotas  
- Uso de **dataclasses + properties** para:
  - Validações locais
  - Redução de blocos de códigos repetidos em contextos diferentes
- Enums para garantir:
  - Estados válidos
  - Tipos consistentes
- **APScheduler** para automação e consistência dos dados
- **SQLite** como banco de dados:
  - Simplicidade
  - Portabilidade
  - Arquivo único (`meu_banco.db`)

---

## Estrutura do diretório do projeto (Inicial)
<p align="center">
<img src="repositorios_projeto_initial.png" alt="Imagem das pastas iniciais do projeto" width="200" height="400">
</p>

## Estrutura do diretório do projeto (Final)

```bash
Sistema_frota/
├── app.py                          # Arquivo principal da aplicação Flask
├── app.spec                        # Configuração para compilar com PyInstaller
├── config.py                       # Configurações da aplicação
├── requirements.txt                # Dependências do projeto
├── README.md                       # Documentação do projeto
│
└── flask_api/                      # Pacote principal da API
    ├── __init__.py                 # Inicialização do pacote
    │
    ├── domain_classes/             # Classes de domínio (entidades do negócio)
    │   ├── dc_abastecimento.py     # Entidade de abastecimento de veículos
    │   ├── dc_historico_veiculo.py # Histórico de eventos do veículo
    │   ├── dc_manutencao.py        # Entidade de manutenção
    │   ├── dc_marca.py             # Marca de veículos
    │   ├── dc_modelo.py            # Modelo de veículos
    │   ├── dc_motorista.py         # Entidade motorista
    │   ├── dc_pessoa.py            # Entidade pessoa (base)
    │   ├── dc_veiculo.py           # Entidade veículo
    │   └── dc_viagem.py            # Entidade viagem
    │
    ├── models/                     # Modelos ORM do banco de dados
    │   ├── __init__.py
    │   ├── db.py                   # Configuração e inicialização do BD
    │   ├── enums.py                # Enumerações do sistema
    │   ├── model_abastecimento.py  # Modelo ORM de abastecimento
    │   ├── model_manutencao.py     # Modelo ORM de manutenção
    │   ├── model_marca.py          # Modelo ORM de marca
    │   ├── model_modelo.py         # Modelo ORM de modelo
    │   ├── model_motorista.py      # Modelo ORM de motorista
    │   ├── model_veiculo.py        # Modelo ORM de veículo
    │   └── model_viagem.py         # Modelo ORM de viagem
    │
    ├── interfaces/                 # Contratos/interfaces
    │   ├── interface_pessoa.py      # Interface para pessoa
    │   └── interface_veiculo.py     # Interface para veículo
    │
    ├── repositories/               # Camada de acesso a dados (Data Access Layer)
    │   ├── __init__.py
    │   ├── manutencao_repo.py       # Repositório de manutenção
    │   ├── abastecimento_repo/
    │   │   └── abastecimento_repo.py # Repositório de abastecimento
    │   ├── motorista_repo/
    │   │   └── motorista_repo.py     # Repositório de motorista
    │   ├── veiculo_repo/
    │   │   └── veiculo_repo.py       # Repositório de veículo
    │   └── viagem_repo/
    │       └── viagem_repo.py        # Repositório de viagem
    │
    ├── routes/                     # Rotas/Endpoints da API
    │   ├── routes.py               # Rotas principais
    │   ├── routes_api.py           # Rotas da API REST
    │   ├── routes_create.py        # Rotas de criação
    │   ├── routes_read.py          # Rotas de leitura
    │   ├── routes_update.py        # Rotas de atualização
    │   ├── routes_delete.py        # Rotas de exclusão
    │   ├── routes_index_options.py # Rotas de opções/menu
    │   └── routes_report.py        # Rotas de relatórios
    │
    ├── templates/                  # Arquivos HTML (interface web)
    │   ├── index.html              # Página inicial
    │   ├── erro.html               # Página de erro
    │   ├── atualizar/              # Templates de atualização
    │   │   ├── atualizar_motorista.html
    │   │   └── atualizar_veiculo.html
    │   ├── delete/                 # Templates de exclusão
    │   │   ├── deletar_motorista.html
    │   │   └── deletar_veiculo.html
    │   ├── forms/                  # Templates de formulários
    │   │   ├── forms.html
    │   │   ├── forms_abastecimento.html
    │   │   ├── forms_manutencao.html
    │   │   ├── forms_veiculo.html
    │   │   └── forms_viagem.html
    │   ├── options/                # Templates de opções/menu
    │   │   ├── motorista_options.html
    │   │   ├── relatorio_options.html
    │   │   └── veiculo_options.html
    │   ├── read/                   # Templates de visualização
    │   │   ├── ver_historico_veiculo.html
    │   │   ├── ver_modelos.html
    │   │   ├── ver_motorista.html
    │   │   └── ver_veiculo.html
    │   └── relatorio/              # Templates de relatórios
    │       ├── relatorio_eficiencia.html
    │       ├── relatorio_km.html
    │       ├── relatorio_manutencao.html
    │       └── relatorio_total_viagens.html
    │
    └── static/                     # Arquivos estáticos (CSS, imagens)
        ├── css/                    # Folhas de estilo
        │   ├── index.css
        │   ├── forms.css
        │   ├── tables.css
        │   └── erro.css
        ├── data/
        │   └── settings.json       # Configurações em JSON
        ├── fonts/                  # Fontes customizadas
        └── img/                    # Imagens do projeto
```




## Diagrama Visual
<p align="center">
  <img src="Diagrama de Classes - Sistema_Frota.png" alt="Imagem do diagrama visual do projeto" width="1500" height="1500">
</p>

# Tecnologias e Módulos — Sistema_frota

## Visão geral
Resumo sucinto das tecnologias principais utilizadas no projeto e dos módulos auxiliares com suas vantagens e razões de uso.

## Frameworks e tecnologias principais

- **Flask**
  - Framework web leve e flexível para Python.
  - Vantagens: minimalista, fácil de estender, ideal para APIs REST e aplicações com templates Jinja2; ótimo ecossistema e documentação.
  - Uso no projeto: roteamento, rendering de templates, blueprints (`flask_api/routes/`) e integração com o scheduler via execução no `app.py`.

- **SQLite3**
  - Banco de dados relacional embarcado (arquivo único `meu_banco.db`).
  - Vantagens: não precisa de servidor separado, portabilidade, bom para desenvolvimento e aplicações de pequeno/médio porte; suporta constraints e foreign keys.
  - Uso no projeto: persistência simples via módulo `flask_api/models/db.py` e acesso direto em repositórios.

- **APScheduler**
  - Agendador de tarefas em background para Python.
  - Vantagens: suportar triggers `cron`, `interval` e `date`; roda jobs sem bloquear o servidor; útil para verificações periódicas e manutenção.
  - Uso no projeto: jobs registrados em `app.py` (verificações diárias de CNH vencida, conclusão de viagens, conclusão de manutenções, preventivas urgentes).

## Módulos e padrões usados

- **Pydantic**
  - Validação e parsing de dados usando type hints.
  - Vantagens: validação automática, mensagens de erro claras, geração de schemas, serialização JSON nativa e segurança nas entradas vindas de formulários/JSON.
  - Uso no projeto: modelos de entrada para criação/atualização (`flask_api/models/` como `Motorista_create`, `Veiculo_create`, `ViagemCreate`, `Abastecimento_create`, `Manutencao_create`).

- **Dataclasses (stdlib)**
  - Estrutura leve para classes de domínio com menos boilerplate.
  - Vantagens: gera automaticamente `__init__`, `__repr__`, fácil leitura e manutenção; permite uso combinado com `field()` para customizações e `properties` para validações.
  - Uso no projeto: classes de domínio em `flask_api/domain_classes/` (Motorista, Veiculo, Abastecimento, Manutencao, Viagem, etc.) com validações encapsuladas via properties.

- **Enums (stdlib enum.Enum)**
  - Tipos enumerados para estados e categorias fixas.
  - Vantagens: evita strings mágicas, melhora legibilidade e segurança de valores, facilita validações e mapeamentos.
  - Uso no projeto: estados e tipos em `flask_api/models/enums.py` (ex.: `Veiculo_status`, `Motorista_status`, `Tipo_combustivel`, `Tipo_manutencao`).

## Padrões de arquitetura aplicados

- **Repository Pattern**
  - Repositórios em `flask_api/repositories/` isolam o acesso a dados (CRUD e queries) da lógica de negócio.
  - Vantagem: maior modularidade, facilidade de testes e manutenção.

- **Separação de camadas**
  - Domain (dataclasses) → Models (Pydantic para entrada) → Repositories (persistência) → Routes (endpoints) → Templates/UI.
  - Vantagem: responsabilidades claras, menor acoplamento e código mais testável.

- **Validação em múltiplas camadas**
  - Validações de tipo e formato com Pydantic (na entrada), validações de domínio nas dataclasses (regras de negócio), e constraints no banco (SQLite).
  - Vantagem: erros capturados cedo e mensagens amigáveis ao usuário, sem quebrar o sistema

## Benefícios principais da escolha tecnológica

- Simplicidade e produtividade (Flask + SQLite) para desenvolvimento e deploy local.
- Validação robusta e tipada com Pydantic e dataclasses, reduz bugs de input.
- Automação e manutenção proativa com APScheduler (tarefas periódicas sem bloquear a API).
- Boa portabilidade do projeto (arquivo de DB único, dependências simples listadas em `requirements.txt`).

## Observações práticas

- Para garantir que o APScheduler rode corretamente, inicie a aplicação com `python app.py` (o `app.py` inicializa os jobs). Executar apenas `flask run` pode não disparar o bloco `if __name__ == '__main__':` e, consequentemente, o scheduler.
- `requirements.txt` contém as dependências principais: `Flask`, `APScheduler`, `pydantic` (ver arquivo para versões exatas).

---

Se quiser, posso:
- gerar uma versão resumida para a primeira seção do README;
- adicionar exemplos rápidos de código para cada módulo (Pydantic model, dataclass, enum);
- atualizar o `README.md` diretamente com esse resumo (com sua autorização).






# Exemplos práticos — Sistema_frota

## 1) Exemplo de request / response (APIs JSON)

### 1.1 Listar motoristas (GET)
Endpoint: `GET /api/motoristas`

Exemplo de requisição (curl):

```bash
curl http://127.0.0.1:5000/api/motoristas
```

Resposta (exemplo):

```json
[
  {
    "cpf": "12345678901",
    "nome": "João Silva",
    "cat_cnh": "B",
    "experiencia_anos": 5,
    "disponibilidade": "ATIVO",
    "cnh_valido_ate": "2026-08-10"
  }
]
```

### 1.2 Listar veículos (GET)
Endpoint: `GET /api/veiculos`

Exemplo de requisição:

```bash
curl http://127.0.0.1:5000/api/veiculos
```

Resposta (exemplo parcial):

```json
[
  {
    "placa": "ABC1D23",
    "ano": 2019,
    "quilometragem": 125000,
    "tipo_veiculo": "CARRO",
    "qtd_litros": 50,
    "consumo_medio_km_l": 12.5,
    "tipo_combustivel": "GASOLINA",
    "status": "ATIVO",
    "modelo": {
      "id": 1,
      "nome_modelo": "Sedan X",
      "tipo_veiculo": "CARRO",
      "tipo_combustivel": "GASOLINA",
      "qtd_litros": 50,
      "consumo_medio_km_l": 12.5
    },
    "marca": {
      "id": 1,
      "nome": "MarcaExemplo"
    }
  }
]
```

### 1.3 Criar viagem (form POST)
Endpoint (form): `POST /criar_viagem`

Campos do form (x-www-form-urlencoded):
- `placa_fk` (ex.: `ABC1D23`)
- `cpf_fk` (ex.: `12345678901`)
- `origem`, `destino`
- `distancia_km` (ex.: `120`)
- `data_chegada` (ex.: `2025-12-17`)

Exemplo (curl — formulário):

```bash
curl -X POST http://127.0.0.1:5000/criar_viagem \
  -d "placa_fk=ABC1D23" \
  -d "cpf_fk=12345678901" \
  -d "origem=Depósito" \
  -d "destino=ClienteA" \
  -d "distancia_km=120" \
  -d "data_chegada=2025-12-17"
```

Resposta esperada (via interface web):
- Se OK: flash "🚗💨 Viagem registrada com sucesso!" e redirect para index.
- Se falha: flash com mensagem de erro (ex.: "❌ Combustível insuficiente para realizar a viagem.")


## 2) Exemplo de fluxo do sistema (registro de uma Viagem)

1. Usuário envia `POST /criar_viagem` com placa, cpf, origem, destino, distancia_km e data_chegada.
2. O servidor:
   - Busca `veiculo` via `repo_get_veiculo(placa_fk)`.
   - Busca `motorista` via `repo_get_motorista(cpf_fk)`.
   - Valida disponibilidade do motorista (`DISPONIBILIDADE == ATIVO`) e status do veículo (`STATUS == ATIVO`).
   - Calcula hodômetro final: `hodometro_final = hodometro_atual + distancia_km`.
   - Calcula litros necessários: `litros_necessarios = distancia_km / consumo_medio`.
   - Verifica combustível suficiente: `litros_necessarios <= litros_atual`.
3. Se tudo OK, dentro de uma única transação (with conectar() as conn):
   - `repo_insert_viagem(conn, viagem, hodometro_atual, hodometro_final)` — insere registro de viagem.
   - `repo_insert_evento_viagem(conn, viagem)` — adiciona evento no histórico do veículo.
   - `repo_update_veiculo_viagem(conn, placa_fk, hodometro_final)` — atualiza quilometragem do veículo.
   - `repo_update_combustivel(conn, placa_fk, novo_nivel_combustivel)` — atualiza nível de combustível.
   - `repo_update_motorista_viagem(conn, cpf_fk)` — marca motorista como "EM_VIAGEM".
   - `conn.commit()` — confirma a transação.
4. Usuário recebe confirmação e histórico/relatórios passam a refletir a nova viagem.


## 3) Exemplo de regra de negócio funcionando

Regra: validação de categoria da CNH para o tipo de veículo
- Local: `flask_api/domain_classes/dc_viagem.py` (função `validar_categoria_cnh`)
- Lógica: motoristas precisam ter categoria mínima para o tipo de veículo:
  - MOTO → mínimo A
  - CARRO → mínimo B
  - CAMINHAO → mínimo C

Cenário de exemplo (erro):
- Motorista: `cat_cnh = "B"`
- Veículo: `tipo_veiculo = "CAMINHAO"`
- Usuário tenta criar viagem com esse par → sistema bloqueia e retorna mensagem de erro.

Exemplo de requisição (simulando tentativa inválida):

```bash
curl -X POST http://127.0.0.1:5000/criar_viagem \
  -d "placa_fk=CAM1234" \
  -d "cpf_fk=11122233344" \
  -d "origem=Depósito" \
  -d "destino=Obra" \
  -d "distancia_km=50" \
  -d "data_chegada=2025-12-17"
```

Resposta esperada (via UI / flash):

❌ CNH incompatível. Para dirigir CAMINHAO, mínimo é C, mas motorista possui B.


## 4) Exemplo de relatório (existente)

4.1 Endpoints JSON de suporte (dados brutos):
- `GET /api/marcas_modelos` — retorna marcas e modelos com dados úteis para relatórios.
- `GET /api/veiculos` — lista detalhada de veículos com consumo e modelo.

Exemplo de uso:

```bash
curl http://127.0.0.1:5000/api/marcas_modelos
curl http://127.0.0.1:5000/api/veiculos
```

4.2 Relatório de ranking de eficiência (UI):
- Rota de template: `GET /relatorio/ranking_eficiencia`
- Arquivo: `flask_api/templates/relatorio/relatorio_eficiencia.html`

Conteúdo conceitual exibido pelo relatório:
- Ranking de veículos ordenado por consumo médio (km/l).
- KM rodados / litros consumidos por veículo.
- Alertas de veículos com consumo fora do padrão.

Exemplo de saída (conceitual):

Ranking de Eficiência
1. Placa: ABC1D23 — 15.2 km/l
2. Placa: XYZ9K87 — 13.4 km/l

Veículos com consumo fora do padrão:
- Placa: DEF4G56 — Consumo atual 6.2 km/l (esperado >= 10 km/l)


## 5) Testes rápidos

- Listar motoristas:
  curl http://127.0.0.1:5000/api/motoristas

- Tentar criar viagem (simular erro de CNH):
  curl -X POST http://127.0.0.1:5000/criar_viagem -d "placa_fk=CAM1234" -d "cpf_fk=11122233344" -d "origem=Depósito" -d "destino=Obra" -d "distancia_km=50" -d "data_chegada=2025-12-17"

- Ver relatório de eficiência (abrir no navegador):
  http://127.0.0.1:5000/relatorio/ranking_eficiencia


## Observações finais

- Operações de escrita (Viagem, Abastecimento, Manutenção) usam validação com Pydantic e dataclasses — erros de tipagem e de negócio aparecem como mensagens amigáveis.
- A ação de registrar viagem é executada dentro de transação DB, garantindo consistência.
- Para depurar, acompanhe os logs no terminal onde `python app.py` está rodando.



