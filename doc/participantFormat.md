# Participant

| Champ | Format | Description |
|-------|--------|-------------|
|MatchId| String | Id de la partie
|SummonerId| String | Id du compte du participant
|QueuesRank| Rank[] | Classement sur les différents fils classés
|ChampionName| String | Nom du champion joué
|Mastery| Int | Nombre de points de maitrise sur le champion joué
|LastTimeChampionPlayed| Int | Date de la dernière partie jouée avec ce champion
| Summoner1 | String | Id du summoner spell 1
| Summoner2 | String | Id du summoner spell 2
| Role | String | Poste du joueur dans la partie
|Team | String | Red ou Blue

# Rank
| Champ | Format | Description |
|-------|--------|-------------|
|queueType| String | Type de fil classé
|tier| String | IRON, BRONZE, SILVER etc
|rank| String | IV, III, II, I 