import random
import unittest

from catalogue import Catalogue
from chargement import preparer_camion, valeur_ponderee
from colis import Colis
from generateur import generer, exemple_enonce
from tri import tri_fusion, tri_par_denombrement


class TestTri(unittest.TestCase):
    def test_tri_fusion_aleatoire(self):
        rng = random.Random(1)
        for n in (0, 1, 2, 7, 100, 1001):
            data = [rng.randint(-50, 50) for _ in range(n)]
            self.assertEqual(tri_fusion(data, lambda x: x), sorted(data))
            self.assertEqual(tri_fusion(data, lambda x: x, True), sorted(data, reverse=True))

    def test_stabilite(self):
        data = [(rng_k, i) for i, rng_k in enumerate([3, 1, 3, 2, 1, 3])]
        self.assertEqual(tri_fusion(data, lambda x: x[0]), sorted(data, key=lambda x: x[0]))
        self.assertEqual(tri_fusion(data, lambda x: x[0], True),
                         sorted(data, key=lambda x: x[0], reverse=True))
        self.assertEqual(tri_par_denombrement(data, lambda x: x[0], 1, 3),
                         sorted(data, key=lambda x: x[0]))


class TestCatalogue(unittest.TestCase):
    def setUp(self):
        self.cat = Catalogue()
        for c in generer(500, graine=3):
            self.cat.ajouter(c)

    def test_recherche(self):
        for c in list(self.cat)[:50]:
            self.assertIs(self.cat.rechercher(c.id), c)
            self.assertIs(self.cat.rechercher_lineaire(c.id), c)
        self.assertIsNone(self.cat.rechercher(-1))

    def test_doublon(self):
        c = next(iter(self.cat))
        with self.assertRaises(KeyError):
            self.cat.ajouter(Colis(c.id, 1, 1, 1, "X"))

    def test_tris_et_cache(self):
        for crit in Catalogue.CRITERES:
            vue = self.cat.trie_par(crit)
            cles = [getattr(c, crit) for c in vue]
            self.assertEqual(cles, sorted(cles))
            self.assertEqual(len(vue), len(self.cat))
        avant = self.cat.trie_par("poids")
        self.cat.ajouter(Colis(1, 1, 1, 1, "X"))
        self.assertEqual(len(self.cat.trie_par("poids")), len(avant) + 1)

    def test_validation(self):
        with self.assertRaises(ValueError):
            Colis(1, 0, 1, 1, "X")
        with self.assertRaises(ValueError):
            Colis(1, 1, 1, 9, "X")


class TestChargement(unittest.TestCase):
    def test_exemple_enonce_partie2(self):
        colis = [Colis(1, 8, 20, 1, "A"), Colis(2, 6, 25, 1, "B"),
                 Colis(3, 5, 18, 1, "C"), Colis(4, 4, 14, 1, "D")]
        ch = preparer_camion(colis, 15, methode="dp")
        self.assertEqual(ch.valeur_totale, 57)  # B + C + D
        self.assertLessEqual(ch.poids_total, 15)

    def test_dp_egal_force_brute(self):
        rng = random.Random(42)
        for essai in range(150):
            n = rng.randint(1, 13)
            colis = generer(n, poids_max=rng.randint(2, 30), graine=essai)
            cap = rng.randint(1, 80)
            alpha = rng.choice([0, 0.5, 1, 3])
            dp = preparer_camion(colis, cap, alpha, "dp")
            brute = preparer_camion(colis, cap, alpha, "brute")
            self.assertLessEqual(dp.poids_total, cap)
            self.assertAlmostEqual(dp.score_total, brute.score_total, places=6)

    def test_glouton_valide_mais_pas_toujours_optimal(self):
        rng = random.Random(7)
        sous_optimal = 0
        for essai in range(100):
            colis = generer(12, poids_max=20, graine=1000 + essai)
            cap = rng.randint(10, 60)
            g = preparer_camion(colis, cap, 0, "glouton")
            d = preparer_camion(colis, cap, 0, "dp")
            self.assertLessEqual(g.poids_total, cap)
            self.assertLessEqual(g.valeur_totale, d.valeur_totale + 1e-9)
            self.assertGreaterEqual(g.valeur_totale, d.valeur_totale / 2 - 1e-9)
            sous_optimal += g.valeur_totale < d.valeur_totale - 1e-9
        self.assertGreater(sous_optimal, 0)

    def test_reduction_ne_change_pas_l_optimum(self):
        # beaucoup de colis de même poids : la réduction élimine, l'optimum reste exact
        colis = [Colis(i, 1 + i % 4, (i * 37) % 23 + 1, 1, "X") for i in range(60)]
        dp = preparer_camion(colis, 9, 0, "dp")
        self.assertLess(dp.nb_apres_reduction, dp.nb_candidats)
        # 9 colis de poids 1 tiennent : l'optimum vaut au moins les 9 meilleurs de poids 1
        poids1 = sorted((c.valeur for c in colis if c.poids == 1), reverse=True)
        self.assertGreaterEqual(dp.valeur_totale, sum(poids1[:9]))

    def test_priorite(self):
        c1 = Colis(1, 10, 100, 1, "X")
        c5 = Colis(2, 10, 100, 5, "X")
        self.assertEqual(valeur_ponderee(c1, 1), 100)
        self.assertEqual(valeur_ponderee(c5, 1), 200)
        self.assertEqual(valeur_ponderee(c5, 0), 100)
        ch = preparer_camion([c1, c5], 10, alpha=1)
        self.assertEqual([c.id for c in ch.colis], [2])

    def test_capacite_trop_petite(self):
        ch = preparer_camion(exemple_enonce(), 1)
        self.assertEqual(ch.colis, [])


if __name__ == "__main__":
    unittest.main()
