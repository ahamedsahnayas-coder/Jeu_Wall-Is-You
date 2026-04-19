# chargeur_donjon.py

"""
Ce fichier charge les fichiers de donjon (.txt) et construit l'etat du jeu.
"""

from modele_donjon import creer_salle, creer_perso, creer_etat_jeu
import re


def convertir_car(type_salle):
    """
    Convertit le caractere de salle en passages [Haut, Droit, Bas, Gauche].
    Accepte les caracteres ASCII (L, -, |, T, +) et les caracteres Unicode de box-drawing.
    Caractere representant le type de salle.
    return liste de booleens [H, D, B, G].

    >>> convertir_car('L')
    [True, True, False, False]
    >>> convertir_car('+')
    [True, True, True, True]
    >>> convertir_car(' ')
    [False, False, False, False]
    """
    # --- Correction : ajout de la table de correspondance Unicode (╬, ╠, ╔, ║, ╥, etc.)
    # requis par la Tache 3 de la consigne, en plus des caracteres ASCII deja presents.
    TABLE = {
        # ASCII (format des fichiers fournis)
        'L':  [True,  True,  False, False],
        '-':  [False, True,  False, True ],
        '|':  [True,  False, True,  False],
        'T':  [True,  True,  True,  False],
        '+':  [True,  True,  True,  True ],
        # Unicode box-drawing (format consigne officielle)
        '╬':  [True,  True,  True,  True ],   # 4 passages
        '╠':  [True,  True,  True,  False],   # 3 passages : H D B
        '╦':  [False, True,  True,  True ],   # 3 passages : D B G
        '╣':  [True,  False, True,  True ],   # 3 passages : H B G
        '╩':  [True,  True,  False, True ],   # 3 passages : H D G
        '╔':  [False, True,  True,  False],   # 2 passages angle : D B
        '╗':  [False, False, True,  True ],   # 2 passages angle : B G
        '╚':  [True,  True,  False, False],   # 2 passages angle : H D
        '╝':  [True,  False, False, True ],   # 2 passages angle : H G
        '═':  [False, True,  False, True ],   # 2 passages opposes : D G
        '║':  [True,  False, True,  False],   # 2 passages opposes : H B
        '╥':  [False, False, True,  False],   # 1 passage : B
        '╨':  [True,  False, False, False],   # 1 passage : H
        '╡':  [False, False, False, True ],   # 1 passage : G
        '╞':  [False, True,  False, False],   # 1 passage : D
    }
    return TABLE.get(type_salle, [False, False, False, False])


def charger_mon_donjon(nom_fichier):
    """
    Charge un fichier de donjon et retourne l'etat complet du jeu.
    Chemin du fichier .txt du donjon.
    return dictionnaire representant l'etat du jeu ou None si erreur.

    >>> Test minimal (necessite un fichier existant pour un vrai test)
    >>> etat = charger_mon_donjon("donjon_test.txt") 
    >>> isinstance(etat, dict) or etat is None
    True
    """
    salles_temp = {}
    info_joueur = None
    liste_dragons = []
    nb_tresors = 0

    max_ligne, max_colonne = 0, 0

    # Ensemble de tous les caracteres de salle reconnus (ASCII + Unicode)
    TYPES_SALLE = {'|', '-', '+', 'T', 'L', '╬', '╠', '╦', '╣', '╩',
                   '╔', '╗', '╚', '╝', '═', '║', '╥', '╨', '╡', '╞'}

    try:
        with open(nom_fichier, 'r', encoding='utf-8') as f:
            for ligne_str in f:
                ligne_str = ligne_str.strip()
                if not ligne_str or ligne_str.startswith('#'):
                    continue
                mots = re.split(r'\s+', ligne_str)
                if not mots:
                    continue
                type_item = mots[0]

                if type_item in TYPES_SALLE and len(mots) >= 3:
                    car, l, c = mots[0], int(mots[1]), int(mots[2])
                    salles_temp[(l, c)] = convertir_car(car)
                    max_ligne = max(max_ligne, l + 1)
                    max_colonne = max(max_colonne, c + 1)
                elif type_item == 'A' and len(mots) >= 3:
                    l, c = int(mots[1]), int(mots[2])
                    niv = int(mots[3]) if len(mots) > 3 else 1
                    info_joueur = (l, c, niv)
                elif type_item == 'D' and len(mots) >= 4:
                    l, c, niv = int(mots[1]), int(mots[2]), int(mots[3])
                    liste_dragons.append(creer_perso(l, c, niv))
                elif type_item.upper() in ['NB_TRESORS', 'NOMBRE_TRESORS', 'TRESORS', 'NBTRESORS'] and len(mots) >= 2:
                    try:
                        nb_tresors = int(mots[1])
                    except ValueError:
                        nb_tresors = 0

    except FileNotFoundError:
        print(f"Erreur: Fichier {nom_fichier} introuvable.")
        return None

    # Construction de la grille finale
    grille_finale = []
    for l in range(max_ligne):
        ligne = []
        for c in range(max_colonne):
            salle = salles_temp.get((l, c), creer_salle(False, False, False, False))
            ligne.append(salle)
        grille_finale.append(ligne)

    # Creation du joueur
    if info_joueur:
        joueur = creer_perso(info_joueur[0], info_joueur[1], info_joueur[2], True)
    else:
        # Position par defaut
        joueur = creer_perso(0, 0, 1, True)

    etat = creer_etat_jeu(grille_finale, joueur, liste_dragons)

    # Stocker le compteur de tresors
    etat['nb_tresors_restants'] = nb_tresors
    etat['tresor_actif'] = None

    return etat
