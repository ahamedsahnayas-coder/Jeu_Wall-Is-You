# modele_donjon.py

"""
Fichier des structures de donnees de base du jeu :
salles, personnages (aventurier/dragons), tresors.
"""

def creer_salle(h, d, b, g):
    """
    Cree une salle representee par une liste des passages ouverts (Haut, Droit, Bas, Gauche).

    Passage vers le Haut (True) ou mur (False).
    Passage vers la Droite (True) ou mur (False).
    Passage vers le Bas (True) ou mur (False).
    Passage vers la Gauche (True) ou mur (False).
    return liste des passages [h, d, b, g].
    
    >>> creer_salle(True, False, True, False)
    [True, False, True, False]
    """
    return [h, d, b, g]


def creer_perso(ligne, colonne, niveau, est_aventurier=False):
    """
    Cree un personnage (aventurier ou dragon).

    Ligne : Ligne initiale du personnage.
    Colonne : Colonne initiale du personnage.
    Niveau : Niveau de force du personnage.
    Bool est_aventurier : True si c'est l'aventurier (joueur), False sinon (monstre).
    return Dictionnaire representant le personnage.
    
    >>> p = creer_perso(1, 2, 3, True)
    >>> lire_position(p)
    (1, 2)
    >>> p['niveau']
    3
    >>> p['est_joueur']
    True
    """
    return {'pos': (ligne, colonne), 'niveau': niveau, 'est_joueur': est_aventurier}


def creer_tresor(ligne, colonne):
    """
    Cree la structure de donnees d'un tresor.

    Ligne : Ligne du tresor.
    Colonne : Colonne du tresor.
    return Dictionnaire representant le tresor.
    """
    return {'pos': (ligne, colonne)}


def creer_tresor_structure(ligne, colonne):
    """
    Nom plus explicite pour creer un tresor.
    """
    return creer_tresor(ligne, colonne)


def creer_etat_jeu(grille, joueur, dragons):
    """
    Assemble l'etat complet du jeu.

    grille : Grille du donjon (liste de listes de salles).
    joueur : Structure de l'aventurier.
    dragons : Liste des structures de dragons.
    return : Dictionnaire representant l'etat du jeu.
    """
    return {'grille': grille, 'joueur': joueur, 'monstres': dragons}


def lire_position(perso):
    """
    Retourne la position (ligne, colonne) d'un personnage.

    dict perso: Le personnage dont on veut lire la position.
    return Tuple (ligne, colonne).
    
    >>> p = creer_perso(2, 3, 1)
    >>> lire_position(p)
    (2, 3)
    """
    return perso['pos']


def modifier_position(perso, nouvelle_pos):
    """
    Met a jour la position (ligne, colonne) d'un personnage.

    dict perso: Le personnage a modifier.
    Tuple nouvelle_pos: La nouvelle position (ligne, colonne).
    
    >>> p = creer_perso(0, 0, 1)
    >>> modifier_position(p, (2, 2))
    >>> lire_position(p)
    (2, 2)
    """
    perso['pos'] = nouvelle_pos


def lire_tresor(etat_jeu):
    """
    Retourne la structure du tresor actif ou None s'il n'y en a pas.

    dict etat_jeu : Etat global du jeu.
    return: Dictionnaire tresor ou None.
    """
    return etat_jeu.get('tresor_actif')


def enlever_tresor(etat_jeu):
    """
    Enleve le tresor actif de l'etat du jeu.
    dict etat_jeu: Etat global du jeu.
    """
    etat_jeu['tresor_actif'] = None
