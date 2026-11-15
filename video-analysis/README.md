# FOIL LAB — Pipeline d'analyse des essais vidéo (pilote)

## Ce qui fonctionne

- File d'attente versionnée dans `manifest.json` (12 références de départ).
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

Le fichier `manifest.json` contient des **références à traiter**, pas 12 analyses réalisées. Les liens renvoyant à une page d'index doivent être remplacés par l'URL précise de chaque vidéo avant une transcription.

## Premier pilote réel — 3 essais (novembre 2026)

Le rapport [Pilote de trois essais](../research/PILOTE_3_TESTS_VIDEO_2026-11-15.md) documente les vidéos AFS Silk V2, Duotone Glide 3.0 D/LAB 825 et KT Halo 670/800. Leurs URL sont préremplies dans [l'interface mobile](review.html) via **« Essai pilote »**. Aucune transcription de ces vidéos n'est encore disponible dans le dépôt ; ne pas présenter les comptes rendus écrits comme des transcriptions.

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

**État du pilote du 15/11/2026 : aucune transcription réellement acquise pour ces trois vidéos.** La transcription automatisée nécessite encore un fichier média autorisé ou une transcription publique exploitable. Les tests GitHub simulent des segments audio injectés et valident la chaîne logicielle, pas la disponibilité d'une vidéo tierce.
