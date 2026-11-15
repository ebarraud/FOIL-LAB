# FOIL LAB — Pipeline d'analyse des essais vidéo (pilote)

## Ce qui fonctionne

- File d'attente versionnée dans `manifest.json` (12 références de départ, complétées par le pilote AFS Hadou).
- Import **local et explicite** de sous-titres `.srt` ou `.vtt` fournis par un utilisateur ou récupérés légalement.
- Détection multilingue (français, allemand, anglais) de passages candidats concernant **takeoff, glide, carving, control**.
- Conservation des extraits courts, minutages, URL, langue et empreinte SHA-256.
- Export JSON avec le statut `transcript_keyword_candidates` : **aucun jugement de performance n'est généré automatiquement**.
- Tests Python hors ligne, exécutés via GitHub Actions sur les pull requests.

## Lancer une analyse

```bash
python video-analysis/analyze.py \
  --id gleiten-duotone-glide3-825 \
  --manifest video-analysis/manifest.json \
  --subtitles ./mes-transcriptions/glide-825.de.vtt \
  --language de \
  --output ./resultats/glide-825.candidates.json
```

L'analyse échoue explicitement si le fichier est vide ou sans horodatage. La CLI n'effectue **aucune connexion réseau** ni téléchargement de vidéo.

## Récupération des sous-titres : une étape séparée

1. Pour les vidéos YouTube que tu es autorisé à traiter, consulte d'abord la transcription publique du lecteur et les paramètres de sous-titrage.
2. Avec les autorisations nécessaires et dans le respect des conditions du service, `yt-dlp --list-subs URL` permet d'inspecter les pistes et `yt-dlp --skip-download --write-subs --sub-langs de,en,fr URL` peut exporter les sous-titres disponibles. Les sous-titres automatiques demandent `--write-auto-subs`. Ces commandes **ne sont pas exécutées automatiquement** dans GitHub.
3. Pour Gleiten.TV, utiliser des sous-titres ou transcriptions explicitement autorisés par la plateforme ou le créateur. En l'absence de transcription, conserver `index_only` ou `editorial_description_only`.
4. Pour les vidéos sans sous-titres et dont on dispose légalement de l'audio, une étape locale de transcription ASR (par exemple Whisper) peut être ajoutée séparément.

**Ne pas versionner les transcriptions intégrales ni les vidéos de tiers sans autorisation.** Le pipeline conserve uniquement des extraits brefs qui sont des *candidats à vérifier* ; la publication de tout extrait doit respecter les règles applicables.

## Validation éditoriale avant une note

Pour chaque passage candidat, contrôler manuellement :
- le contexte avant/après et une éventuelle négation, ironie ou comparaison ;
- la marque, la génération et la **taille réellement testée** ;
- le rider, la board, le mât, le stabilisateur et les conditions ;
- le sens réel des mots (par exemple « pumping » = propulsion, pas nécessairement meilleure glisse) ;
- l'indépendance du testeur et une possible reprise/traduction d'un essai existant.

Ensuite seulement, créer une affirmation **validée** avec source, contexte, date et niveau de confiance. Aucun score ne doit être écrit automatiquement dans `data/model_variants.json`.

## Ce qui reste à développer

- Découverte automatisée de nouvelles vidéos via APIs/feeds autorisés.
- Traitement ASR du contenu audio auquel on dispose légalement d'un accès.
- Extraction sémantique revue par un humain (plus nuancée que les mots-clés).
- Interface de validation des passages, et connexion à la base de connaissances FOIL LAB.
- Lot pilote de 20 transcriptions *réellement obtenues* pour mesurer la couverture.

## Principe de traçabilité

`index_only` ≠ `editorial_description_only` ≠ `transcript_keyword_candidates` ≠ `human_verified_claims` ≠ `full_video_reviewed`.

Le fichier `manifest.json` distingue les **références à traiter** et les transcriptions examinées ; une entrée ne signifie pas que la vidéo a été intégralement regardée. Les liens renvoyant à une page d'index doivent être remplacés par l'URL précise de chaque vidéo avant une transcription.

## Premier pilote réel — 3 essais (novembre 2026)

