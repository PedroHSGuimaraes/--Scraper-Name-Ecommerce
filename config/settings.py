# Importação das bibliotecas necessárias
# os: Para operações com arquivos e diretórios
# json: Para ler e escrever arquivos de configuração JSON
# logging: Para registrar informações e erros
import os
import json
import logging

class Settings:
    """
    Classe responsável por gerenciar todas as configurações da aplicação
    
    Esta classe permite:
    1. Carregar configurações de um arquivo JSON
    2. Manter configurações padrão
    3. Acessar configurações de forma hierárquica (ex: google_api.api_key)
    4. Modificar configurações em tempo de execução
    """
    
    def __init__(self, config_path=None):
        """
        Inicializa as configurações da aplicação
        
        Parâmetros:
            config_path (str): Caminho para um arquivo JSON de configuração personalizada
                             Se não fornecido, usa apenas as configurações padrão
        """
        # Configurações padrão que serão usadas caso não haja arquivo de configuração
        # ou se alguma configuração estiver faltando no arquivo
        self.default_config = {
            # Configurações gerais da aplicação
            "default_input_file": "lojas_oficiais_emergencia.json",  # Arquivo padrão com lista de lojas
            "output_directory": "resultados",                        # Pasta onde serão salvos os resultados
            
            # Configurações da API do Google
            # Usadas para fazer buscas por informações das lojas
            "google_api": {
                "api_key": "AIzaSyDkwgWLJ_NISwA6Nk-4X0__e68jRK7eyLw",  # Chave de API do Google
                "engine_id": "47366a2537ee841e9"                        # ID do mecanismo de busca personalizado
            },
            
            # Configurações do processo de scraping
            "scraping": {
                "max_retries": 3,     # Número máximo de tentativas em caso de erro
                "base_delay": 5,      # Tempo base de espera entre requisições (segundos)
                "timeout": 30         # Tempo máximo de espera por requisição (segundos)
            }
        }
        
        # Cria uma cópia das configurações padrão
        # Esta cópia será modificada com as configurações personalizadas
        self.config = self.default_config.copy()
        
        # Se foi fornecido um arquivo de configuração e ele existe,
        # carrega as configurações personalizadas
        if config_path and os.path.exists(config_path):
            self._load_from_file(config_path)
    
    def _load_from_file(self, config_path):
        """
        Carrega configurações personalizadas de um arquivo JSON
        
        Este método:
        1. Lê o arquivo JSON de configuração
        2. Mescla as configurações com as padrões
        3. Registra sucesso ou erro no log
        
        Parâmetros:
            config_path (str): Caminho para o arquivo JSON de configuração
        """
        try:
            # Abre e lê o arquivo JSON com encoding UTF-8
            with open(config_path, 'r', encoding='utf-8') as f:
                custom_config = json.load(f)
            
            # Mescla as configurações personalizadas com as padrões
            # As configurações personalizadas têm prioridade
            self._merge_configs(self.config, custom_config)
            logging.info(f"Configurações carregadas de {config_path}")
        except Exception as e:
            logging.error(f"Erro ao carregar configurações: {str(e)}")
    
    def _merge_configs(self, base, custom):
        """
        Mescla duas estruturas de configuração de forma recursiva
        
        Este método permite mesclar configurações aninhadas, por exemplo:
        base = {"a": {"b": 1}}
        custom = {"a": {"c": 2}}
        resultado = {"a": {"b": 1, "c": 2}}
        
        Parâmetros:
            base (dict): Dicionário base (será modificado)
            custom (dict): Dicionário com configurações personalizadas
        """
        for key, value in custom.items():
            # Se ambos os valores são dicionários, mescla recursivamente
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            # Caso contrário, substitui o valor
            else:
                base[key] = value
    
    def get(self, key, default=None):
        """
        Obtém o valor de uma configuração usando uma chave
        
        Suporta acesso hierárquico usando pontos, por exemplo:
        - "google_api.api_key" retorna a chave da API do Google
        - "scraping.timeout" retorna o timeout do scraping
        
        Parâmetros:
            key (str): Chave da configuração (pode conter pontos para acesso hierárquico)
            default: Valor a retornar se a chave não existir
            
        Retorna:
            O valor da configuração ou o valor padrão fornecido
        """
        # Se a chave contém pontos, é um acesso hierárquico
        if "." in key:
            parts = key.split(".")
            current = self.config
            
            # Navega pela hierarquia de configurações
            for part in parts:
                if part not in current:
                    return default
                current = current[part]
            
            return current
        
        # Se não tem pontos, é um acesso direto
        return self.config.get(key, default)
    
    def set(self, key, value):
        """
        Define um novo valor para uma configuração
        
        Suporta definição hierárquica usando pontos, por exemplo:
        - set("google_api.api_key", "nova_chave")
        - set("scraping.timeout", 60)
        
        Parâmetros:
            key (str): Chave da configuração (pode conter pontos para acesso hierárquico)
            value: Novo valor para a configuração
        """
        # Se a chave contém pontos, é uma definição hierárquica
        if "." in key:
            parts = key.split(".")
            current = self.config
            
            # Navega pela hierarquia, criando dicionários vazios se necessário
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Define o valor no último nível
            current[parts[-1]] = value
        else:
            # Se não tem pontos, é uma definição direta
            self.config[key] = value
