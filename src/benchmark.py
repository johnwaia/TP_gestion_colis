import random
import time

from catalogue import Catalogue
from chargement import preparer_camion
from generateur import generer
from tri import tri_fusion, tri_par_denombrement

TAILLES = [100, 1_000, 10_000, 100_000]
NB_RECHERCHES = 1_000


def chrono(f, *args, repetitions=1):
    meilleur = float("inf")
    for _ in range(repetitions):
        t = time.perf_counter()
        resultat = f(*args)
        meilleur = min(meilleur, time.perf_counter() - t)
    return meilleur, resultat


def ms(t):
    return f"{t * 1000:10.2f}"


def main():
    print("Temps en millisecondes (meilleur de plusieurs répétitions)\n")
    lignes = []
    for n in TAILLES:
        colis = generer(n, graine=n)
        rng = random.Random(0)
        ids = [rng.choice(colis).id for _ in range(NB_RECHERCHES)]
        rep = 3 if n <= 10_000 else 1

        def ajout():
            cat = Catalogue()
            for c in colis:
                cat.ajouter(c)
            return cat

        t_ajout, cat = chrono(ajout, repetitions=rep)
        t_hash, _ = chrono(lambda: [cat.rechercher(i) for i in ids], repetitions=rep)
        t_lin, _ = chrono(lambda: [cat.rechercher_lineaire(i) for i in ids], repetitions=1)
        t_fusion, _ = chrono(lambda: tri_fusion(colis, lambda c: c.poids), repetitions=rep)
        t_sorted, _ = chrono(lambda: sorted(colis, key=lambda c: c.poids), repetitions=rep)
        t_denomb, _ = chrono(lambda: tri_par_denombrement(colis, lambda c: c.priorite, 1, 5), repetitions=rep)
        t_dp, ch_dp = chrono(lambda: preparer_camion(colis, 1000, 1.0, "dp"))
        t_gl, ch_gl = chrono(lambda: preparer_camion(colis, 1000, 1.0, "glouton"))

        lignes.append((n, t_ajout, t_hash, t_lin, t_fusion, t_sorted, t_denomb, t_dp, t_gl,
                       ch_dp.nb_apres_reduction, ch_dp.score_total, ch_gl.score_total))

    print(f"{'n':>8} | {'ajout n':>10} | {'1000 rech.':>10} | {'1000 rech.':>10} | "
          f"{'tri fusion':>10} | {'sorted()':>10} | {'dénombr.':>10}")
    print(f"{'':>8} | {'(dict)':>10} | {'hash O(1)':>10} | {'lin. O(n)':>10} | "
          f"{'poids':>10} | {'Timsort':>10} | {'priorité':>10}")
    for l in lignes:
        print(f"{l[0]:>8} | {ms(l[1])} | {ms(l[2])} | {ms(l[3])} | {ms(l[4])} | {ms(l[5])} | {ms(l[6])}")

    print(f"\nChargement d'un camion de 1 000 kg (alpha = 1)")
    print(f"{'n':>8} | {'utiles':>7} | {'DP (ms)':>10} | {'glouton':>10} | "
          f"{'score DP':>10} | {'score glouton':>13} | écart")
    for l in lignes:
        ecart = 100 * (l[10] - l[11]) / l[10]
        print(f"{l[0]:>8} | {l[9]:>7} | {ms(l[7])} | {ms(l[8])} | {l[10]:>10.1f} | "
              f"{l[11]:>13.1f} | {ecart:.2f} %")

    print("\nInfluence de la capacité C sur la DP (n = 10 000)")
    colis = generer(10_000, graine=5)
    for cap in (100, 500, 1_000, 2_000):
        t, ch = chrono(lambda: preparer_camion(colis, cap, 1.0, "dp"))
        print(f"  C = {cap:>5} kg : {ms(t)} ms, {ch.nb_apres_reduction} colis utiles, "
              f"n_utiles × C = {ch.nb_apres_reduction * cap:,}")


if __name__ == "__main__":
    main()
