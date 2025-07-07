from flask import Flask
from api.reservas import reservas_bp
from sistema.main import carregar_dados
import os

app = Flask(__name__)

carregar_dados()

app.register_blueprint(reservas_bp, url_prefix="/reservas")

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1" 
    app.run(debug=debug_mode)
