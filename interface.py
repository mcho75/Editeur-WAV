import os
import tkinter as tk


class Interface:

    def __init__(self):
        self.fen = tk.Tk()
        self.fen.resizable(False, False)

    def lancer(self):
        self.fen.mainloop()