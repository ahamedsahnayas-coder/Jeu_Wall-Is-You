# regles_jeu.py

"""
Ce fichier contient la logique du jeu : murs, rotation de salle, gestion des intentions,
deplacements, interactions (combat/tresor), deplacement des dragons aleatoires,
et les sauvegardes.
"""

from modele_donjon import (
    lire_position, modifier_position, creer_tresor_structure,
    lire_tresor
)
import random
import json
import os
from collections import deque


def mur_ouvert(grille, pos_dep, pos_arr):
    """
    Verifie si le passage est ouvert entre deux cases adjacentes.

    Grille du donjon.
    pos_dep : position de depart (ligne, colonne).
    pos_arr : position d'arrivee (ligne, colonne).
    return True si le mur est ouvert dans les deux sens, False sinon.

    >>> Necessite une grille de test
    >>> g = [[[True, True, True, True]], [[True, True, True, True]]]
    >>> mur_ouvert(g, (0, 0), (1, 0)) # Mouvement HAUT vers BAS et inversement
    False
    """
    l1, c1 = pos_dep
    l2, c2 = pos_arr

    # Doit etre adjacent
    if abs(l1 - l2) + abs(c1 - c2) != 1:
        return False

    # Verifie les limites de la grille
    if not (0 <= l2 < len(grille) and 0 <= c2 < len(grille[0])):
        return False

    salle_dep = grille[l1][c1]
    salle_arr = grille[l2][c2]

    # Indices des passages : H=0, D=1, B=2, G=3
    if l1 != l2:  # Mouvement vertical
        if l2 < l1:  # Vers le Haut
            return salle_dep[0] and salle_arr[2]
        else:  # Vers le Bas
            return salle_dep[2] and salle_arr[0]
    else:  # Mouvement horizontal
        if c2 > c1:  # Vers la Droite
            return salle_dep[1] and salle_arr[3]
        else:  # Vers la Gauche
            return salle_dep[3] and salle_arr[1]


def tourner_salle(salle):
    """
    Tourne la salle de 90 degres horaire (H->D, D->B, B->G, G->H).
    La rotation horaire signifie : ce qui allait en Haut va maintenant a Droite,
    ce qui allait a Droite va en Bas, etc.
    Donc le nouveau tableau est : [G, H, D, B] (l'ancien G devient le nouveau H, etc.)

    Correction : l'ancienne implementation faisait pop(3)+insert(0) ce qui donnait
    [ancien_G, ancien_H, ancien_D, ancien_B] = rotation ANTI-horaire.
    La rotation HORAIRE correcte est : premier = dernier_avant = salle[-1], soit
    on deplace le dernier element (G) en premiere position (H), ce qui correspond a
    une rotation horaire des passages dans l'espace.

    Verification :
    salle L = [True, True, False, False] (H=T, D=T, B=F, G=F)
    apres rotation horaire -> [False, True, True, False] (H=F, D=T, B=T, G=F) = salle L tournee 90 degres

    >>> salle = [True, True, False, False]
    >>> tourner_salle(salle)
    >>> salle
    [False, True, True, False]
    """
    # CORRECTION : pop(3) retire G, insert(0, G) place G en H.
    # Cela correspond bien a une rotation horaire :
    # nouveau H = ancien G, nouveau D = ancien H, nouveau B = ancien D, nouveau G = ancien B
    if salle:
        dernier = salle.pop(3)
        salle.insert(0, dernier)


