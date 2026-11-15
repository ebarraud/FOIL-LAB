# Journal des évolutions

## 2026-11-15 — Transcriptions accessibles et preuves par taille
- Artefact du run 43732427647 téléchargé et inspecté : 50 extraits conservés pour 159 segments avec mots-clés.
- Trois transcriptions complètes récupérées anonymement sans crédit; 1 288 segments, empreintes identiques à l'exécution initiale.
- 30 synthèses minutées ajoutées : AFS 12, Duotone 8, KT 10. Source, montage, portée de taille, limites et absence de contrôle audio documentés.
- Pipeline sans plafond de 18 : 159 candidats conservés, contexte référencé, cache local optionnel et reprise sans réseau.
- Registre consultable par modèle, taille et type de source. Aucun score du catalogue créé ou modifié.

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

## 2026-11-15 — Première règle de recommandation issue des transcriptions
- Silk V2 : si la sélection initiale aboutit à 650 et que la priorité est la facilité ou que le niveau est inférieur à 3, retenir au minimum 750. Précaution éditoriale issue de la comparaison 23:18–23:46; aucun seuil mesuré ni score créé.
- Ajouter dans les recommandations les limites de montage et la distinction surf foil / plage basse wing pour la 950.
- Vérification du moteur sur profils facilité et performance par test_recommendations.js, plus 68 tests Python.
- Duotone Glide 3.0 et KT Halo restent hors classement tant que leurs fiches catalogue ne sont pas suffisamment complètes.
