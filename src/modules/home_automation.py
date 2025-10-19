#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Automação Residencial do JARVIS
Integração com dispositivos IoT e smart home
"""

import requests
import json
import asyncio
from datetime import datetime, time
import threading
from core.logger import JarvisLogger
from core.events import EventManager, Events

class HomeAutomationManager:
    """Gerenciador de automação residencial"""
    
    def __init__(self, config):
        self.config = config
        self.logger = JarvisLogger(__name__)
        self.event_manager = EventManager.get_instance()
        
        # Configurações de automação
        self.home_config = config.get('home_automation', {})
        
        # Integrações disponíveis
        self.integrations = {}
        
        # Estados dos dispositivos
        self.device_states = {}
        
        # Rotinas programadas
        self.scheduled_routines = []
        
        self._initialize_integrations()
        self._setup_event_handlers()
        
        self.logger.automation("Sistema de automação inicializado")
    
    def _initialize_integrations(self):
        """Inicializa integrações com sistemas de automação"""
        # Home Assistant
        if self.home_config.get('home_assistant', {}).get('enabled', False):
            self.integrations['home_assistant'] = HomeAssistantIntegration(
                self.home_config['home_assistant']
            )
        
        # Philips Hue
        if self.home_config.get('philips_hue', {}).get('enabled', False):
            self.integrations['philips_hue'] = PhilipsHueIntegration(
                self.home_config['philips_hue']
            )
        
        # Simulador (para testes)
        self.integrations['simulator'] = DeviceSimulator()
    
    def _setup_event_handlers(self):
        """Configura handlers de eventos"""
        self.event_manager.subscribe(Events.AUTOMATION_TRIGGERED, self._on_automation_triggered)
    
    def _on_automation_triggered(self, data):
        """Handler para eventos de automação"""
        if not data:
            return
        
        action = data.get('action', '')
        location = data.get('location', 'all')
        
        asyncio.create_task(self._execute_action(action, location, data))
    
    async def _execute_action(self, action, location, parameters):
        """Executa uma ação de automação"""
        try:
            self.logger.automation(f"Executando ação: {action} em {location}")
            
            if action == 'turn_on_lights':
                await self._control_lights(True, location)
            elif action == 'turn_off_lights':
                await self._control_lights(False, location)
            elif action == 'set_temperature':
                temperature = parameters.get('temperature', 22)
                await self._set_temperature(temperature, location)
            elif action == 'play_music':
                await self._play_music(parameters.get('playlist', 'relaxing'))
            elif action == 'security_arm':
                await self._arm_security()
            elif action == 'security_disarm':
                await self._disarm_security()
            else:
                self.logger.automation(f"Ação desconhecida: {action}")
                
        except Exception as e:
            self.logger.error(f"Erro ao executar ação {action}: {e}")
    
    async def _control_lights(self, turn_on, location):
        """Controla iluminação"""
        state = "on" if turn_on else "off"
        action_text = "acendendo" if turn_on else "apagando"
        
        # Tentar cada integração
        success = False
        
        for name, integration in self.integrations.items():
            try:
                result = await integration.control_lights(state, location)
                if result:
                    success = True
                    self.logger.automation(f"{action_text.capitalize()} luzes via {name}")
                    break
            except Exception as e:
                self.logger.automation(f"Falha em {name}: {e}")
        
        if success:
            # Atualizar estado
            self.device_states[f'lights_{location}'] = state
            
            # Emitir evento
            self.event_manager.emit(Events.DEVICE_CONNECTED, {
                'device_type': 'lights',
                'location': location,
                'state': state,
                'timestamp': datetime.now().isoformat()
            })
        else:
            self.logger.automation(f"Falha ao {action_text} luzes em {location}")
    
    async def _set_temperature(self, temperature, location):
        """Controla temperatura/clima"""
        for name, integration in self.integrations.items():
            try:
                result = await integration.set_temperature(temperature, location)
                if result:
                    self.logger.automation(f"Temperatura ajustada para {temperature}°C via {name}")
                    self.device_states[f'climate_{location}'] = temperature
                    return
            except Exception as e:
                continue
        
        self.logger.automation(f"Falha ao ajustar temperatura para {temperature}°C")
    
    async def _play_music(self, playlist):
        """Controla reprodução de música"""
        for name, integration in self.integrations.items():
            try:
                result = await integration.play_music(playlist)
                if result:
                    self.logger.automation(f"Música iniciada via {name}")
                    return
            except Exception as e:
                continue
        
        self.logger.automation("Falha ao iniciar música")
    
    async def _arm_security(self):
        """Arma sistema de segurança"""
        self.logger.automation("Armando sistema de segurança")
        # Implementar integração com sistema de segurança
        
    async def _disarm_security(self):
        """Desarma sistema de segurança"""
        self.logger.automation("Desarmando sistema de segurança")
        # Implementar integração com sistema de segurança
    
    def create_routine(self, name, actions, trigger_type="time", trigger_value=None):
        """Cria uma rotina automatizada"""
        routine = {
            'name': name,
            'actions': actions,
            'trigger_type': trigger_type,
            'trigger_value': trigger_value,
            'enabled': True,
            'created_at': datetime.now().isoformat()
        }
        
        self.scheduled_routines.append(routine)
        self.logger.automation(f"Rotina '{name}' criada")
        return routine
    
    def get_device_states(self):
        """Retorna estados atuais dos dispositivos"""
        return self.device_states.copy()
    
    def get_available_devices(self):
        """Retorna lista de dispositivos disponíveis"""
        devices = []
        
        for name, integration in self.integrations.items():
            try:
                integration_devices = integration.get_devices()
                for device in integration_devices:
                    device['integration'] = name
                devices.extend(integration_devices)
            except:
                continue
        
        return devices

class HomeAssistantIntegration:
    """Integração com Home Assistant"""
    
    def __init__(self, config):
        self.base_url = config.get('url', 'http://localhost:8123')
        self.token = config.get('api_token')
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        self.logger = JarvisLogger(__name__)
    
    async def control_lights(self, state, location):
        """Controla luzes via Home Assistant"""
        if not self.token:
            return False
        
        try:
            service = "light.turn_on" if state == "on" else "light.turn_off"
            entity_id = f"light.{location}" if location != 'all' else "light.*"
            
            data = {
                "entity_id": entity_id
            }
            
            response = requests.post(
                f"{self.base_url}/api/services/light/{service.split('.')[1]}",
                headers=self.headers,
                json=data,
                timeout=5
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Erro Home Assistant: {e}")
            return False
    
    async def set_temperature(self, temperature, location):
        """Ajusta temperatura via Home Assistant"""
        # Implementar controle de clima
        return False
    
    async def play_music(self, playlist):
        """Controla música via Home Assistant"""
        # Implementar controle de mídia
        return False
    
    def get_devices(self):
        """Lista dispositivos do Home Assistant"""
        return []

class PhilipsHueIntegration:
    """Integração com Philips Hue"""
    
    def __init__(self, config):
        self.bridge_ip = config.get('bridge_ip')
        self.username = config.get('username')
        self.base_url = f"http://{self.bridge_ip}/api/{self.username}"
        self.logger = JarvisLogger(__name__)
    
    async def control_lights(self, state, location):
        """Controla luzes Philips Hue"""
        if not self.bridge_ip or not self.username:
            return False
        
        try:
            # Descobrir luzes por localização
            lights_response = requests.get(f"{self.base_url}/lights", timeout=5)
            if lights_response.status_code != 200:
                return False
            
            lights = lights_response.json()
            target_lights = []
            
            if location == 'all':
                target_lights = list(lights.keys())
            else:
                # Filtrar por nome/localização
                for light_id, light_info in lights.items():
                    if location.lower() in light_info.get('name', '').lower():
                        target_lights.append(light_id)
            
            # Controlar luzes
            success = True
            for light_id in target_lights:
                data = {"on": state == "on"}
                response = requests.put(
                    f"{self.base_url}/lights/{light_id}/state",
                    json=data,
                    timeout=5
                )
                if response.status_code != 200:
                    success = False
            
            return success and len(target_lights) > 0
            
        except Exception as e:
            self.logger.error(f"Erro Philips Hue: {e}")
            return False
    
    async def set_temperature(self, temperature, location):
        """Hue não controla temperatura"""
        return False
    
    async def play_music(self, playlist):
        """Hue não controla música"""
        return False
    
    def get_devices(self):
        """Lista lâmpadas Hue"""
        try:
            response = requests.get(f"{self.base_url}/lights", timeout=5)
            if response.status_code == 200:
                lights = response.json()
                return [
                    {
                        'id': light_id,
                        'name': info.get('name', f'Light {light_id}'),
                        'type': 'light',
                        'state': info.get('state', {}).get('on', False)
                    }
                    for light_id, info in lights.items()
                ]
        except:
            pass
        return []

class DeviceSimulator:
    """Simulador de dispositivos para testes"""
    
    def __init__(self):
        self.logger = JarvisLogger(__name__)
        self.simulated_devices = {
            'lights': {
                'sala': False,
                'quarto': False,
                'cozinha': False,
                'banheiro': False
            },
            'climate': {
                'temperatura': 22
            },
            'music': {
                'playing': False,
                'playlist': None
            }
        }
    
    async def control_lights(self, state, location):
        """Simula controle de luzes"""
        is_on = state == "on"
        
        if location == 'all':
            for room in self.simulated_devices['lights']:
                self.simulated_devices['lights'][room] = is_on
            self.logger.automation(f"🏠 [SIM] Todas as luzes {'acesas' if is_on else 'apagadas'}")
        else:
            if location in self.simulated_devices['lights']:
                self.simulated_devices['lights'][location] = is_on
                self.logger.automation(f"🏠 [SIM] Luz da {location} {'acesa' if is_on else 'apagada'}")
            else:
                self.logger.automation(f"🏠 [SIM] Local '{location}' não encontrado")
        
        return True
    
    async def set_temperature(self, temperature, location):
        """Simula controle de temperatura"""
        self.simulated_devices['climate']['temperatura'] = temperature
        self.logger.automation(f"🏠 [SIM] Temperatura ajustada para {temperature}°C")
        return True
    
    async def play_music(self, playlist):
        """Simula reprodução de música"""
        self.simulated_devices['music']['playing'] = True
        self.simulated_devices['music']['playlist'] = playlist
        self.logger.automation(f"🏠 [SIM] Tocando playlist: {playlist}")
        return True
    
    def get_devices(self):
        """Lista dispositivos simulados"""
        devices = []
        
        # Adicionar luzes
        for room, state in self.simulated_devices['lights'].items():
            devices.append({
                'id': f'light_{room}',
                'name': f'Luz {room}',
                'type': 'light',
                'state': state,
                'location': room
            })
        
        # Adicionar termostato
        devices.append({
            'id': 'climate_main',
            'name': 'Controle de Clima',
            'type': 'climate',
            'state': self.simulated_devices['climate']['temperatura'],
            'location': 'casa'
        })
        
        return devices