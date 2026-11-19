# Journal des évolutions

## 2026-11-19 — Calibrage sourcé des surfaces et ailes débutant
- Surface générique encadrée par les tableaux SURF Magazin : plancher en vent faible (débutants jusqu’à 20 nds, programme vent léger, vent < 10 nds ; niveau ≥ 2 en freeride/glisse jusqu’à 15 nds), plafond au maximum « vent très léger ». Surf, saut et vitesse sans plancher.
- AFS Evo : colonne vent fort (> 20 nds) du tableau AFS.
- Ajout F-ONE Gravity (1800, 2200) et Armstrong CF V2 (950, 1200, 1600, 2050), dimensions constructeur, sans essai relié ni note : le niveau 0 n’avait qu’une famille.
- Balayage : premiers choix à plus de 150 cm² hors repère SURF ramenés de 382 à 36 profils (freeride/vent léger/glisse).
- Toujours absents : Gong, Sabfoil, Takuma, Indiana, North (tableaux de tailles officiels non relevés).

## 2026-11-19 — Corrections issues d’un balayage de 8 100 profils
- Silk V2 : le repère AFS (750 cm² à 75 kg) ne s’applique plus qu’au programme carving, conformément au tableau AFS (freeride : Enduro). Auparavant, un rider de 85 kg niveau 2 en freeride à 12 nds recevait une Silk V2 850 en tête.
- Classement : l’écart est aussi mesuré contre la cible générique du rider ; une famille dotée d’un repère constructeur n’obtient plus un écart nul automatique.
- Freeride : les familles spécialisées (surf, saut, vitesse) passent derrière les familles polyvalentes.
- Débutants (niveaux 0–1) avec un programme non adapté : 20 % des profils balayés n’obtenaient aucune aile ; l’interface affiche désormais la sélection freeride avec une explication.
- Limites constatées non corrigées faute de source chiffrée : surfaces des niveaux 3–4 souvent sous le repère SURF Magazin en vent léger ; une seule famille (AFS Evo) au niveau 0.

## 2026-11-19 — Onglet « Wing et montage »
- Taille de wing (aile à main) : repère SURF Magazin par poids et type de spot (intérieur 6–15 nds / côte 12–20+ nds), tailles Duotone Unit 2026 dont la plage publiée contient le vent courant, signal « vent au plancher de la plage ».
- Contrôle indépendant de chaque aile avant retenue contre les tableaux SURF Magazin (débutant/vent léger et expérimenté), avec écart en cm² ; tolérance explicite pour vent soutenu ou programme surf/saut/vitesse.
- Mât (75 / 75–85 / 82–85 / 85–90 / 90 cm), fuselage et allongement visé selon niveau, plan d’eau et programme (Duotone, SURF Magazin).
- Registre `data/research/expert_setup_guides.json`, test `test_expert_setup.js` (parité registre/code, bornes de poids, logique, sources) ajouté à la CI.
- Non intégré : taille de stabilisateur (aucune règle chiffrée dans les sources consultées) ; Gong Cruzader Point LW (la fiche officielle 2026 ne publie les dimensions complètes que pour la 5'9 80 L).

## 2026-11-19 — Cohérence catalogue, moteur et documentation
- `data/model_variants.json` couvre désormais les 149 tailles du moteur (40 ajoutées depuis les métadonnées embarquées, entrées existantes inchangées, aucune note). Nouvel outil `video-analysis/sync_model_variants.js` et contrôle `--check` dans `test_catalogue.js`.
- Comparateur : les lignes de notes 1–5 ne s’affichent plus lorsqu’aucune taille sélectionnée n’est notée ; les textes précisent qu’aucune note n’est publiée actuellement.
- Moteur : les repères AFS Enduro et Silk V2 conservent le facteur « vent léger » (1,18) déjà appliqué à la cible générique. Avant, ce programme était ignoré pour ces deux familles. Test de non-régression ajouté ; aucune nouvelle valeur ni note.
- README réécrit (mentions obsolètes de dépôt privé, Pages non activé et branche de travail retirées) ; pied de page daté du 19 novembre.

## 2026-11-19 — Documentation centrale du projet
- Ajout de `docs/FONCTIONNEMENT_ARCHITECTURE_ACCES.md` : objectif, flux vidéo et écrit, moteur, stockage public/local, accès, secrets, automatisations, publication et reprise après incident.
- Le README pointe vers ce document et indique désormais correctement que le dépôt et GitHub Pages sont publics.
- Ajout d’un contrôle de non-régression sur la présence du document, ses liens locaux et ses rubriques opérationnelles essentielles.

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
