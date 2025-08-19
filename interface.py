import tkinter as tk
import encodage
import winsound


class Grille(tk.Canvas):

    def __init__(self, boss):
        self.longueur_totale = 100
        self.liste_rectangles = []

        tk.Canvas.__init__(self, boss, width=800, height=500, bg=palette["bg1"], highlightthickness=0,
                           scrollregion=(0, 0, 5000, 1000))

        self.bind("<MouseWheel>", self.scroll_vertical)
        self.bind("<Shift-MouseWheel>", self.scroll_horizontal)
        self.bind("<B1-ButtonRelease>", self.ajouter_note)

        self.bordure = 50
        self.intitules = 100
        self.longueur_sec = 50
        self.hauteur = 20

        self.tracer_lignes()

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
            self.create_text(self.bordure+self.intitules-10, self.bordure+self.hauteur*i+self.hauteur//2, text=notes[i][0], anchor=tk.E, fill=palette["fg"])

    def ajouter_note(self, event):
        position = (round(self.canvasx(event.x)) - self.intitules - self.bordure) * 4 // self.longueur_sec
        note = (round(self.canvasy(event.y)) - self.bordure) // self.hauteur
        if (0 <= position < self.longueur_totale * 4) and (0 <= note < len(notes)):
            print(position, notes[note][0])
            self.liste_rectangles.append(RectangleNote(self, note, position))  # TODO : prendre en compte duree=0.25


class RectangleNote:

    def __init__(self, boss, numero_note, position):
        self.boss = boss
        self.numero_note = numero_note
        self.note_encodage = encodage.Note(notes[self.numero_note][1], 1000, 1, position)
        pos_x = self.boss.bordure+self.boss.intitules+(self.note_encodage.position*self.boss.longueur_sec//4)
        pos_y = self.boss.bordure+self.numero_note*self.boss.hauteur
        self.sprite = self.boss.create_rectangle(pos_x, pos_y, pos_x+(self.boss.longueur_sec//4), pos_y+self.boss.hauteur,
                                                 width=0, fill=palette["accent"])
        if notes[self.numero_note][1] >= 37:
            winsound.Beep(notes[self.numero_note][1], 250)

    def actualiser(self, note, duree, position):
        pass


class Interface:

    def __init__(self):

        self.fen = tk.Tk()
        self.fen.resizable(False, False)
        self.grille = Grille(self.fen)
        self.scrollbarx = tk.Scrollbar(self.fen, orient=tk.HORIZONTAL, command=self.grille.xview, bd=1)
        self.scrollbary = tk.Scrollbar(self.fen, orient=tk.VERTICAL, command=self.grille.yview, bd=1)
        self.grille.configure(xscrollcommand=self.scrollbarx.set, yscrollcommand=self.scrollbary.set)

        self.grille.grid(row=0, column=0)
        self.scrollbarx.grid(row=1, column=0, sticky=tk.EW)
        self.scrollbary.grid(row=0, column=1, sticky=tk.NS)

    def recuperer_notes(self):
        partition = encodage.Partition(100)
        for rectangle in self.grille.liste_rectangles:
            partition.ajouter(rectangle.encodage_note)

    def lancer(self):
        self.fen.mainloop()

palette = {"bg1":"#2B2B2B", "bg2":"#313335", "bg3":"#3C3F41", "fg":"#A5A59D", "accent":"#05BFBD"}
note_names = ["Do", "Do#", "Ré", "Ré#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"]
notes = []
for n in range(0, 120):
    octave = (n // 12) - 1
    name = note_names[n % 12] + str(octave)
    freq = round(440 * 2 ** ((n - 69) / 12))
    notes.append((name, freq))
notes.reverse()