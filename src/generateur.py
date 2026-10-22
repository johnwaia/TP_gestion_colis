import csv
import random

from colis import Colis

VILLES = ["Paris", "Lille", "Lyon", "Marseille", "Bordeaux", "Nantes",
          "Toulouse", "Strasbourg", "Rennes", "Nice"]


def exemple_enonce():
    return [
        Colis(101, 8, 20, 2, "Paris"),
        Colis(102, 3, 10, 5, "Lille"),
        Colis(103, 12, 40, 1, "Lyon"),
        Colis(104, 5, 25, 4, "Paris"),
        Colis(105, 2, 15, 3, "Lille"),
    ]


def generer(n, id_depart=1000, poids_max=50, graine=None):
    rng = random.Random(graine)
    ids = list(range(id_depart, id_depart + n))
    rng.shuffle(ids)
    resultat = []
    for i in ids:
        poids = rng.randint(1, poids_max)
        valeur = round(poids * rng.uniform(1, 6) + rng.uniform(0, 20), 2)
        resultat.append(Colis(i, poids, valeur, rng.randint(1, 5), rng.choice(VILLES)))
    return resultat


def charger_csv(chemin):
    with open(chemin, newline="", encoding="utf-8") as f:
        lecteur = csv.reader(f, delimiter=";")
        next(lecteur, None)
        return [Colis(int(l[0]), int(l[1]), float(l[2]), int(l[3]), l[4])
            for l in lecteur if l]


def sauver_csv(colis, chemin):
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        ecrivain = csv.writer(f, delimiter=";")
        ecrivain.writerow(["id", "poids", "valeur", "priorite", "destination"])
        for c in colis:
            ecrivain.writerow([c.id, c.poids, c.valeur, c.priorite, c.destination])
