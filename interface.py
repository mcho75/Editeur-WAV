import tkinter as tk
from tkinter import ttk, filedialog
import encodage
import winsound
import os


class Grille(tk.Canvas):
    """ Interface graphique contenant les differentes notes. """

    def __init__(self, boss):

        # initialisation des variables locales
        self.boss = boss
        self.longueur_totale = 400
        self.liste_rectangles = []
        self.rectangle_survole = None
        self.dragging = 0
        self.instrument_var = tk.IntVar()
        self.bpm = 60

        # initialisation des parametres graphiques
        self.bordure = 20
        self.intitules = 100
        self.longueur_temps = 15
        self.hauteur = 20

        # creation du canvas
        tk.Canvas.__init__(self, boss.fen, width=800, height=500, bg=palette["bg1"], highlightthickness=0,
                           scrollregion=(0, 0, 5000, 1000))
        self.surbrillance = self.create_rectangle(0, 0, 0, 0, fill=palette["bg2"])

        # ajout des interactions de la souris
        self.bind("<MouseWheel>", self.scroll_vertical)            # scrolling vertical
        self.bind("<Shift-MouseWheel>", self.scroll_horizontal)    # scrolling horizontal
        self.bind("<B1-ButtonRelease>", self.ajouter_note)         # ajout d'une note apres un clic
        self.bind("<Motion>", self.deplacement_souris)             # deplacement de la souris relachee
        self.bind("<B1-Motion>", self.deplacement_clic)            # deplacement des bordures d'une note

        self.tracer_lignes()

    def deplacement_souris(self, event):
        """ Deplacement de la souris sur la grille (relachee). """

        position = (round(self.canvasx(event.x)) - self.intitules - self.bordure) / self.longueur_temps
        note = (round(self.canvasy(event.y)) - self.bordure) // self.hauteur

        # deplacement du cadre de surbrillance sur la ligne du pointeur
        if (0 <= position < self.longueur_totale) and (0 <= note < len(notes)):
            pos_y = self.bordure + note * self.hauteur
            self.coords(self.surbrillance, self.bordure, pos_y, self.longueur_totale * self.longueur_temps + self.bordure + self.intitules, pos_y+self.hauteur)

        # detection de la case sur laquelle se trouve la souris
        self.config(cursor="arrow")
        self.rectangle_survole = None
        for rectangle in self.liste_rectangles:
            # pour chaque rectangle, on verifie si la souris est dessus
            if rectangle.note_encodage.position <= position < rectangle.note_encodage.position + rectangle.note_encodage.duree:
                if rectangle.note_encodage.numero_note == note:
                    self.config(cursor="hand1")                    # on est sur une note
                    self.rectangle_survole = rectangle
                    if position - (self.rectangle_survole.note_encodage.position + self.rectangle_survole.note_encodage.duree) > -0.3:
                        self.config(cursor="sb_h_double_arrow")    # on est sur la gauche d'une note
                    if position - rectangle.note_encodage.position < 0.3:
                        self.config(cursor="sb_h_double_arrow")    # on est sur la droite d'une note

    def deplacement_clic(self, event):
        """ Deplacement de la souris sur la grille (cliquee). """

        position = (round(self.canvasx(event.x)) - self.intitules - self.bordure) / self.longueur_temps

        if self.rectangle_survole is not None:
            if self.dragging == 0:       # on n'a pas encore commence a deplacer les bordures
                if position - (self.rectangle_survole.note_encodage.position + self.rectangle_survole.note_encodage.duree) > -0.3:
                    self.dragging = 1
                elif position - self.rectangle_survole.note_encodage.position < 0.3:
                    self.dragging = 2
            elif self.dragging == 1:     # on deplace la bordure droite
                self.rectangle_survole.note_encodage.duree = round(position) - self.rectangle_survole.note_encodage.position
                self.rectangle_survole.actualiser()
            elif self.dragging == 2:     # on deplace la bordure gauche
                self.rectangle_survole.note_encodage.duree += self.rectangle_survole.note_encodage.position - round(position)
                self.rectangle_survole.note_encodage.position = round(position)
                self.rectangle_survole.actualiser()

    def scroll_horizontal(self, event):
        """ Scroll horizontal de la grille. """
        self.xview_scroll(-event.delta//50, tk.UNITS)

    def scroll_vertical(self, event):
        """ Scroll vertical de la grille. """
        self.yview_scroll(-event.delta//50, tk.UNITS)

    def tracer_lignes(self):
        """ Ajout des lignes de la grille. """

        self.configure(scrollregion=(0, 0, (self.longueur_temps*self.longueur_totale)+self.intitules+(2*self.bordure), self.hauteur*len(notes)+(2*self.bordure)))
        self.create_line(self.bordure, self.bordure, self.bordure, self.hauteur*len(notes)+self.bordure, fill=palette["bg3"])

        # ajout des lignes verticales
        for i in range(0, self.longueur_totale + 1):
            pos_x = i * self.longueur_temps + self.bordure + self.intitules
            self.create_line(pos_x, self.bordure, pos_x, self.hauteur*len(notes)+self.bordure, fill=[palette["bg2"], palette["bg3"]][i % 4 == 0])

        # ajout des lignes horizontales
        for i in range(0, len(notes) + 1):
            pos_y = i * self.hauteur + self.bordure
            self.create_line(self.bordure, pos_y, self.longueur_totale*self.longueur_temps+self.intitules+self.bordure, pos_y, fill=palette["bg3"])

        # ajout du nom des notes
        for i in range(len(notes)):
            self.create_text(self.bordure+self.intitules-10, self.bordure+self.hauteur*i+self.hauteur//2, text=notes[i][0], anchor=tk.E, fill=palette["fg1"])

    def ajouter_note(self, event):
        """ Si possible, ajout ou suppression d'une note a l'emplacement du pointeur. """

        position = (round(self.canvasx(event.x)) - self.intitules - self.bordure) / self.longueur_temps
        note = (round(self.canvasy(event.y)) - self.bordure) // self.hauteur

        if self.dragging == 0:

            # suppression d'une note
            if self.rectangle_survole is not None:
                self.delete(self.rectangle_survole.sprite)
                self.liste_rectangles.remove(self.rectangle_survole)
                self.rectangle_survole = None

            # ajout d'une note
            elif (0 <= position < self.longueur_totale * 4) and (0 <= note < len(notes)):
                print(position, notes[note][0])
                self.liste_rectangles.append(RectangleNote(self, note, int(position), 1, self.instrument_var.get()))
                self.rectangle_survole = self.liste_rectangles[-1]
                winsound.Beep(notes[note][1], 60 * 250 // self.bpm)

        self.dragging = 0

    def importer_partition(self, partition):
        """ Importation d'une partition fournie en argument. """
        self.bpm = partition.bpm
        self.boss.tempo.set(self.bpm)
        while len(self.liste_rectangles) > 0:
            self.delete(self.liste_rectangles[0].sprite)
            self.liste_rectangles.pop(0)
        for note in partition.liste_notes:
            self.liste_rectangles.append(RectangleNote(self, note.numero_note, note.position, note.duree, note.instrument))

    def recuperer_notes(self):
        """ Retourne la partition associee aux notes placees dans la grille. """
        longueur_max = 0
        for rectangle in self.liste_rectangles:
            longueur_max = max(rectangle.note_encodage.position + rectangle.note_encodage.duree, longueur_max)
        partition = encodage.Partition(longueur_max, self.bpm)
        for rectangle in self.liste_rectangles:
            partition.ajouter(rectangle.note_encodage)
        return partition


class RectangleNote:
    """ Rectangle de la grille associe a une unique note. """

    def __init__(self, boss, numero_note, position, duree, instrument):
        self.boss = boss
        self.note_encodage = encodage.Note(notes[numero_note][1], numero_note, 5000, duree, round(position), instrument)
        self.sprite = self.boss.create_rectangle(0, 0, 0, 0, width=1, outline=palette["bg1"], fill=palette["instrument"+str(instrument)])
        self.actualiser()

    def actualiser(self):
        """ Modification de la position du rectangle selon les parametres de la note associee. """
        pos_x = self.boss.bordure + self.boss.intitules + (self.note_encodage.position * self.boss.longueur_temps)
        pos_y = self.boss.bordure + self.note_encodage.numero_note * self.boss.hauteur
        self.boss.coords(self.sprite, pos_x, pos_y, pos_x+(self.boss.longueur_temps*self.note_encodage.duree), pos_y+self.boss.hauteur)


class Interface:
    """ Fenetre contenant la grille et les parametres. """

    def __init__(self):

        # configuration de la fenetre
        self.fen = tk.Tk()
        self.fen.config(bg=palette["bg2"])
        self.fen.title("Editeur WAV")
        self.fen.resizable(False, False)

        # configuration du style des differents widgets
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TScrollbar", troughcolor=palette["bg2"], background=palette["fg1"], arrowcolor=palette["bg1"], bordercolor=palette["bg3"])
        style.configure("TButton", background=palette["fg1"], foreground=palette["bg1"], relief=tk.FLAT, width=20)
        style.configure("TRadiobutton", background=palette["bg2"], foreground=palette["fg1"], relief=tk.FLAT, width=20)
        style.configure("TScale", background=palette["fg1"], troughcolor=palette["bg2"], relief=tk.FLAT, width=20)
        style.map("TScrollbar", background=[("active", palette["fg2"])])
        style.map("TButton", background=[("active", palette["fg2"])])
        style.map("TRadiobutton", background=[("active", palette["bg2"])])
        style.map("TScale", background=[("active", palette["fg2"])])

        # creation des widgets
        self.grille = Grille(self)
        self.scrollbarx = ttk.Scrollbar(self.fen, orient=tk.HORIZONTAL, command=self.grille.xview, style="TScrollbar")
        self.scrollbary = ttk.Scrollbar(self.fen, orient=tk.VERTICAL, command=self.grille.yview, style="TScrollbar")
        self.grille.configure(xscrollcommand=self.scrollbarx.set, yscrollcommand=self.scrollbary.set)
        self.frame = tk.Frame(self.fen, bg=palette["bg1"])
        self.bou1 = ttk.Button(self.frame, text="Exporter", command=self.exporter_son, style="TButton")
        self.bou2 = ttk.Button(self.frame, text="Enregistrer", command=self.sauvegarder_fichier, style="TButton")
        self.bou3 = ttk.Button(self.frame, text="Ouvrir", command=self.ouvrir_fichier, style="TButton")
        self.tempo = ttk.Scale(self.frame, from_=60, to=240, orient="horizontal", command=self.changer_tempo, style="TScale")
        self.instruments = tk.Frame(self.frame, bg=palette["bg2"])
        self.titre_synthe = tk.Label(self.instruments, text="Synthé", bg=palette["bg2"], fg=palette["fg2"], anchor=tk.CENTER)
        self.titre_sample = tk.Label(self.instruments, text="Samples", bg=palette["bg2"], fg=palette["fg2"], anchor=tk.CENTER)
        for i in range(len(instruments)):
            ttk.Radiobutton(self.instruments, text=instruments[i], variable=self.grille.instrument_var, value=i,
                            style="TRadiobutton").grid(row=i+1, column=0, padx=10)
        for i in range(len(samples)):
            ttk.Radiobutton(self.instruments, text=samples_noms[i], variable=self.grille.instrument_var, value=-1-i,
                            style="TRadiobutton").grid(row=len(instruments)+2+i, column=0, padx=10)

        # placement des widgets dans la fenetre
        self.grille.grid(row=0, column=0, padx=(10, 0), pady=(10, 0))
        self.scrollbarx.grid(row=1, column=0, padx=10, pady=(0, 10), sticky=tk.EW)
        self.scrollbary.grid(row=0, column=1, pady=10, sticky=tk.NS)
        self.frame.grid(row=0, column=2, rowspan=2, padx=10, pady=10, sticky=tk.NSEW)
        self.bou1.grid(row=0, column=0, padx=10, pady=10)
        self.bou2.grid(row=1, column=0, padx=10)
        self.bou3.grid(row=2, column=0, padx=10, pady=10)
        self.tempo.grid(row=3, column=0, padx=10, pady=10, sticky=tk.EW)
        self.instruments.grid(row=4, column=0, padx=10, pady=10)
        self.titre_synthe.grid(row=0, column=0, padx=10, pady=10)
        self.titre_sample.grid(row=len(instruments)+1, column=0, padx=10, pady=10)

        self.tempo.set(60)

    def changer_tempo(self, event):
        """ Changement du tempo via le slider. """
        self.grille.bpm = int(self.tempo.get() / 10) * 10
        print(self.grille.bpm)

    def ouvrir_fichier(self):
        """ Ouverture d'un fichier .txt via une boite de dialogue. """
        chemin = filedialog.askopenfilename(title="Ouvrir", filetypes=[("Fichier texte", "*.txt"), ("Tous les fichiers", "*.*")])
        partition = encodage.Partition(0, 60)
        partition.ouvrir(chemin)
        self.grille.importer_partition(partition)

    def sauvegarder_fichier(self):
        """ Enregistrement d'un fichier via une boite de dialogue. """
        chemin = filedialog.asksaveasfilename(title="Enregistrer", filetypes=[("Fichier texte", "*.txt"), ("Tous les fichiers", "*.*")],
                                              defaultextension=".txt")
        partition = self.grille.recuperer_notes()
        partition.sauvegarder(chemin)

    def exporter_son(self):
        """ Exportation du son via une boite de dialogue. """
        chemin = filedialog.asksaveasfilename(title="Exporter", filetypes=[("Fichier .wav", "*.wav"), ("Tous les fichiers", "*.*")],
                                              defaultextension=".wav")
        self.changer_tempo(None)
        fichier = encodage.FichierWAV()
        fichier.convertir_notes(self.grille.recuperer_notes(), samples, notes_associees)
        fichier.ecrire(chemin)
        os.startfile(chemin)

    def lancer(self):
        """ Lancement de l'interface graphique. """
        self.fen.mainloop()


# variables globales du projet
palette = {"bg1":"#2B2B2B", "bg2":"#313335", "bg3":"#3C3F41", "fg1":"#A5A59D", "fg2":"#CCCCC2",
           "instrument-1":"#001219", "instrument-2":"#005f73", "instrument-3":"#0a9396", "instrument-4":"#94d2bd",
           "instrument-5":"#e9d8a6", "instrument-6":"#ee9b00", "instrument-7":"#ca6702", "instrument-8":"#bb3e03",
           "instrument-9":"#ae2012", "instrument-10":"#9b2226",
           "instrument0":"#F94144", "instrument1":"#F3722C", "instrument2":"#F8961E", "instrument3":"#F9844A",
           "instrument4":"#F9C74F", "instrument5":"#90BE6D", "instrument6":"#43AA8B", "instrument7":"#4D908E",
           "instrument8":"#577590", "instrument9":"#277DA1"}
instruments = ["Sinusoide", "Piano", "Xylophone", "Triangle", "Ocarina"]
samples_str = ["basse", "choeur", "clap", "guitare", "piano", "tambour", "violon"]
samples_noms = ["Basse", "Chœur", "Clap", "Guitare", "Piano", "Tambour", "Violon"]
notes_associees = [246, 526, 819, 518, 527, 160, 785]
samples = encodage.recuperer_samples(samples_str)

# calcul des frequences avec le nom associe
note_names_fr = ["Do", "Do#", "Ré", "Ré#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"]
note_names_en = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
notes = []
for n in range(0, 120):
    octave = (n // 12) - 1
    name = note_names_en[n % 12] + str(octave) + " / " + note_names_fr[n % 12] + str(octave)
    frequence = round(440 * 2 ** ((n - 69) / 12))
    notes.append((name, frequence))
notes.reverse()