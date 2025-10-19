# Integração do JARVIS com o Sistema Principal

#Para integrar todos os módulos, você precisa atualizar o arquivo principal:

import sys
import os

# Adicionar src ao Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.jarvis import JARVIS
from modules.home_automation import HomeAutomationManager
from ai.learning import LearningSystem
from web.app import JarvisWebInterface

class EnhancedJARVIS(JARVIS):
    """JARVIS aprimorado com todos os módulos"""
    
    def __init__(self, config):
        super().__init__(config)
        
        # Módulos adicionais
        self.home_automation = None
        self.learning_system = None
        self.web_interface = None
    
    async def initialize(self):
        """Inicializa todos os componentes incluindo novos módulos"""
        await super().initialize()
        
        # Inicializar automação residencial
        self.logger.system("🏠 Inicializando automação residencial...")
        self.home_automation = HomeAutomationManager(self.config)
        
        # Inicializar sistema de aprendizado
        self.logger.system("🧠 Inicializando sistema de aprendizado...")
        self.learning_system = LearningSystem(self.config)
        
        # Inicializar interface web (em thread separada)
        self.logger.system("🌐 Inicializando interface web...")
        self.web_interface = JarvisWebInterface(self.config)
        self.web_interface.run(threaded=True)
        
        self.logger.system("✅ Todos os módulos inicializados!")
    
    async def shutdown(self):
        """Finaliza todos os módulos"""
        if self.learning_system:
            self.learning_system.shutdown()
        
        await super().shutdown()

# Para usar o JARVIS completo, substitua a importação no main.py:
# from core.jarvis import JARVIS
# por:
# from enhanced_jarvis import EnhancedJARVIS as JARVIS