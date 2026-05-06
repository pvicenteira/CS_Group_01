# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 11:22:25 2026

@author: emmac
"""
import tkinter as tk

class ExcelConfigurator(tk.Tk):
    """Stage 1: Definition of the base graphical interface."""

    def __init__(self):
        super().__init__()
        self.geometry("400x200")
        self.title('Capture Configuration')
        self.resizable(False, False)


        self.lbl_status = None
        self.btn_stop = None
        self.lbl_name = None
        self.ent_name = None
        self.btn_accept = None

        self.config = {
            'excel_name': "",
            'reading': True
        }

        self.setup_ui()

    def setup_ui(self):
        """Initial configuration screen."""
        self.lbl_name = tk.Label(self, text="Excel file name:", font=("Arial", 11))
        self.lbl_name.pack(pady=10)

        self.ent_name = tk.Entry(self, font=("Arial", 11), width=30)
        self.ent_name.pack(pady=5)
        self.ent_name.insert(0, "Study_Result")

        self.btn_accept = tk.Button(self, text="Start Analysis",
                                    bg="green", fg="white",
                                    font=("Arial", 11, "bold"),
                                    command=self.prepare_analysis)
        self.btn_accept.pack(pady=20)

    def prepare_analysis(self):
        """Logical transition between windows."""
        self.config['excel_name'] = f"{self.ent_name.get().strip()}.xlsx"
        self.show_control_window()

    def show_control_window(self):
        """Status screen during the process."""
        for widget in self.winfo_children():
            widget.destroy()

        self.title("Analysis in progress...")
        self.geometry("300x150")

        self.lbl_status = tk.Label(self, text="Interface ready. Waiting for logic...", fg="blue")
        self.lbl_status.pack(pady=20)

        self.btn_stop = tk.Button(self, text="STOP ANALYSIS",
                                  bg="red", fg="white",
                                  font=("Arial", 12, "bold"),
                                  command=self.destroy)
        self.btn_stop.pack(pady=10)

    def run(self):
        """Loop"""
        self.mainloop()


APP = ExcelConfigurator()
APP.run()
