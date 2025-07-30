from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from datetime import datetime
import time

integracoes_teste_bp = Blueprint('integracoes_teste', __name__)

# Dados simulados para teste
CLIENTES_SIMULADOS = [
    {
        'id': 1,
        'name': 'NEWSGPS',
        'CNPJ': '11810190000129',
        'email': 'contato@newsgps.com',
        'status': 'Cliente Ativo'
    },
    {
        'id': 2,
        'name': 'Empresa Teste',
        'CNPJ': '12345678000195',
        'email': 'teste@empresa.com',
        'status': 'Cliente Ativo'
    }
]

INTEGRACOES_SIMULADAS = {
    1: [
        {
            'sistema': 'Smart Bus',
            'entidade': 'Passagem',
            'ultima_atualizacao': '2025-07-25T02:29:47.14',
            'retorno_erro': False,
            'status': 'Ativo'
        },
        {
            'sistema': 'Sistema Próprio',
            'entidade': 'Bilhetes',
            'ultima_atualizacao': '2025-07-29T15:45:22.33',
            'retorno_erro': False,
            'status': 'Ativo'
        }
    ],
    2: [
        {
            'sistema': 'Totalbus',
            'entidade': 'Escala',
            'ultima_atualizacao': '2025-07-28T08:15:10.55',
            'retorno_erro': True,
            'status': 'Com Erro'
        }
    ]
}

@integracoes_teste_bp.route('/consultar-por-cliente/<int:cliente_id>', methods=['GET'])
@cross_origin()
def consultar_integracoes_por_cliente_teste(cliente_id):
    """Versão de teste para consulta de integrações de um cliente específico"""
    try:
        # Simular delay de rede
        time.sleep(1)
        
        # Buscar cliente simulado
        cliente = next((c for c in CLIENTES_SIMULADOS if c['id'] == cliente_id), None)
        
        if not cliente:
            return jsonify({
                'success': False,
                'error': 'Cliente não encontrado no Supabase'
            }), 404
        
        cnpj = cliente.get('CNPJ')
        
        if not cnpj:
            return jsonify({
                'success': False,
                'error': 'Cliente não possui CNPJ cadastrado'
            }), 400
        
        # Buscar integrações simuladas
        integracoes = INTEGRACOES_SIMULADAS.get(cliente_id, [])
        
        resultado = {
            'cnpj': cnpj,
            'empresa_encontrada': True,
            'id_cliente': cliente_id,
            'nome_empresa': cliente['name'],
            'integracoes': integracoes,
            'erro': None,
            'timestamp': datetime.now().isoformat(),
            'cliente_supabase': {
                'id': cliente.get('id'),
                'name': cliente.get('name'),
                'email': cliente.get('email'),
                'status': cliente.get('status')
            }
        }
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@integracoes_teste_bp.route('/consultar-por-cnpj', methods=['POST'])
@cross_origin()
def consultar_integracoes_por_cnpj_teste():
    """Versão de teste para consulta direta por CNPJ"""
    try:
        data = request.get_json()
        cnpj = data.get('cnpj')
        
        if not cnpj:
            return jsonify({
                'success': False,
                'error': 'CNPJ é obrigatório'
            }), 400
        
        # Simular delay de rede
        time.sleep(1)
        
        # Normalizar CNPJ
        cnpj_limpo = cnpj.replace(" ", "").replace(".", "").replace("/", "").replace("-", "")
        
        # Buscar cliente por CNPJ
        cliente = None
        for c in CLIENTES_SIMULADOS:
            cnpj_cliente = c['CNPJ'].replace(" ", "").replace(".", "").replace("/", "").replace("-", "")
            if cnpj_cliente == cnpj_limpo:
                cliente = c
                break
        
        if not cliente:
            resultado = {
                'cnpj': cnpj,
                'empresa_encontrada': False,
                'id_cliente': None,
                'nome_empresa': None,
                'integracoes': [],
                'erro': 'Empresa não encontrada com o CNPJ fornecido',
                'timestamp': datetime.now().isoformat()
            }
        else:
            integracoes = INTEGRACOES_SIMULADAS.get(cliente['id'], [])
            resultado = {
                'cnpj': cnpj,
                'empresa_encontrada': True,
                'id_cliente': cliente['id'],
                'nome_empresa': cliente['name'],
                'integracoes': integracoes,
                'erro': None,
                'timestamp': datetime.now().isoformat()
            }
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@integracoes_teste_bp.route('/clientes', methods=['GET'])
@cross_origin()
def listar_clientes_teste():
    """Lista todos os clientes simulados"""
    try:
        return jsonify({
            'success': True,
            'data': CLIENTES_SIMULADOS
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao buscar clientes: {str(e)}'
        }), 500

@integracoes_teste_bp.route('/teste-conectividade', methods=['GET'])
@cross_origin()
def teste_conectividade_simulado():
    """Testa a conectividade simulada"""
    resultado = {
        'supabase': True,
        'api_integracoes': True,
        'detalhes': {
            'supabase': 'Conectado com sucesso (simulado)',
            'api_integracoes': 'Autenticação bem-sucedida (simulado)'
        }
    }
    
    return jsonify({
        'success': True,
        'data': resultado
    })

