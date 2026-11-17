# Audit de couverture et d’intégration — 16 novembre 2026

L’objectif est la qualité du configurateur, pas le volume de références. Cette revue couvre les chemins de découverte, qualification, collecte, métadonnées, publication et catalogue, les scripts Python compilables, les scripts JavaScript embarqués et les workflows. Les tests ne constituent pas une garantie d’absence de tout défaut.

## Défauts corrigés et vérifications

- Recherche écrite limitée à un seul éditeur et domaine Pimpyourride : registre étendu à Tonic Mag (foils/planches), Foiling Magazine, Wingpassion et MACkite. Chaque éditeur garde son statut d’accès. Les articles de même éditeur ne sont pas des sources indépendantes supplémentaires.
- Titres d’index sans le mot « review » perdus : reconnaissance des liens d’articles dans les rubriques de tests, sans transformer les liens en verdicts. Pagination, filtres de rubrique et domaines externes rejetés. Test simulant un autre éditeur et un lien externe ajouté.
- Modèles sans tableau de notes invisibles dans le catalogue : tous les volumes et tailles déjà référencés sont affichables, avec « Non noté » au lieu d’un score fabriqué. Test de complétude comparant le catalogue aux familles du moteur ajouté.
- Analyses conservées dans des fichiers mais peu consultables : bibliothèque de synthèses vidéo et écrites intégrée au catalogue. Les textes externes sont affichés via textContent. Les nouveaux essais historiques F-ONE restent séparés des SK8 V3/TITAN 2.
- Pilotes Glide/Halo et certaines planches sans rattachement au filtre de taille essayée : registre de liens explicites famille/taille/génération ajouté, avec limites de transcription et absence de contrôle audio.
- Langue allemande imposée au pilote de disponibilité : langue inconnue désormais « auto », langue connue préservée. Test ajouté.
- Noms de chaînes présents dans l’API mais non reportés : channelTitle conservé dans publisher. KiteWorld Shop : deux URLs et l’auteur @kiteworldshop vérifiés par YouTube oEmbed ; aucun essai technique revendiqué sur la seule base de cette vérification.
- Groupement de titres effaçant années et construction D/LAB : ces éléments sont préservés pour éviter les rapprochements trompeurs. Les groupes de titres restent des candidats, jamais des doublons supprimés automatiquement.
- Recherche YouTube poursuivie après blocage : arrêt sur401/403/429/5xx et délai persistant. Les chaînes connues passent avant les requêtes générales. Enrichissement et sondes tiennent compte de ce délai. Test vérifiant un seul appel puis aucun pendant la pause ajouté.
- Nombre de requêtes de métadonnées théorique : compteur remplacé par les appels effectivement lancés ; arrêt après erreur bloquante. Test ajouté.
- Extraction de mots-clés de sous-titres nommée « transcript_analyzed » : statut technique remis à false, champ keyword_candidates_extracted séparé.
- Ancien pilote gratuit exécuté automatiquement à chaque changement : exécution réseau désormais manuelle ; tests hors réseau conservés en CI, respect de la pause et arrêt après blocage dans le pilote. Pas de recours payant.
- CI ne couvrant pas index.html et le catalogue : déclencheurs élargis et tests JavaScript des recommandations et du catalogue ajoutés.

## Enrichissement publié avec cette revue

- 80 pistes d’articles trouvées dans les index accessibles de plusieurs éditeurs, non comptées comme articles analysés.
- Sept corps d’essais écrits lus et résumés brièvement : SK8 950 2023, Seven Seas 1400 première génération, Phantom Carbon1780 2021, ancien Phantom1080 (surf prone), ancien Gravity Carbon2200, Cabrinha Prestige905 2026 et StarboardMF820 2026 (SUP downwind seulement). Empreintes HTML enregistrées ; aucune copie intégrale publiée.
- Neuf références fabricant F-ONE EAGLE X et ESCAPE TITAN2 ajoutées sans note et sans statut « testé ». Géométrie issue des tableaux fabricant ; montage à vérifier.
- Le catalogue passe de109 à164 tailles consultables :148 tailles déjà présentes dans les familles du moteur, plus16 fiches explicitement sourcées. Cela ne signifie pas158 essais ni158 nouvelles recommandations.
-139 études consultables au moment de cette livraison :128 revues de transcriptions, quatre essais écrits déjà documentés et sept nouveaux. Certaines sont des qualifications hors périmètre ou du contenu limité ; leur méthode est affichée. Plusieurs relatent le même auteur ou un même essai sur deux supports.

## Validation

81 tests Python, deux suites JavaScript, compilation des scripts Python, vérification syntaxique des scripts HTML, contrôle des empreintes et bornes temporelles des128 revues locales : réussis. Vérification navigateur locale :164 tailles ; recherche F-ONE avec filtre exact donne cinq essais historiques séparés ; comparaison de fiches sans notes affiche « Non noté », sans erreur console observée.

## Travail restant explicite

L’exploration du Web n’est pas exhaustive. Les80 pistes écrites ne sont pas80 essais lus. La collecte de transcriptions reste limitée par les délais fournisseur. Les essais lus ne modifient le moteur qu’après identification fiable du produit et du montage. Les associations restantes et les nouvelles références doivent continuer à être traitées par lots, sans déclarer tout Internet ou tous les modèles vérifiés.

Complément : les deux textes KiteWorld Shop WAKA Glide77L et Code680R ont ensuite été lus intégralement. WAKA : cinq volumes fabricant et contraintes de niveau ; Code680R : option avancée glisse, aucun saut, aucune réduction automatique de surface. Le filtre exact reçoit les liens des essais pilotes et des tailles de planches effectivement identifiées.

Autre défaut constaté : les109 anciennes variantes héritaient de notes numériques explicitement non validées dans leur propre fichier source. Ces notes ont été retirées et ne sont pas remplacées. Le catalogue conserve les métadonnées et les preuves sans transformer un avis qualitatif en score. Un éventuel barème ultérieur devra être explicitement validé.
