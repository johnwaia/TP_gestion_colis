from colis import Colis, PRIORITE_MIN, PRIORITE_MAX
from tri import tri_fusion, tri_par_denombrement


class Catalogue:
    CRITERES = ("poids", "valeur", "priorite")

    def __init__(self):
        self._par_id = {}
        self._cache = {}

    def __len__(self):
        return len(self._par_id)

    def __iter__(self):
        return iter(self._par_id.values())

    def ajouter(self, colis: Colis):
        if colis.id in self._par_id:
            raise KeyError(f"Un colis avec l'identifiant {colis.id} existe déjà.")
        self._par_id[colis.id] = colis
        self._cache.clear()

    def supprimer(self, id_colis):
        colis = self._par_id.pop(id_colis)
        self._cache.clear()
        return colis

    def rechercher(self, id_colis):
        return self._par_id.get(id_colis)

    def rechercher_lineaire(self, id_colis):
        for c in self._par_id.values():
            if c.id == id_colis:
                return c
        return None

    def prochain_id(self):
        return max(self._par_id, default=100) + 1

    def trie_par(self, critere, decroissant=False):
        if critere not in self.CRITERES:
            raise ValueError(f"Critère inconnu : {critere}")
        cle_cache = (critere, decroissant)
        if cle_cache not in self._cache:
            colis = list(self._par_id.values())
            if critere == "priorite":
                vue = tri_par_denombrement(colis, lambda c: c.priorite,
                                           PRIORITE_MIN, PRIORITE_MAX, decroissant)
            elif critere == "poids":
                vue = tri_fusion(colis, lambda c: c.poids, decroissant)
            else:
                vue = tri_fusion(colis, lambda c: c.valeur, decroissant)
            self._cache[cle_cache] = vue
        return self._cache[cle_cache]

    def statistiques(self):
        n = len(self)
        if n == 0:
            return None
        poids_total = 0
        valeur_totale = 0.0
        par_priorite = [0] * (PRIORITE_MAX + 1)
        par_destination = {}
        for c in self._par_id.values():
            poids_total += c.poids
            valeur_totale += c.valeur
            par_priorite[c.priorite] += 1
            par_destination[c.destination] = par_destination.get(c.destination, 0) + 1
        return {
            "nombre": n,
            "poids_total": poids_total,
            "valeur_totale": valeur_totale,
            "poids_moyen": poids_total / n,
            "valeur_moyenne": valeur_totale / n,
            "par_priorite": {p: par_priorite[p] for p in range(PRIORITE_MIN, PRIORITE_MAX + 1)},
            "par_destination": par_destination,
        }
