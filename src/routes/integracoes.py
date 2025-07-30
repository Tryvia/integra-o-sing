from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import requests
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from supabase import create_client, Client
import os

integracoes_bp = Blueprint('integracoes', __name__)

# Configurações do Supabase
SUPABASE_URL = os.environ.get('SUPABASE_URL', "https://mzjdmhgkrroajmsfwryu.supabase.co")
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im16amRtaGdrcnJvYWptc2Z3cnl1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgyMzMwMzUsImV4cCI6MjA2MzgwOTAzNX0.tQCwUfFCV7sD-IexQviU0XEPcbn9j5uK9NSUbH-OeBc")

# Configurações da API de integrações
INTEGRACOES_BASE_URL = os.environ.get('API_BASE_URL', "http://192.168.40.11:50231")
INTEGRACOES_USER = os.environ.get('API_USER', "integracaoportal")
INTEGRACOES_PASSWORD = os.environ.get('API_PASSWORD', "cadeadoNG1")

# Cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class IntegracaoService:
    """Serviço para consultar integrações ativas"""
    
    def __init__(self):
        self.token = None
        self.session = requests.Session()
        self.session.timeout = 10
    
    def autenticar(self) -> bool:
        """Autentica na API de integrações"""
        try:
            url = f"{INTEGRACOES_BASE_URL}/api/OAuth/Login"
            payload = {
                "user": INTEGRACOES_USER,
                "password": INTEGRACOES_PASSWORD
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            # Tentar diferentes formatos de resposta para o token
            try:
                token_data = response.json()
                if 'token' in token_data:
                    self.token = token_data['token']
                elif 'access_token' in token_data:
                    self.token = token_data['access_token']
                elif 'accessToken' in token_data:
                    self.token = token_data['accessToken']
                else:
                    self.token = response.text.strip('"')
            except json.JSONDecodeError:
                self.token = response.text.strip('"')
            
            # Configurar header de autorização
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            })
            
            return True
            
        except Exception as e:
            print(f"Erro na autenticação: {e}")
            return False
    
    def obter_empresas(self) -> List[Dict[str, Any]]:
        """Obtém lista de empresas"""
        try:
            url = f"{INTEGRACOES_BASE_URL}/api/SingServices/GetEmpresas"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Erro ao obter empresas: {e}")
            return []
    
    def obter_integracoes(self, id_cliente: int) -> List[Dict[str, Any]]:
        """Obtém integrações para um cliente"""
        try:
            url = f"{INTEGRACOES_BASE_URL}/api/SingServices/GetIntegracao"
            params = {'idCliente': id_cliente}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Erro ao obter integrações: {e}")
            return []
    
    def consultar_por_cnpj(self, cnpj: str) -> Dict[str, Any]:
        """Consulta integrações por CNPJ"""
        resultado = {
            'cnpj': cnpj,
            'empresa_encontrada': False,
            'id_cliente': None,
            'nome_empresa': None,
            'integracoes': [],
            'erro': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Obter empresas
            empresas = self.obter_empresas()
            if not empresas:
                resultado['erro'] = 'Não foi possível obter a lista de empresas'
                return resultado
            
            # Normalizar CNPJ
            cnpj_limpo = cnpj.replace(" ", "").replace(".", "").replace("/", "").replace("-", "")
            
            # Buscar empresa por CNPJ
            empresa_encontrada = None
            for empresa in empresas:
                cnpj_empresa = empresa.get('cnpj', '').replace(" ", "").replace(".", "").replace("/", "").replace("-", "")
                if cnpj_empresa == cnpj_limpo:
                    empresa_encontrada = empresa
                    break
            
            if not empresa_encontrada:
                resultado['erro'] = 'Empresa não encontrada com o CNPJ fornecido'
                return resultado
            
            resultado['empresa_encontrada'] = True
            resultado['id_cliente'] = empresa_encontrada.get('id')
            resultado['nome_empresa'] = empresa_encontrada.get('nome', '').strip()
            
            # Obter integrações
            integracoes = self.obter_integracoes(resultado['id_cliente'])
            
            # Processar integrações
            for integracao in integracoes:
                integracao_processada = {
                    'sistema': integracao.get('sistema'),
                    'entidade': integracao.get('entidade'),
                    'ultima_atualizacao': integracao.get('dataUltimaIntegracao'),
                    'retorno_erro': integracao.get('erro', False),
                    'status': 'Ativo' if not integracao.get('erro', False) else 'Com Erro'
                }
                resultado['integracoes'].append(integracao_processada)
            
        except Exception as e:
            resultado['erro'] = f'Erro interno: {str(e)}'
        
        return resultado

@integracoes_bp.route('/consultar-por-cliente/<int:cliente_id>', methods=['GET'])
@cross_origin()
def consultar_integracoes_por_cliente(cliente_id):
    """Consulta integrações de um cliente específico do Supabase"""
    try:
        # Buscar cliente no Supabase
        response = supabase.table('clients').select('*').eq('id', cliente_id).execute()
        
        if not response.data:
            return jsonify({
                'success': False,
                'error': 'Cliente não encontrado no Supabase'
            }), 404
        
        cliente = response.data[0]
        cnpj = cliente.get("CNPJ")
        if cnpj is None:
            cnpj = ""
        
        if not cnpj:
            return jsonify({
                'success': False,
                'error': 'Cliente não possui CNPJ cadastrado'
            }), 400
        
        # Criar serviço e autenticar
        service = IntegracaoService()
        if not service.autenticar():
            return jsonify({
                'success': False,
                'error': 'Falha na autenticação com a API de integrações'
            }), 500
        
        # Consultar integrações
        resultado = service.consultar_por_cnpj(cnpj)
        
        # Adicionar dados do cliente do Supabase
        resultado['cliente_supabase'] = {
            'id': cliente.get('id'),
            'name': cliente.get('name'),
            'email': cliente.get('email'),
            'phone': cliente.get('phone'),
            'status': cliente.get('status'),
            'group': cliente.get('group'),
            'subgroup': cliente.get('subgroup')
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

@integracoes_bp.route('/consultar-por-cnpj', methods=['POST'])
@cross_origin()
def consultar_integracoes_por_cnpj():
    """Consulta integrações diretamente por CNPJ"""
    try:
        data = request.get_json()
        cnpj = data.get('cnpj')
        
        if not cnpj:
            return jsonify({
                'success': False,
                'error': 'CNPJ é obrigatório'
            }), 400
        
        # Criar serviço e autenticar
        service = IntegracaoService()
        if not service.autenticar():
            return jsonify({
                'success': False,
                'error': 'Falha na autenticação com a API de integrações'
            }), 500
        
        # Consultar integrações
        resultado = service.consultar_por_cnpj(cnpj)
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@integracoes_bp.route('/clientes', methods=['GET'])
@cross_origin()
def listar_clientes():
    """Lista todos os clientes do Supabase"""
    try:
        response = supabase.table('clients').select('id, name, email, CNPJ, status, group, subgroup').execute()
        
        return jsonify({
            'success': True,
            'data': response.data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao buscar clientes: {str(e)}'
        }), 500

@integracoes_bp.route('/teste-conectividade', methods=['GET'])
@cross_origin()
def teste_conectividade():
    """Testa a conectividade com as APIs"""
    resultado = {
        'supabase': False,
        'api_integracoes': False,
        'detalhes': {}
    }
    
    # Testar Supabase
    try:
        response = supabase.table('clients').select('count').execute()
        resultado['supabase'] = True
        resultado['detalhes']['supabase'] = 'Conectado com sucesso'
    except Exception as e:
        resultado['detalhes']['supabase'] = f'Erro: {str(e)}'
    
    # Testar API de integrações
    try:
        service = IntegracaoService()
        if service.autenticar():
            resultado['api_integracoes'] = True
            resultado['detalhes']['api_integracoes'] = 'Autenticação bem-sucedida'
        else:
            resultado['detalhes']['api_integracoes'] = 'Falha na autenticação'
    except Exception as e:
        resultado['detalhes']['api_integracoes'] = f'Erro: {str(e)}'
    
    return jsonify({
        'success': True,
        'data': resultado
    })

