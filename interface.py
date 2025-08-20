import tkinter as tk
from tkinter import ttk
import encodage
import winsound
import os


class Grille(tk.Canvas):

    def __init__(self, boss):
        self.longueur_totale = 100
        self.liste_rectangles = []
        self.rectangle_survole = None
        self.dragging = 0

        tk.Canvas.__init__(self, boss, width=800, height=500, bg=palette["bg1"], highlightthickness=0,
                           scrollregion=(0, 0, 5000, 1000))
        self.surbrillance = self.create_rectangle(0, 0, 0, 0, fill=palette["bg2"])

        self.bind("<MouseWheel>", self.scroll_vertical)
        self.bind("<Shift-MouseWheel>", self.scroll_horizontal)
        self.bind("<B1-ButtonRelease>", self.ajouter_note)
        self.bind("<Motion>", self.deplacement_souris)
        self.bind("<B1-Motion>", self.deplacement_clic)

        self.bordure = 20
        self.intitules = 100
        self.longueur_sec = 50
        self.hauteur = 20

        self.tracer_lignes()

    def deplacement_souris(self, event):
        position = (round(self.canvasx(event.x)) - self.intitules - self.bordure) * 4 / self.longueur_sec
        note = (round(self.canvasy(event.y)) - self.bordure) // self.hauteur
        if (0 <= position < self.longueur_totale * 4) and (0 <= note < len(notes)):
            pos_y = self.bordure + note * self.hauteur
            self.coords(self.surbrillance, self.bordure, pos_y,
                        self.longueur_totale * self.longueur_sec + self.bordure + self.intitules, pos_y+self.hauteur)
        self.config(cursor="arrow")
        self.rectangle_survole = None
        for rectangle in self.liste_rectangles:
            self.itemconfig(rectangle.sprite, fill=palette["fg2"])
            if rectangle.note_encodage.position <= position * 250 < rectangle.note_encodage.position + rectangle.note_encodage.duree:
                if rectangle.numero_note == note:
                    self.rectangle_survole = rectangle
                    self.itemconfig(rectangle.sprite, fill=palette["fg1"])
                    if position - (self.rectangle_survole.note_encodage.position + self.rectangle_survole.note_encodage.duree) / 250 > -0.3:
                        self.config(cursor="sb_h_double_arrow")
                    if position - rectangle.note_encodage.position / 250 < 0.3:
                        self.config(cursor="sb_h_double_arrow")

    def deplacement_clic(self, event):
        position = (round(self.canvasx(event.x)) - self.intitules - self.bordure) * 4 / self.longueur_sec
        if self.rectangle_survole is not None:
            if self.dragging == 0:
                if position - (self.rectangle_survole.note_encodage.position + self.rectangle_survole.note_encodage.duree) / 250 > -0.3:
                    self.dragging = 1
                elif position - self.rectangle_survole.note_encodage.position / 250 < 0.3:
                    self.dragging = 2
            elif self.dragging == 1:
                self.rectangle_survole.note_encodage.duree = round(position) * 250 - self.rectangle_survole.note_encodage.position
                self.rectangle_survole.actualiser()
            elif self.dragging == 2:
                self.rectangle_survole.note_encodage.duree += self.rectangle_survole.note_encodage.position - round(position) * 250
                self.rectangle_survole.note_encodage.position = round(position) * 250
                self.rectangle_survole.actualiser()

    def scroll_horizontal(self, event):
        self.xview_scroll(-event.delta//50, tk.UNITS)

    def scroll_vertical(self, event):
        self.yview_scroll(-event.delta//50, tk.UNITS)

    def tracer_lignes(self):
        self.configure(scrollregion=(0, 0, (self.longueur_sec*self.longueur_totale)+self.intitules+(2*self.bordure), self.hauteur*len(notes)+(2*self.bordure)))
        self.create_line(self.bordure, self.bordure, self.bordure, self.hauteur*len(notes)+self.bordure, fill=palette["bg3"])
        for i in range(0, self.longueur_totale * 4 + 1):
            pos_x = i * self.longueur_sec // 4 + self.bordure + self.intitules
            self.create_line(pos_x, self.bordure, pos_x, self.hauteur*len(notes)+self.bordure, fill=[palette["bg2"], palette["bg3"]][i % 4 == 0])
        for i in range(0, len(notes) + 1):
            pos_y = i * self.hauteur + self.bordure
            self.create_line(self.bordure, pos_y, self.longueur_totale*self.longueur_sec+self.intitules+self.bordure, pos_y, fill=palette["bg3"])
        for i in range(len(notes)):
            self.create_text(self.bordure+self.intitules-10, self.bordure+self.hauteur*i+self.hauteur//2, text=notes[i][0], anchor=tk.E, fill=palette["fg1"])

    def ajouter_note(self, event):
        position = (round(self.canvasx(event.x)) - self.intitules - self.bordure) * 4 / self.longueur_sec
        note = (round(self.canvasy(event.y)) - self.bordure) // self.hauteur
        if self.dragging == 0:
            if self.rectangle_survole is not None:
                self.delete(self.rectangle_survole.sprite)
                self.liste_rectangles.remove(self.rectangle_survole)
                self.rectangle_survole = None
            elif (0 <= position < self.longueur_totale * 4) and (0 <= note < len(notes)):
                print(position, notes[note][0])
                self.liste_rectangles.append(RectangleNote(self, note, position*250))
                self.rectangle_survole = self.liste_rectangles[-1]
        self.dragging = 0


class RectangleNote:

    def __init__(self, boss, numero_note, position):
        self.boss = boss
        self.numero_note = numero_note
        self.note_encodage = encodage.Note(notes[self.numero_note][1], 10000, 250, round(position // 250) * 250)
        pos_x = self.boss.bordure + self.boss.intitules + (round(position // 250) * self.boss.longueur_sec // 4)
        pos_y = self.boss.bordure + self.numero_note * self.boss.hauteur
        self.sprite = self.boss.create_rectangle(pos_x, pos_y, pos_x+(self.boss.longueur_sec//4), pos_y+self.boss.hauteur,
                                                 width=1, fill=palette["fg2"], outline=palette["fg1"])
        if notes[self.numero_note][1] >= 37:
            winsound.Beep(notes[self.numero_note][1], 250)

    def actualiser(self):
        pos_x = self.boss.bordure + self.boss.intitules + (self.note_encodage.position // 250 * self.boss.longueur_sec // 4)
        pos_y = self.boss.bordure + self.numero_note * self.boss.hauteur
        self.boss.coords(self.sprite, pos_x, pos_y, pos_x+(self.boss.longueur_sec*self.note_encodage.duree//1000), pos_y+self.boss.hauteur)


class Interface:

    def __init__(self):

        self.fen = tk.Tk()
        self.fen.config(bg=palette["bg2"])
        self.fen.title("Editeur WAV")
        self.fen.resizable(False, False)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TScrollbar", troughcolor=palette["bg2"], background=palette["fg1"], arrowcolor=palette["bg1"], bordercolor=palette["bg3"])
        style.configure("TButton", background=palette["fg1"], foreground=palette["bg1"], relief=tk.FLAT, width=20)
        style.map("TScrollbar", background=[("active", palette["fg2"])])
        style.map("TButton", background=[("active", palette["fg2"])])

        self.grille = Grille(self.fen)
        self.scrollbarx = ttk.Scrollbar(self.fen, orient=tk.HORIZONTAL, command=self.grille.xview, style="TScrollbar")
        self.scrollbary = ttk.Scrollbar(self.fen, orient=tk.VERTICAL, command=self.grille.yview, style="TScrollbar")
        self.grille.configure(xscrollcommand=self.scrollbarx.set, yscrollcommand=self.scrollbary.set)
        self.frame = tk.Frame(self.fen, borderwidth=2, bg=palette["bg1"])
        self.bou1 = ttk.Button(self.frame, text="Exporter", command=self.exporter_son, style="TButton")
        self.bou2 = ttk.Button(self.frame, text="Sauvegarder", command=self.exporter_son, style="TButton")
        self.bou3 = ttk.Button(self.frame, text="Ouvrir", command=self.exporter_son, style="TButton")

        self.grille.grid(row=0, column=0, padx=(10, 0), pady=(10, 0))
        self.scrollbarx.grid(row=1, column=0, padx=10, pady=(0, 10), sticky=tk.EW)
        self.scrollbary.grid(row=0, column=1, pady=10, sticky=tk.NS)
        self.frame.grid(row=0, column=2, rowspan=2, padx=10, pady=10, sticky=tk.NSEW)
        self.bou1.grid(row=0, column=0, padx=10, pady=10)
        self.bou2.grid(row=1, column=0, padx=10)
        self.bou3.grid(row=2, column=0, padx=10, pady=10)

    def recuperer_notes(self):
        longueur_max = 0
        for rectangle in self.grille.liste_rectangles:
            longueur_max = max(rectangle.note_encodage.position + rectangle.note_encodage.duree, longueur_max)
        partition = encodage.Partition(longueur_max)
        for rectangle in self.grille.liste_rectangles:
            partition.ajouter(rectangle.note_encodage)
        return partition

    def exporter_son(self):
        fichier = encodage.Fichier()
        fichier.convertir_notes(self.recuperer_notes())
        fichier.ecrire("test.wav")
        os.startfile("test.wav")

    def lancer(self):
        self.fen.mainloop()

palette = {"bg1":"#2B2B2B", "bg2":"#313335", "bg3":"#3C3F41", "fg1":"#A5A59D", "fg2":"#CCCCC2", "accent":"#05BFBD"}
note_names_fr = ["Do", "Do#", "Ré", "Ré#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"]
note_names_en = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
notes = []
for n in range(0, 120):
    octave = (n // 12) - 1
    name = note_names_en[n % 12] + str(octave) + " / " + note_names_fr[n % 12] + str(octave)
    freq = round(440 * 2 ** ((n - 69) / 12))
    notes.append((name, freq))
notes.reverse()