#!/usr/bin/env python3
"""
Script de Configuración del Sistema de Monitoreo de Nivel de Agua
=================================================================

Este script ayuda a configurar el sistema de monitoreo de nivel de agua
de manera interactiva.
"""

import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox

class SetupWizard:
    def __init__(self):
        self.config = {
            'channel_id': 3000780,
            'read_api_key': 'YL15EX55LIH30PQ3',
            'write_api_key': 'YL15EX55LIH30PQ3',
            'nivel_maximo_cm': 4.0,
            'altura_sensor_ultra': 45.0,
            'umbral_alerta_cm': 10.0,
            'update_interval': 15
        }
        
        self.setup_gui()
    
    def setup_gui(self):
        """Configurar la interfaz gráfica del wizard"""
        self.root = tk.Tk()
        self.root.title("Configuración del Sistema de Monitoreo de Agua")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="🔧 Configuración del Sistema", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Crear pestañas
        self.create_thingspeak_tab()
        self.create_system_tab()
        self.create_advanced_tab()
        
        # Botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="💾 Guardar Configuración", 
                  command=self.save_config).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🔄 Cargar Configuración", 
                  command=self.load_config).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="✅ Finalizar", 
                  command=self.finish_setup).pack(side=tk.RIGHT)
        
        # Cargar configuración existente si existe
        self.load_existing_config()
    
    def create_thingspeak_tab(self):
        """Crear pestaña de configuración de ThingSpeak"""
        thingspeak_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(thingspeak_frame, text="📡 ThingSpeak")
        
        # Información
        info_text = """
        Configuración de ThingSpeak:
        
        1. Ve a https://thingspeak.com
        2. Crea una cuenta o inicia sesión
        3. Crea un nuevo canal
        4. Configura dos campos:
           - Campo 1: Nivel del tubo
           - Campo 2: Nivel de la calle
        5. Obtén las API keys
        """
        
        ttk.Label(thingspeak_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 20))
        
        # Channel ID
        ttk.Label(thingspeak_frame, text="Channel ID:").pack(anchor=tk.W)
        self.channel_var = tk.StringVar(value=str(self.config['channel_id']))
        ttk.Entry(thingspeak_frame, textvariable=self.channel_var, width=50).pack(fill=tk.X, pady=(0, 10))
        
        # Read API Key
        ttk.Label(thingspeak_frame, text="Read API Key:").pack(anchor=tk.W)
        self.read_key_var = tk.StringVar(value=self.config['read_api_key'])
        ttk.Entry(thingspeak_frame, textvariable=self.read_key_var, width=50).pack(fill=tk.X, pady=(0, 10))
        
        # Write API Key
        ttk.Label(thingspeak_frame, text="Write API Key:").pack(anchor=tk.W)
        self.write_key_var = tk.StringVar(value=self.config['write_api_key'])
        ttk.Entry(thingspeak_frame, textvariable=self.write_key_var, width=50).pack(fill=tk.X, pady=(0, 10))
        
        # Botón de prueba
        ttk.Button(thingspeak_frame, text="🧪 Probar Conexión", 
                  command=self.test_thingspeak).pack(pady=(20, 0))
    
    def create_system_tab(self):
        """Crear pestaña de configuración del sistema"""
        system_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(system_frame, text="⚙️ Sistema")
        
        # Nivel máximo del tubo
        ttk.Label(system_frame, text="Nivel Máximo del Tubo (cm):").pack(anchor=tk.W)
        self.max_tubo_var = tk.StringVar(value=str(self.config['nivel_maximo_cm']))
        ttk.Entry(system_frame, textvariable=self.max_tubo_var, width=20).pack(anchor=tk.W, pady=(0, 10))
        
        # Altura del sensor ultrasónico
        ttk.Label(system_frame, text="Altura del Sensor Ultrasónico (cm):").pack(anchor=tk.W)
        self.altura_var = tk.StringVar(value=str(self.config['altura_sensor_ultra']))
        ttk.Entry(system_frame, textvariable=self.altura_var, width=20).pack(anchor=tk.W, pady=(0, 10))
        
        # Umbral de alerta
        ttk.Label(system_frame, text="Umbral de Alerta (cm):").pack(anchor=tk.W)
        self.umbral_var = tk.StringVar(value=str(self.config['umbral_alerta_cm']))
        ttk.Entry(system_frame, textvariable=self.umbral_var, width=20).pack(anchor=tk.W, pady=(0, 10))
        
        # Intervalo de actualización
        ttk.Label(system_frame, text="Intervalo de Actualización (segundos):").pack(anchor=tk.W)
        self.interval_var = tk.StringVar(value=str(self.config['update_interval']))
        ttk.Entry(system_frame, textvariable=self.interval_var, width=20).pack(anchor=tk.W, pady=(0, 10))
    
    def create_advanced_tab(self):
        """Crear pestaña de configuración avanzada"""
        advanced_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(advanced_frame, text="🔧 Avanzado")
        
        # Información sobre el hardware
        hardware_info = """
        Configuración del Hardware ESP32:
        
        Conexiones:
        - Sensor resistivo: Pin 34
        - Sensor ultrasónico TRIG: Pin 26
        - Sensor ultrasónico ECHO: Pin 25
        - Alarma (LED/Buzzer): Pin 27
        
        Configuración WiFi:
        - SSID: "Karen"
        - Password: "Karen8318"
        """
        
        ttk.Label(advanced_frame, text=hardware_info, justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 20))
        
        # Opciones avanzadas
        ttk.Label(advanced_frame, text="Opciones Avanzadas:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Checkbox para auto-inicio
        self.auto_start_var = tk.BooleanVar()
        ttk.Checkbutton(advanced_frame, text="Iniciar automáticamente con Windows", 
                       variable=self.auto_start_var).pack(anchor=tk.W, pady=2)
        
        # Checkbox para logs detallados
        self.detailed_logs_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_frame, text="Logs detallados", 
                       variable=self.detailed_logs_var).pack(anchor=tk.W, pady=2)
        
        # Checkbox para exportación automática
        self.auto_export_var = tk.BooleanVar()
        ttk.Checkbutton(advanced_frame, text="Exportación automática de datos", 
                       variable=self.auto_export_var).pack(anchor=tk.W, pady=2)
    
    def test_thingspeak(self):
        """Probar conexión con ThingSpeak"""
        try:
            import requests
            
            channel_id = int(self.channel_var.get())
            read_key = self.read_key_var.get()
            
            url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json"
            params = {'api_key': read_key, 'results': 1}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'feeds' in data:
                    messagebox.showinfo("✅ Conexión Exitosa", 
                                      f"Conexión a ThingSpeak establecida correctamente.\n"
                                      f"Channel: {channel_id}\n"
                                      f"Datos disponibles: {len(data['feeds'])} registros")
                else:
                    messagebox.showwarning("⚠️ Sin Datos", 
                                         "Conexión exitosa pero no hay datos en el canal.")
            else:
                messagebox.showerror("❌ Error de Conexión", 
                                   f"Error {response.status_code}: {response.text}")
                
        except ValueError:
            messagebox.showerror("❌ Error", "Channel ID debe ser un número válido")
        except ImportError:
            messagebox.showerror("❌ Error", "La librería 'requests' no está instalada")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al conectar: {e}")
    
    def save_config(self):
        """Guardar configuración actual"""
        try:
            # Validar y actualizar configuración
            self.config.update({
                'channel_id': int(self.channel_var.get()),
                'read_api_key': self.read_key_var.get(),
                'write_api_key': self.write_key_var.get(),
                'nivel_maximo_cm': float(self.max_tubo_var.get()),
                'altura_sensor_ultra': float(self.altura_var.get()),
                'umbral_alerta_cm': float(self.umbral_var.get()),
                'update_interval': int(self.interval_var.get()),
                'auto_start': self.auto_start_var.get(),
                'detailed_logs': self.detailed_logs_var.get(),
                'auto_export': self.auto_export_var.get()
            })
            
            # Guardar en archivo
            with open('config.json', 'w') as f:
                json.dump(self.config, f, indent=2)
            
            messagebox.showinfo("✅ Configuración Guardada", 
                              "La configuración se ha guardado exitosamente en 'config.json'")
            
        except ValueError as e:
            messagebox.showerror("❌ Error de Validación", 
                               f"Error en los valores: {e}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al guardar: {e}")
    
    def load_config(self):
        """Cargar configuración desde archivo"""
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
            
            # Actualizar interfaz
            self.channel_var.set(str(self.config.get('channel_id', '')))
            self.read_key_var.set(self.config.get('read_api_key', ''))
            self.write_key_var.set(self.config.get('write_api_key', ''))
            self.max_tubo_var.set(str(self.config.get('nivel_maximo_cm', '')))
            self.altura_var.set(str(self.config.get('altura_sensor_ultra', '')))
            self.umbral_var.set(str(self.config.get('umbral_alerta_cm', '')))
            self.interval_var.set(str(self.config.get('update_interval', '')))
            self.auto_start_var.set(self.config.get('auto_start', False))
            self.detailed_logs_var.set(self.config.get('detailed_logs', True))
            self.auto_export_var.set(self.config.get('auto_export', False))
            
            messagebox.showinfo("✅ Configuración Cargada", 
                              "La configuración se ha cargado desde 'config.json'")
            
        except FileNotFoundError:
            messagebox.showwarning("⚠️ Archivo No Encontrado", 
                                 "No se encontró el archivo 'config.json'")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al cargar: {e}")
    
    def load_existing_config(self):
        """Cargar configuración existente si existe"""
        try:
            with open('config.json', 'r') as f:
                existing_config = json.load(f)
                self.config.update(existing_config)
                
                # Actualizar interfaz
                self.channel_var.set(str(self.config.get('channel_id', '')))
                self.read_key_var.set(self.config.get('read_api_key', ''))
                self.write_key_var.set(self.config.get('write_api_key', ''))
                self.max_tubo_var.set(str(self.config.get('nivel_maximo_cm', '')))
                self.altura_var.set(str(self.config.get('altura_sensor_ultra', '')))
                self.umbral_var.set(str(self.config.get('umbral_alerta_cm', '')))
                self.interval_var.set(str(self.config.get('update_interval', '')))
                self.auto_start_var.set(self.config.get('auto_start', False))
                self.detailed_logs_var.set(self.config.get('detailed_logs', True))
                self.auto_export_var.set(self.config.get('auto_export', False))
                
        except FileNotFoundError:
            pass  # No hay configuración existente
        except Exception as e:
            print(f"Error al cargar configuración existente: {e}")
    
    def finish_setup(self):
        """Finalizar configuración"""
        try:
            # Guardar configuración
            self.save_config()
            
            # Crear archivo de configuración para el programa principal
            config_code = f"""
# Configuración generada automáticamente por setup.py
CHANNEL_ID = {self.config['channel_id']}
READ_API_KEY = "{self.config['read_api_key']}"
WRITE_API_KEY = "{self.config['write_api_key']}"
NIVEL_MAXIMO_CM = {self.config['nivel_maximo_cm']}
ALTURA_SENSOR_ULTRA = {self.config['altura_sensor_ultra']}
UMBRAL_ALERTA_CM = {self.config['umbral_alerta_cm']}
UPDATE_INTERVAL = {self.config['update_interval']}
AUTO_START = {self.config['auto_start']}
DETAILED_LOGS = {self.config['detailed_logs']}
AUTO_EXPORT = {self.config['auto_export']}
"""
            
            with open('config.py', 'w') as f:
                f.write(config_code)
            
            messagebox.showinfo("✅ Configuración Completada", 
                              "La configuración se ha completado exitosamente.\n\n"
                              "Ahora puedes ejecutar el programa principal:\n"
                              "python water_level_monitor.py")
            
            self.root.destroy()
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al finalizar: {e}")
    
    def run(self):
        """Ejecutar el wizard"""
        self.root.mainloop()

def main():
    """Función principal"""
    print("🔧 Iniciando Configuración del Sistema de Monitoreo de Agua")
    print("=" * 60)
    
    wizard = SetupWizard()
    wizard.run()

if __name__ == "__main__":
    main() 