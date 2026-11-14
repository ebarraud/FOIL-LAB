# Journal des évolutions

## 2026-11-14
- Dépôt GitHub initialisé.
- Documentation méthodologique et registre de sources ajoutés.
- Import du configurateur V4 et du catalogue structuré : **à effectuer**.
- Notes par modèle : à vérifier progressivement avec les preuves spécifiques à chaque taille.

## 2026-11-14 — Migration V5
- Import effectif du configurateur V4 dans `index.html`.
- Refonte mobile-first : parcours en trois étapes, progression, navigation tactile, recommandations dépliées en fin de parcours, accessibilité clavier.
- Export du registre structuré en `data/model_variants.json` (72 ailes et 37 boards).
- **À faire :** lier dynamiquement le JSON au moteur, compléter les preuves par taille et tester sur appareils physiques ; GitHub Pages pas encore activé.

## 2026-11-14 — V5, synchronisation du catalogue
- En lecture HTTP(S), chargement de `data/model_variants.json` dans les fiches de comparaison et de recommandation.
- En mode `file://`, conservation du jeu de données intégré comme solution de repli.
- Confiance des notes propre à la variante (ne plus la déduire automatiquement d’un seul essai).
- Travail préparé sur branche dédiée, en attente de revue avant fusion sur `main`.
- Les règles de présélection par profil demeurent embarquées et doivent être progressivement alignées sur les variantes JSON.
