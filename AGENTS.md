# FOIL LAB work tracking

## Règle permanente : aller jusqu'au résultat autorisé

L'utilisateur autorise la poursuite autonome du travail FOIL LAB, de la découverte des vidéos à la collecte, l'analyse technique, la vérification des sources et montages, l'intégration défendable au configurateur, les tests appropriés et la publication sur GitHub. Ne pas attendre une nouvelle demande « go » à chaque étape ni arrêter après une livraison intermédiaire quand du travail autorisé reste réalisable.

- Poursuivre les étapes nécessaires jusqu'au résultat concret. Mettre à jour le tableau de bord avec les statuts réels, les preuves, les améliorations publiées et les points restant à résoudre.
- Une collecte limitée ou bloquée n'arrête pas la lecture des transcriptions locales, les vérifications, les intégrations ou les tests indépendants du blocage. Respecter les délais du fournisseur et ne pas utiliser de crédits payants.
- Une intégration différée exige un motif précis et une prochaine action. Résoudre les vérifications accessibles au lieu d'accumuler des résumés ou de transférer implicitement cette tâche à l'utilisateur.
- Ne pas forcer une intégration : données insuffisantes, traduction ambiguë et contenu hors périmètre restent explicitement documentés. Aucun score inventé, aucune compatibilité supposée et aucune prétention d'écoute ou de validation humaine non réalisée.
- Solliciter l'utilisateur uniquement pour une information, une décision ou une autorisation réellement indispensable et non déjà fournie. Ne pas lui demander de reconfirmer les actions couvertes par cette règle.
- Être exact sur l'activité : le suivi planifié travaille par passages; ne pas prétendre qu'une analyse tourne en continu entre les passages. À chaque passage autorisé, avancer effectivement sur les tâches réalisables plutôt que seulement consulter les compteurs.

When actually starting a transcript analysis or verification session, run:
`python video-analysis/analysis_activity.py VIDEO_ID in_progress --step "Concrete work being performed"`
Publish the activity files and generated progress.json so the public dashboard reflects real activity. Refresh the marker during sustained work; it expires after 20 minutes.

Before ending or interrupting the session, record `completed` or `paused` using the same command and publish the resulting files. Never leave an active marker merely because work is planned. A completed session does not itself mean a validated analysis or a rule integrated into the recommendation engine; those require evidence records and appropriate tests.
