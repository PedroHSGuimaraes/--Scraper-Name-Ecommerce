# Importação das bibliotecas necessárias
# re: Para usar expressões regulares na extração de dados
# ContactInfo: Nossa classe para armazenar informações de contato
# logging: Para registrar informações e erros durante a execução
import re
from domain.entities.contact_info import ContactInfo
import logging

class ExtractContactsUseCase:
    """
    Classe responsável por extrair informações de contato de textos
    
    Esta classe implementa a lógica para:
    1. Extrair e-mails usando expressões regulares
    2. Extrair números de telefone com validação e deduplicação
    3. Extrair links e números de WhatsApp
    4. Extrair links de redes sociais (Facebook, Instagram, etc.)
    
    A classe mantém um registro global de telefones para evitar duplicatas
    entre diferentes lojas e limita o número de telefones por loja.
    """
    
    def __init__(self, phone_registry=None):
        """
        Inicializa o caso de uso de extração de contatos
        
        Parâmetros:
            phone_registry (dict): Dicionário opcional para registrar
                                 telefones já encontrados e suas lojas
        """
        # Registro global de telefones para evitar duplicatas entre lojas
        self.phone_registry = phone_registry or {}
        
        # Configuração do logger para esta classe
        self.logger = logging.getLogger(__name__)
    
    def normalize_phone(self, phone):
        """
        Normaliza um número de telefone removendo toda formatação
        
        Remove todos os caracteres não numéricos do telefone,
        mantendo apenas os dígitos. Isso ajuda a identificar
        números duplicados mesmo com formatações diferentes.
        
        Parâmetros:
            phone (str): Número de telefone com qualquer formatação
            
        Retorna:
            str: Apenas os dígitos do número de telefone
        """
        return ''.join(filter(str.isdigit, phone))
    
    def execute(self, text, url, store_name=None):
        """
        Extrai todas as informações de contato de um texto
        
        Este é o método principal que coordena a extração de:
        - E-mails
        - Telefones
        - WhatsApp
        - Redes sociais
        
        Parâmetros:
            text (str): Texto completo para extrair informações
            url (str): URL de origem do texto
            store_name (str): Nome da loja (opcional, para registro)
            
        Retorna:
            ContactInfo: Objeto com todas as informações extraídas
        """
        # Cria um novo objeto para armazenar as informações
        contact_info = ContactInfo()
        
        # Extração de e-mails usando expressão regular
        # Padrão: usuario@dominio.extensao
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        contact_info.emails = list(set(emails))  # Remove duplicatas
        
        # Extração de telefones com lógica especial
        self._extract_phones(text, contact_info, store_name)
        
        # Extração de informações do WhatsApp
        self._extract_whatsapp(text, contact_info)
        
        # Extração de links das redes sociais
        self._extract_social_media(text, contact_info)
        
        return contact_info
    
    def _extract_phones(self, text, contact_info, store_name):
        """
        Extrai números de telefone do texto com lógica avançada
        
        Este método:
        1. Encontra números de telefone usando expressão regular
        2. Normaliza os números para comparação
        3. Remove duplicatas locais e globais
        4. Prioriza números internacionais
        5. Limita a 5 telefones por loja
        
        Parâmetros:
            text (str): Texto para extrair telefones
            contact_info (ContactInfo): Objeto para armazenar os números
            store_name (str): Nome da loja para registro global
        """
        # Padrão para encontrar números de telefone
        # Suporta vários formatos comuns no Brasil
        phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,3}\)?[-.\s]?\d{4,5}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        
        # Listas para controle de duplicatas
        unique_phones = []          # Números formatados únicos
        normalized_phones = []      # Números normalizados para comparação
        
        # Separação por prioridade
        prioritized_phones = []     # Números internacionais (+XX ou 00XX)
        regular_phones = []         # Números locais
        
        # Processa cada telefone encontrado
        for phone in phones:
            # Normaliza para comparação
            norm_phone = self.normalize_phone(phone)
            
            # Pula se já estiver no registro global
            if norm_phone in self.phone_registry:
                continue
                
            # Pula se for duplicata local
            if norm_phone in normalized_phones:
                continue
                
            # Verifica se tem número mínimo de dígitos
            if len(norm_phone) < 8:  # Padrão brasileiro
                continue
                
            # Classifica por formato
            if '+' in phone or phone.startswith('00'):
                prioritized_phones.append((phone, norm_phone))
            else:
                regular_phones.append((phone, norm_phone))
        
        # Combina as listas, priorizando números internacionais
        all_phones = prioritized_phones + regular_phones
        
        # Limita a 5 telefones únicos por loja
        for phone, norm_phone in all_phones:
            if len(unique_phones) >= 5:
                break
                
            unique_phones.append(phone)
            normalized_phones.append(norm_phone)
            
            # Registra no dicionário global se tiver nome da loja
            if store_name:
                self.phone_registry[norm_phone] = store_name
        
        # Salva os telefones no objeto de contato
        contact_info.phones = unique_phones
    
    def _extract_whatsapp(self, text, contact_info):
        """
        Extrai links e números de WhatsApp do texto
        
        Procura por links do WhatsApp em vários formatos:
        - api.whatsapp.com
        - wa.me
        - whatsapp.com
        
        Parâmetros:
            text (str): Texto para extrair informações
            contact_info (ContactInfo): Objeto para armazenar os dados
        """
        # Padrão para encontrar links do WhatsApp
        whatsapp_pattern = r'(?:https?://)?(?:api\.whatsapp\.com|wa\.me|whatsapp\.com)/(?:send\?phone=)?(\d+)'
        whatsapp_links = re.findall(whatsapp_pattern, text)
        
        # Salva tanto os links formatados quanto os números puros
        contact_info.whatsapp["links"] = [f"https://wa.me/{num}" for num in whatsapp_links]
        contact_info.whatsapp["numbers"] = whatsapp_links
    
    def _extract_social_media(self, text, contact_info):
        """
        Extrai links de redes sociais do texto
        
        Procura por links das principais redes sociais:
        - Facebook: Páginas de perfil ou empresa
        - Instagram: Perfis
        - Twitter: Perfis
        - LinkedIn: Perfis pessoais ou empresariais
        - YouTube: Canais de usuário ou empresa
        
        Parâmetros:
            text (str): Texto para extrair links
            contact_info (ContactInfo): Objeto para armazenar os links
        """
        # Padrões para cada rede social
        social_patterns = {
            'facebook': r'(?:https?://)?(?:www\.)?facebook\.com/[a-zA-Z0-9.]+',
            'instagram': r'(?:https?://)?(?:www\.)?instagram\.com/[a-zA-Z0-9_.]+',
            'twitter': r'(?:https?://)?(?:www\.)?twitter\.com/[a-zA-Z0-9_]+',
            'linkedin': r'(?:https?://)?(?:www\.)?linkedin\.com/(?:company|in)/[a-zA-Z0-9_-]+',
            'youtube': r'(?:https?://)?(?:www\.)?youtube\.com/(?:user|channel|c)/[a-zA-Z0-9_-]+'
        }
        
        # Extrai links de cada rede social
        for platform, pattern in social_patterns.items():
            matches = re.findall(pattern, text)
            contact_info.social_media[platform] = list(set(matches))  # Remove duplicatas