def trouver_meilleur_dragon_accessible(etat_jeu, ignore_murs=False):
    """
    Trouve le dragon de plus haut niveau accessible ET battable.

    ignore_murs=False : cherche un dragon accessible via les passages reels (BFS avec murs).
    ignore_murs=True  : cherche un dragon battable en ignorant les murs (BFS libre),
                        utilise pour l'indice bleu (Bonus 2).
    """
    grille = etat_jeu['grille']
    joueur = etat_jeu['joueur']
    pos_joueur = lire_position(joueur)
    niv_joueur = joueur['niveau']
    l_max, c_max = len(grille), len(grille[0])

    meilleur_dragon = None
    max_niveau = -1

    for dragon in etat_jeu.get('monstres', []):
        # L'aventurier ne vise que ce qu'il peut tuer
        if dragon['niveau'] <= niv_joueur:
            pos_d = lire_position(dragon)
            if ignore_murs:
                # CORRECTION : ignore_murs=True doit verifier l'accessibilite geometrique
                # (case dans les limites), pas retourner True directement.
                # On verifie juste que la position est valide dans la grille.
                accessible = (0 <= pos_d[0] < l_max and 0 <= pos_d[1] < c_max)
            else:
                # Pour l'intention rouge : on verifie l'acces reel via BFS avec murs
                chemin = calculer_bfs(grille, pos_joueur, pos_d, l_max, c_max)
                accessible = chemin is not None

            if accessible:
                if dragon['niveau'] > max_niveau:
                    max_niveau = dragon['niveau']
                    meilleur_dragon = pos_d

    return meilleur_dragon


def trouver_chemin_intention(etat_jeu, pos_cible=None):
    """
    Calcule le chemin d'intention (ligne rouge).
    Priorite 1 : Tresor (si accessible)
    Priorite 2 : Meilleur dragon accessible et battable (automatique)
    Priorite 3 : Position cible du clic
    """
    grille = etat_jeu['grille']
    pos_joueur = lire_position(etat_jeu['joueur'])
    l_max, c_max = len(grille), len(grille[0])

    # 1. TRESOR PRIORITAIRE
    tresor = lire_tresor(etat_jeu)
    if tresor is not None:
        chemin_vers_tresor = calculer_bfs(grille, pos_joueur, tresor['pos'], l_max, c_max)
        if chemin_vers_tresor:
            return chemin_vers_tresor

    # 2. DRAGON AUTOMATIQUE
    pos_dragon = trouver_meilleur_dragon_accessible(etat_jeu, ignore_murs=False)
    if pos_dragon:
        return calculer_bfs(grille, pos_joueur, pos_dragon, l_max, c_max)

    # 3. CLIC JOUEUR
    if pos_cible:
        return calculer_bfs(grille, pos_joueur, pos_cible, l_max, c_max)

    return None


def calculer_chemin_indice(etat_jeu):
    """
    Bonus 2 : Calcule un chemin vers le meilleur dragon battable,
    meme si les murs sont fermes (BFS sans contrainte de passages).
    Affiche la ligne bleue d'indice.
    """
    grille = etat_jeu['grille']
    pos_joueur = lire_position(etat_jeu['joueur'])
    l_max, c_max = len(grille), len(grille[0])

    # On cherche la cible dragon battable en ignorant les murs
    cible_pos = trouver_meilleur_dragon_accessible(etat_jeu, ignore_murs=True)

    if cible_pos:
        # BFS libre (sans contrainte de murs)
        queue = deque([pos_joueur])
        parents = {pos_joueur: None}
        while queue:
            curr = queue.popleft()
            if curr == cible_pos:
                path = []
                while curr is not None:
                    path.append(curr)
                    curr = parents[curr]
                path.reverse()
                return path
            l, c = curr
            for dl, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nxt = (l + dl, c + dc)
                if 0 <= nxt[0] < l_max and 0 <= nxt[1] < c_max and nxt not in parents:
                    parents[nxt] = curr
                    queue.append(nxt)
    return None


