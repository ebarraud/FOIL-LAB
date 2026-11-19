# Audit des formulaires — 19 novembre 2026

Périmètre : les cinq pages HTML publiées, leurs champs statiques et listes construites en JavaScript. Contrôles hors réseau exécutés sur les registres réels ; ce bilan ne prétend pas certifier tous les navigateurs ni tous les profils possibles.

- Profil, pratique et matériel : labels associés aux champs ; largeur et longueur hors des plages déclarées bloquent les résultats avec explication plutôt que produire une sélection trompeuse. Les contrôles de recommandations couvrent les exclusions de niveau, programme, taille et génération.
- Catalogue : complétude des 149 variantes du moteur et 57 fiches étendues ; absence de notes inventées ; rattachement des preuves aux tailles exactes ; sélection et filtres des preuves contrôlés par les suites catalogue et bibliothèque.
- Sources : inventaire dédupliqué de 296 références, dont 211 vidéos ; les liens de veille restent distincts des lectures réalisées.
- Tableau de bord : tous les choix d'étape, chaque éditeur et chaque langue du registre sont exercés. Les résultats par éditeur/langue correspondent aux effectifs du fichier publié.
- Registre des preuves : 199 dossiers provenant des différents registres, filtres et unités vérifiés ; avertissement de chargement partiel présent.
- Lecteur d'analyses : les 174 options du registre vidéo sont disponibles ; une URL demandant un dossier absent affiche désormais une explication au lieu d'ouvrir silencieusement le premier dossier.
- Import de transcription : 211 références chargées dynamiquement ; échec de chargement explicite ; 150 passages candidats conservés sans limite de 120 ; refus du texte sans minutage et des URL à protocole exécutable ; remise à zéro du texte, des résultats et de la langue.

Validation : 84 tests Python et cinq suites JavaScript réussis. La nouvelle suite test_forms.js est exécutée dans GitHub Actions pour prévenir les régressions. Aucun appel au fournisseur de transcriptions, aucune nouvelle analyse technique ni règle hydrodynamique revendiquée par cet audit.
