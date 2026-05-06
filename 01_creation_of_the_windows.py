# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 12:44:27 2026

@author: emmac
"""
import time
import tkinter as tk
from tkinter import messagebox
import serial
import pandas as pd


class ExcelConfigurator(tk.Tk):
    """Stage 4: Complete system with persistent saving to Excel."""

    def __init__(self):
        super().__init__()
        self.geometry("400x200")
        self.title('Capture Configuration')
        self.resizable(False, False)

        self.lbl_name = None
        self.ent_name = None
        self.btn_accept = None
        self.lbl_status = None
        self.btn_stop = None

        self.config = {
            'excel_name': "",
            'serial_port': 'COM3',
            'arduino': None,
            'reading': True
        }
        self.recorded_data = []
        self.setup_ui()

    def setup_ui(self):
        """Configures the initial interface elements."""
        self.lbl_name = tk.Label(self, text="Excel file name:", font=("Arial", 11))
        self.lbl_name.pack(pady=10)
        self.ent_name = tk.Entry(self, font=("Arial", 11), width=30)
        self.ent_name.pack(pady=5)
        self.ent_name.insert(0, "Study_Result")
        self.btn_accept = tk.Button(self, text="Start Analysis", bg="green", fg="white",
                                    font=("Arial", 11, "bold"),
                                    command=self.prepare_analysis)
        self.btn_accept.pack(pady=20)

    def prepare_analysis(self):
        """Prepares the file and starts the serial connection."""
        self.config['excel_name'] = f"{self.ent_name.get().strip()}.xlsx"
        try:
            self.config['arduino'] = serial.Serial(self.config['serial_port'], 9600, timeout=1)
            time.sleep(2)
            self.show_control_window()
            self.reading_loop()
        except serial.SerialException:
            messagebox.showerror("Connection Error",
                                 f"Could not open {self.config['serial_port']}")

    def show_control_window(self):
        """Switches to the data monitoring interface."""
        for widget in self.winfo_children():
            widget.destroy()

        self.title("Analysis in progress...")
        self.geometry("300x150")
        self.lbl_status = tk.Label(self, text="Capturing data from Arduino...", fg="blue")
        self.lbl_status.pack(pady=20)
        self.btn_stop = tk.Button(self, text="STOP ANALYSIS", bg="red", fg="white",
                                  font=("Arial", 12, "bold"),
                                  command=self.finalize_all)
        self.btn_stop.pack(pady=10)

    def reading_loop(self):
        """Lectura en tiempo real."""
        if not self.config['reading']:
            return
        try:
            arduino = self.config['arduino']
            if arduino and arduino.in_waiting > 0:
                raw = arduino.readline().decode('utf-8', errors='ignore').strip()
                if raw.startswith("DATA>"):
                    content = raw.replace("DATA>", "")
                    values = content.split(',')
                    if len(values) >= 6:
                        entry = {
                            "Timestamp": time.strftime("%H:%M:%S"),
                            "Temp": values[0], "Hum": values[1],
                            "Light": values[2], "Noise": values[3],
                            "Score": values[4], "Status": values[5]
                        }
                        self.recorded_data.append(entry)
                        
                        # OPCIONAL: Solo imprimimos en consola para no saturar el disco
                        print(f"Dato recibido: {entry['Timestamp']}")

            # Se vuelve a llamar cada 100ms para leer, pero NO guarda el Excel aquí
            self.after(100, self.reading_loop)

        except Exception as e:
            print(f"Error: {e}")
            self.finalize_all()

    def finalize_all(self):
        """Guarda todo y cierra al presionar STOP."""
        self.config['reading'] = False
        
        
        if self.recorded_data:
            df = pd.DataFrame(self.recorded_data)
            df.to_excel(self.config['excel_name'], index=False)
            messagebox.showinfo("Éxito", f"Datos guardados en {self.config['excel_name']}")
        
        if self.config['arduino']:
            self.config['arduino'].close()
        self.destroy()

    def run(self):
        """Starts the application loop."""
        self.mainloop()

APP = ExcelConfigurator()
APP.run()
