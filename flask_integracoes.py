#!/usr/bin/env python3
"""
API Flask para consultar integrações de clientes
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
from typing import Optional, Dict, List

app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem

class SupabaseIntegracoes:
    def __init__(self):
        # Configurações do Supabase
        self.supabase_url = "https://mzjdmhgkrroajmsfwryu.supabase.co"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im16amRtaGdrcnJvYWptc2Z3cnl1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgyMzMwMzUsImV4cCI6MjA2MzgwOTAzNX0.tQCwUfFCV7sD-IexQviU0XEPcbn9j5uK9NSUbH-OeBc"
        
        # Configurações da API externa de integrações
        self.api_integracoes_url = "http://192.168.40.11:50231/api/SingServices/GetIntegracao"
        self.api_integracoes_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6ImludGVncmFjYW9wb3J0YWwiLCJyb2xlIjoiU2luZ1NlcnZpY2VzIiwiVmlnZW5jaWEiOiIxNTIiLCJDbGllbnRlIjoiMSIsIm5iZiI6MTc1NDQxOTcwOSwiZXhwIjoxNzU0NTA2MTA5LCJpYXQiOjE3NTQ0MTk3MDl9.924S2wEdqw2ewEy43T8wqRLM-Y9msJoU_Jp0UqhukiE"
        
        # Headers para Supabase
        self.supabase_headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }
        
        # Headers para API de integrações
        self.api_headers = {
            "accept": "*/*",
            "Authorization": self.api_integracoes_token
        }

    def buscar_cliente_por_id(self, client_id: int) -> Optional[Dict]:
        """Busca um cliente no Supabase pelo ID"""
        try:
            url = f"{self.supabase_url}/rest/v1/clients"
            params = {
                "id": f"eq.{client_id}",
                "select": "*"
            }
            
            response = requests.get(url, headers=self.supabase_headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                return data[0]
            else:
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar cliente: {e}")
            return None

    def buscar_cliente_por_id_cliente(self, id_cliente: str) -> Optional[Dict]:
        """Busca um cliente no Supabase pelo campo id_cliente"""
        try:
            url = f"{self.supabase_url}/rest/v1/clients"
            params = {
                "id_cliente": f"eq.{id_cliente}",
                "select": "*"
            }
            
            response = requests.get(url, headers=self.supabase_headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                return data[0]
            else:
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar cliente por id_cliente: {e}")
            return None

    def buscar_integracoes_ativas(self, id_cliente: str) -> List[Dict]:
        """Busca as integrações ativas para um cliente via API externa"""
        try:
            url = f"{self.api_integracoes_url}?idCliente={id_cliente}"
            
            response = requests.get(url, headers=self.api_headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Se a resposta for uma lista, retorna diretamente
            if isinstance(data, list):
                return data
            # Se for um dicionário, verifica se tem uma chave com lista de integrações
            elif isinstance(data, dict):
                # Procura por chaves comuns que podem conter as integrações
                for key in ['integracoes', 'data', 'items', 'results']:
                    if key in data and isinstance(data[key], list):
                        return data[key]
                # Se não encontrou lista, retorna o próprio dicionário como item único
                return [data]
            else:
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar integrações: {e}")
            return []

    def obter_integracoes_cliente(self, client_id: int = None, id_cliente: str = None) -> Dict:
        """Função principal que busca o cliente e suas integrações ativas"""
        cliente = None
        
        # Busca o cliente primeiro por ID, depois por id_cliente
        if client_id:
            cliente = self.buscar_cliente_por_id(client_id)
        elif id_cliente:
            cliente = self.buscar_cliente_por_id_cliente(id_cliente)
        
        if not cliente:
            return {
                "erro": "Cliente não encontrado",
                "cliente": None,
                "integracoes": []
            }
        
        # Usa o campo id_cliente do registro encontrado para buscar integrações
        cliente_id_para_api = cliente.get('id_cliente')
        
        if not cliente_id_para_api:
            return {
                "erro": "Cliente não possui id_cliente definido",
                "cliente": cliente,
                "integracoes": []
            }
        
        # Busca as integrações ativas
        integracoes = self.buscar_integracoes_ativas(cliente_id_para_api)
        
        return {
            "erro": None,
            "cliente": cliente,
            "integracoes": integracoes
        }

    def listar_todos_clientes(self) -> List[Dict]:
        """Lista todos os clientes do Supabase"""
        try:
            url = f"{self.supabase_url}/rest/v1/clients"
            params = {
                "select": "id,name,email,phone,id_cliente,status,group,subgroup"
            }
            
            response = requests.get(url, headers=self.supabase_headers, params=params)
            response.raise_for_status()
            
            return response.json()
                
        except requests.exceptions.RequestException as e:
            print(f"Erro ao listar clientes: {e}")
            return []


# Instância global do serviço
integracoes_service = SupabaseIntegracoes()

@app.route('/')
def home():
    """Página inicial da API"""
    return jsonify({
        "message": "API de Integrações de Clientes",
        "endpoints": {
            "/clientes": "Lista todos os clientes",
            "/cliente/<int:client_id>/integracoes": "Busca integrações por ID do cliente",
            "/cliente/id_cliente/<id_cliente>/integracoes": "Busca integrações por id_cliente"
        }
    })

@app.route('/clientes')
def listar_clientes():
    """Lista todos os clientes"""
    try:
        clientes = integracoes_service.listar_todos_clientes()
        return jsonify({
            "success": True,
            "data": clientes,
            "total": len(clientes)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/cliente/<int:client_id>/integracoes')
def obter_integracoes_por_id(client_id):
    """Busca integrações de um cliente pelo ID"""
    try:
        resultado = integracoes_service.obter_integracoes_cliente(client_id=client_id)
        
        if resultado.get('erro'):
            return jsonify({
                "success": False,
                "error": resultado['erro']
            }), 404
        
        return jsonify({
            "success": True,
            "cliente": resultado['cliente'],
            "integracoes": resultado['integracoes'],
            "total_integracoes": len(resultado['integracoes'])
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/cliente/id_cliente/<id_cliente>/integracoes')
def obter_integracoes_por_id_cliente(id_cliente):
    """Busca integrações de um cliente pelo id_cliente"""
    try:
        resultado = integracoes_service.obter_integracoes_cliente(id_cliente=id_cliente)
        
        if resultado.get('erro'):
            return jsonify({
                "success": False,
                "error": resultado['erro']
            }), 404
        
        return jsonify({
            "success": True,
            "cliente": resultado['cliente'],
            "integracoes": resultado['integracoes'],
            "total_integracoes": len(resultado['integracoes'])
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/health')
def health_check():
    """Endpoint de verificação de saúde da API"""
    return jsonify({
        "status": "healthy",
        "message": "API funcionando corretamente"
    })

if __name__ == '__main__':
    print("🚀 Iniciando API de Integrações...")
    print("📋 Endpoints disponíveis:")
    print("   GET /clientes - Lista todos os clientes")
    print("   GET /cliente/<id>/integracoes - Busca integrações por ID")
    print("   GET /cliente/id_cliente/<id_cliente>/integracoes - Busca integrações por id_cliente")
    print("   GET /health - Verificação de saúde")
    print("\n🌐 Acesse: http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

