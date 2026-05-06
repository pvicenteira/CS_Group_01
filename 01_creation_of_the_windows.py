# -*- coding: utf-8 -*-
"""
Monitor de Estudio Pro - Versión con modo Append (Continuar)
"""
import os
import time
import tkinter as tk
from tkinter import messagebox
import serial
import pandas as pd

class ExcelConfigurator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("400x250")
        self.title('Monitor de Estudio Pro')

        self.lbl_status = None
        self.ent_name = None
        self.placeholder_text = "Nombre del archivo..."

        self.config = {
            'excel_name': "",
            'serial_port': 'COM5', # Asegúrate de que este sea tu puerto
            'arduino': None,
            'reading': True
        }
        self.recorded_data = []
        self.setup_ui()

    def setup_ui(self):
        """Configuración de la interfaz inicial."""
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(
            self, text="Nombre del archivo Excel:", font=("Arial", 11)
        ).pack(pady=10)

        self.ent_name = tk.Entry(self, font=("Arial", 11), width=30, fg='grey')
        self.ent_name.insert(0, self.placeholder_text)
        self.ent_name.bind("<FocusIn>", self._clear_placeholder)
        self.ent_name.bind("<FocusOut>", self._add_placeholder)
        self.ent_name.pack(pady=5)

        tk.Button(
            self, text="Iniciar Captura", bg="green", fg="white",
            font=("Arial", 11, "bold"), command=self.prepare_analysis
        ).pack(pady=20)

    def _clear_placeholder(self, _event):
        if self.ent_name.get() == self.placeholder_text:
            self.ent_name.delete(0, tk.END)
            self.ent_name.config(fg='black')

    def _add_placeholder(self, _event):
        if not self.ent_name.get():
            self.ent_name.insert(0, self.placeholder_text)
            self.ent_name.config(fg='grey')

    def prepare_analysis(self):
        """Lógica para cargar datos existentes o crear nuevos."""
        name_input = self.ent_name.get().strip()

        if not name_input or name_input == self.placeholder_text:
            messagebox.showwarning("Advertencia", "Escribe un nombre válido.")
            return

        full_name = f"{name_input}.xlsx"
        self.config['excel_name'] = full_name
        self.recorded_data = [] # Limpiar lista actual por si acaso

        # LÓGICA DE CONTINUAR (APPEND)
        if os.path.exists(full_name):
            # Pregunta: Sí (Continuar), No (Reemplazar), Cancelar (Salir)
            respuesta = messagebox.askyesnocancel(
                "Archivo existente",
                f"El archivo '{full_name}' ya existe.\n\n"
                "¿Deseas CARGAR los datos anteriores y CONTINUAR?\n"
                "(Si pulsas 'No', el archivo se borrará y empezará de cero)"
            )

            if respuesta is None: # Cancelar
                return

            if respuesta: # Sí - Cargar datos
                try:
                    df_previa = pd.read_excel(full_name)
                    self.recorded_data = df_previa.to_dict('records')
                    print(f"Cargados {len(self.recorded_data)} registros del archivo.")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")
                    return

        # Abrir Puerto Serial
        try:
            self.config['arduino'] = serial.Serial(
                self.config['serial_port'], 9600, timeout=1
            )
            time.sleep(2)
            self.show_control_window()
            self.config['reading'] = True
            self.reading_loop()
        except serial.SerialException:
            messagebox.showerror("Error", f"No se encontró el Arduino en {self.config['serial_port']}")

    def show_control_window(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.lbl_status = tk.Label(
            self, text=f"Capturando en: {self.config['excel_name']}\nRegistros actuales: {len(self.recorded_data)}",
            fg="blue", font=("Arial", 10, "italic")
        )
        self.lbl_status.pack(pady=30)

        tk.Button(
            self, text="DETENER Y GUARDAR", bg="red", fg="white",
            font=("Arial", 12, "bold"), command=self.finalize_all
        ).pack()

    def reading_loop(self):
        """Bucle de lectura corregido para el desvío del ruido."""
        if not self.config['reading']:
            return

        try:
            arduino = self.config['arduino']
            if arduino and arduino.in_waiting > 0:
                raw = arduino.readline().decode('utf-8', errors='ignore').strip()

                if raw.startswith("DATA>"):
                    content = raw.replace("DATA>", "")
                    v = content.split(',')

                    # Verificamos que lleguen todos los campos (10 en total)
                    if len(v) >= 10:
                        entry = {
                            "Hora": time.strftime("%H:%M:%S"),
                            "Temperatura": v[0],
                            "Humedad": v[1],
                            "Luz": v[2],
                            "Ruido_dB": v[3],
                            "Puntaje": v[4],
                            "Estado_Global": v[5],
                            "Alerta_Temp": v[6],
                            "Alerta_Hum": v[7],
                            "Alerta_Luz": v[8],
                            "Alerta_Ruido": v[9]
                        }
                        self.recorded_data.append(entry)
                        # Actualizar contador en pantalla
                        self.lbl_status.config(text=f"Capturando en: {self.config['excel_name']}\nRegistros totales: {len(self.recorded_data)}")
                        print(f"Registro OK - Ruido: {v[3]} dB")

            self.after(100, self.reading_loop)
        except Exception as e:
            print(f"Error en lectura: {e}")
            self.finalize_all()

    def finalize_all(self):
        """Guarda todo en el Excel."""
        self.config['reading'] = False
        if self.recorded_data:
            try:
                df = pd.DataFrame(self.recorded_data)
                df.to_excel(self.config['excel_name'], index=False)
                messagebox.showinfo("Éxito", f"Se guardaron {len(self.recorded_data)} registros en {self.config['excel_name']}")
            except Exception as e:
                messagebox.showerror("Error al guardar", f"No se pudo guardar: {e}")

        if self.config['arduino']:
            self.config['arduino'].close()
        self.destroy()

    def run(self):
        self.mainloop()

APP = ExcelConfigurator()
APP.run()
