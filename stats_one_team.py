import requests
import pandas as pd

league_id = 803723
season = 2019
target_team_id = 1

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
            onTeamId = player['playerPoolEntry']['onTeamId']

            proj, act = None, None
            for stat in player['playerPoolEntry']['player']['stats']:
                if stat['scoringPeriodId'] != week:
                    continue
                if stat['statSourceId'] == 0:
                    act = stat['appliedTotal']
                elif stat['statSourceId'] == 1:
                    proj = stat['appliedTotal']

            data.append([
                onTeamId, name, position, proj, act
            ])

player_totals = pd.DataFrame(data,
                    columns=['Team_Id', 'Player', 'Position', 'Total Proj', 'Total Actual'])
player_totals = player_totals.groupby(player_totals['Player']).sum().drop('Team_Id', axis=1)

player_data = pd.DataFrame(data,
                    columns=['Team_Id', 'Player', 'Position', 'Mean Proj', 'Mean Actual'])
player_data = player_data.groupby(player_data['Player']).mean().drop('Team_Id', axis=1)

stdev_data = pd.DataFrame(data,
                    columns=['Team_Id', 'Player', 'Position', 'Stdev Proj', 'Stdev Actual'])
stdev_data = stdev_data.groupby(stdev_data['Player']).std().drop('Team_Id', axis=1)

teams = pd.DataFrame(data,
                    columns=['Team_Id', 'Player', 'Position', 'Proj', 'Actual']
                    ).drop('Position', axis=1
                    ).drop('Proj', axis=1
                    ).drop('Actual', axis=1)
teams = teams.groupby(teams['Player']).mean()

complete = player_totals.merge(
    player_data.merge(
        stdev_data,
        on='Player',
        how='inner'
    ),
    on='Player',
    how='inner'
    ).merge(teams, on='Player', how='inner')

by_team = complete[complete['Team_Id'] == target_team_id]
by_team = by_team.reindex(columns=['Total Actual', 'Mean Actual', 'Stdev Actual', 'Mean Proj', 'Stdev Proj'])

print(by_team)
