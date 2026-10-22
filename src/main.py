from catalogue import Catalogue
from chargement import preparer_camion
from colis import Colis, ENTETE, PRIORITE_MIN, PRIORITE_MAX
import generateur

TAILLE_PAGE = 20

def lire_entier(message, mini=None, maxi=None, defaut=None):
    while True:
        brut = input(message).strip()
        if not brut and defaut is not None:
            return defaut
        try:
            v = int(brut)
        except ValueError:
            print("  -> Entier attendu.")
            continue
        if (mini is not None and v < mini) or (maxi is not None and v > maxi):
            print(f"  -> Valeur attendue entre {mini} et {maxi}.")
            continue
        return v


def lire_reel(message, mini=0.0, defaut=None):
    while True:
        brut = input(message).strip().replace(",", ".")
        if not brut and defaut is not None:
            return defaut
        try:
            v = float(brut)
            if v >= mini:
                return v
        except ValueError:
            pass
        print(f"  -> Nombre >= {mini} attendu.")


def afficher_liste(colis, titre):
    """Affichage paginé : indispensable avec 100 000 colis."""
    total = len(colis)
    print(f"\n--- {titre} ({total} colis) ---")
    if total == 0:
        print("(aucun colis)")
        return
    debut = 0
    while debut < total:
        print(ENTETE)
        for c in colis[debut:debut + TAILLE_PAGE]:
            print(c)
        debut += TAILLE_PAGE
        if debut < total:
            rep = input(f"[{debut}/{total}] Entrée = suite, q = arrêter : ").strip().lower()
            if rep == "q":
                break


def afficher_chargement(ch):
    if ch is None:
        print("\nAucun chargement préparé (menu 5).")
        return
    afficher_liste(ch.colis, "Chargement du camion")
    print(f"Capacité        : {ch.capacite} kg")
    print(f"Poids chargé    : {ch.poids_total} kg ({100 * ch.poids_total / ch.capacite:.1f} %)")
    print(f"Valeur chargée  : {ch.valeur_totale:.2f} €")
    if ch.alpha:
        print(f"Score pondéré   : {ch.score_total:.2f} (alpha = {ch.alpha})")
    print(f"Méthode         : {ch.methode} ({'optimale' if ch.optimal else 'approchée'})")
    print(f"Colis candidats : {ch.nb_candidats} -> {ch.nb_apres_reduction} après réduction")
    print(f"Durée           : {ch.duree * 1000:.1f} ms")


def action_ajouter(cat):
    print("\n--- Ajout d'un colis ---")
    ident = lire_entier(f"Identifiant [{cat.prochain_id()}] : ", mini=0, defaut=cat.prochain_id())
    if cat.rechercher(ident):
        print("Cet identifiant existe déjà.")
        return
    poids = lire_entier("Poids (kg, entier) : ", mini=1)
    valeur = lire_reel("Valeur (€) : ")
    prio = lire_entier(f"Priorité ({PRIORITE_MIN}=faible .. {PRIORITE_MAX}=urgent) : ",
                       PRIORITE_MIN, PRIORITE_MAX)
    dest = input("Destination : ").strip() or "Inconnue"
    cat.ajouter(Colis(ident, poids, valeur, prio, dest))
    print("Colis ajouté.")


def action_rechercher(cat):
    ident = lire_entier("Identifiant recherché : ")
    c = cat.rechercher(ident)
    if c:
        print(ENTETE)
        print(c)
    else:
        print("Aucun colis avec cet identifiant.")


def action_organiser(cat):
    print("\n1. Par poids\n2. Par valeur\n3. Par priorité")
    choix = lire_entier("Critère : ", 1, 3)
    critere = Catalogue.CRITERES[choix - 1]
    decroissant = input("Ordre décroissant ? (o/N) : ").strip().lower() == "o"
    vue = cat.trie_par(critere, decroissant)
    afficher_liste(vue, f"Colis triés par {critere} {'décroissant' if decroissant else 'croissant'}")


def action_preparer(cat):
    if len(cat) == 0:
        print("Aucun colis.")
        return None
    capacite = lire_entier("Capacité du camion (kg) [50] : ", mini=1, defaut=50)
    alpha = lire_reel("Importance de la priorité alpha (0 = ignorer, 1 = défaut) [1] : ", defaut=1.0)
    print("Méthode : 1. Automatique (exacte si possible)  2. Exacte (DP)  3. Gloutonne")
    m = lire_entier("Choix [1] : ", 1, 3, defaut=1)
    ch = preparer_camion(list(cat), capacite, alpha, ["auto", "dp", "glouton"][m - 1])
    afficher_chargement(ch)
    return ch


def action_statistiques(cat):
    s = cat.statistiques()
    if not s:
        print("Aucun colis.")
        return
    print(f"\nNombre de colis : {s['nombre']}")
    print(f"Poids total     : {s['poids_total']} kg (moyenne {s['poids_moyen']:.2f})")
    print(f"Valeur totale   : {s['valeur_totale']:.2f} € (moyenne {s['valeur_moyenne']:.2f})")
    print("Par priorité    : " + ", ".join(f"P{p}={n}" for p, n in s["par_priorite"].items()))
    print("Par destination :")
    for d, n in sorted(s["par_destination"].items(), key=lambda x: -x[1]):
        print(f"   {d:<12} {n}")


def action_donnees(cat):
    print("\n1. Charger l'exemple de l'énoncé\n2. Générer des colis aléatoires"
          "\n3. Importer un CSV\n4. Exporter en CSV")
    choix = lire_entier("Choix : ", 1, 4)
    try:
        if choix == 1:
            nouveaux = generateur.exemple_enonce()
        elif choix == 2:
            n = lire_entier("Nombre de colis : ", 1)
            nouveaux = generateur.generer(n, id_depart=cat.prochain_id())
        elif choix == 3:
            nouveaux = generateur.charger_csv(input("Chemin du fichier : ").strip())
        else:
            generateur.sauver_csv(list(cat), input("Chemin du fichier : ").strip())
            print("Exporté.")
            return
    except (OSError, ValueError, IndexError) as e:
        print(f"Erreur : {e}")
        return
    ajoutes = 0
    for c in nouveaux:
        try:
            cat.ajouter(c)
            ajoutes += 1
        except KeyError:
            pass
    print(f"{ajoutes} colis ajoutés ({len(nouveaux) - ajoutes} doublons ignorés).")


MENU = """
===== GESTION DES LIVRAISONS =====
1. Afficher les colis
2. Ajouter un colis
3. Rechercher un colis
4. Organiser les colis (tri)
5. Préparer un camion
6. Afficher le chargement
7. Afficher les statistiques
8. Données (exemple / génération / CSV)
0. Quitter"""


def main():
    cat = Catalogue()
    for c in generateur.exemple_enonce():
        cat.ajouter(c)
    chargement = None
    while True:
        print(MENU)
        choix = lire_entier("Choix : ", 0, 8)
        if choix == 0:
            break
        elif choix == 1:
            afficher_liste(list(cat), "Colis (ordre d'insertion)")
        elif choix == 2:
            action_ajouter(cat)
        elif choix == 3:
            action_rechercher(cat)
        elif choix == 4:
            action_organiser(cat)
        elif choix == 5:
            chargement = action_preparer(cat) or chargement
        elif choix == 6:
            afficher_chargement(chargement)
        elif choix == 7:
            action_statistiques(cat)
        elif choix == 8:
            action_donnees(cat)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()
