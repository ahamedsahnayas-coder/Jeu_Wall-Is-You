<div align="center">

# 🏰 Wall Is You

### Jeu de puzzle en Python — BUT Informatique 1 · SAE-01

*Vous n'êtes pas l'aventurier. Vous êtes le donjon.*

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FLTK](https://img.shields.io/badge/UI-FLTK-orange?style=flat-square)](https://pypi.org/project/fltk/)
[![Pillow](https://img.shields.io/badge/Images-Pillow-green?style=flat-square)](https://pillow.readthedocs.io/)
[![License](https://img.shields.io/badge/License-Academic-lightgrey?style=flat-square)]()

</div>

---

## 📖 Présentation

**Wall Is You** est un jeu de puzzle développé en Python dans le cadre d'un projet académique de première année de BUT Informatique.

Le concept inverse les rôles du jeu de donjon classique : **le joueur contrôle le donjon**, pas l'aventurier. Un aventurier autonome et particulièrement naïf s'aventure dans votre donjon pour en tuer les dragons. Votre mission ? **Réorienter les salles** pour lui tracer un chemin stratégique, placer des trésors pour le guider, et faire en sorte qu'il affronte les monstres dans le bon ordre — sans se faire tuer.

> *Chaque clic sur une salle la fait pivoter de 90° dans le sens horaire. Quand vous êtes prêt, appuyez sur Espace : l'aventurier suit sa ligne rouge et agit.*

---

## ✨ Fonctionnalités

### 🎮 Gameplay de base
| Action | Commande |
|--------|----------|
| Faire pivoter une salle | Clic droit |
| Valider le tour / déplacer l'aventurier | `Espace` |
| Définir manuellement la destination | Clic gauche |
| Placer un trésor | `Ctrl` + Clic droit |
| Sauvegarder la partie | `S` |
| Recommencer le niveau | `R` |
| Revenir au menu | `Échap` |

### 🧩 Variantes implémentées
- **Trésors** — Le donjon dispose d'un stock de trésors (défini par niveau). Placer un trésor dans une salle vide (`Ctrl + clic droit`) attire l'aventurier en priorité, même en présence de dragons accessibles. Un seul trésor actif à la fois. Outil stratégique indispensable pour certains niveaux.
- **Sauvegarde** — La partie en cours peut être enregistrée (`S`) dans un fichier JSON et rechargée automatiquement à la prochaine ouverture du même niveau.
- **Déplacement des dragons** — Après chaque tour de l'aventurier, chaque dragon survivant se déplace aléatoirement d'une case accessible. Si un dragon rencontre l'aventurier, les règles de combat s'appliquent normalement.

### ⭐ Bonus implémentés
| # | Nom | Description | Touche |
|---|-----|-------------|--------|
| 2 | **Indices** | Affiche en bleu un chemin possible vers le prochain dragon, même si les salles ne sont pas encore bien orientées | `I` |
| 4 | **Mode Tour Unique** | Joue un tour complet automatiquement : si un chemin existe, l'aventurier agit ; sinon, les dragons bougent quand même. Le jeu avance toujours. | `U` |
| 6 | **Plus courts chemins** | L'algorithme BFS garantit que l'aventurier emprunte systématiquement le chemin le plus court vers sa cible, sans détours inutiles | *(automatique)* |

---

## 🎯 Règles du jeu

```
┌─────────────────────────────────────────────────┐
│  L'aventurier commence au niveau 1.              │
│                                                  │
│  Il cible toujours le dragon de plus haut        │
│  niveau qui lui est accessible.                  │
│                                                  │
│  ✅  Dragon niveau ≤ joueur  →  il le tue        │
│       et gagne un niveau.                        │
│                                                  │
│  ❌  Dragon niveau > joueur  →  GAME OVER        │
│                                                  │
│  🏆  Tous les dragons vaincus  →  VICTOIRE !     │
│                                                  │
│  💎  Trésor accessible  →  priorité absolue      │
│       (l'aventurier ignore les dragons)          │
└─────────────────────────────────────────────────┘
```

**Votre rôle de donjon :**
- Réorienter les salles pour ouvrir ou fermer des passages
- Placer des trésors pour détourner l'aventurier
- Forcer l'aventurier à affronter les dragons dans un ordre précis
- Utiliser l'indice (ligne bleue) pour anticiper les réorientations nécessaires

---

## 🗂️ Structure du projet

```
wall-is-you/
│
├── jeu_principal.py       # Boucle principale, interface FLTK, événements
├── regles_jeu.py          # Logique métier : BFS, combats, dragons, sauvegardes
├── chargeur_donjon.py     # Lecture des fichiers .txt, construction de l'état
├── modele_donjon.py       # Structures de données : salles, personnages, trésor
│
├── donjon_4-5.txt         # Niveau 1  — grille 4 lignes × 5 colonnes
├── donjon_5-7.txt         # Niveau 2  — grille 5 lignes × 7 colonnes
├── donjon_6-10.txt        # Niveau 3  — grille 6 lignes × 10 colonnes
│
├── images/
│   ├── salle_1.gif        # Salle 1 passage
│   ├── salle_2_angle.gif  # Salle 2 passages en angle
│   ├── salle_2_opposes.gif
│   ├── salle_3.gif
│   ├── salle_4.gif
│   ├── A.gif              # Aventurier
│   ├── D1.gif             # Dragon niveau 1
│   ├── D2.gif             # Dragon niveau 2
│   ├── D3.gif             # Dragon niveau 3
│   └── tresor.gif
│
├── temporaire_images/     # Créé automatiquement au lancement
│   ├── salle_tournee_*    # Images GIF pré-calculées des rotations (cache)
│   └── sauvegarde_*.json  # Fichiers de sauvegarde par niveau
│
└── fltk.py                # Bibliothèque graphique (à placer à la racine)
```

---

## ⚙️ Installation et lancement

### Prérequis

- Python 3.8+
- `fltk.py` disponible dans le dossier racine du projet
- Bibliothèques Python :

```bash
pip install Pillow
```

> **Note :** Pillow est optionnel. Sans lui, les rotations d'images ne seront pas appliquées visuellement (les salles s'afficheront dans leur orientation par défaut), mais le jeu reste entièrement fonctionnel.

### Lancement

```bash
# 1. Cloner le dépôt
git clone https://github.com/<votre-username>/wall-is-you.git
cd wall-is-you

# 2. Installer les dépendances
pip install Pillow

# 3. Lancer le jeu
python jeu_principal.py
```

---

## 🗺️ Format des fichiers de niveaux

Les niveaux sont définis dans des fichiers `.txt` lisibles. Chaque salle est décrite par un caractère représentant ses passages :

| Caractère | Passages ouverts | ASCII | Unicode |
|-----------|-----------------|-------|---------|
| 4 directions | H · D · B · G | `+` | `╬` |
| 3 directions | H · D · B | `T` | `╠` `╦` `╣` `╩` |
| 2 directions (angle) | H · D | `L` | `╔` `╗` `╚` `╝` |
| 2 directions (opposés) | H · B | `\|` | `║` |
| 2 directions (opposés) | D · G | `-` | `═` |
| 1 direction | B seulement | *(1-passage)* | `╥` `╨` `╡` `╞` |

**Exemple de fichier de niveau :**
```
# Donjon 4x5
L 0 0          # salle ligne 0, colonne 0 — type L (passages H et D)
+ 0 4          # salle ligne 0, colonne 4 — type + (4 passages)
A 3 0 1        # Aventurier en (3,0), niveau 1
D 0 4 1        # Dragon niveau 1 en (0,4)
D 2 0 2        # Dragon niveau 2 en (2,0)
D 0 0 3        # Dragon niveau 3 en (0,0)
NB_TRESORS 2   # 2 trésors disponibles pour ce niveau
```

---

## 🔬 Choix techniques

### Architecture MVC

Le projet adopte une séparation claire des responsabilités :

- **Modèle** (`modele_donjon.py`) — Structures de données pures. Une salle = `[H, D, B, G]` (liste de 4 booléens). Un personnage = `{'pos': (l, c), 'niveau': n, 'est_joueur': bool}`.
- **Contrôleur** (`regles_jeu.py`) — Toute la logique métier : rotation, BFS, combats, interactions, déplacements.
- **Vue** (`jeu_principal.py`) — Interface FLTK, événements, dessin, cache d'images.
- **Chargeur** (`chargeur_donjon.py`) — Lecture des fichiers `.txt`, construction de l'état initial.

### Algorithme BFS (Bonus 6)

La recherche de chemin utilise un **BFS (Breadth-First Search)** qui garantit le chemin de longueur minimale.

```
Complexité : O(V + E)
  V = nombre de cases (sommets) = N × M
  E = nombre de passages ouverts (arêtes) ≤ 4 × N × M

Sur un niveau 6×10 (60 cases) : ~240 arêtes max → exécution instantanée.
```

Deux variantes du BFS coexistent :
- **BFS avec murs** → chemin d'intention rouge (passages réels uniquement)
- **BFS sans murs** → chemin d'indice bleu (Bonus 2, ignore les orientations)

### Système de cache d'images

Chaque rotation de salle génère une image GIF transformée via Pillow. Pour éviter de recalculer ces rotations à chaque rafraîchissement, un **cache** associe chaque paire `(chemin_image, angle)` à son fichier GIF pré-calculé dans `temporaire_images/`. Résultat : chaque rotation n'est calculée qu'une seule fois par session.

### Priorités de l'intention automatique

```
1. Trésor actif accessible    →  priorité absolue
2. Dragon le plus fort accessible et battable  →  automatique
3. Destination choisie manuellement (clic gauche)
```

---

## 👥 Équipe

| Membre | Rôle principal |
|--------|---------------|
| **BEN OUIRANE Waël** | Logique métier & Algorithmes (BFS, intention, Bonus 4 & 6) |
| **AHAMEDSAH Nayas** | Interface & Visuel (FLTK, rotations Pillow, cache, menus) |
| **LECHAR Millan** | Structures de données & Chargement (modèle, .txt, sauvegarde JSON) |

---

## 📚 Contexte académique

> Projet réalisé dans le cadre de la **SAE-01 — Initiation au développement**  
> **BUT Informatique 1** · Année 2025–2026  
> Rendu final (Rendu 3) incluant : Tâches 1–4 · Variantes 1–3 · Bonus 2, 4 & 6

---

<div align="center">

*Fait avec 🧱 et beaucoup de rotations de salles*

</div>
