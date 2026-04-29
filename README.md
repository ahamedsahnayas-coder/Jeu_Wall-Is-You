# Wall Is You — Jeu de puzzle en Python

Projet réalisé en binôme dans le cadre de la SAE-01 du BUT Informatique 1 (2025-2026).

Wall Is You est un jeu de puzzle où **vous contrôlez le donjon**, pas l'aventurier.
Un aventurier se déplace automatiquement dans votre donjon et cherche à tuer les dragons.
Votre rôle est de réorienter les salles pour lui tracer le bon chemin, et de l'aider à
affronter les monstres dans le bon ordre sans se faire tuer.

---

## Lancer le jeu

Avoir Python 3 et `fltk.py` dans le même dossier que les fichiers du projet.

Puis lancer :
```bash
python jeu_principal.py
```

---

## Commandes

| Action | Commande |
|--------|----------|
| Tourner une salle | Clic droit |
| Valider le tour | Espace |
| Choisir une destination manuellement | Clic gauche |
| Placer un trésor | Ctrl + Clic droit |
| Afficher l'indice (ligne bleue) | I |
| Mode automatique (tour unique) | U |
| Sauvegarder | S |
| Recommencer | R |
| Menu principal | Échap |

---

## Fonctionnalités

- **3 niveaux** : 4×5, 5×7 et 6×10
- **Intention automatique** : une ligne rouge indique en permanence le chemin de l'aventurier
- **Trésors** : placer un trésor attire l'aventurier en priorité, utile pour le guider
- **Sauvegarde** : la partie est sauvegardée dans un fichier JSON et rechargée automatiquement
- **Déplacement des dragons** : après chaque tour, les dragons bougent aléatoirement
- **Indice** (touche I) : affiche un chemin possible même si les salles sont mal orientées
- **Mode tour unique** (touche U) : joue un tour complet automatiquement, même si l'aventurier ne peut pas bouger (les dragons bougent quand même)
- **Plus courts chemins** : l'algorithme BFS garantit que l'aventurier prend toujours le chemin le plus court

---

## Organisation du code

```
├── jeu_principal.py     # Interface graphique et boucle principale
├── regles_jeu.py        # Logique du jeu (BFS, combats, déplacements...)
├── chargeur_donjon.py   # Lecture des fichiers de niveaux (.txt)
├── modele_donjon.py     # Structures de données (salles, personnages, trésor)
├── donjon_4-5.txt
├── donjon_5-7.txt
├── donjon_6-10.txt
└── images/              # Ressources graphiques (.gif)
```

---

## Réalisé par

**Nayas AHAMEDSAH** — Interface & Visuel
- Design des menus et ergonomie générale
- Rotation des images de salles via Pillow
- Système de cache pour optimiser les performances
- Gestion des ressources graphiques dans `temporaire_images/`

**Waël BEN OUIRANE** — Logique métier & Algorithmes
- Algorithme de recherche de chemin BFS (`regles_jeu.py`)
- Calcul de l'intention automatique et indice (ligne bleue)
- Mode tour unique (touche `U`)
- Gestion des combats et conditions de fin de partie

**Millan LECHAR** — Structures de données & Chargement
- Structures de données dans `modele_donjon.py` (salles, personnages, trésor)
- Chargement des niveaux depuis les fichiers `.txt` (`chargeur_donjon.py`)
- Système de sauvegarde et chargement au format JSON
