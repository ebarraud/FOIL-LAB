# Gleiten.TV : preuves issues des réponses des testeurs — 14 novembre 2026

## Découverte vérifiée

La page officielle de l'essai **Duotone Glide 3.0 D/LAB 825** contient des réponses de l'équipe Gleiten.TV aux questions des lecteurs. Il ne s'agit **ni d'une transcription vidéo, ni d'une mesure instrumentée**.

Source primaire : https://gleiten.tv/video/4935-duotone-glide-3-0-dlab-825-foil-test-2026/

### Observations utiles (paraphrases)

- **1100 cm² :** le média apprécie particulièrement ses capacités de glisse et pumping, mais indique que ce modèle peut manquer de maniabilité selon les attentes du pratiquant (réponse du **23/10/2026** à un utilisateur de 74 kg).
- **825 cm² :** conseillé comme alternative ou complément pour ce même cas. Ce n'est pas un minimum de vent universel.
- **950 cm² :** présenté comme comparable en prestation à l'**AFS Enduro 1100**, avec un ressenti plus sportif attribué au Glide 3.0 (réponse du **01/11/2026**).
- **Portance précoce et vitesse :** l'équipe répond qu'un décollage précoce ne pénalise pas la vitesse de pointe. Sans valeur mesurée, ni montage ni taille précis dans cette réponse.

Les **cinq affirmations structurées** et leurs limites sont dans `data/research/gleiten_editorial_qa_2026-11-14.json`. Ce sont des éléments d'expertise utiles, mais **non indépendants les uns des autres** puisqu'ils proviennent de la même rédaction et du même essai.

## Statuts de preuve

- Vidéo repérée : **oui**
- Réponses techniques de la rédaction inspectées : **oui**
- Sous-titres ou transcription intégrale obtenus : **non**
- Vidéo intégralement analysée : **non**
- Conditions et montage de l'essai suffisamment documentés pour calculer une note : **non**
- Notes modifiées dans `data/model_variants.json` : **aucune**

## Limite technique confirmée

Le pilote `yt-dlp` exécuté sur les runners GitHub a échoué sur les pages Gleiten.TV (extracteur non pris en charge) et sur les deux URL YouTube testées (erreurs d'extraction/réseau) : voir `video-analysis/REPORT_2026-11-14.md`.

Ces échecs ne signifient pas qu'il n'existe pas de sous-titres. On peut importer une transcription autorisée depuis `video-analysis/review.html`, mais le module ne peut actuellement prétendre avoir analysé toutes les vidéos.

## Prochaine étape

Chercher des URL YouTube **exactes** hébergeant les mêmes essais et des transcriptions accessibles avec les autorisations appropriées ; si le média héberge exclusivement les vidéos, demander un accès aux sous-titres ou à des synthèses écrites. En parallèle, collecter ces Q&A officielles sur un ensemble de modèles pour étoffer les preuves qualitatives indépendamment des transcriptions.