Le rapport [Pilote de trois essais](../research/PILOTE_3_TESTS_VIDEO_2026-11-15.md) documente les vidéos AFS Silk V2, Duotone Glide 3.0 D/LAB 825 et KT Halo 670/800. Leurs URL sont préremplies dans [l'interface mobile](review.html) via **« Essai pilote »**. Les trois transcriptions ont été effectivement récupérées et examinées le 15/11/2026. Les fichiers intégraux restent hors Git ; le dépôt publie des preuves courtes et des synthèses avec minutages et limites. Ne pas confondre l'examen du texte transcrit avec le visionnage de la vidéo.

**Import de transcription YouTube horodatée :**

1. Depuis la vidéo YouTube, ouvrir la description et l'option **Afficher la transcription** si elle est proposée. Les fonctions de sélection/copie peuvent dépendre du navigateur, du terminal, de la vidéo et des réglages du créateur. Si le texte n'est pas copiable, demander un fichier SRT/VTT au média ou utiliser une transcription légalement fournie.
2. Conserver les **minutages** avec le texte (par exemple `0:15 Der Start ist einfach` ou `0:15` suivi de `Der Start ist einfach` sur la ligne suivante). **Un texte sans minutage est volontairement refusé.**
3. Ouvrir `https://ebarraud.github.io/FOIL-LAB/video-analysis/review.html` dans Chrome, sélectionner le modèle, coller le texte ou importer un fichier `.txt`, `.srt` ou `.vtt`.
4. Cliquer **Analyser les passages** puis vérifier la taille du foil réellement testée, le sens des comparaisons, les négations et le contexte. Exporter ensuite le JSON des passages candidats ; aucune note n'est ajoutée automatiquement.

Le script local `analyze.py` accepte aussi `--subtitles ./transcription-horodatee.txt` et renseigne `transcript_format=youtube_timestamped_copy`. Il **n'invente jamais la durée du dernier passage** et ne télécharge aucun média.


## Chaîne locale audio autorisé → Whisper → observations horodatées

Le script `video-analysis/transcribe_local.py` traite **uniquement** un fichier audio ou vidéo déjà présent localement, et seulement après confirmation que son traitement est autorisé. Il ne télécharge aucune vidéo de YouTube ou Gleiten.TV. L'ASR peut être imprécise : son résultat est à vérifier avant attribution d'une observation.

Installation sur un ordinateur disposant de Python 3.12 et, selon le format, de FFmpeg :

```bash
python -m pip install faster-whisper
```

Exemple avec une **copie audio fournie avec autorisation** pour le test AFS Silk V2 :

```bash
python video-analysis/transcribe_local.py \
  --audio ./media-autorise/afs-silk-v2.m4a \
  --language fr \
  --video-id youtube-DMlWjjIcwss \
  --video-title "AFS Silk V2 650/750/950" \
  --video-url "https://www.youtube.com/watch?v=DMlWjjIcwss" \
  --publisher "Pimpyourride" \
  --confirm-media-rights
```

Deux sorties locales non versionnées sont produites sous `video-analysis/local-results/` : un SRT horodaté, et un JSON contenant les passages techniques détectés, un hash de l'audio, la provenance et le statut de validation. **Le système ne génère aucune note automatique.** Cette procédure fonctionne également pour le Duotone et le KT, à condition de disposer du média dans des conditions autorisées.

## Registre public des preuves

La page [evidence.html](evidence.html) lit directement le JSON source du pilote et distingue observations écrites, réponses d'auteurs et fiches vidéo sans contenu technique. Le lien public est https://ebarraud.github.io/FOIL-LAB/video-analysis/evidence.html. Elle permet de consulter les trois modèles et les tailles exactes sans confondre observations vérifiées et analyses vidéo intégrales.

**État vérifié au 15/11/2026 : 3 transcriptions acquises gratuitement**, soit 834, 218 et 236 segments. Les 159 segments contenant des mots-clés sont des candidats, pas 159 affirmations validées. Les tests logiciels utilisent des réponses simulées ; la preuve d'acquisition réelle est distincte (artefact et empreintes du lot pilote).

## Ancienne option via fournisseur payant (désactivée par défaut)

Les tentatives directes `yt-dlp --list-subs` depuis GitHub Actions ont échoué même pour des vidéos signalées comme sous-titrées par l'API YouTube. La clé GitHub `YOUTUBE_APU` sert **uniquement** à la recherche et aux métadonnées.

Le workflow manuel historique [Pilot genuine YouTube transcripts (opt-in)](../.github/workflows/hosted-transcript-pilot.yml) utilise, de façon optionnelle, l'API documentée de [TranscriptAPI.com](https://transcriptapi.com/docs/getting-started/). Le service est tiers, indépendant de YouTube et peut facturer des crédits ; son usage doit respecter les conditions et droits applicables.

**Cette option n'est pas nécessaire pour le pilote gratuit. Elle ne doit être utilisée qu'avec une autorisation distincte de frais :**

1. Souscrire et disposer d'une clé d'API du fournisseur, selon ses conditions. Ne pas placer cette clé dans les fichiers du dépôt, dans le navigateur, ni dans le chat.
2. Créer un secret GitHub Actions nommé exactement **`TRANSCRIPT_API_KEY`** sous Settings → Secrets and variables → Actions.
3. Dans Actions, choisir **Pilot genuine YouTube transcripts (opt-in)** et déclencher `Run workflow`. L'option `confirm_provider_charges` est par défaut `no` : le programme ne facture alors rien, même si une clé existe.
4. Choisir `yes` seulement si l'utilisation de crédits a été explicitement autorisée ; le nombre de vidéos est limité à 1–3 par exécution.
5. Consulter le rapport généré en artefact GitHub : les extraits techniques courts sont horodatés. Le texte intégral des vidéos n'est pas conservé dans le dépôt ni dans l'artefact.

La première sélection comprend **AFS Silk V2**, **Duotone Glide 3.0 D/LAB 825** et **KT Halo**. Le programme valide les segments obtenus (`start`, `duration`, `text`), conserve les horodatages, détecte les mots-clés et produit des liens YouTube vers les passages. **Il n'attribue aucune note et ne qualifie pas les extraits de conclusions tant qu'ils ne sont pas validés.**

Sans clé et autorisation de frais, cette ancienne option reste désactivée. Le pipeline gratuit décrit ci-dessous n'appelle pas ce fournisseur et ne lit aucune clé payante.


## Pilote gratuit : tous les candidats et reprise hors ligne

`free_transcript_pilot.py` utilise uniquement l'endpoint public anonyme de FreeTranscriptAPI, sans clé ni crédit payant. La disponibilité d'un service tiers n'est pas garantie. Le schéma v2 conserve **tous les segments correspondant aux mots-clés**, dans l'ordre chronologique : le plafond de 18 par vidéo est supprimé. Sur les mêmes transcriptions que l'exécution [43732427647](https://github.com/ebarraud/FOIL-LAB/actions/runs/43732427647), cela représente 120 + 25 + 14 = **159 candidats**, contre 18 + 18 + 14 = 50 auparavant. Les empreintes normalisées SHA-256 sont identiques aux trois empreintes de l'artefact d'origine.

Acquisition gratuite et cache **local optionnel** pour lire le contexte complet :

```bash
python video-analysis/free_transcript_pilot.py \
  --limit 3 \
  --cache-dir video-analysis/local-results/transcripts \
  --output video-analysis/local-results/free-transcript-pilot.json
```

Retraitement strictement hors ligne, sans nouvel appel réseau :

```bash
python video-analysis/free_transcript_pilot.py \
  --input-dir video-analysis/local-results/transcripts \
  --context-seconds 8 \
  --output video-analysis/local-results/free-transcript-pilot.json
```

Chaque fichier d'entrée est nommé `VIDEO_ID.json` (par exemple `DMlWjjIcwss.json`). Il peut contenir la réponse JSON originale du fournisseur ou un cache normalisé produit par `--cache-dir`. Un cache normalisé est vérifié par son identifiant vidéo et son SHA-256. Un fichier absent, invalide ou modifié produit un échec explicite pour cette vidéo, sans repli sur le réseau. Le cache n'est pas écrit sans `--cache-dir` ; les transcriptions intégrales ne doivent pas être versionnées ou publiées sans autorisation.

Le rapport comporte :

- `technical_keyword_segments` : nombre de segments ayant au moins une catégorie, **pas un nombre d'occurrences lexicales ni de conclusions** ;
- `keyword_category_segment_counts` et `keyword_category_matches` : compteurs par catégorie, avec chevauchement possible ;
- `candidate_count`, `candidates_omitted` et `candidate_selection` : couverture explicite, sans plafond silencieux ;
- pour chaque candidat : identifiant stable basé sur l'index, début, fin, extrait de 130 caractères au maximum et indicateur de troncature ;
- `context` : bornes, indices des segments et lien minuté couvrant les 8 secondes avant/après par défaut ; le texte de contexte reste dans le cache local ;
- `size_mentions` : mentions numériques des tailles recherchées, y compris dans les segments sans mot-clé ; `size_hints_in_segment` et `size_hints_in_context` distinguent la position des mentions ;
- `size_tested`, `claim` et `polarity` restent `null` ; aucun score n'est produit.

Les indices sont comptés à partir de zéro dans le tableau `segments` du cache normalisé. Ils permettent de retrouver le contexte exact et la fin du passage, notamment une négation ou une comparaison placée dans le segment suivant. La fenêtre se règle avec `--context-seconds` ; pour une analyse approfondie, lire également les autres passages de la transcription complète.

Les tailles du titre servent uniquement de **pistes numériques non validées** : elles ne prouvent ni la taille testée ni la portée d'une observation. Une taille voisine peut désigner un autre foil, une comparaison ou une erreur de sous-titrage. Le repérage ne comprend pas toutes les formes dictées des nombres et ne résout pas les erreurs ASR. Le vocabulaire de mots-clés du premier pilote est conservé pour comparer honnêtement la couverture : il peut manquer des propos techniques et détecter des faux positifs. Le texte doit être examiné avant toute conclusion.

Validation du pipeline :

```bash
python -m unittest discover -s video-analysis -p 'test_*.py' -v
```

Les tests vérifient notamment la conservation des candidats après le 18e, les limites et comparaisons dans le contexte, l'absence d'attribution automatique des tailles, les temps non finis, les caches altérés, la reprise hors ligne et la conservation des empreintes.
