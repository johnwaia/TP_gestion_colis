# Gestion des livraisons : chargement de camions

Programme de gestion de colis et de préparation du chargement d'un camion
(problème du sac à dos 0/1 avec prise en compte de la priorité).

## Langage : Python 3.10+

## Structure

```
projet/
├── src/
│   ├── main.py          menu interactif (point d'entrée)
│   ├── colis.py         classe Colis + validation
│   ├── catalogue.py     stockage (table de hachage), tris, statistiques
│   ├── tri.py           tri fusion et tri par dénombrement (codés à la main)
│   ├── chargement.py    sac à dos : programmation dynamique, glouton, force brute
│   ├── generateur.py    exemple de l'énoncé, génération aléatoire, CSV
│   ├── benchmark.py     mesures de temps (100 à 100 000 colis)
│   └── tests.py         tests unitaires
├── README.md
└── rapport.pdf
```

## Utilisation

```bash
cd src
python main.py            
python -m unittest tests  
python benchmark.py 
```

Au démarrage, les 5 colis de l'énoncé sont chargés. Le menu **8. Données** permet
de générer 100 / 1 000 / 10 000 / 100 000 colis aléatoires, ou d'importer/exporter
un CSV (`id;poids;valeur;priorite;destination`).

```
===== GESTION DES LIVRAISONS =====
1. Afficher les colis
2. Ajouter un colis
3. Rechercher un colis
4. Organiser les colis (tri)
5. Préparer un camion
6. Afficher le chargement
7. Afficher les statistiques
8. Données (exemple / génération / CSV)
0. Quitter
```

## Conventions

- **Poids** : entier en kg (nécessaire pour la programmation dynamique, qui indexe
  un tableau par la capacité).
- **Priorité** : de 1 (faible) à 5 (très urgent). Plus le chiffre est grand, plus le colis est prioritaire.
- **Règle de priorité** : `valeur_pondérée = valeur × (1 + α × (priorité − 1) / 4)`.
  α = 0 ignore la priorité ; α = 1 (par défaut) donne à un colis de priorité 5 deux fois
  le poids de sa valeur. L'utilisateur choisit α au moment de préparer le camion.

## Résumé des choix algorithmiques

| Opération | Stratégie | Temps | Espace |
|---|---|---|---|
| Ajouter un colis | table de hachage (`dict`) | O(1) amorti | O(1) |
| Rechercher par ID | table de hachage | O(1) moyen | O(1) |
| Trier par poids / valeur | tri fusion (codé à la main), mis en cache | O(n log n) | O(n) |
| Trier par priorité | tri par dénombrement (5 seaux) | O(n) | O(n) |
| Préparer le camion | réduction par dominance + programmation dynamique | O(n log n + n'·C) | O(n'·C) octets |
| Variante rapide | glouton valeur/poids (non optimal) | O(n log n) | O(n) |
| Statistiques | un seul parcours | O(n) | O(d) |

n = nombre de colis, C = capacité (kg), n' ≤ C·ln C = nombre de colis restants après réduction.
Le détail et les mesures sont dans `rapport.pdf`.
