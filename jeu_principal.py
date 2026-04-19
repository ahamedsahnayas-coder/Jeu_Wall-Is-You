# jeu_principal.py

"""
Ce fichier comporte la gestion du menu, du dessin (salles, entites, tresor),
des interactions (clics, touches),
et la gestion des fichiers temporaires d'images.
"""

from fltk import *
import fltk as _fltk
from modele_donjon import lire_position, modifier_position, creer_tresor, lire_tresor
from chargeur_donjon import charger_mon_donjon
from regles_jeu import (
    tourner_salle,
    deplacer_dragons_aleatoire,
    place_tresor,
    sauvegarder_etat,
    charger_sauvegarde,
    supprimer_sauvegarde,
    trouver_chemin_intention,
    deplacer_joueur,
    calculer_chemin_indice,
    calculer_bfs
)
from shutil import copyfile
import os
import random
import glob
import time

try:
    from PIL import Image
    PIL_DISPONIBLE = True
except ImportError:
    PIL_DISPONIBLE = False


# CONSTANTES

TAILLE_CASE = 100
TAILLE_ENTITE = 50
COULEUR_FOND = 'gray10'

NOM_FICHIERS_NIVEAUX = ["donjon_4-5.txt", "donjon_5-7.txt", "donjon_6-10.txt"]
LIBELLES_NIVEAUX = ["Donjon 4 x 5", "Donjon 5 x 7", "Donjon 6 x 10"]
NOM_FICHIER_SAUVEGARDE = "sauvegarde_{}.json"

DOSSIER_TEMP = "temporaire_images"
if not os.path.exists(DOSSIER_TEMP):
    os.makedirs(DOSSIER_TEMP)


# IMAGES
CHEMINS_SALLES_BASE = {
    4: "images/salle_4.gif",
    3: "images/salle_3.gif",
    2: {
        "opposes": "images/salle_2_opposes.gif",
        "angle":   "images/salle_2_angle.gif"
    },
    1: "images/salle_1.gif"
}

IMAGE_AVENTURIER = "images/A.gif"
IMAGES_DRAGONS = {
    1: "images/D1.gif",
    2: "images/D2.gif",
    3: "images/D3.gif"
}
IMAGE_TRESOR = "images/tresor.gif"


# Cache et gestion de fenetres
id_fenetre = 0
cache_rotations = {}
cache_entites = {}


def chemin_temporaire(origine, suffixe):
    """
    Renvoie un nom de fichier temporaire simple dans le dossier temporaire_images.
    """
    nom_base = os.path.basename(origine)
    if "ent" in suffixe:
        nom_final = f"entite_{id_fenetre}_{nom_base}"
    else:
        nom_final = f"salle_tournee_{suffixe}_{id_fenetre}_{nom_base}"
    return os.path.join(DOSSIER_TEMP, nom_final)


def tourner_image(origine, rotation_deg):
    """
    Retourne un chemin vers un GIF tourne.
    """
    cle = (origine, rotation_deg, id_fenetre)
    if cle in cache_rotations:
        return cache_rotations[cle]

    dest = chemin_temporaire(origine, f"deg{rotation_deg}")

    if PIL_DISPONIBLE:
        try:
            img = Image.open(origine)
            img_t = img.rotate(-rotation_deg, expand=True)
            img_t.save(dest, format="GIF")
        except Exception:
            try:
                copyfile(origine, dest)
            except Exception:
                dest = origine
    else:
        try:
            copyfile(origine, dest)
        except Exception:
            dest = origine

    cache_rotations[cle] = dest
    return dest


def copier_entite(origine):
    """
    Copie l'image d'entite.
    """
    cle = (origine, id_fenetre)
    if cle in cache_entites:
        return cache_entites[cle]

    dest = chemin_temporaire(origine, "ent")

    try:
        copyfile(origine, dest)
    except Exception:
        dest = origine

    cache_entites[cle] = dest
    return dest


# ROTATION

def rotation_passages(passages, k):
    """
    Applique k rotations (90 degres horaire) sur la liste passages (H,D,B,G).
    """
    p = tuple(passages)
    for _ in range(k % 4):
        p = (p[-1], p[0], p[1], p[2])
    return p


