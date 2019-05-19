# -*- coding: utf-8 -*-
"""
Created on Sun May 12 20:32:30 2019

@author: Leevi
"""
#%%
from nhl_api import NHLapi
from NHL_functions import prev_season_ability

api = NHLapi()

#%%
df1718 = api.get_games(start='2017-10-01', end='2018-05-01')
df1718 = df1718.query('game_type == "R"')
df1819 = api.get_games(start='2018-10-01', end='2019-05-01')
df1819 = df1819.query('game_type == "R"')

#teams = api.get_teams()

standings = api.get_standings(season=20172018)
standings['score'] = prev_season_ability(standings.points)
#%%

standings

