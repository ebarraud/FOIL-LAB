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
