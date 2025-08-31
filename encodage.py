import math
import struct
import random
import librosa
import numpy as np


class FichierWAV:
    """ Outil de lecture et ecriture d'un fichier .wav. """

    def __init__(self):
        self.riff = 1179011410
        self.file_type = 1163280727
        self.fmt = 544501094
        self.length_fmt_data = 16
        self.fmt_type = 1
        self.sample_rate = 44100
        self.bits_per_sample = 16
        self.data_header = 1635017060
        self.echantillons = []

    def ouvrir(self, chemin):
        """ Ouverture d'un fichier .wav dont le chemin est passe en entree. """

        # lecture du fichier .wav
        with open(chemin, "rb") as f:
            data = f.read()

        # recuperation des informations du header
        self.riff = struct.unpack_from("I", data, 0)[0]
        self.file_type = struct.unpack_from("I", data, 8)[0]
        self.fmt = struct.unpack_from("I", data, 12)[0]
        self.length_fmt_data = struct.unpack_from("I", data, 16)[0]
        self.fmt_type = struct.unpack_from("H", data, 20)[0]
        self.sample_rate = struct.unpack_from("I", data, 24)[0]
        self.bits_per_sample = struct.unpack_from("H", data, 34)[0]

        # lecture des echantillons
        self.echantillons = []
        for k in range(0, 71):
            self.data_header = struct.unpack_from("I", data, k)[0]
            if self.data_header == 1635017060:    # cas particulier des samples recuperes
                data_size = struct.unpack_from("I", data, k+4)[0]
                for i in range(k + 8, data_size, self.bits_per_sample // 8 * 2):
                    self.echantillons.append([(struct.unpack_from("hh", data, i))[0], (struct.unpack_from("hh", data, i))[1]])

    def ecrire(self, chemin):
        """ Ecriture d'un fichier .wav dans le chemin passe en entree. """

        data_size = len(self.echantillons) * 2 * self.bits_per_sample // 8 + 44
        with open(chemin, "wb") as f:

            # ecriture du header
            header = struct.pack("I", self.riff)
            header += struct.pack("I", data_size + 36)
            header += struct.pack("I", self.file_type)
            header += struct.pack("I", self.fmt)
            header += struct.pack("I", self.length_fmt_data)
            header += struct.pack("H", self.fmt_type)
            header += struct.pack("H", 2)
            header += struct.pack("I", self.sample_rate)
            header += struct.pack("I", self.sample_rate * self.bits_per_sample * 2 // 8)
            header += struct.pack("H", self.bits_per_sample * 2 // 8)
            header += struct.pack("H", self.bits_per_sample)
            header += struct.pack("I", self.data_header)
            header += struct.pack("I", data_size)
            f.write(header)

            # ecriture des echantillons en evitant la saturation
            for i in self.echantillons:
                f.write(struct.pack("hh", max(-32768, min(i[0], 32767)), max(-32768, min(i[0], 32767))))

    def convertir_notes(self, partition, samples, notes_associees):
        """ Conversion d'une partition en signal numerique. """

        self.echantillons = [[0, 0] for i in range(partition.duree_totale * 60 * 250 // partition.bpm * self.sample_rate // 1000)]
        sample_shift = np.array([])
        for note in partition.liste_notes:
            offset = random.randint(0, self.sample_rate // note.frequence)

            # si la note provient des samples, on utilise librosa
            if note.instrument < 0:
                steps = 12 * math.log(note.frequence / notes_associees[-note.instrument-1], 2)
                tableau = np.array(samples[-note.instrument-1]).astype("float32")
                stereo = np.array([tableau[:, 0], tableau[:, 1]])
                sample_shift = (librosa.effects.pitch_shift(stereo / 32767, sr=self.sample_rate, n_steps=steps) * 32767).astype(int)

            # on itere sur tous les echantillons concernes par la note
            for k in range(0, note.duree * 60 * 250 // partition.bpm * self.sample_rate // 1000):
                valeur = 0

                # samples
                if note.instrument < 0:
                    if k < len(sample_shift[0]):
                        valeur = sample_shift[0][k]
                    if note.duree * 60 * 250 // partition.bpm * self.sample_rate // 1000 < len(sample_shift[0]):
                        if k >= note.duree * 60 * 250 // partition.bpm * self.sample_rate / 1000 - self.sample_rate / 20:
                            valeur *= (note.duree * 60 * 250 // partition.bpm * self.sample_rate / 1000 - k) * 20 / self.sample_rate
                    else:
                        if k >= len(sample_shift[0]) - self.sample_rate / 20:
                            valeur *= (len(sample_shift[0]) - k) * 20 / self.sample_rate

                # sinusoide
                if note.instrument == 0:
                    valeur = note.amplitude * math.sin(2 * math.pi * note.frequence * (k / self.sample_rate + offset))

                # piano
                if note.instrument == 1:
                    valeur = 0.6 * math.sin(2 * math.pi * note.frequence * (k / self.sample_rate + offset)) * math.exp(-0.0015 * 2 * math.pi * note.frequence * k / self.sample_rate)
                    valeur += 0.4 * math.sin(4 * math.pi * note.frequence * (k / self.sample_rate + offset)) * math.exp(-0.0015 * 2 * math.pi * note.frequence * k / self.sample_rate)
                    valeur += valeur ** 3
                    valeur *= 1 + 16 * k / self.sample_rate * math.exp(-6 * k / self.sample_rate)
                    valeur *= note.amplitude
                    if k >= note.duree * 60 * 250 // partition.bpm * self.sample_rate // 1000 - self.sample_rate / 20:
                        valeur *= (note.duree * 60 * 250 // partition.bpm * self.sample_rate / 1000 - k) / (self.sample_rate / 20)

                # xylophone
                if note.instrument == 2:
                    valeur = note.amplitude * math.sin(2 * math.pi * note.frequence * (k / self.sample_rate + offset))
                    valeur *= math.exp(-8 * k / self.sample_rate)

                # triangle
                if note.instrument == 3:
                    for j in range(10):
                        valeur += (-1) ** j * math.sin(2 * math.pi * (2 * j - 1) * note.frequence * (k / self.sample_rate + offset)) / (2 * j + 1) ** 2
                    valeur *= 8 / math.pi / math.pi * note.amplitude

                # ocarina
                if note.instrument == 4:
                    valeur = note.amplitude * math.sin(2 * math.pi * note.frequence * (k / self.sample_rate + offset))
                    attenuation = 1 / 20
                    if k < self.sample_rate * attenuation:
                        valeur *= k / (self.sample_rate * attenuation)
                    if k >= note.duree * 60 * 250 // partition.bpm * self.sample_rate // 1000 - self.sample_rate * attenuation:
                        valeur *= (note.duree * 60 * 250 // partition.bpm * self.sample_rate / 1000 - k) / (self.sample_rate * attenuation)
                    valeur *= math.exp(-k / self.sample_rate)

                self.echantillons[k + note.position * 60 * 250 // partition.bpm * self.sample_rate // 1000][0] += int(valeur)
                self.echantillons[k + note.position * 60 * 250 // partition.bpm * self.sample_rate // 1000][1] += int(valeur)


class Note:
    """ Note definie par sa frequence, son instrument associe et sa position temporelle. """

    def __init__(self, frequence, numero_note, amplitude, duree, position, instrument):
        self.frequence = frequence
        self.amplitude = amplitude
        self.duree = duree
        self.position = position
        self.instrument = instrument
        self.numero_note = numero_note


class Partition:
    """ Ensemble de notes. """

    def __init__(self, duree_totale, bpm):
        self.duree_totale = duree_totale
        self.bpm = bpm
        self.liste_notes = []

    def ajouter(self, note):
        """ Ajout d'une note a la partition. """
        self.liste_notes.append(note)

    def ouvrir(self, chemin):
        """ Lecture d'une partition stockee dans le fichier .txt dont le chemin est passe en entree. """
        with open(chemin, "r") as f:
            lignes = f.readlines()
        self.bpm = int(lignes[0])
        for ligne in lignes[1:]:
            frequence, numero_note, amplitude, duree, position, instrument = [int(i) for i in ligne.split(" ")]
            self.duree_totale = max(self.duree_totale, position+duree)
            self.ajouter(Note(frequence, numero_note, amplitude, duree, position, instrument))

    def sauvegarder(self, chemin):
        """ Enregistrement de la partition a l'emplacement passe en entree. """
        with open(chemin, "w") as f:
            f.write("{}\n".format(self.bpm))
            for note in self.liste_notes:
                f.write("{} {} {} {} {} {}\n".format(note.frequence, note.numero_note, note.amplitude, note.duree, note.position, note.instrument))


def recuperer_samples(liste_samples):
    """ Recuperation des donneees des samples du repertoire samples. """
    fichier = FichierWAV()
    resultat = []
    for sample in liste_samples:
        fichier.ouvrir("samples/"+sample+".wav")
        resultat.append(fichier.echantillons)
    return resultat