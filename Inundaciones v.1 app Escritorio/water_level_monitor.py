#!/usr/bin/env python3
"""
Sistema de Administración de Monitoreo de Nivel de Agua
=======================================================

Este programa administra un sistema de monitoreo de nivel de agua que utiliza:
- Sensor resistivo para medir nivel en tubo
- Sensor ultrasónico para medir nivel en calle
- ThingSpeak para almacenamiento en la nube
- Sistema de alertas para niveles peligrosos

Autor: Sistema de Monitoreo de Agua
Versión: 1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
import threading
import time
import datetime
import csv
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

class WaterLevelMonitor:
    def __init__(self):
        # Configuración de ThingSpeak
        self.channel_id = 3000780
        self.read_api_key = "YL15EX55LIH30PQ3"  # Necesitarás la API key de lectura
        self.write_api_key = "YL15EX55LIH30PQ3"
        
        # Configuración del sistema
        self.nivel_maximo_cm = 4.0
        self.altura_sensor_ultra = 45.0
        self.umbral_alerta_cm = 10.0
        
        # Datos en tiempo real
        self.nivel_tubo = 0.0
        self.nivel_calle = 0.0
        self.ultima_actualizacion = None
        self.estado_alerta = False
        
        # Historial de datos
        self.historial_tubo = []
        self.historial_calle = []
        self.historial_tiempo = []
        
        # Configurar GUI
        self.setup_gui()
        
        # Iniciar monitoreo en segundo plano
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def setup_gui(self):
        """Configurar la interfaz gráfica principal"""
        self.root = tk.Tk()
        self.root.title("Sistema de Monitoreo de Nivel de Agua")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="🌊 Sistema de Monitoreo de Nivel de Agua", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Panel de estado actual
        self.create_status_panel(main_frame)
        
        # Panel de gráficos
        self.create_charts_panel(main_frame)
        
        # Panel de control
        self.create_control_panel(main_frame)
        
        # Panel de logs
        self.create_logs_panel(main_frame)
        
        # Configurar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_status_panel(self, parent):
        """Crear panel de estado actual"""
        status_frame = ttk.LabelFrame(parent, text="Estado Actual", padding="10")
        status_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Nivel del tubo
        ttk.Label(status_frame, text="📏 Nivel del Tubo:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.tubo_label = ttk.Label(status_frame, text="0.00 cm", font=('Arial', 12, 'bold'))
        self.tubo_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Nivel de la calle
        ttk.Label(status_frame, text="🌊 Nivel de la Calle:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.calle_label = ttk.Label(status_frame, text="0.00 cm", font=('Arial', 12, 'bold'))
        self.calle_label.grid(row=0, column=3, sticky=tk.W, padx=(0, 20))
        
        # Estado de alerta
        ttk.Label(status_frame, text="🚨 Estado de Alerta:").grid(row=0, column=4, sticky=tk.W, padx=(0, 10))
        self.alerta_label = ttk.Label(status_frame, text="NORMAL", font=('Arial', 12, 'bold'), foreground='green')
        self.alerta_label.grid(row=0, column=5, sticky=tk.W, padx=(0, 20))
        
        # Última actualización
        ttk.Label(status_frame, text="🕐 Última Actualización:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.update_label = ttk.Label(status_frame, text="Nunca", font=('Arial', 10))
        self.update_label.grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=(10, 0))
        
        # Estado de conexión
        ttk.Label(status_frame, text="📡 Estado de Conexión:").grid(row=1, column=2, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.connection_label = ttk.Label(status_frame, text="Desconectado", font=('Arial', 10), foreground='red')
        self.connection_label.grid(row=1, column=3, sticky=tk.W, padx=(0, 20), pady=(10, 0))
    
    def create_charts_panel(self, parent):
        """Crear panel de gráficos"""
        charts_frame = ttk.LabelFrame(parent, text="Gráficos en Tiempo Real", padding="10")
        charts_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        charts_frame.columnconfigure(0, weight=1)
        charts_frame.rowconfigure(0, weight=1)
        
        # Crear figura de matplotlib
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title('Nivel de Agua en Tiempo Real')
        self.ax.set_xlabel('Tiempo')
        self.ax.set_ylabel('Nivel (cm)')
        self.ax.grid(True, alpha=0.3)
        
        # Canvas para matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, charts_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Inicializar líneas del gráfico
        self.line_tubo, = self.ax.plot([], [], 'b-', label='Nivel Tubo', linewidth=2)
        self.line_calle, = self.ax.plot([], [], 'r-', label='Nivel Calle', linewidth=2)
        self.ax.legend()
        
        # Configurar límites del gráfico
        self.ax.set_ylim(0, 50)
    
    def create_control_panel(self, parent):
        """Crear panel de control"""
        control_frame = ttk.LabelFrame(parent, text="Controles", padding="10")
        control_frame.grid(row=2, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Botones de control
        ttk.Button(control_frame, text="🔄 Actualizar Datos", 
                  command=self.manual_update).grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(control_frame, text="💾 Exportar Datos", 
                  command=self.export_data).grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(control_frame, text="⚙️ Configuración", 
                  command=self.show_config).grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(control_frame, text="📊 Estadísticas", 
                  command=self.show_stats).grid(row=3, column=0, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(control_frame, text="🔔 Probar Alerta", 
                  command=self.test_alert).grid(row=4, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Configuración de umbrales
        config_frame = ttk.LabelFrame(control_frame, text="Configuración", padding="5")
        config_frame.grid(row=5, column=0, pady=(20, 0), sticky=(tk.W, tk.E))
        
        ttk.Label(config_frame, text="Umbral de Alerta (cm):").grid(row=0, column=0, sticky=tk.W)
        self.umbral_var = tk.StringVar(value=str(self.umbral_alerta_cm))
        ttk.Entry(config_frame, textvariable=self.umbral_var, width=10).grid(row=0, column=1, padx=(5, 0))
        
        ttk.Button(config_frame, text="Aplicar", 
                  command=self.apply_config).grid(row=1, column=0, columnspan=2, pady=(5, 0))
    
    def create_logs_panel(self, parent):
        """Crear panel de logs"""
        logs_frame = ttk.LabelFrame(parent, text="Logs del Sistema", padding="10")
        logs_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(0, weight=1)
        
        # Área de texto para logs
        self.log_text = scrolledtext.ScrolledText(logs_frame, height=8, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Botones de log
        log_buttons_frame = ttk.Frame(logs_frame)
        log_buttons_frame.grid(row=1, column=0, pady=(5, 0), sticky=(tk.W, tk.E))
        
        ttk.Button(log_buttons_frame, text="Limpiar Logs", 
                  command=self.clear_logs).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(log_buttons_frame, text="Guardar Logs", 
                  command=self.save_logs).pack(side=tk.LEFT)
    
    def log_message(self, message):
        """Agregar mensaje al log"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        print(log_entry.strip())
    
    def get_thingspeak_data(self):
        """Obtener datos de ThingSpeak"""
        try:
            url = f"https://api.thingspeak.com/channels/{self.channel_id}/feeds.json"
            params = {
                'api_key': self.read_api_key,
                'results': 1  # Solo el último dato
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data['feeds']:
                feed = data['feeds'][0]
                self.nivel_tubo = float(feed.get('field1', 0))
                self.nivel_calle = float(feed.get('field2', 0))
                self.ultima_actualizacion = feed.get('created_at', '')
                return True
            else:
                self.log_message("⚠️ No hay datos disponibles en ThingSpeak")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_message(f"❌ Error al conectar con ThingSpeak: {e}")
            return False
        except (KeyError, ValueError) as e:
            self.log_message(f"❌ Error al procesar datos: {e}")
            return False
    
    def update_gui(self):
        """Actualizar la interfaz gráfica"""
        # Actualizar etiquetas de estado
        self.tubo_label.config(text=f"{self.nivel_tubo:.2f} cm")
        self.calle_label.config(text=f"{self.nivel_calle:.2f} cm")
        
        # Actualizar estado de alerta
        if self.estado_alerta:
            self.alerta_label.config(text="ALERTA", foreground='red')
        else:
            self.alerta_label.config(text="NORMAL", foreground='green')
        
        # Actualizar última actualización
        if self.ultima_actualizacion:
            try:
                dt = datetime.datetime.fromisoformat(self.ultima_actualizacion.replace('Z', '+00:00'))
                local_time = dt.astimezone().strftime("%H:%M:%S")
                self.update_label.config(text=local_time)
            except:
                self.update_label.config(text="Error de formato")
        
        # Actualizar estado de conexión
        if self.ultima_actualizacion:
            self.connection_label.config(text="Conectado", foreground='green')
        else:
            self.connection_label.config(text="Desconectado", foreground='red')
        
        # Actualizar gráfico
        self.update_chart()
    
    def update_chart(self):
        """Actualizar gráfico en tiempo real"""
        if len(self.historial_tiempo) > 0:
            # Limitar a los últimos 50 puntos
            max_points = 50
            if len(self.historial_tiempo) > max_points:
                times = self.historial_tiempo[-max_points:]
                tubo_data = self.historial_tubo[-max_points:]
                calle_data = self.historial_calle[-max_points:]
            else:
                times = self.historial_tiempo
                tubo_data = self.historial_tubo
                calle_data = self.historial_calle
            
            # Convertir tiempos a minutos desde el inicio
            if len(times) > 1:
                start_time = times[0]
                time_minutes = [(t - start_time).total_seconds() / 60 for t in times]
                
                self.line_tubo.set_data(time_minutes, tubo_data)
                self.line_calle.set_data(time_minutes, calle_data)
                
                # Ajustar límites del eje X
                if len(time_minutes) > 1:
                    self.ax.set_xlim(0, max(time_minutes))
                
                self.canvas.draw()
    
    def check_alerts(self):
        """Verificar si hay alertas activas"""
        old_alert = self.estado_alerta
        
        # Verificar si el nivel de la calle está por encima del umbral
        if self.nivel_calle >= self.umbral_alerta_cm:
            self.estado_alerta = True
            if not old_alert:
                self.log_message(f"🚨 ALERTA: Nivel de agua en la calle ({self.nivel_calle:.2f} cm) supera el umbral ({self.umbral_alerta_cm} cm)")
                self.show_alert_popup()
        else:
            self.estado_alerta = False
            if old_alert:
                self.log_message("✅ Alerta desactivada: Nivel de agua normalizado")
    
    def show_alert_popup(self):
        """Mostrar popup de alerta"""
        messagebox.showwarning(
            "🚨 ALERTA DE NIVEL DE AGUA",
            f"¡Nivel de agua peligroso!\n\nNivel en la calle: {self.nivel_calle:.2f} cm\nUmbral: {self.umbral_alerta_cm} cm\n\n¡Tome las precauciones necesarias!"
        )
    
    def monitor_loop(self):
        """Bucle principal de monitoreo"""
        while self.running:
            try:
                if self.get_thingspeak_data():
                    # Agregar datos al historial
                    current_time = datetime.datetime.now()
                    self.historial_tiempo.append(current_time)
                    self.historial_tubo.append(self.nivel_tubo)
                    self.historial_calle.append(self.nivel_calle)
                    
                    # Verificar alertas
                    self.check_alerts()
                    
                    # Actualizar GUI en el hilo principal
                    self.root.after(0, self.update_gui)
                    
                    self.log_message(f"📊 Datos actualizados - Tubo: {self.nivel_tubo:.2f} cm, Calle: {self.nivel_calle:.2f} cm")
                else:
                    self.log_message("⚠️ No se pudieron obtener datos")
                
                # Esperar 15 segundos antes de la siguiente actualización
                time.sleep(15)
                
            except Exception as e:
                self.log_message(f"❌ Error en el bucle de monitoreo: {e}")
                time.sleep(30)  # Esperar más tiempo en caso de error
    
    def manual_update(self):
        """Actualización manual de datos"""
        self.log_message("🔄 Actualización manual solicitada...")
        if self.get_thingspeak_data():
            self.update_gui()
            self.check_alerts()
            self.log_message("✅ Actualización manual completada")
        else:
            self.log_message("❌ Error en actualización manual")
    
    def export_data(self):
        """Exportar datos a CSV"""
        try:
            filename = f"water_level_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Timestamp', 'Nivel_Tubo_cm', 'Nivel_Calle_cm', 'Alerta'])
                
                for i, time in enumerate(self.historial_tiempo):
                    alerta = "SI" if (i < len(self.historial_calle) and 
                                    self.historial_calle[i] >= self.umbral_alerta_cm) else "NO"
                    writer.writerow([
                        time.strftime('%Y-%m-%d %H:%M:%S'),
                        self.historial_tubo[i] if i < len(self.historial_tubo) else 0,
                        self.historial_calle[i] if i < len(self.historial_calle) else 0,
                        alerta
                    ])
            
            self.log_message(f"💾 Datos exportados a {filename}")
            messagebox.showinfo("Exportación", f"Datos exportados exitosamente a {filename}")
            
        except Exception as e:
            self.log_message(f"❌ Error al exportar datos: {e}")
            messagebox.showerror("Error", f"Error al exportar datos: {e}")
    
    def show_config(self):
        """Mostrar ventana de configuración"""
        config_window = tk.Toplevel(self.root)
        config_window.title("Configuración del Sistema")
        config_window.geometry("400x300")
        config_window.transient(self.root)
        config_window.grab_set()
        
        # Configuración de ThingSpeak
        ttk.Label(config_window, text="Configuración de ThingSpeak", font=('Arial', 12, 'bold')).pack(pady=10)
        
        ttk.Label(config_window, text="Channel ID:").pack(anchor=tk.W, padx=20)
        channel_var = tk.StringVar(value=str(self.channel_id))
        ttk.Entry(config_window, textvariable=channel_var, width=30).pack(padx=20, pady=(0, 10))
        
        ttk.Label(config_window, text="Read API Key:").pack(anchor=tk.W, padx=20)
        read_key_var = tk.StringVar(value=self.read_api_key)
        ttk.Entry(config_window, textvariable=read_key_var, width=30).pack(padx=20, pady=(0, 10))
        
        # Configuración del sistema
        ttk.Label(config_window, text="Configuración del Sistema", font=('Arial', 12, 'bold')).pack(pady=(20, 10))
        
        ttk.Label(config_window, text="Nivel Máximo Tubo (cm):").pack(anchor=tk.W, padx=20)
        max_tubo_var = tk.StringVar(value=str(self.nivel_maximo_cm))
        ttk.Entry(config_window, textvariable=max_tubo_var, width=30).pack(padx=20, pady=(0, 10))
        
        ttk.Label(config_window, text="Altura Sensor Ultrasónico (cm):").pack(anchor=tk.W, padx=20)
        altura_var = tk.StringVar(value=str(self.altura_sensor_ultra))
        ttk.Entry(config_window, textvariable=altura_var, width=30).pack(padx=20, pady=(0, 10))
        
        def save_config():
            try:
                self.channel_id = int(channel_var.get())
                self.read_api_key = read_key_var.get()
                self.nivel_maximo_cm = float(max_tubo_var.get())
                self.altura_sensor_ultra = float(altura_var.get())
                self.log_message("⚙️ Configuración actualizada")
                config_window.destroy()
            except ValueError as e:
                messagebox.showerror("Error", f"Valor inválido: {e}")
        
        ttk.Button(config_window, text="Guardar", command=save_config).pack(pady=20)
    
    def show_stats(self):
        """Mostrar estadísticas del sistema"""
        if not self.historial_tubo:
            messagebox.showinfo("Estadísticas", "No hay datos disponibles para mostrar estadísticas.")
            return
        
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Estadísticas del Sistema")
        stats_window.geometry("500x400")
        stats_window.transient(self.root)
        
        # Calcular estadísticas
        tubo_stats = {
            'Máximo': max(self.historial_tubo),
            'Mínimo': min(self.historial_tubo),
            'Promedio': sum(self.historial_tubo) / len(self.historial_tubo)
        }
        
        calle_stats = {
            'Máximo': max(self.historial_calle),
            'Mínimo': min(self.historial_calle),
            'Promedio': sum(self.historial_calle) / len(self.historial_calle)
        }
        
        # Mostrar estadísticas
        ttk.Label(stats_window, text="Estadísticas del Sistema", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Estadísticas del tubo
        ttk.Label(stats_window, text="📏 Nivel del Tubo", font=('Arial', 12, 'bold')).pack(pady=(20, 10))
        for key, value in tubo_stats.items():
            ttk.Label(stats_window, text=f"{key}: {value:.2f} cm").pack()
        
        # Estadísticas de la calle
        ttk.Label(stats_window, text="🌊 Nivel de la Calle", font=('Arial', 12, 'bold')).pack(pady=(20, 10))
        for key, value in calle_stats.items():
            ttk.Label(stats_window, text=f"{key}: {value:.2f} cm").pack()
        
        # Información general
        ttk.Label(stats_window, text="📊 Información General", font=('Arial', 12, 'bold')).pack(pady=(20, 10))
        ttk.Label(stats_window, text=f"Total de mediciones: {len(self.historial_tiempo)}").pack()
        
        if len(self.historial_tiempo) > 1:
            tiempo_total = self.historial_tiempo[-1] - self.historial_tiempo[0]
            ttk.Label(stats_window, text=f"Tiempo de monitoreo: {tiempo_total}").pack()
    
    def test_alert(self):
        """Probar el sistema de alertas"""
        self.log_message("🔔 Probando sistema de alertas...")
        self.show_alert_popup()
        self.log_message("✅ Prueba de alerta completada")
    
    def apply_config(self):
        """Aplicar configuración de umbral"""
        try:
            self.umbral_alerta_cm = float(self.umbral_var.get())
            self.log_message(f"⚙️ Umbral de alerta actualizado a {self.umbral_alerta_cm} cm")
            self.check_alerts()  # Revisar alertas con el nuevo umbral
        except ValueError:
            messagebox.showerror("Error", "El umbral debe ser un número válido")
    
    def clear_logs(self):
        """Limpiar logs"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("🧹 Logs limpiados")
    
    def save_logs(self):
        """Guardar logs a archivo"""
        try:
            filename = f"system_logs_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.log_text.get(1.0, tk.END))
            
            self.log_message(f"💾 Logs guardados en {filename}")
            messagebox.showinfo("Logs", f"Logs guardados exitosamente en {filename}")
        except Exception as e:
            self.log_message(f"❌ Error al guardar logs: {e}")
            messagebox.showerror("Error", f"Error al guardar logs: {e}")
    
    def on_closing(self):
        """Manejar cierre de la aplicación"""
        self.running = False
        self.log_message("🛑 Cerrando aplicación...")
        self.root.destroy()
    
    def run(self):
        """Ejecutar la aplicación"""
        self.log_message("🚀 Iniciando Sistema de Monitoreo de Nivel de Agua")
        self.log_message(f"📡 Conectando a ThingSpeak Channel: {self.channel_id}")
        self.root.mainloop()

def main():
    """Función principal"""
    try:
        app = WaterLevelMonitor()
        app.run()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        messagebox.showerror("Error", f"Error al iniciar la aplicación: {e}")

if __name__ == "__main__":
    main() 