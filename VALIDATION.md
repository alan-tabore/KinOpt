# Valider une modification de KinOpt

Les tests vérifient des situations précises et empêchent le retour des erreurs
déjà corrigées. Ils ne prouvent ni l'absence de toutes les erreurs, ni la validité
scientifique de chaque ajustement réalisé avec le logiciel.

## À quoi servent les tests ?

| Partie | Ce que l'on vérifie | Exemple de problème évité |
| --- | --- | --- |
| Import des données | Format, valeurs finies, temps croissant, température en Kelvin, conversion et cohérence de son évolution avec la vitesse | Lancer une optimisation sur un fichier invalide ou réutiliser les anciennes données après un import raté |
| Interpolation | Domaine commun aux expériences, alignement des colonnes après filtrage, variantes linéaire et cubique | Associer une conversion à la mauvaise température ou extrapoler hors des mesures |
| Analyse isoconversionnelle | Retrouver une énergie d'activation connue sur des expériences synthétiques | Accepter des résultats numériques incorrects malgré l'absence de message d'erreur |
| Modèles et fonctions de coût | Formules sur des exemples connus, certains cas limites et configurations invalides | Diviser par une vitesse expérimentale nulle dans le coût relatif |
| Interface d'optimisation | Paramètres transmis, saisies incorrectes, échec, annulation et possibilité de relancer | Utiliser les mauvais paramètres de Tg ou laisser le bouton dans un état bloqué |
| Méthodes d'optimisation | Petit problème dont le minimum est connu, pour Nelder-Mead, basinhopping, differential_evolution et shgo | Mal transmettre les arguments à SciPy ou remplacer le résultat du solveur par un essai rejeté |
| Résultats | Sauvegarde puis relecture de deux expériences de longueurs différentes, échec d'écriture | Simuler avec les lignes de remplissage ou la conversion initiale d'une autre expérience |
| Lots et comparaisons | Processus isolés, concurrence limitée, annulation ciblée, reprise, progression, validation réservée et imports historiques | Saturer la machine, perdre la file ou comparer des métriques incompatibles |

Dans beaucoup de tests de l'interface, le démarrage du calcul est remplacé par
un enregistrement des paramètres : on teste la préparation du calcul sans
attendre une optimisation longue. D'autres tests exécutent réellement SciPy.
Un test démarre un véritable thread Qt et vérifie que l'annulation permet de
revenir à un état utilisable. Les fichiers produits par les tests sont temporaires.

## Exécuter les contrôles localement

Depuis la racine du dépôt, créer un environnement isolé. Sous Linux :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pip check
QT_QPA_PLATFORM=offscreen MPLBACKEND=Agg python -m pytest
```

Sous Windows, dans PowerShell :

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[test]'
.\.venv\Scripts\python.exe -m pip check
$env:QT_QPA_PLATFORM = 'offscreen'
$env:MPLBACKEND = 'Agg'
.\.venv\Scripts\python.exe -m pytest
```

Fermer ce terminal après les tests avant de lancer l'interface normalement :
le réglage `offscreen` masque les fenêtres dans cette session.

`offscreen` permet de tester les composants graphiques sans ouvrir de fenêtres.
Pour une partie seulement :

```bash
QT_QPA_PLATFORM=offscreen python -m pytest kinopt/tests/test_gui_optimization.py
python -m pytest kinopt/tests/test_data_extraction.py
```

Pour voir les lignes et embranchements encore non exercés :

```bash
QT_QPA_PLATFORM=offscreen MPLBACKEND=Agg python -m pytest --cov --cov-report=term --cov-report=html
```

Ouvrir ensuite `htmlcov/index.html`. Le fichier d'interface généré par Qt et les
blocs de démonstration `if __name__ == '__main__'` sont exclus de cette mesure.
Le pourcentage mesure le code parcouru, pas la qualité d'une validation scientifique.

Dans le terminal PowerShell configuré ci-dessus, utiliser
`.\.venv\Scripts\python.exe -m pytest --cov --cov-report=term --cov-report=html`.

## Ce que GitHub vérifie

Chaque pull request et chaque modification de `master` déclenchent :

- les tests Linux sous Python 3.9 et 3.10 avec les versions scientifiques et Qt
  historiques définies dans `ci/constraints-legacy.txt` ;
- les tests Linux sous Python 3.14 avec les dépendances disponibles lors de l'installation ;
- les tests Windows dans un environnement virtuel, sous Python 3.10 avec les
  dépendances historiques et sous Python 3.14 avec les dépendances actuelles ;
