from flask_api import create_app
from flask_api.models.db import preencher_dados_fixos

app = create_app()
preencher_dados_fixos()


if __name__ == "__main__":
    app.run(debug=True)