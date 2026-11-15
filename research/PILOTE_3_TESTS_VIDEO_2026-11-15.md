# FOIL LAB EXPERT — Pilote de trois essais vidéo (15 novembre 2026)

## Périmètre et méthode

Fenêtre temporelle glissante : **15 novembre 2024 → 15 novembre 2026**. Trois essais de **foils** wingfoil déjà identifiés : AFS Silk V2 (650/750/950), Duotone Glide 3.0 D/LAB 825 et KT Halo (670/800).

**Important : aucun des trois films n'a été intégralement regardé ni transcrit pendant ce pilote.** Les pages YouTube identifient les contenus. Les informations techniques ci-dessous proviennent exclusivement de comptes rendus écrits à la première personne ou de réponses publiées par les auteurs, pas de la piste audio. Les conditions et les réglages sont conservés afin de ne pas attribuer à une aile un comportement qui dépend d'un stabilisateur.

## 1. AFS Silk V2 (650 / 750 / 950)

- Vidéo repérée : https://www.youtube.com/watch?v=DMlWjjIcwss
- Essai détaillé écrit par Hadou, publié le **14 octobre 2026** : https://www.pimpyourride.fr/afs-silk-v2-foil-review/
- **750 cm² :** son auteur indique remplacer sa Silk V1 850 par cette Silk V2 750, avec moins d'effort au pumping, plus de glisse et une transition rail-to-rail qui conserve la maniabilité du V1.
- **950 cm² :** en *surffoil*, la tolérance à basse vitesse change sensiblement lorsqu'il remplace le U-Carve 130 par le **U-Surf 135**. Ce constat **ne constitue pas** une mesure de la plage basse wingfoil.
- **650 cm² :** l'auteur rapporte davantage de vivacité dans les virages et une plage basse étonnante lors de freefly/wing dans les petites bosses. Il a dû reculer le foil de **2 à 3 cm** sur les rails par rapport à la 750 pour équilibrer son montage.
- **Limite de vitesse :** essai subjectif où une Armstrong MA 690 lui semble plus rapide ; il préfère le compromis tolérance / carving du Silk V2.
- **Montage :** mât Skinny 80, fuselage Advanced pour la revue, stabilisateurs adaptés aux usages (U-Carve et U-Surf).
- **Biais à signaler :** l'auteur indique apprécier particulièrement AFS ; une fiche écrite et sa vidéo du même auteur ne représentent **pas deux avis indépendants**.

Ces phrases reprennent des constats **attribués au testeur** ; aucune vitesse maximale mesurée ni coefficient universel d'efficacité n'est déduit.

## 2. Duotone Glide 3.0 D/LAB 825

- Vidéo YouTube repérée : https://www.youtube.com/watch?v=aiWA2W7hKos
- Page de l'essai Gleiten.TV du **21 octobre 2026** : https://gleiten.tv/video/4935-duotone-glide-3-0-dlab-825-foil-test-2026/
- **Réponse de Gleiten.TV du 23/10 :** pour un pratiquant de **74 kg**, l'équipe qualifie les capacités de glisse et de pumping du **1100** d'excellentes, mais prévient qu'il pourrait manquer de vivacité en virage ; elle suggère le **825** comme alternative ou complément.
- **Réponse de Gleiten.TV du 01/11 :** le **950** est rapproché de l'AFS Enduro **1100** en performances perçues, le Glide 3.0 étant ressenti comme plus sportif.
- **Prudence :** ces deux réponses concernent des tailles *autres que le 825 réellement mis en avant dans le titre de la vidéo* ; ne pas transformer automatiquement ces propos en note de test du 825.

## 3. KT Halo 670 / 800

- Vidéo YouTube repérée : https://www.youtube.com/watch?v=zesN5IeyRQM
- Test répertorié par Gleiten.TV le **4 août 2026** : https://gleiten.tv/foil/test/wingfoil/foil/
- **Pas de constat technique attribuable au testeur accessible dans les sources inspectées.** La fiche conserve uniquement titre, date, tailles et lien vidéo. Ne pas inventer des scores de vitesse, plage basse, pumping ou carving.

## État vérifiable du pilote

| Indicateur | Résultat |
|---|---:|
| Vidéos identifiées avec URL directe | 3 |
| Modèles documentés | 3 |
| Essais écrits détaillés consultés | 1 |
| Questions/réponses techniques des auteurs consultées | 1 |
| Transcriptions intégrales obtenues | **0** |
| Vidéos visionnées intégralement | **0** |
| Notes publiées automatiquement | **0** |

La preuve structurée se trouve dans `data/research/pilot_3_video_tests_2026-11-15.json`.

## Pipeline de transcription : limites et suite

1. La clé **YouTube Data API** permet uniquement de découvrir et d'identifier les vidéos publiques, pas de télécharger les sous-titres d'une chaîne tierce.
2. Le pilote `yt-dlp --list-subs` sur les runners GitHub a déjà échoué pour les vidéos testées : **erreurs réseau/extracteur**. Répéter le même appel sur des centaines de vidéos n'apporterait aucun contenu vérifiable.
3. Pour accéder légalement au contenu parlé, obtenir des fichiers SRT/VTT auprès des médias, utiliser des transcriptions publiques dans leurs conditions autorisées ou traiter localement un audio légalement fourni (ASR Whisper).
4. La page mobile `video-analysis/review.html` sait déjà accepter SRT/VTT et exporter des passages horodatés candidats, à vérifier manuellement.
5. **Ne modifier les notes du configurateur qu'après recoupement et attribution exacte à la taille testée.**

## Sources consultées

- https://www.pimpyourride.fr/afs-silk-v2-foil-review/
- https://gleiten.tv/video/4935-duotone-glide-3-0-dlab-825-foil-test-2026/
- https://gleiten.tv/foil/test/wingfoil/foil/
