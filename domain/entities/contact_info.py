class ContactInfo:
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
        }
    
    @classmethod
    def from_dict(cls, data):
        """Cria uma instância a partir de um dicionário."""
        if not data:
            return cls()
        
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
        """Combina duas instâncias de ContactInfo, evitando duplicatas."""
        if not isinstance(other, ContactInfo):
            return self
        
        self.emails = list(set(self.emails + other.emails))
        self.phones = list(set(self.phones + other.phones))
        
        self.whatsapp["links"] = list(set(self.whatsapp["links"] + other.whatsapp["links"]))
        self.whatsapp["numbers"] = list(set(self.whatsapp["numbers"] + other.whatsapp["numbers"]))
        
        for platform in self.social_media:
            if platform in other.social_media:
                self.social_media[platform] = list(set(
                    self.social_media[platform] + other.social_media[platform]
                ))
        
        return self