REFERENCE_PASSAGES = {
    4: (True, True, True, True),
    3: (True, True, True, False),
    2: {
        "opposes": (True, False, True, False),
        "angle":   (True, True, False, False),
    },
    1: (True, False, False, False)
}


def trouver_rotation_visuelle(passages, nb, sous_type):
    """
    Trouver la rotation necessaire (0, 90, 180, 270) pour aligner l'image
    de reference avec les passages donnes.
    """
    p = tuple(bool(x) for x in passages)
    ref = REFERENCE_PASSAGES[2][sous_type] if nb == 2 else REFERENCE_PASSAGES[nb]
    for k in range(4):
        if rotation_passages(ref, k) == p:
            return k * 90
    return 0


def type_salle(passages):
    """
    Retourne (nb_passages, sous_type) de la salle.
    """
    p = tuple(bool(x) for x in passages)
    nb = sum(1 for v in p if v)
    if nb == 2:
        if (p[0] and p[2]) or (p[1] and p[3]):
            return 2, "opposes"
        return 2, "angle"
    return nb, None


# CENTRAGE FENETRE

def centrer_fenetre(largeur, hauteur):
    """
    Centre la fenetre active (cree_fenetre) sur l'ecran.
    """
    try:
        canevas = getattr(_fltk, "__canevas", None)
        if canevas is None:
            return
        root = canevas.root
        ecran_largeur = root.winfo_screenwidth()
        ecran_hauteur = root.winfo_screenheight()
        x = max(0, (ecran_largeur - largeur) // 2)
        y = max(0, (ecran_hauteur - hauteur) // 2)
        root.geometry(f"{int(largeur)}x{int(hauteur)}+{x}+{y}")
    except Exception:
        pass


# DESSIN DES SALLES

def dessiner_salle_image(lig, col, passages):
    """
    Dessine la salle (image) a la position lig,col selon les passages.
    """
    x = col * TAILLE_CASE
    y = lig * TAILLE_CASE

    nb, sous_type = type_salle(passages)

    if nb == 4:
        origine = CHEMINS_SALLES_BASE[4]
    elif nb == 3:
        origine = CHEMINS_SALLES_BASE[3]
    elif nb == 2:
        origine = CHEMINS_SALLES_BASE[2][sous_type]
    elif nb == 1:
        origine = CHEMINS_SALLES_BASE[1]
    else:
        rectangle(x, y, x + TAILLE_CASE, y + TAILLE_CASE, remplissage='black')
        return

    rotation_deg = trouver_rotation_visuelle(passages, nb, sous_type)
    chemin_tourne = tourner_image(origine, rotation_deg)

    try:
        image(x, y, chemin_tourne, largeur=TAILLE_CASE, hauteur=TAILLE_CASE, ancrage='nw')
    except TypeError:
        image(x, y, chemin_tourne, TAILLE_CASE, TAILLE_CASE, 'nw')


# DESSIN DES ENTITES

def dessiner_entites(etat_jeu):
    """
    Dessine dragons, aventurier, et tresor si present.
    """
    def centre(l, c):
        return c * TAILLE_CASE + TAILLE_CASE // 2, l * TAILLE_CASE + TAILLE_CASE // 2

    for dragon in etat_jeu.get('monstres', []):
        l, c = lire_position(dragon)
        niveau = dragon['niveau']
        cx, cy = centre(l, c)
        chemin_orig = IMAGES_DRAGONS.get(niveau, IMAGES_DRAGONS.get(1))
        chemin_aff = copier_entite(chemin_orig)
        try:
            image(cx - TAILLE_ENTITE // 2, cy - TAILLE_ENTITE // 2, chemin_aff,
                  largeur=TAILLE_ENTITE, hauteur=TAILLE_ENTITE, ancrage='nw')
        except TypeError:
            image(cx - TAILLE_ENTITE // 2, cy - TAILLE_ENTITE // 2, chemin_aff,
                  TAILLE_ENTITE, TAILLE_ENTITE, 'nw')
        texte(cx, cy, str(niveau), taille=10, couleur='white', ancrage='center')

    joueur = etat_jeu.get('joueur')
    if joueur:
        l, c = lire_position(joueur)
        if l >= 0:
            cx, cy = centre(l, c)
            chemin_a = copier_entite(IMAGE_AVENTURIER)
            try:
                image(cx - TAILLE_ENTITE // 2, cy - TAILLE_ENTITE // 2, chemin_a,
                      largeur=TAILLE_ENTITE, hauteur=TAILLE_ENTITE, ancrage='nw')
            except TypeError:
                image(cx - TAILLE_ENTITE // 2, cy - TAILLE_ENTITE // 2, chemin_a,
                      TAILLE_ENTITE, TAILLE_ENTITE, 'nw')
            texte(cx, cy, str(joueur['niveau']), taille=12, couleur='black', ancrage='center')

    # Tresor
    tresor = lire_tresor(etat_jeu)
    if tresor is not None:
        l, c = tresor['pos']
        if l >= 0:
            cx, cy = centre(l, c)
            chemin_tresor_aff = copier_entite(IMAGE_TRESOR)
            try:
                image(cx - TAILLE_ENTITE // 2, cy - TAILLE_ENTITE // 2, chemin_tresor_aff,
                      largeur=TAILLE_ENTITE, hauteur=TAILLE_ENTITE, ancrage='nw')
            except TypeError:
                image(cx - TAILLE_ENTITE // 2, cy - TAILLE_ENTITE // 2, chemin_tresor_aff,
                      TAILLE_ENTITE, TAILLE_ENTITE, 'nw')


def dessiner_intention(chemin_coords, couleur='red'):
    """
    Dessine la ligne materialisant le chemin d'intention ou l'indice.
    """
    if not chemin_coords or len(chemin_coords) < 2:
        return

    def centre(l, c):
        return c * TAILLE_CASE + TAILLE_CASE // 2, l * TAILLE_CASE + TAILLE_CASE // 2

    points = []
    for l, c in chemin_coords:
        points.extend(centre(l, c))
    for i in range(0, len(points) - 2, 2):
        ligne(points[i], points[i + 1], points[i + 2], points[i + 3],
              couleur=couleur, epaisseur=4, tag='intention')


# DESSIN COMPLET DU DONJON

def dessiner_donjon(etat_jeu, chemin_intention=None, chemin_indice=None):
    """
    Dessine l'ensemble du donjon (salles, entites) et le chemin d'intention/indice.
    """
    grille = etat_jeu['grille']
    for lig, ligne_case in enumerate(grille):
        for col, salle in enumerate(ligne_case):
            dessiner_salle_image(lig, col, salle)

    if chemin_indice:
        dessiner_intention(chemin_indice, couleur='blue')
    if chemin_intention:
        dessiner_intention(chemin_intention, couleur='red')

    dessiner_entites(etat_jeu)


# MESSAGE ET MENU

def afficher_message(largeur, hauteur, msg, couleur_txt):
    """
    Affiche un message centre au milieu de l'ecran.
    """
    cx, cy = largeur // 2, hauteur // 2
    rectangle(0, cy - 30, largeur, cy + 30, remplissage='black')
    texte(cx, cy, msg, taille=24, couleur=couleur_txt, ancrage='center')


def dessiner_menu(largeur, hauteur):
    """
    Dessine le menu principal avec les options de niveau.
    """
    efface_tout()
    rectangle(0, 0, largeur, hauteur, remplissage='gray10')
    texte(largeur // 2, hauteur // 6, "Wall is you", taille=50, couleur='#8B0000', ancrage='center', police="Impact")
    texte(largeur // 2, hauteur // 3, "Choisissez un niveau", taille=25, couleur='#0000FF', ancrage='center', police="Helvetica")
    y_depart = hauteur // 2 - 50
    for i, libelle in enumerate(LIBELLES_NIVEAUX):
        y_pos = y_depart + i * 80
        rectangle(largeur // 4, y_pos, 3 * largeur // 4, y_pos + 60,
                  couleur='#E6B800', remplissage='#333333', epaisseur=3)
        texte(largeur // 2, y_pos + 30, libelle, taille=25, couleur='#F0F0F0', ancrage='center', police="Impact")


def clic_menu(x, y, largeur, hauteur):
    """
    Gere le clic dans le menu pour selectionner un niveau.
    """
    y_depart = hauteur // 2 - 50
    for i in range(len(NOM_FICHIERS_NIVEAUX)):
        y_pos = y_depart + i * 80
        if (largeur // 4 < x < 3 * largeur // 4) and (y_pos < y < y_pos + 60):
            return i
    return -1


def gerer_rotation(etat_jeu, x, y):
    """
    Gere la rotation de la salle cliquee (clic droit sans Ctrl).
    """
    col, lig = x // TAILLE_CASE, y // TAILLE_CASE
    if 0 <= lig < len(etat_jeu['grille']) and 0 <= col < len(etat_jeu['grille'][0]):
        tourner_salle(etat_jeu['grille'][lig][col])
        return True
    return False


def gerer_placement_tresor(etat_jeu, x, y):
    """
    Gere l'action de placer un tresor (Ctrl + Clic Droit).
    """
    col, lig = x // TAILLE_CASE, y // TAILLE_CASE
    pos = (lig, col)
    if 0 <= lig < len(etat_jeu['grille']) and 0 <= col < len(etat_jeu['grille'][0]):
        return place_tresor(etat_jeu, pos)
    return False


def gerer_intention_joueur(etat_jeu, x, y):
    """
    Definit le chemin d'intention (ligne rouge) vers la salle cliquee (Clic Gauche).
    """
    col, lig = x // TAILLE_CASE, y // TAILLE_CASE
    pos_cible = (lig, col)
    l_max, c_max = len(etat_jeu['grille']), len(etat_jeu['grille'][0])
    chemin_coords = calculer_bfs(etat_jeu['grille'], etat_jeu['joueur']['pos'], pos_cible, l_max, c_max)
    return chemin_coords


def gerer_deplacement_joueur(etat_jeu, chemin_intention):
    """
    Declenche le mouvement de l'aventurier le long du chemin d'intention (Espace).
    """
    if not chemin_intention:
        return False
    if deplacer_joueur(etat_jeu, chemin_intention):
        deplacer_dragons_aleatoire(etat_jeu)
        return True
    return False


# BOUCLE PRINCIPALE

def boucle_principale():
    """
    Boucle principale de l'application, gestion du menu et des evenements du jeu.
    """
    global id_fenetre, cache_rotations, cache_entites

    largeur_menu, hauteur_menu = 1000, 700
    etat_jeu = None
    mode = 'MENU'
    index_niveau = 0
    victoire = False
    defaite = False
    message_timer = 0
    intention_chemin = None
    indice_chemin = None
    bloquer_auto = False
    indice_actif = False

    def obtenir_nom_fichier_sauvegarde(index):
        if 0 <= index < len(NOM_FICHIERS_NIVEAUX):
            niv_id = NOM_FICHIERS_NIVEAUX[index].replace('donjon_', '').replace('.txt', '')
            nom_f = NOM_FICHIER_SAUVEGARDE.format(niv_id)
            return os.path.join(DOSSIER_TEMP, nom_f)
        return os.path.join(DOSSIER_TEMP, NOM_FICHIER_SAUVEGARDE.format('defaut'))

    id_fenetre += 1
    cache_rotations = {}
    cache_entites = {}
    cree_fenetre(largeur_menu, hauteur_menu)
    centrer_fenetre(largeur_menu, hauteur_menu)

    try:
        while True:
            if mode == 'MENU':
                dessiner_menu(largeur_menu, hauteur_menu)

            elif mode in ['JEU', 'FIN']:
                if etat_jeu is None:
                    mise_a_jour()
                    continue

                # Tache 4 : Calcul automatique de l'intention
                tresor_accessible = False
                if lire_tresor(etat_jeu):
                    temp_chemin = trouver_chemin_intention(etat_jeu)
                    if temp_chemin and temp_chemin[-1] == lire_tresor(etat_jeu)['pos']:
                        tresor_accessible = True

                if not (victoire or defaite):
                    if tresor_accessible:
                        intention_chemin = trouver_chemin_intention(etat_jeu)
                        bloquer_auto = False
                    elif not bloquer_auto:
                        intention_chemin = trouver_chemin_intention(etat_jeu)

                # Bonus 2 : Calcul de l'indice (ligne bleue)
                if not (victoire or defaite) and indice_actif:
                    indice_chemin = calculer_chemin_indice(etat_jeu)
                else:
                    indice_chemin = None

                largeur_jeu = len(etat_jeu['grille'][0]) * TAILLE_CASE
                hauteur_jeu = len(etat_jeu['grille']) * TAILLE_CASE

                if largeur_jeu != largeur_fenetre() or hauteur_jeu != hauteur_fenetre():
                    ferme_fenetre()
                    id_fenetre += 1
                    cache_rotations = {}
                    cache_entites = {}
                    cree_fenetre(largeur_jeu, hauteur_jeu)
                    centrer_fenetre(largeur_jeu, hauteur_jeu)

                efface_tout()
                dessiner_donjon(etat_jeu, intention_chemin, indice_chemin)

                partie_finie_avant_maj = victoire or defaite

                if not etat_jeu.get('monstres') and not victoire:
                    victoire = True
                if lire_position(etat_jeu['joueur']) == (-1, -1) and not defaite:
                    defaite = True

                if (victoire or defaite) and not partie_finie_avant_maj:
                    fichier_a_supprimer = obtenir_nom_fichier_sauvegarde(index_niveau)
                    supprimer_sauvegarde(fichier_a_supprimer)
                    intention_chemin = None
                    indice_chemin = None
                    mode = 'FIN'

                if victoire:
                    afficher_message(largeur_jeu, hauteur_jeu, "VICTOIRE !", 'green')
                elif defaite:
                    afficher_message(largeur_jeu, hauteur_jeu, "GAME OVER", 'red')

                if message_timer > 0:
                    if not (victoire or defaite):
                        afficher_message(largeur_jeu, hauteur_jeu, "Partie sauvegardee !", 'yellow')
                    message_timer -= 1

            mise_a_jour()
            ev = donne_ev()
            if ev is None:
                continue
            tev = type_ev(ev)

            if mode == 'MENU' and tev == 'ClicGauche':
                res = clic_menu(abscisse(ev), ordonnee(ev), largeur_menu, hauteur_menu)
                if isinstance(res, int) and res != -1:
                    index_niveau = res
                    nom_fichier_sauvegarde = obtenir_nom_fichier_sauvegarde(index_niveau)
                    doc = charger_sauvegarde(nom_fichier_sauvegarde)
                    if doc:
                        etat_jeu = doc
                    else:
                        etat_jeu = charger_mon_donjon(NOM_FICHIERS_NIVEAUX[index_niveau])
                    if etat_jeu is not None:
                        mode = 'JEU'
                        victoire = defaite = False
                        message_timer = 0
                        intention_chemin = None
                        indice_chemin = None
                        bloquer_auto = False
                        indice_actif = False

            elif mode == 'JEU' or mode == 'FIN':
                if tev == 'ClicGauche' and not (victoire or defaite):
                    chemin_calcule = gerer_intention_joueur(etat_jeu, abscisse(ev), ordonnee(ev))
                    if chemin_calcule is not None and len(chemin_calcule) > 1:
                        intention_chemin = chemin_calcule
                        bloquer_auto = True

                elif tev == 'ClicDroit' and not (victoire or defaite):
                    x, y = abscisse(ev), ordonnee(ev)
                    if touche_pressee("Control_L") or touche_pressee("Control_R"):
                        if gerer_placement_tresor(etat_jeu, x, y):
                            bloquer_auto = False
                    else:
                        if gerer_rotation(etat_jeu, x, y):
                            bloquer_auto = False

                elif tev == 'Touche':
                    t = touche(ev)
                    if t in ['r', 'R']:
                        etat_jeu = charger_mon_donjon(NOM_FICHIERS_NIVEAUX[index_niveau])
                        victoire = defaite = False
                        intention_chemin = None
                        indice_chemin = None
                        mode = 'JEU'
                        bloquer_auto = False
                        indice_actif = False
                    elif t == 'Escape':
                        ferme_fenetre()
                        id_fenetre += 1
                        cache_rotations = {}
                        cache_entites = {}
                        cree_fenetre(largeur_menu, hauteur_menu)
                        centrer_fenetre(largeur_menu, hauteur_menu)
                        mode = 'MENU'
                        victoire = defaite = False
                    elif not (victoire or defaite):
                        if t in ['s', 'S']:
                            nom_fichier_sauvegarde = obtenir_nom_fichier_sauvegarde(index_niveau)
                            sauvegarder_etat(etat_jeu, nom_fichier_sauvegarde)
                            message_timer = 10
                        elif t == 'space':
                            if gerer_deplacement_joueur(etat_jeu, intention_chemin):
                                bloquer_auto = False
                        elif t in ['i', 'I']:
                            # Bonus 2 : activer/desactiver l'indice bleu
                            indice_actif = not indice_actif
                        elif t in ['u', 'U']:
                            # Bonus 4 : Mode tour unique.
                            # CORRECTION BUG : avant, si trouver_chemin_intention() retournait
                            # None (aucun dragon accessible), la boucle s'arretait sans que
                            # les dragons jouent leur tour.
                            # CORRECTION : 1 appui sur U = 1 tour complet (joueur + dragons),
                            # meme si le joueur ne peut pas bouger. Les dragons jouent
                            # systematiquement leur tour dans tous les cas.
                            bloquer_auto = False
                            largeur_jeu = len(etat_jeu['grille'][0]) * TAILLE_CASE
                            hauteur_jeu = len(etat_jeu['grille']) * TAILLE_CASE
                            while True:
                                c_auto = trouver_chemin_intention(etat_jeu)

                                if not c_auto:
                                    # Aucun chemin joueur : le joueur ne bouge pas,
                                    # MAIS les dragons jouent quand meme leur tour.
                                    deplacer_dragons_aleatoire(etat_jeu)
                                    # Verification victoire/defaite apres le tour des dragons
                                    if not etat_jeu.get('monstres'):
                                        victoire = True
                                    if lire_position(etat_jeu['joueur']) == (-1, -1):
                                        defaite = True
                                    # Rafraichissement et arret de la boucle (1 tour joue)
                                    indice_courant = calculer_chemin_indice(etat_jeu) if indice_actif else None
                                    efface_tout()
                                    dessiner_donjon(etat_jeu, None, indice_courant)
                                    mise_a_jour()
                                    time.sleep(0.3)
                                    break

                                # Chemin disponible : le joueur se deplace
                                joueur_a_bouge = deplacer_joueur(etat_jeu, c_auto)
                                if not joueur_a_bouge:
                                    # Le joueur n'a pas pu bouger malgre un chemin :
                                    # les dragons jouent quand meme leur tour
                                    deplacer_dragons_aleatoire(etat_jeu)
                                    break

                                # Apres le deplacement du joueur, les dragons jouent
                                deplacer_dragons_aleatoire(etat_jeu)

                                # Verification de victoire/defaite
                                if not etat_jeu.get('monstres'):
                                    victoire = True
                                    break
                                if lire_position(etat_jeu['joueur']) == (-1, -1):
                                    defaite = True
                                    break

                                # Rafraichissement graphique a chaque etape
                                indice_courant = calculer_chemin_indice(etat_jeu) if indice_actif else None
                                efface_tout()
                                dessiner_donjon(etat_jeu, c_auto, indice_courant)
                                mise_a_jour()
                                time.sleep(0.3)

                            if victoire or defaite:
                                fichier_a_supprimer = obtenir_nom_fichier_sauvegarde(index_niveau)
                                supprimer_sauvegarde(fichier_a_supprimer)
                                intention_chemin = None
                                indice_chemin = None
                                mode = 'FIN'
    finally:
        try:
            ferme_fenetre()
        except:
            pass


if __name__ == '__main__':
    boucle_principale()

