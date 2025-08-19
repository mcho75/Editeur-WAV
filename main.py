import encodage
import interface
import os


if __name__ == "__main__":
    fichier = encodage.Fichier()
    partition = encodage.Partition(5000)
    partition.ajouter(encodage.Note(440, 10000, 2000, 1000))
    fichier.convertir_notes(partition)
    # fichier.ecrire("resultat.wav")
    # os.startfile("resultat.wav")
    i = interface.Interface()
    i.lancer()