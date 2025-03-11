import logging
import signal
import sys
import os
import traceback
from datetime import datetime

class ScrapingController:
    """Controlador para gerenciar operações de scraping."""
    
    def __init__(self, process_stores_usecase, presenter, config):
        self.process_stores_usecase = process_stores_usecase
        self.presenter = presenter
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.collected_results = []
    
    def setup_signal_handlers(self):
        """Configura manipuladores de sinais para interrupção limpa."""
        signal.signal(signal.SIGINT, self._handle_interrupt)
    
    def _handle_interrupt(self, signal_num, frame):
        """Manipula interrupção Ctrl+C."""
        self.logger.info("\n\nInterrupção detectada (Ctrl+C). Finalizando de forma limpa...")
        self._save_intermediate_results("interrompido")
        sys.exit(0)
    
    def _save_intermediate_results(self, suffix="parcial"):
        """Salva resultados intermediários."""
        if not self.collected_results:
            self.logger.warning("Nenhum resultado para salvar.")
            return
            
        # Criar diretório de saída se não existir
        os.makedirs("resultados", exist_ok=True)
        
        # Salvar em vários formatos
        output_base = f"resultados/contatos_{suffix}"
        
        # Converter para dicionários
        results_dict = [store.to_dict() for store in self.collected_results]
        
        # JSON
        self.presenter.save_json(results_dict, f"{output_base}.json")
        
        # CSV
        self.presenter.save_csv(results_dict, f"{output_base}.csv")
        
        # HTML
        self.presenter.save_html(results_dict, f"{output_base}.html")
    
    def process_stores(self, json_file_path=None):
        """
        Processa lojas de um arquivo JSON.
        
        Args:
            json_file_path: Caminho do arquivo JSON com lojas
            
        Returns:
            bool: True se o processamento foi bem-sucedido
        """
        try:
            # Usar arquivo padrão se não especificado
            if not json_file_path:
                json_file_path = self.config.get("default_input_file", "lojas_oficiais_emergencia.json")
            
            # Caminho para arquivo de saída
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"resultados/contatos_processados_{timestamp}.json"
            
            # Processar lojas
            self.logger.info(f"Iniciando processamento de lojas de: {json_file_path}")
            
            processed_stores = self.process_stores_usecase.execute(
                json_file_path=json_file_path,
                output_file=output_file
            )
            
            # Armazenar resultados para acesso posterior
            self.collected_results = processed_stores
            
            # Salvar em múltiplos formatos
            self._save_intermediate_results("final")
            
            self.logger.info(f"Processamento concluído. {len(processed_stores)} lojas processadas.")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao processar lojas: {str(e)}")
            traceback.print_exc()
            return False
