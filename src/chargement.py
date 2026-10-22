import time
from dataclasses import dataclass, field
from itertools import combinations

from colis import PRIORITE_MIN, PRIORITE_MAX
from tri import tri_fusion

LIMITE_OPERATIONS_DP = 30_000_000

def valeur_ponderee(colis, alpha):
    facteur = 1 + alpha * (colis.priorite - PRIORITE_MIN) / (PRIORITE_MAX - PRIORITE_MIN)
    return colis.valeur * facteur


@dataclass
class Chargement:
    colis: list
    capacite: int
    methode: str
    optimal: bool
    alpha: float = 0.0
    duree: float = 0.0
    nb_candidats: int = 0
    nb_apres_reduction: int = 0
    poids_total: int = field(init=False)
    valeur_totale: float = field(init=False)
    score_total: float = field(init=False)

    def __post_init__(self):
        self.poids_total = sum(c.poids for c in self.colis)
        self.valeur_totale = sum(c.valeur for c in self.colis)
        self.score_total = sum(valeur_ponderee(c, self.alpha) for c in self.colis)

def reduire_par_dominance(colis, capacite, valeur_de):
    candidats = [c for c in colis if c.poids <= capacite]
    par_valeur = tri_fusion(candidats, valeur_de, decroissant=True)
    deja_garde = {}
    gardes = []
    for c in par_valeur:
        k = deja_garde.get(c.poids, 0)
        if k < capacite // c.poids:
            deja_garde[c.poids] = k + 1
            gardes.append(c)
    return candidats, gardes

def sac_a_dos_dp(colis, capacite):
    capacite = min(capacite, sum(c.poids for c in colis))
    dp = [0.0] * (capacite + 1)
    decisions = []
    for c in colis:
        w, v = c.poids, c._v
        pris = bytearray(capacite + 1)
        for cap in range(capacite, w - 1, -1):
            alt = dp[cap - w] + v
            if alt > dp[cap]:
                dp[cap] = alt
                pris[cap] = 1
        decisions.append(pris)

    selection = []
    cap = capacite
    for i in range(len(colis) - 1, -1, -1):
        if decisions[i][cap]:
            selection.append(colis[i])
            cap -= colis[i].poids
    selection.reverse()
    return selection

def sac_a_dos_glouton(colis, capacite):
    ordre = tri_fusion(colis, lambda c: c._v / c.poids, decroissant=True)
    selection, poids = [], 0
    for c in ordre:
        if poids + c.poids <= capacite:
            selection.append(c)
            poids += c.poids
    if colis:
        meilleur_seul = max(colis, key=lambda c: c._v)
        if meilleur_seul._v > sum(c._v for c in selection):
            selection = [meilleur_seul]
    return selection

def sac_a_dos_force_brute(colis, capacite):
    meilleure, meilleure_valeur = [], 0.0
    for k in range(1, len(colis) + 1):
        for combi in combinations(colis, k):
            if sum(c.poids for c in combi) <= capacite:
                v = sum(c._v for c in combi)
                if v > meilleure_valeur:
                    meilleure, meilleure_valeur = list(combi), v
    return meilleure

class _Vue:
    __slots__ = ("colis", "poids", "_v")

    def __init__(self, colis, v):
        self.colis = colis
        self.poids = colis.poids
        self._v = v


def preparer_camion(colis, capacite, alpha=0.0, methode="auto"):
    if capacite <= 0:
        raise ValueError("La capacité doit être strictement positive.")
    debut = time.perf_counter()
    vues = [_Vue(c, valeur_ponderee(c, alpha)) for c in colis]

    candidats, utiles = reduire_par_dominance(vues, capacite, lambda x: x._v)

    if methode == "auto":
        methode = "dp" if len(utiles) * capacite <= LIMITE_OPERATIONS_DP else "glouton"

    if methode == "dp":
        selection, optimal = sac_a_dos_dp(utiles, capacite), True
    elif methode == "glouton":
        selection, optimal = sac_a_dos_glouton(utiles, capacite), False
    elif methode == "brute":
        if len(utiles) > 22:
            raise ValueError("Force brute limitée à 22 colis utiles.")
        selection, optimal = sac_a_dos_force_brute(utiles, capacite), True
    else:
        raise ValueError(f"Méthode inconnue : {methode}")

    return Chargement(
        colis=[v.colis for v in selection],
        capacite=capacite,
        methode=methode,
        optimal=optimal,
        alpha=alpha,
        duree=time.perf_counter() - debut,
        nb_candidats=len(candidats),
        nb_apres_reduction=len(utiles),
    )
