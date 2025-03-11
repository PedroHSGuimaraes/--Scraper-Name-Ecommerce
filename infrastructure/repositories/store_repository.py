'''
STORE REPOSITORY - BANCO DE DADOS DAS LOJAS

Propósito Geral:
Este arquivo atua como um "bibliotecário" digital que:
1. Localiza e lê arquivos de dados das lojas (como ler livros de uma prateleira)
2. Guarda novos dados de lojas (como arquivar novos livros)
3. Organiza os dados em formato JSON (como organizar fichas de catálogo)

Fluxo de Trabalho:
[Arquivo JSON] ↔ [StoreRepository] ↔ [Resto da Aplicação]

Bibliotecas Externas:
- json: Para ler/escrever dados estruturados
- os: Para verificar existência de arquivos e criar diretórios
- logging: Para registro de operações e erros
'''

import json
import os
import logging

class StoreRepository:
    """
    Banco de Dados Simplificado para Lojas
    
    Analogia: Funciona como um arquivista que guarda fichas de lojas em gavetas (arquivos)
    
    Boas Práticas:
    - Tratamento de erros para evitar falhas da aplicação
    - Registro detalhado (logs) para facilitar diagnóstico
    - Validação da existência de arquivos antes da leitura
    """
    
    def __init__(self):
        '''
        INICIALIZAÇÃO DO SISTEMA
        
        Configuração do sistema de registro (logging)
        - Logger é como um diário que registra tudo que acontece
        - Cada entrada no diário contém data, hora e mensagem
        '''
        self.logger = logging.getLogger(__name__)
    
    def load_stores(self, file_path):
        '''
        LEITOR DE LOJAS
        
        Fluxo passo a passo:
        1. Verifica se o "livro" (arquivo) existe na "biblioteca" (diretório)
        2. Abre o "livro" e lê todo seu conteúdo
        3. Traduz o formato JSON para algo que o Python entende
        4. Registra quantas "fichas de lojas" foram encontradas
        
        Parâmetro:
        - file_path: Endereço completo do arquivo (como endereço de uma casa)
        
        Retorno:
        - Lista de lojas (como uma pilha de fichas) ou lista vazia se algo der errado
        
        Possíveis Problemas:
        - Arquivo inexistente: Retorna lista vazia (gaveta sem fichas)
        - Arquivo com formato incorreto: Retorna lista vazia (livro ilegível)
        - Outros erros inesperados: Registra o problema e retorna lista vazia
        '''
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(file_path):
                self.logger.error(f"Arquivo não encontrado: {file_path}")
                return []
            
            # Ler arquivo JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                stores_data = json.load(f)
                
            self.logger.info(f"Carregadas {len(stores_data)} lojas de {file_path}")
            return stores_data
            
        except json.JSONDecodeError:
            self.logger.error(f"Erro ao decodificar JSON de {file_path}")
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar lojas de {file_path}: {str(e)}")
            return []
    
    def save_stores(self, stores_data, file_path):
        '''
        GRAVADOR DE LOJAS
        
        Fluxo passo a passo:
        1. Cria a "pasta" (diretório) se ela não existir (como criar uma nova gaveta)
        2. Abre o "livro de registros" (arquivo) para escrita
        3. Converte os dados das lojas para formato JSON (linguagem universal)
        4. Escreve os dados formatados no arquivo
        5. Anota no sistema de logs quantas lojas foram salvas
        
        Parâmetros:
        - stores_data: Lista com informações das lojas (como pilha de fichas)
        - file_path: Local onde salvar o arquivo (endereço da gaveta)
        
        Retorno:
        - True: Operação bem-sucedida (missão cumprida)
        - False: Ocorreu algum erro (missão falhou)
        
        Boas Práticas:
        - Cria automaticamente diretórios necessários (ensure_ascii=False preserva acentos)
        - Formatação com indent=2 para fácil leitura humana do arquivo
        - Tratamento de erros para evitar falhas cascata no sistema
        '''
        try:
            # Criar diretório de destino se não existir
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Salvar como JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(stores_data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Dados de {len(stores_data)} lojas salvos em {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar dados em {file_path}: {str(e)}")
            return False