- la cohérence des dépendances, les erreurs de syntaxe et les noms non définis ;
- la construction puis l'installation du paquet, et l'ouverture de son interface
  par `kinopt` (le véritable `kinopt.exe` sous Windows), `python -m kinopt` et
  l'ancien script, hors du dépôt, avec un dossier de résultats contenant des espaces ;
- un rapport de couverture téléchargeable dans les artefacts du workflow.

Le contrôle final `build` réussit seulement si les cinq environnements réussissent.
La matrice vérifie trois configurations Linux et deux Windows x64 sur les
machines hébergées de GitHub. Elle ne certifie pas tous les postes Windows
10/11, toutes les architectures ni toutes les combinaisons de versions.

## Contrôle manuel avant fusion

1. Importer un jeu de données habituel et vérifier les courbes, unités et messages.
2. Lancer une petite optimisation avec des réglages connus et examiner le statut
   de convergence, les paramètres, le coût et la courbe obtenue.
3. Vérifier l'annulation puis la possibilité de relancer une optimisation.
4. Sauvegarder puis relire le résultat ; comparer les expériences affichées aux
   données d'origine, notamment si leurs longueurs diffèrent.
5. Préparer au moins deux travaux, choisir deux calculs simultanés, puis vérifier
   leur progression, l'annulation d'un seul travail et la comparaison finale.
6. Importer un fichier avec colonnes réordonnées ou unités non standard dans
   l'assistant, puis vérifier les valeurs converties et les courbes.

Un résultat fini peut provenir d'un calcul arrêté par son budget d'itérations.
Il faut lire le statut SciPy : un fichier sauvegardé ne signifie pas que la
convergence est atteinte.

## Intégrer sur la branche principale

Dans ce dépôt, la branche principale s'appelle `master`.

1. Ouvrir la pull request et vérifier sa branche de destination. Si elle dépend
   d'une autre branche de correction, fusionner d'abord la correction préalable,
   puis choisir `master` comme destination et vérifier à nouveau la différence.
2. Relire les onglets **Commits** et **Files changed**, effectuer le contrôle
   manuel, et attendre la réussite des contrôles sur la dernière version.
3. Passer la pull request de brouillon à **Ready for review**.
4. Choisir **Create a merge commit** pour conserver les commits distincts.
   **Squash and merge** les regrouperait en un seul commit.
5. Une fois la fusion faite, mettre à jour la copie locale :

```bash
git switch master
git pull --ff-only
```

Il est recommandé de protéger `master` en imposant le passage par une pull
request et la réussite du contrôle `build`. Le workflow lance les contrôles ;
la protection de branche est un réglage GitHub séparé qui rend leur réussite
obligatoire avant fusion.

Voir la documentation GitHub sur la [fusion des pull requests](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-a-pull-request)
et la [protection des branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).

## Limites et prochaines validations

- Les hessiennes analytiques et les nombreuses variantes de simulation restent
  à couvrir. Les jacobiennes et gradients analytiques des lois de vitesse
  fournies sont vérifiés sur les solveurs locaux compatibles.
- Les tests isoconversionnels utilisent un cas isotherme synthétique idéal.
  Ajouter des références non isothermes et des données bruitées sera nécessaire
  pour une validation scientifique plus large.
- Les essais courts des solveurs ne prouvent pas leur convergence sur des modèles
  complexes. Les processus concurrents sont testés avec des calculs courts ; la
  consommation mémoire et les performances de longues campagnes restent à
  mesurer sur la machine cible.
- L'annulation intervient au prochain point de contrôle du solveur : une
  évaluation longue peut retarder l'arrêt. Le thread n'est pas tué brutalement.
- La compatibilité visuelle avec les différents bureaux Linux et postes Windows
  reste à vérifier manuellement. Les tests GitHub ouvrent Qt en mode `offscreen`.
  Les lanceurs et le choix du dossier de résultats sont testés séparément :
  par défaut, les résultats vont dans `Documents/KinOpt/results`, avec prise en
  compte du dossier Documents configuré sur le bureau. L'option `--results-dir`
  permet d'en choisir un autre. Les anciens résultats du dépôt restent lisibles.

L'import impose actuellement un écart relatif de `1e-5` et absolu de `1e-8`
entre l'intégrale de la vitesse et la variation de conversion, comme auparavant.
L'adéquation de cette tolérance à des mesures expérimentales réelles reste à
examiner. Les erreurs de données déclenchent désormais une exception explicite
dans l'API ; les scripts qui dépendaient de l'ancien retour de zéros doivent
être adaptés. L'interpolation commune utilise l'intersection des domaines
mesurés pour éviter l'extrapolation.
