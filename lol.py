
import os
import pandas as pd
from riotwatcher import LolWatcher, ApiError
from dotenv import load_dotenv
import json
load_dotenv(os.path.dirname(os.path.realpath(__file__))+'/.env')
# global variables
MATCHS_CSV_FILE = os.getenv("DATA_FOLDER")+"/matchsData.csv"
PARTICIPANTS_CSV_FILE = os.getenv("DATA_FOLDER")+"/participantsData.csv"
SUMMONERS_CSV_FILE = os.getenv("DATA_FOLDER")+"/summonersData.csv"
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


def formatQueues(queues):
    formattedQueues = {
        'RANKED_SOLO_5x5': {
            'tier': None,
            'rank': None,
            "wins": None,
            "losses": None,
            "leaguePoints": None
        },
        'RANKED_FLEX_SR': {
            'tier': None,
            'rank': None,
            "wins": None,
            "losses": None,
            "leaguePoints": None}}
    for queue in queues:
        formattedQueues[queue['queueType']] = {
            "tier": queue['tier'],
            "rank": queue['rank'],
            "wins": queue['wins'],
            "losses": queue['losses'],
            "leaguePoints": queue['leaguePoints']}
    return formattedQueues


def summoner_to_csv(matchId, participant):
    summonerQueues = watcher.league.by_summoner(
        my_region, participant['summonerId'])
    queuesToSave = [{"queueType": value['queueType'],
                     "tier": value['tier'],
                     "rank": value['rank'],
                     "wins": value['wins'],
                     "losses": value['losses'],
                     "leaguePoints": value['leaguePoints']} for value in summonerQueues]
    formatedQueues = formatQueues(queuesToSave)
    summonerToSave = {
        "MatchId": [matchId],
        "SummonerId": [participant['summonerId']],
        "SummonerName": [participant['summonerName']],
        "SummonerLevel": [participant["summonerLevel"]],
        "SoloTier": [formatedQueues['RANKED_SOLO_5x5']['tier']],
        "SoloRank": [formatedQueues['RANKED_SOLO_5x5']['rank']],
        "SoloWins": [formatedQueues['RANKED_SOLO_5x5']['wins']],
        "SoloLosses": [formatedQueues['RANKED_SOLO_5x5']['losses']],
        "SoloLP": [formatedQueues['RANKED_SOLO_5x5']['leaguePoints']],
        "FlexTier": [formatedQueues['RANKED_FLEX_SR']['tier']],
        "FlexRank": [formatedQueues['RANKED_FLEX_SR']['rank']],
        "FlexWins": [formatedQueues['RANKED_FLEX_SR']['wins']],
        "FlexLosses": [formatedQueues['RANKED_FLEX_SR']['losses']],
        "FlexLP": [formatedQueues['RANKED_FLEX_SR']['leaguePoints']],
    }
    saveDatas(summonerToSave, SUMMONERS_CSV_FILE)


def participant_to_csv(matchId, participant):
    summonerQueues = watcher.league.by_summoner(
        my_region, participant['summonerId'])
    summoner_to_csv(matchId, participant)
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
