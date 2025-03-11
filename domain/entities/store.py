import datetime
from domain.entities.contact_info import ContactInfo

class Store:
    """Entidade que representa uma loja."""
    
    def __init__(self, name, url, contact_info=None, extracted_at=None):
        self.name = name
        self.url = url
        self.contact_info = contact_info or ContactInfo()
        self.extracted_at = extracted_at or datetime.datetime.now().isoformat()
        self.success = True
        self.error = None
    
    def to_dict(self):
        """Converte a entidade para formato de dicionário."""
        result = {
            "nome_loja": self.name,
            "url": self.url,
            "success": self.success,
            "scrapingTime": self.extracted_at
        }
        
        if self.success:
            result["data"] = self.contact_info.to_dict()
        else:
            result["error"] = self.error
            
        return result
    
    @classmethod
    def from_dict(cls, data):
        """Cria uma instância a partir de um dicionário."""
        if not data:
            return None
            
        store = cls(
            name=data.get("nome_loja", "Desconhecido"),
            url=data.get("url", ""),
            extracted_at=data.get("scrapingTime", datetime.datetime.now().isoformat())
        )
        
        store.success = data.get("success", False)
        if store.success:
            store.contact_info = ContactInfo.from_dict(data.get("data", {}))
        else:
            store.error = data.get("error", "Erro desconhecido")
            
        return store
