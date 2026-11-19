# FOIL LAB EXPERT

Configurateur indépendant d'aide au choix de **foils et boards de wingfoil**.

- Site public : <https://ebarraud.github.io/FOIL-LAB/>
- **Documentation centrale :** [fonctionnement, objectif, architecture, stockage et accès](docs/FONCTIONNEMENT_ARCHITECTURE_ACCES.md)

Le dépôt et le site GitHub Pages sont publics. Les transcriptions intégrales, caches locaux et secrets restent hors Git.

## Objectif
Proposer une sélection restreinte (jusqu'à trois ailes avant et trois boards) adaptée au rider, complétée par la taille de wing et le montage (mât, fuselage, allongement) d'après des repères sourcés, en distinguant les spécifications constructeur, les essais indépendants, les retours des pratiquants et les extrapolations.

## Organisation
- `index.html` — configurateur mobile (profil, conditions, matériel), moteur de recommandation et catalogue embarqué.
- `data/model_variants.json` — une entrée par taille du moteur : métadonnées, confiance, sources. Aucune note de performance n'est publiée (`qualitative_scores: null`).
- `data/research/expert_setup_guides.json` — repères sourcés de l'onglet « Wing et montage » (tailles de wing, plages constructeur, mât, fuselage, allongement), vérifiés par `test_expert_setup.js`.
- `data/research/` — registres publics des preuves (transcriptions lues, essais écrits, liens preuve → taille, décisions).
- `progress.html`, `video-analysis/evidence.html`, `video-analysis/reviews.html`, `video-analysis/review.html` — suivi, registre des preuves, lectures et import local.
- `docs/METHODOLOGY.md` — méthode d'évaluation ; `research/CHANGELOG.md` — historique.

Les compteurs courants (vidéos, analyses, essais, tailles) se lisent dans le tableau de bord et les fichiers d'état ; ils ne sont pas recopiés ici.

## Mise à jour du catalogue
1. Modifier les familles et tailles dans `index.html` (`FOILS`, `BOARDS`, `KB_FOILS`, `KB_BOARDS`, `VERIFY`).
2. Lancer `node video-analysis/sync_model_variants.js` : les tailles nouvelles sont ajoutées à `data/model_variants.json`, les entrées existantes sont conservées telles quelles. `--check` signale tout écart (contrôlé en CI par `test_catalogue.js`).
3. Relier les preuves à la taille exacte dans `data/research/catalogue_evidence_links.json`.

En ligne, le configurateur relit le JSON et les registres au démarrage. Ouvert en `file://`, il utilise ses données intégrées.

## Validation
```text
python -m unittest discover -s video-analysis -p "test_*.py" -q
node video-analysis/test_recommendations.js
node video-analysis/test_catalogue.js
node video-analysis/test_evidence_library.js
node video-analysis/test_site_links.js
node video-analysis/test_forms.js
node video-analysis/test_expert_setup.js
```

## Précautions
Aucune note de décollage, glisse, carving ou contrôle n'est actuellement publiée ; un barème futur serait ordinal et éditorial (1–5), pas une mesure physique. Les surfaces et volumes recommandés sont des hypothèses de sélection. Les compatibilités de composants doivent être vérifiées par génération et constructeur. Aucun contenu tiers ne doit être copié sans respecter sa licence.
