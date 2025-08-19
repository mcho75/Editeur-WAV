import math
import struct


class Fichier:

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
        with open(chemin, "rb") as f:
            data = f.read()
        self.riff = struct.unpack_from("I", data, 0)[0]
        self.file_type = struct.unpack_from("I", data, 8)[0]
        self.fmt = struct.unpack_from("I", data, 12)[0]
        self.length_fmt_data = struct.unpack_from("I", data, 16)[0]
        self.fmt_type = struct.unpack_from("H", data, 20)[0]
        self.sample_rate = struct.unpack_from("I", data, 24)[0]
        self.bits_per_sample = struct.unpack_from("H", data, 34)[0]
        self.data_header = struct.unpack_from("I", data, 36)[0]
        self.echantillons = []
        data_size = struct.unpack_from("I", data, 40)[0]
        for i in range(44, data_size, self.bits_per_sample // 8 * 2):
            self.echantillons.append([(struct.unpack_from("hh", data, i))[0], (struct.unpack_from("hh", data, i))[1]])
        # print(self.echantillons)

    def ecrire(self, chemin):
        data_size = len(self.echantillons) * 2 * self.bits_per_sample // 8 + 44
        with open(chemin, "wb") as f:
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
            for i in self.echantillons:
                f.write(struct.pack("hh", i[0], i[1]))

    def convertir_notes(self, partition):
        self.echantillons = [[0, 0] for i in range(partition.duree_totale*self.sample_rate//1000)]
        for note in partition.liste_notes:
            for k in range(note.position*self.sample_rate//1000, (note.position+note.duree)*self.sample_rate//1000):
                valeur = int(note.amplitude * math.sin(2 * math.pi * note.frequence * k / self.sample_rate))
                self.echantillons[k][0] += valeur
                self.echantillons[k][1] += valeur
        # print(self.echantillons)

    def interpolation(self):
        self.sample_rate *= 2
        n = len(self.echantillons)
        nouveau = []
        for i in range(0, n-1):
            nouveau.append(self.echantillons[i])
            nouveau.append([(self.echantillons[i][0] + self.echantillons[i+1][0]) // 2,
                            (self.echantillons[i][1] + self.echantillons[i+1][1]) // 2])
        nouveau.append(self.echantillons[-1])
        nouveau.append(self.echantillons[-1])
        self.echantillons = nouveau.copy()

    def echo(self, delai, facteur):
        for i in range(len(self.echantillons)-1, delai-1, -1):
            self.echantillons[i][0] += int(self.echantillons[i-delai][0] * facteur)
            self.echantillons[i][1] += int(self.echantillons[i-delai][1] * facteur)


class Note:

    def __init__(self, frequence, amplitude, duree, position):
        self.frequence = frequence
        self.amplitude = amplitude
        self.duree = duree
        self.position = position


class Partition:

    def __init__(self, duree_totale):
        self.duree_totale = duree_totale
        self.liste_notes = []

    def ajouter(self, note):
        self.liste_notes.append(note)