def calculer_bfs(grille, depart, arrivee, l_max, c_max):
    """
    Calcule le plus court chemin entre depart et arrivee en respectant les passages (murs).
    Utilise un BFS (parcours en largeur) garantissant le chemin de longueur minimale.
    Bonus 6 : ce BFS produit toujours le plus court chemin, contrairement a un algorithme naif.

    grille : la grille du donjon.
    depart : tuple (ligne, colonne) de depart.
    arrivee : tuple (ligne, colonne) d'arrivee.
    l_max, c_max : dimensions de la grille.
    return : liste de tuples representant le chemin, ou None si inaccessible.
    """
    if depart == arrivee:
        return [depart]

    queue = deque([depart])
    parents = {depart: None}
    trouve = False

    while queue:
        curr = queue.popleft()
        if curr == arrivee:
            trouve = True
            break
        l, c = curr
        for dl, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nxt = (l + dl, c + dc)
            if 0 <= nxt[0] < l_max and 0 <= nxt[1] < c_max:
                if nxt not in parents and mur_ouvert(grille, curr, nxt):
                    parents[nxt] = curr
                    queue.append(nxt)

    if not trouve:
        return None

    path = []
    curr = arrivee
    while curr is not None:
        path.append(curr)
        curr = parents[curr]
    path.reverse()
    return path


def deplacer_joueur(etat_jeu, chemin_intention):
    """
    Deplace l'aventurier le long du chemin d'intention jusqu'au premier obstacle
    (tresor, dragon, ou fin du chemin).

    CORRECTION : le chemin_intention doit commencer par la position actuelle du joueur.
    Si ce n'est pas le cas (chemin obsolete apres rotation de salle), on ne deplace pas.
    """
    joueur = etat_jeu['joueur']
    pos_act = lire_position(joueur)
    grille = etat_jeu['grille']

    if not chemin_intention or chemin_intention[0] != pos_act or len(chemin_intention) <= 1:
        return False

    pos_finale = pos_act
    mouvement_effectue = False

    pos_tresor = lire_tresor(etat_jeu)['pos'] if lire_tresor(etat_jeu) else None

    for pos_next in chemin_intention[1:]:
        if not mur_ouvert(grille, pos_finale, pos_next):
            break

        if pos_next == pos_tresor:
            pos_finale = pos_next
            mouvement_effectue = True
            break

        is_dragon_blocking = False
        for monstre in etat_jeu.get('monstres', []):
            if lire_position(monstre) == pos_next:
                is_dragon_blocking = True
                break

        if is_dragon_blocking:
            pos_finale = pos_next
            mouvement_effectue = True
            break

        pos_finale = pos_next
        mouvement_effectue = True

    if mouvement_effectue:
        modifier_position(joueur, pos_finale)
        gerer_interactions(etat_jeu)
        return True

    return False


def gerer_interactions(etat_jeu):
    """
    Gere les interactions apres le deplacement de l'aventurier (tresor ou combat).
    """
    joueur = etat_jeu['joueur']
    pos_joueur = lire_position(joueur)
    dragons_restants = []
    monstre_mort = False
    partie_perdue = False

    tres = lire_tresor(etat_jeu)
    if tres and tres['pos'] == pos_joueur:
        etat_jeu['tresor_actif'] = None
        if 'nb_tresors_restants' in etat_jeu and etat_jeu['nb_tresors_restants'] > 0:
            etat_jeu['nb_tresors_restants'] -= 1
        return

    for monstre in etat_jeu.get('monstres', []):
        if lire_position(monstre) == pos_joueur:
            if monstre['niveau'] <= joueur['niveau']:
                monstre_mort = True
            else:
                partie_perdue = True
                dragons_restants.append(monstre)
        else:
            dragons_restants.append(monstre)

    etat_jeu['monstres'] = dragons_restants
    if monstre_mort:
        joueur['niveau'] += 1

    if partie_perdue:
        modifier_position(joueur, (-1, -1))


def place_tresor(etat_jeu, pos):
    """
    Place un tresor si la case est libre et s'il reste des tresors disponibles.
    Variante Tresor : le donjon peut placer un tresor par clic droit dans une salle inoccupee.
    Il ne peut y avoir qu'un seul tresor actif a la fois.
    """
    l, c = pos
    if not (0 <= l < len(etat_jeu['grille']) and 0 <= c < len(etat_jeu['grille'][0])):
        return False

    if 'nb_tresors_restants' not in etat_jeu or etat_jeu['nb_tresors_restants'] <= 0:
        return False

    if lire_tresor(etat_jeu) is not None:
        return False

    if lire_position(etat_jeu['joueur']) == pos:
        return False

    for m in etat_jeu.get('monstres', []):
        if lire_position(m) == pos:
            return False

    etat_jeu['tresor_actif'] = creer_tresor_structure(pos[0], pos[1])
    return True


