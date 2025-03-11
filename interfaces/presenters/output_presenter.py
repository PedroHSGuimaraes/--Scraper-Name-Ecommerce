import json
import pandas as pd
import logging
import os

class OutputPresenter:
    """Apresentador para formatar e salvar resultados."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def save_json(self, data, output_path):
        """Salva dados em formato JSON."""
        try:
            # Garantir que o diretório exista
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Dados JSON salvos em {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar JSON: {str(e)}")
            return False
    
    def save_csv(self, data, output_path):
        """Converte e salva dados em formato CSV."""
        try:
            # Converter para formato planificado para CSV
            flat_data = self._flatten_data(data)
            
            if not flat_data:
                self.logger.warning("Nenhum dado válido para exportar como CSV")
                return False
            
            # Criar DataFrame e salvar
            df = pd.DataFrame(flat_data)
            
            # Garantir que o diretório exista
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            df.to_csv(output_path, index=False, encoding='utf-8')
            self.logger.info(f"Dados CSV salvos em {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar CSV: {str(e)}")
            return False
    
    def save_html(self, data, output_path):
        """Converte e salva dados em formato HTML."""
        try:
            # Converter para formato planificado
            flat_data = self._flatten_data(data)
            
            if not flat_data:
                self.logger.warning("Nenhum dado válido para exportar como HTML")
                return False
            
            # Criar DataFrame e salvar como HTML
            df = pd.DataFrame(flat_data)
            
            # Garantir que o diretório exista
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            df.to_html(output_path, index=False, border=1, classes='table table-striped')
            self.logger.info(f"Tabela HTML salva em {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar HTML: {str(e)}")
            return False
    
    def _flatten_data(self, data):
        """Converte dados aninhados em formato planificado para CSV/HTML."""
        flat_records = []
        
        for item in data:
            if not isinstance(item, dict):
                continue
                
            # Verificar se é um resultado bem-sucedido
            success = item.get('success', False)
            
            flat_record = {
                'nome_loja': item.get('nome_loja', 'Desconhecido'),
                'url': item.get('url', ''),
                'success': success,
                'data_scraping': item.get('scrapingTime', '')
            }
            
            # Adicionar dados de contato se bem-sucedido
            if success and 'data' in item:
                contact_data = item['data']
                
                # Emails
                flat_record['emails'] = ', '.join(contact_data.get('emails', []))
                
                # Telefones
                flat_record['telefones'] = ', '.join(contact_data.get('phones', []))
                
                # WhatsApp
                whatsapp = contact_data.get('whatsapp', {})
                flat_record['whatsapp_links'] = ', '.join(whatsapp.get('links', []))
                flat_record['whatsapp_numeros'] = ', '.join(whatsapp.get('numbers', []))
                
                # Redes sociais
                social = contact_data.get('socialMedia', {})
                for network in ['facebook', 'instagram', 'twitter', 'linkedin', 'youtube']:
                    flat_record[network] = ', '.join(social.get(network, []))
            else:
                # Adicionar mensagem de erro
                flat_record['erro'] = item.get('error', 'Erro desconhecido')
            
            flat_records.append(flat_record)
            
        return flat_records
