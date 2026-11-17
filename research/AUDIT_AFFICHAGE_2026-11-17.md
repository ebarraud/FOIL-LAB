# Audit des omissions d’affichage — 17 novembre 2026

Les cinq pages HTML ont été examinées : configurateur, suivi, preuves, lectures vidéo et import de transcription. La présence de preuves dans un JSON ne suffisait pas à les rendre accessibles partout.

Corrections :

- `evidence.html` ne chargeait que les trois pilotes et quatre essais écrits. Il charge désormais les sept registres nécessaires et rassemble 177 dossiers : 166 dossiers vidéo examinés et 11 essais écrits. Ce ne sont pas 177 modèles distincts, ni 177 essais indépendants.
- Recherche par modèle ou éditeur, sélection de dossier, types de sources et tailles/volumes explicitement distingués. Les notes dont la taille est commune ou non isolée gardent leur réserve ; elles ne deviennent pas des preuves spécifiques par simple filtrage.
- Les trois pilotes, le dossier board isolé, les 162 lectures du registre, les quatre anciens essais écrits et les sept nouveaux essais écrits sont couverts par un test de complétude. Les pistes d’articles non lus restent exclues du compteur.
- Encadré pilote du configurateur et lien de l’outil d’import renommés pour ne plus présenter trois exemples comme la totalité. La page des lectures vidéo pointe vers le registre complet.
- L’import ne masque plus silencieusement les candidats après le 120e. Le texte complet n’est pas publié : ce sont uniquement des extraits du texte importé localement par l’utilisateur.
- Des espaces finaux dans les noms Pasty Adventures et Wingfoil Max créaient de faux «0 vidéo collectée» et deux choix d’éditeur. Les noms sont normalisés par identité de chaîne et espaces retirés. Test de régression ajouté.
- Échec partiel de chargement signalé, résultats des autres registres conservés, état vide explicite.

Validation : 83 tests Python, quatre suites JavaScript (recommandations, catalogue, couverture des preuves et liens internes), contrôle syntaxique des pages/scripts, empreintes et bornes temporelles des 162 lectures. Les tests contrôlent la présence de chaque source ; ils ne prouvent pas l’exactitude de chaque appréciation technique ou l’absence de tout autre défaut.
