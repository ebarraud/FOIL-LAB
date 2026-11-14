# Acquisition de transcriptions : pilote vérifiable

Le module `acquire.py` ajoute un **essai réseau contrôlé** à l'analyse locale de `analyze.py`. Le traitement est destiné aux sous-titres accessibles dans le respect des droits et des conditions des plateformes. Il ne contourne aucune restriction, ne récupère pas la vidéo ni l'audio, ne stocke pas les transcriptions complètes dans Git et n'ouvre pas de session utilisateur.

## Deux commandes séparées

**Vérifier la disponibilité (sans récupérer les sous-titres)**

```bash
python -m pip install yt-dlp
python video-analysis/acquire.py --mode probe --publisher YouTube --limit 2 --output probes/youtube.json
python video-analysis/acquire.py --mode probe --publisher Gleiten.TV --limit 3 --output probes/gleiten.json
```

**Analyser des sous-titres accessibles et dont le traitement est autorisé**

```bash
python video-analysis/acquire.py --mode fetch --accept-platform-terms --publisher YouTube --limit 2 --output probes/youtube-fetch.json
```

Le mode `fetch` ne conserve pas les transcriptions : il calcule les nombres de passages candidats par thème, puis supprime les fichiers temporaires. Il ne produit **aucune note** et ne classe **aucun modèle**. Les conclusions détaillées nécessitent encore une transcription autorisée analysée avec `analyze.py`, puis une validation humaine.

## Essai GitHub Actions

Le workflow `Video Caption Acquisition Pilot` lance les tests et une vérification réseau sur les deux URLs YouTube et trois pages Gleiten.TV déjà identifiées. Les résultats sont des **statuts** (accès réussi, lien non exploitable, sous-titres éventuellement repérés, restrictions réseau), enregistrés dans un artefact temporaire. Le workflow **n'exécute pas `fetch`** et ne distribue aucun sous-titre.

Les erreurs réseau et les refus d'accès sont des résultats du test, pas des preuves d'absence de sous-titres ou d'échec du modèle d'IA.

## Limitations connues

- Certains domaines ne sont pas gérés par un extracteur yt-dlp, même lorsque les vidéos sont publiques.
- Le fournisseur peut bloquer les serveurs GitHub Actions (403/429, CAPTCHA). Ne pas contourner de restrictions.
- Les sous-titres automatiques transcrivent parfois incorrectement les termes de foil, et les traductions peuvent introduire des erreurs.
- Une comparaison ne compte qu'un testeur indépendant par essai original : une version allemande et sa traduction ne forment pas deux avis distincts.
- Les contenus de Gleiten.TV peuvent ne pas avoir de piste de sous-titres disponible. Dans ce cas, demander une transcription autorisée au média ou analyser son compte rendu éditorial.
- Le mode `probe` ne confirme pas le contenu technique et ne peut pas attribuer de note de performance.

## Étape de validation suivante

Après le rapport de disponibilité, traiter prioritairement les sous-titres réellement accessibles, importer les passages horodatés vers des preuves révisées et relier ces preuves à la variante exacte du modèle (taille, millésime, montage). Ne pas mettre à jour automatiquement le moteur de recommandation sans recoupement.

## Utilisation depuis le téléphone

L'application publiée contient aussi `/video-analysis/review.html`. Elle permet de **sélectionner un fichier SRT/VTT ou coller une transcription horodatée dans Chrome sur Android**, d'identifier localement les passages techniques et d'exporter les candidats JSON. Aucune transcription n'est envoyée au serveur. L'écran est accessible depuis la rubrique Sources de FOIL LAB.

L'outil signale explicitement **zéro note validée** : il ne remplace pas une analyse éditoriale contextualisée.

## Résultat réel de la première sonde GitHub

Voir [REPORT_2026-11-14.md](REPORT_2026-11-14.md) : deux liens YouTube ont renvoyé des erreurs de réseau/extraction et trois pages Gleiten.TV ont été rejetées comme non prises en charge. **Aucune transcription récupérée dans ce premier lot.** Ce n'est pas la preuve que les sous-titres n'existent pas.
