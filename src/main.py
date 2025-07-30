import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.integracoes import integracoes_bp
from src.routes.integracoes_teste import integracoes_teste_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Habilitar CORS para todas as rotas
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(integracoes_bp, url_prefix='/api/integracoes')
app.register_blueprint(integracoes_teste_bp, url_prefix='/api/integracoes-teste')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Rota de health check para o Render
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'message': 'API de Integrações funcionando'}, 200

# Rota raiz
@app.route('/')
def index():
    return {'message': 'API de Integrações Ativas', 'status': 'online'}, 200

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

