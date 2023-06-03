
import cassiopeia as cass
import os
import pandas as pd
import requests
from riotwatcher import LolWatcher, ApiError
# global variables
MATCHS_CSV_FILE = os.getcwd()+"/personnal_projects/lol_win_prediction/data/matchsData.csv"
PARTICIPANTS_CSV_FILE = os.getcwd(
)+"/personnal_projects/lol_win_prediction/data/participantsData.csv"
API_KEY = "RGAPI-66517d87-c127-4a19-b582-1bd8cb45f635"
watcher = LolWatcher(API_KEY)
my_region = 'euw1'
playersName = ["xXItachiDBakaUwu", "xXLivaïDBakaUwu", "Robert 2 Quimper",
               "xXSasukeDBakaUwu", "xXVegetaDBakaUwu", "Vomi Surprise"]


def teamIdWin(team):
    return team['win']

# enregistrement des infos dans le document correspondant


def saveDatas(data, path):
    pd.DataFrame(data).to_csv(
        path, index=False, header=not os.path.exists(path), mode="a" if os.path.exists(path) else "w")

# dans l'historique de l'utilisateur, retire les matchs déjà enregistrés


def matchNotSaved(history):
    print(history)
    matchsToSave = history
    if (os.path.exists(MATCHS_CSV_FILE)):
        matchsSaved = pd.read_csv(MATCHS_CSV_FILE)["MatchId"].values
        matchsToSave = [value for value in history if value not in matchsSaved]
    return matchsToSave


# récupération des stats d'un joueur dans une partie précise


def participant_to_csv(matchId, participant):
    summonerQueues = watcher.league.by_summoner(
        my_region, participant['summonerId'])
    queuesToSave = [{"queueType": value['queueType'], "tier": value['tier'],
                     "rank": value['rank']} for value in summonerQueues]
    mastery = watcher.champion_mastery.by_summoner_by_champion(
        my_region, participant['summonerId'], participant['championId'])
    masteryPoints = mastery['championPoints']
    lastTimeChampionPlayed = mastery['lastPlayTime']
    participantToSave = {
        "MatchId": [matchId],
        "SummonerId": [participant['summonerId']],
        "SummonerLevel": [participant["summonerLevel"]],
        "QueuesRanks": [queuesToSave],
        "ChampionName": [participant['championName']],
        "Mastery": [masteryPoints],
        "LastTimeChampionPlayed": [lastTimeChampionPlayed],
        "Summoner1": [participant['summoner1Id']],
        "Summoner2": [participant['summoner2Id']],
        "Role": [participant['individualPosition']],
        "Team": ["Red" if participant["teamId"] == 100 else "Blue"]}
    saveDatas(participantToSave, PARTICIPANTS_CSV_FILE)


def match_to_csv(match):
    match_detail = watcher.match.by_id(my_region, match)
    if (match_detail['info']['gameMode'] == "CLASSIC"):
        for participant in match_detail['info']['participants']:
            participant_to_csv(
                match_detail['metadata']['matchId'], participant)
        matchToSave = {'MatchId': [match_detail['metadata']['matchId']],
                       'TeamWin': ["Red" if list(filter(lambda team: team['win'], match_detail['info']['teams']))[0]['teamId'] == 100 else "Blue"]}
        saveDatas(matchToSave, MATCHS_CSV_FILE)


if __name__ == "__main__":
    for playerName in playersName:
        player = watcher.summoner.by_name(
            my_region, playerName)
    # print(watcher.league.by_summoner(my_region, me['id']))
        history = matchNotSaved(
            watcher.match.matchlist_by_puuid(my_region, player['puuid']))
        for match in history:
            match_to_csv(match)
