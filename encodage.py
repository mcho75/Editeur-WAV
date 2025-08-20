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
                f.write(struct.pack("hh", max(-32768, min(i[0], 32767)), max(-32768, min(i[0], 32767))))

    def convertir_notes(self, partition):
        self.echantillons = [[0, 0] for i in range(partition.duree_totale*self.sample_rate//1000)]
        for note in partition.liste_notes:
            i = 0
            for k in range(0, note.duree*self.sample_rate//1000):
                valeur = 0

                if note.instrument == 0:   # sinusoide
                    # facteur = 1.0
                    # attenuation = 1 / 20
                    # if i < self.sample_rate * attenuation:
                    #     facteur = i / (self.sample_rate * attenuation)
                    # if i >= note.duree * self.sample_rate // 1000 - self.sample_rate * attenuation:
                    #     facteur = (note.duree * self.sample_rate / 1000 - i) / (self.sample_rate * attenuation)
                    # valeur = int(facteur * note.amplitude * math.sin(2 * math.pi * note.frequence * k / self.sample_rate))
                    valeur = note.amplitude * math.sin(2 * math.pi * note.frequence * k / self.sample_rate)

                if note.instrument == 1:   # piano
                    valeur = 0.6 * math.sin(2 * math.pi * note.frequence * k / self.sample_rate) * math.exp(-0.0015 * 2 * math.pi * note.frequence * k / self.sample_rate)
                    valeur += 0.4 * math.sin(4 * math.pi * note.frequence * k / self.sample_rate) * math.exp(-0.0015 * 2 * math.pi * note.frequence * k / self.sample_rate)
                    valeur += valeur ** 3
                    valeur *= 1 + 16 * k / self.sample_rate * math.exp(-6 * k / self.sample_rate)
                    valeur *= note.amplitude

                if note.instrument == 2:   # xylophone
                    valeur = note.amplitude * math.sin(2 * math.pi * note.frequence * k / self.sample_rate)
                    valeur *= math.exp(-8 * k / self.sample_rate)

                if note.instrument == 3:   # triangle
                    for i in range(10):
                        valeur += (-1) ** i * math.sin(2 * math.pi * (2 * i - 1) * note.frequence * k / self.sample_rate) / (2 * i + 1) ** 2
                    valeur *= 8 / math.pi / math.pi * note.amplitude

                self.echantillons[k + note.position * self.sample_rate // 1000][0] += int(valeur)
                self.echantillons[k + note.position * self.sample_rate // 1000][1] += int(valeur)
                i += 1
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

    def __init__(self, frequence, amplitude, duree, position, instrument):
        self.frequence = frequence
        self.amplitude = amplitude
        self.duree = duree
        self.position = position
        self.instrument = instrument


class Partition:

    def __init__(self, duree_totale):
        self.duree_totale = duree_totale
        self.liste_notes = []

    def ajouter(self, note):
        self.liste_notes.append(note)