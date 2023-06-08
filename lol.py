
import os
import pandas as pd
from riotwatcher import LolWatcher, ApiError
from dotenv import load_dotenv
import json
load_dotenv(os.path.dirname(os.path.realpath(__file__))+'/.env')
# global variables
MATCHS_CSV_FILE = os.getenv("DATA_FOLDER")+"/matchsData.csv"
PARTICIPANTS_CSV_FILE = os.getenv("DATA_FOLDER")+"/participantsData.csv"
watcher = LolWatcher(os.getenv("API_KEY"))
my_region = os.getenv("REGION")
players = open(os.path.dirname(os.path.realpath(__file__)) +
               '/players.json', encoding='utf-8')
playersName = json.load(players)['playersName']


def saveDatas(data, path):  # enregistrement des infos dans le document correspondant
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
    masteryPoints = None
    lastTimeChampionPlayed = None
    try:
        mastery = watcher.champion_mastery.by_summoner_by_champion(
            my_region, participant['summonerId'], participant['championId'])
        masteryPoints = mastery['championPoints']
        lastTimeChampionPlayed = mastery['lastPlayTime']
    except:
        print("Can't access mastery points")

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
        history = matchNotSaved(
            watcher.match.matchlist_by_puuid(my_region, player['puuid']))
        for match in history:
            match_to_csv(match)
