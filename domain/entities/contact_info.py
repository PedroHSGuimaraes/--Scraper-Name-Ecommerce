class ContactInfo:
<<<<<<< HEAD
    """
    Classe que representa todas as informações de contato de uma loja
    
    Esta classe armazena e gerencia:
    1. Endereços de e-mail
    2. Números de telefone
    3. Contatos de WhatsApp (links e números)
    4. Links para redes sociais (Facebook, Instagram, etc.)
    
    Também fornece métodos para:
    - Converter os dados para dicionário (para salvar em JSON)
    - Criar uma instância a partir de um dicionário
    - Combinar informações de diferentes fontes
    """
    
    def __init__(self, emails=None, phones=None, whatsapp=None, social_media=None):
        """
        Inicializa uma nova instância de ContactInfo
        
        Parâmetros:
            emails (list): Lista de endereços de e-mail
            phones (list): Lista de números de telefone
            whatsapp (dict): Dicionário com links e números do WhatsApp
            social_media (dict): Dicionário com links das redes sociais
        
        Todos os parâmetros são opcionais. Se não fornecidos,
        serão inicializados como listas ou dicionários vazios.
        """
        # Inicializa a lista de e-mails (vazia se não fornecida)
        self.emails = emails or []
        
        # Inicializa a lista de telefones (vazia se não fornecida)
        self.phones = phones or []
        
        # Inicializa informações do WhatsApp
        # Mantém tanto os links (wa.me) quanto os números
        self.whatsapp = whatsapp or {"links": [], "numbers": []}
        
        # Inicializa links das redes sociais
        # Cada rede social tem sua própria lista de links
        self.social_media = social_media or {
            "facebook": [],    # Links do Facebook
            "instagram": [],   # Links do Instagram
            "twitter": [],     # Links do Twitter
            "linkedin": [],    # Links do LinkedIn
            "youtube": []      # Links do YouTube
        }
    
    def to_dict(self):
        """
        Converte as informações de contato para um dicionário
        
        Este método é útil para:
        1. Salvar os dados em um arquivo JSON
        2. Enviar os dados para uma API
        3. Serializar os dados para transporte
        
        Retorna:
            dict: Dicionário com todos os dados de contato
        """
        return {
            "emails": self.emails,           # Lista de e-mails
            "phones": self.phones,           # Lista de telefones
            "whatsapp": self.whatsapp,       # Dados do WhatsApp
            "socialMedia": self.social_media # Links das redes sociais
=======
    """Entidade que representa informações de contato de uma loja."""
    
    def __init__(self, emails=None, phones=None, whatsapp=None, social_media=None):
        self.emails = emails or []
        self.phones = phones or []
        self.whatsapp = whatsapp or {"links": [], "numbers": []}
        self.social_media = social_media or {
            "facebook": [],
            "instagram": [],
            "twitter": [],
            "linkedin": [],
            "youtube": []
        }
    
    def to_dict(self):
        """Converte a entidade para formato de dicionário."""
        return {
            "emails": self.emails,
            "phones": self.phones,
            "whatsapp": self.whatsapp,
            "socialMedia": self.social_media
>>>>>>> origin/main
        }
    
    @classmethod
    def from_dict(cls, data):
<<<<<<< HEAD
        """
        Cria uma nova instância de ContactInfo a partir de um dicionário
        
        Este método é útil para:
        1. Carregar dados de um arquivo JSON
        2. Receber dados de uma API
        3. Deserializar dados recebidos
        
        Parâmetros:
            data (dict): Dicionário com os dados de contato
                        Se None, cria uma instância vazia
        
        Retorna:
            ContactInfo: Nova instância com os dados fornecidos
        """
        # Se não recebeu dados, cria uma instância vazia
        if not data:
            return cls()
        
        # Cria uma nova instância com os dados do dicionário
        # Se alguma chave não existir, usa uma lista/dicionário vazio
=======
        """Cria uma instância a partir de um dicionário."""
        if not data:
            return cls()
        
>>>>>>> origin/main
        return cls(
            emails=data.get("emails", []),
            phones=data.get("phones", []),
            whatsapp=data.get("whatsapp", {"links": [], "numbers": []}),
            social_media=data.get("socialMedia", {
                "facebook": [],
                "instagram": [],
                "twitter": [],
                "linkedin": [],
                "youtube": []
            })
        )

    def merge(self, other):
<<<<<<< HEAD
        """
        Combina os dados desta instância com outra instância de ContactInfo
        
        Este método é útil quando:
        1. Temos contatos da mesma loja em páginas diferentes
        2. Queremos combinar dados de várias fontes
        3. Precisamos atualizar informações existentes
        
        O método:
        1. Remove duplicatas automaticamente
        2. Mantém a ordem dos dados
        3. Preserva os dados existentes
        
        Parâmetros:
            other (ContactInfo): Outra instância para combinar
        
        Retorna:
            self: A própria instância atualizada
        """
        # Verifica se o parâmetro é uma instância válida de ContactInfo
        if not isinstance(other, ContactInfo):
            return self
        
        # Combina e-mails, removendo duplicatas
        self.emails = list(set(self.emails + other.emails))
        
        # Combina telefones, removendo duplicatas
        self.phones = list(set(self.phones + other.phones))
        
        # Combina dados do WhatsApp, removendo duplicatas
        self.whatsapp["links"] = list(set(self.whatsapp["links"] + other.whatsapp["links"]))
        self.whatsapp["numbers"] = list(set(self.whatsapp["numbers"] + other.whatsapp["numbers"]))
        
        # Combina links das redes sociais, removendo duplicatas
        # Faz isso para cada plataforma que existe em ambas as instâncias
=======
        """Combina duas instâncias de ContactInfo, evitando duplicatas."""
        if not isinstance(other, ContactInfo):
            return self
        
        self.emails = list(set(self.emails + other.emails))
        self.phones = list(set(self.phones + other.phones))
        
        self.whatsapp["links"] = list(set(self.whatsapp["links"] + other.whatsapp["links"]))
        self.whatsapp["numbers"] = list(set(self.whatsapp["numbers"] + other.whatsapp["numbers"]))
        
>>>>>>> origin/main
        for platform in self.social_media:
            if platform in other.social_media:
                self.social_media[platform] = list(set(
                    self.social_media[platform] + other.social_media[platform]
                ))
        
        return self
