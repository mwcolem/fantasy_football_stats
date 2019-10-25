import requests
import pandas as pd

league_id = 803723
season = 2019

slotcodes = {
    0 : 'QB', 2 : 'RB', 4 : 'WR',
    6 : 'TE', 16: 'Def', 17: 'K',
    20: 'Bench', 21: 'IR', 23: 'Flex'
}

url = 'https://fantasy.espn.com/apis/v3/games/ffl/seasons/' + \
      str(season) + '/segments/0/leagues/' + str(league_id) + \
      '?view=mMatchup&view=mMatchupScore'

data = []
for week in range(1, 17):

    r = requests.get(url,
                     params={'scoringPeriodId': week})
    d = r.json()

    for team in d['teams']:
        team_id = team['id']
        for player in team['roster']['entries']:
            name = player['playerPoolEntry']['player']['fullName']
            slot = player['lineupSlotId']
            position = slotcodes[slot]

            proj, act = None, None
            for stat in player['playerPoolEntry']['player']['stats']:
                if stat['scoringPeriodId'] != week:
                    continue
                if stat['statSourceId'] == 0:
                    act = stat['appliedTotal']
                elif stat['statSourceId'] == 1:
                    proj = stat['appliedTotal']

            data.append([
                name, position, proj, act
            ])

player_totals = pd.DataFrame(data,
                    columns=['Player', 'Position', 'Total Proj', 'Total Actual'])
player_totals = player_totals.groupby(player_totals['Player']).sum()

player_data = pd.DataFrame(data,
                    columns=['Player', 'Position', 'Mean Proj', 'Mean Actual'])
player_data = player_data.groupby(player_data['Player']).mean()

stdev_data = pd.DataFrame(data,
                    columns=['Player', 'Position', 'Stdev Proj', 'Stdev Actual'])
stdev_data = stdev_data.groupby(stdev_data['Player']).std()

complete = player_totals.merge(
    player_data.merge(
        stdev_data,
        on='Player',
        how='inner'
    ),
    on='Player',
    how='inner')

complete = complete.drop('Total Proj', axis=1)

# print(complete.sort_values(by=['Player']))
print(complete.sort_values(by=['Total Actual'], ascending=False).head())
