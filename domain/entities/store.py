# Importação das bibliotecas necessárias
# datetime: Para registrar o momento da extração dos dados
# ContactInfo: Nossa classe personalizada para gerenciar informações de contato
import datetime
from domain.entities.contact_info import ContactInfo

class Store:
    """
    Classe que representa uma loja e seus dados extraídos
    
    Esta classe armazena e gerencia:
    1. Informações básicas da loja (nome e URL)
    2. Dados de contato (através da classe ContactInfo)
    3. Metadados da extração (data/hora e status)
    4. Informações de erro, se houver
    
    Também fornece métodos para:
    - Converter os dados para dicionário (para salvar em JSON)
    - Criar uma instância a partir de um dicionário
    """
    
    def __init__(self, name, url, contact_info=None, extracted_at=None):
        """
        Inicializa uma nova instância de Store
        
        Parâmetros:
            name (str): Nome da loja
            url (str): URL da loja
            contact_info (ContactInfo): Objeto com informações de contato
            extracted_at (str): Data/hora da extração em formato ISO
        
        Os parâmetros contact_info e extracted_at são opcionais:
        - Se contact_info não for fornecido, cria um novo objeto vazio
        - Se extracted_at não for fornecido, usa a data/hora atual
        """
        # Dados básicos da loja
        self.name = name        # Nome da loja
        self.url = url          # URL da loja
        
        # Informações de contato (usa um novo objeto se não fornecido)
        self.contact_info = contact_info or ContactInfo()
        
        # Data e hora da extração em formato ISO
        # Se não fornecido, usa o momento atual
        self.extracted_at = extracted_at or datetime.datetime.now().isoformat()
        
        # Status da extração
        self.success = True     # Indica se a extração foi bem-sucedida
        self.error = None       # Armazena mensagem de erro, se houver
    
    def to_dict(self):
        """
        Converte os dados da loja para um dicionário
        
        Este método é útil para:
        1. Salvar os dados em um arquivo JSON
        2. Enviar os dados para uma API
        3. Serializar os dados para transporte
        
        O formato do dicionário varia dependendo do sucesso da extração:
        - Se sucesso: inclui os dados de contato
        - Se erro: inclui a mensagem de erro
        
        Retorna:
            dict: Dicionário com todos os dados da loja
        """
        # Cria o dicionário base com informações comuns
        result = {
            "nome_loja": self.name,          # Nome da loja
            "url": self.url,                 # URL da loja
            "success": self.success,         # Status da extração
            "scrapingTime": self.extracted_at # Data/hora da extração
        }
        
        # Adiciona dados específicos baseado no status
        if self.success:
            # Se sucesso, inclui os dados de contato
            result["data"] = self.contact_info.to_dict()
        else:
            # Se erro, inclui a mensagem de erro
            result["error"] = self.error
            
        return result
    
    @classmethod
    def from_dict(cls, data):
        """
        Cria uma nova instância de Store a partir de um dicionário
        
        Este método é útil para:
        1. Carregar dados de um arquivo JSON
        2. Receber dados de uma API
        3. Deserializar dados recebidos
        
        Parâmetros:
            data (dict): Dicionário com os dados da loja
                        Se None, retorna None
        
        Retorna:
            Store: Nova instância com os dados fornecidos
                  ou None se não houver dados
        """
        # Se não recebeu dados, retorna None
        if not data:
            return None
            
        # Cria uma nova instância com os dados básicos
        store = cls(
            name=data.get("nome_loja", "Desconhecido"),  # Nome da loja (ou "Desconhecido")
            url=data.get("url", ""),                      # URL da loja (ou vazio)
            extracted_at=data.get("scrapingTime",         # Data/hora da extração
                                datetime.datetime.now().isoformat())
        )
        
        # Define o status da extração
        store.success = data.get("success", False)
        
        # Adiciona dados específicos baseado no status
        if store.success:
            # Se sucesso, carrega os dados de contato
            store.contact_info = ContactInfo.from_dict(data.get("data", {}))
        else:
            # Se erro, carrega a mensagem de erro
            store.error = data.get("error", "Erro desconhecido")
            
        return store
