import re
from domain.entities.contact_info import ContactInfo
import logging

class ExtractContactsUseCase:
    """Caso de uso para extração de informações de contato de texto."""
    
    def __init__(self, phone_registry=None):
        self.phone_registry = phone_registry or {}
        self.logger = logging.getLogger(__name__)
    
    def normalize_phone(self, phone):
        """Normaliza um número de telefone removendo formatação."""
        return ''.join(filter(str.isdigit, phone))
    
    def execute(self, text, url, store_name=None):
        """
        Extrai informações de contato do texto fornecido.
        
        Args:
            text (str): Texto para extração
            url (str): URL da origem
            store_name (str): Nome da loja para registro
            
        Returns:
            ContactInfo: Objeto com informações de contato extraídas
        """
        contact_info = ContactInfo()
        
        # Extração de emails
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        contact_info.emails = list(set(emails))
        
        # Extração de telefones
        self._extract_phones(text, contact_info, store_name)
        
        # Extração de WhatsApp
        self._extract_whatsapp(text, contact_info)
        
        # Extração de redes sociais
        self._extract_social_media(text, contact_info)
        
        return contact_info
    
    def _extract_phones(self, text, contact_info, store_name):
        """Extrai números de telefone com lógica para evitar duplicatas e limitar a 5."""
        phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,3}\)?[-.\s]?\d{4,5}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        
        unique_phones = []
        normalized_phones = []
        
        # Classificação por prioridade
        prioritized_phones = []
        regular_phones = []
        
        for phone in phones:
            norm_phone = self.normalize_phone(phone)
            
            # Pular se já estiver no registro global
            if norm_phone in self.phone_registry:
                continue
                
            # Pular se já estiver na lista atual
            if norm_phone in normalized_phones:
                continue
                
            # Verificar validade mínima (8+ dígitos para brasileiro)
            if len(norm_phone) < 8:
                continue
                
            # Classificar por formato
            if '+' in phone or phone.startswith('00'):
                prioritized_phones.append((phone, norm_phone))
            else:
                regular_phones.append((phone, norm_phone))
        
        # Combinar por prioridade
        all_phones = prioritized_phones + regular_phones
        
        # Limitar a 5 telefones únicos
        for phone, norm_phone in all_phones:
            if len(unique_phones) >= 5:
                break
                
            unique_phones.append(phone)
            normalized_phones.append(norm_phone)
            
            # Registrar no dicionário global
            if store_name:
                self.phone_registry[norm_phone] = store_name
        
        contact_info.phones = unique_phones
    
    def _extract_whatsapp(self, text, contact_info):
        """Extrai links e números de WhatsApp."""
        whatsapp_pattern = r'(?:https?://)?(?:api\.whatsapp\.com|wa\.me|whatsapp\.com)/(?:send\?phone=)?(\d+)'
        whatsapp_links = re.findall(whatsapp_pattern, text)
        contact_info.whatsapp["links"] = [f"https://wa.me/{num}" for num in whatsapp_links]
        contact_info.whatsapp["numbers"] = whatsapp_links
    
    def _extract_social_media(self, text, contact_info):
        """Extrai links de redes sociais."""
        social_patterns = {
            'facebook': r'(?:https?://)?(?:www\.)?facebook\.com/[a-zA-Z0-9.]+',
            'instagram': r'(?:https?://)?(?:www\.)?instagram\.com/[a-zA-Z0-9_.]+',
            'twitter': r'(?:https?://)?(?:www\.)?twitter\.com/[a-zA-Z0-9_]+',
            'linkedin': r'(?:https?://)?(?:www\.)?linkedin\.com/(?:company|in)/[a-zA-Z0-9_-]+',
            'youtube': r'(?:https?://)?(?:www\.)?youtube\.com/(?:user|channel|c)/[a-zA-Z0-9_-]+'
        }
        
        for platform, pattern in social_patterns.items():
            matches = re.findall(pattern, text)
            contact_info.social_media[platform] = list(set(matches))
