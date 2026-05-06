# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 12:38:30 2026

@author: emmac
"""
import time
import tkinter as tk
from tkinter import messagebox
import serial

class ExcelConfigurator(tk.Tk):
    """Stage 2: Physical hardware connection via Serial."""

    def __init__(self):
        super().__init__()
        self.geometry("400x200")
        self.title('Capture Configuration')


        self.lbl_name = None
        self.ent_name = None
        self.btn_accept = None
        self.lbl_status = None
        self.btn_stop = None

        self.config = {
            'excel_name': "",
            'serial_port': 'COM5',
            'arduino': None,
            'reading': True
        }
        self.setup_ui()

    def setup_ui(self):
        """Configures the elements of the initial interface."""
        self.lbl_name = tk.Label(self, text="Excel file name:", font=("Arial", 11))
        self.lbl_name.pack(pady=10)
        self.ent_name = tk.Entry(self, font=("Arial", 11), width=30)
        self.ent_name.pack(pady=5)
        self.ent_name.insert(0, "Study_Result")
        self.btn_accept = tk.Button(self, text="Start Analysis", bg="green", fg="white",
                                    command=self.prepare_analysis)
        self.btn_accept.pack(pady=20)

    def prepare_analysis(self):
        """Prepares the file name and attempts to connect to the serial port."""
        self.config['excel_name'] = f"{self.ent_name.get().strip()}.xlsx"
        try:

            self.config['arduino'] = serial.Serial(self.config['serial_port'], 9600, timeout=1)
            time.sleep(2)
            self.show_control_window()
        except serial.SerialException:

            messagebox.showerror("Connection Error",
                                 f"Could not open {self.config['serial_port']}")

    def show_control_window(self):
        """Clears the screen and displays monitoring controls."""
        for widget in self.winfo_children():
            widget.destroy()
        self.title("Analysis in progress...")
        self.lbl_status = tk.Label(self, text="Connected to Arduino on COM5", fg="green")
        self.lbl_status.pack(pady=20)
        self.btn_stop = tk.Button(self, text="STOP & CLOSE", bg="red", fg="white",
                                  command=self.finalize_all)
        self.btn_stop.pack(pady=10)

    def finalize_all(self):
        """Safely closes the serial connection and destroys the window."""
        if self.config['arduino']:
            self.config['arduino'].close()
        self.destroy()

    def run(self):
        """Starts the main application loop."""
        self.mainloop()


APP = ExcelConfigurator()
APP.run()
