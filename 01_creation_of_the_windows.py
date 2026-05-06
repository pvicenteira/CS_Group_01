# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 12:40:38 2026

@author: emmac
"""
import time
import tkinter as tk
import serial

class ExcelConfigurator(tk.Tk):
    """Stage 3: Mapping received data to Python variables."""

    def __init__(self):
        super().__init__()

        self.ent_name = None
        self.lbl_status = None


        self.config = {
            'excel_name': "",
            'serial_port': 'COM5',
            'arduino': None,
            'reading': True
        }
        self.setup_ui()

    def setup_ui(self):
        """Configures the graphical interface elements."""
        tk.Label(self, text="Excel file name:").pack(pady=10)


        self.ent_name = tk.Entry(self)
        self.ent_name.pack()
        self.ent_name.insert(0, "Study_Result")

        tk.Button(self, text="Start", command=self.prepare_analysis).pack(pady=20)

    def prepare_analysis(self):
        """Starts the connection and the reading loop."""
        self.config['excel_name'] = f"{self.ent_name.get().strip()}.xlsx"
        try:
            self.config['arduino'] = serial.Serial(self.config['serial_port'], 9600, timeout=1)
            time.sleep(2)
            self.show_control_window()
            self.reading_loop()
        except serial.SerialException as error:

            print(f"Connection error: {error}")

    def show_control_window(self):
        """Clears the interface and displays the processing status."""
        for widget in self.winfo_children():
            widget.destroy()
        self.lbl_status = tk.Label(self, text="Processing Data Variables...", fg="blue")
        self.lbl_status.pack(pady=20)

    def reading_loop(self):
        """Logic to parse the data received via serial."""
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
                    print(f"Data Captured: Temp={entry['Temp']}°C, Hum={entry['Hum']}%")

        self.after(100, self.reading_loop)

    def run(self):
        """Runs the main Tkinter loop."""
        self.mainloop()


APP = ExcelConfigurator()
APP.run()