def deplacer_dragons_aleatoire(etat_jeu):
    """
    Deplace chaque dragon survivant d'une case aleatoirement.
    Variante Deplacement des dragons : apres le tour de l'aventurier,
    chaque dragon se deplace d'une case accessible aleatoirement.
    Si un dragon rencontre l'aventurier, les regles de combat s'appliquent.
    """
    grille = etat_jeu['grille']
    joueur = etat_jeu['joueur']
    dragons_restants = []
    pos_joueur = lire_position(joueur)

    for monstre in etat_jeu.get('monstres', []):
        if pos_joueur == (-1, -1):
            dragons_restants.append(monstre)
            continue

        pos = lire_position(monstre)
        l, c = pos
        voisins_possibles = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dl, dc in directions:
            pos_voisin = (l + dl, c + dc)
            if mur_ouvert(grille, pos, pos_voisin):
                voisins_possibles.append(pos_voisin)

        nouveau_pos = pos
        if voisins_possibles:
            nouveau_pos = random.choice(voisins_possibles)

        modifier_position(monstre, nouveau_pos)

        if nouveau_pos == pos_joueur:
            if monstre['niveau'] <= joueur['niveau']:
                joueur['niveau'] += 1
            else:
                modifier_position(joueur, (-1, -1))
                dragons_restants.append(monstre)
        else:
            dragons_restants.append(monstre)

    etat_jeu['monstres'] = dragons_restants


def sauvegarder_etat(etat_jeu, fichier):
    """
    Sauvegarde l'etat du jeu dans un fichier JSON.
    Variante Sauvegarde : permet d'enregistrer une partie en cours.
    """
    def convertir_pour_json(o):
        if isinstance(o, tuple):
            return list(o)
        if isinstance(o, dict):
            return {k: convertir_pour_json(v) for k, v in o.items()}
        if isinstance(o, list):
            return [convertir_pour_json(v) for v in o]
        return o

    tresor_actif = lire_tresor(etat_jeu)
    a_sauvegarder = {
        'grille': etat_jeu['grille'],
        'joueur': convertir_pour_json(etat_jeu['joueur']),
        'monstres': convertir_pour_json(etat_jeu['monstres']),
        'nb_tresors_restants': etat_jeu.get('nb_tresors_restants', 0),
        'tresor_actif': convertir_pour_json(tresor_actif) if tresor_actif is not None else None,
    }
    try:
        with open(fichier, 'w', encoding='utf-8') as f:
            json.dump(a_sauvegarder, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erreur sauvegarde dans {fichier}:", e)


def charger_sauvegarde(fichier):
    """
    Charge une sauvegarde depuis un fichier JSON.
    Variante Sauvegarde : permet de reprendre une partie enregistree.
    """
    try:
        with open(fichier, 'r', encoding='utf-8') as f:
            doc = json.load(f)

        def fixer_position(entite):
            if 'pos' in entite and isinstance(entite['pos'], list):
                entite['pos'] = tuple(entite['pos'])
            return entite

        doc['joueur'] = fixer_position(doc['joueur'])
        doc['monstres'] = [fixer_position(m) for m in doc['monstres']]
        tresor = doc.get('tresor_actif')
        if tresor is not None:
            doc['tresor_actif'] = fixer_position(tresor)
        return doc
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Erreur chargement sauvegarde depuis {fichier}:", e)
        return None


def supprimer_sauvegarde(fichier):
    """
    Supprime le fichier de sauvegarde en fin de partie.
    """
    try:
        if os.path.exists(fichier):
            os.remove(fichier)
            return True
        return False
    except Exception as e:
        print(f"Erreur lors de la suppression de la sauvegarde {fichier}:", e)
        return False
