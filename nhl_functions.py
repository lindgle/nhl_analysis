# -*- coding: utf-8 -*-
"""
Created on Sun May 12 20:37:49 2019
Helper functions for NHL stuff

@author: Leevi
"""
import numpy as np

def prev_season_ability(x):
    '''
    Computes previous season ability
    Input:
    -----
    x - vector of points
    '''
    
    x_max = np.max(x)
    x_min = np.min(x)
    
    res = 2*x/(x_max - x_min) - (x_max + x_min)/((x_max - x_min))
    
    return res

def game_number(df):
    '''
    Computes previous game number from games df for home and away teams
    Input:
    -----
    df - data frame containing home_team and away team columns
    '''
    if ('away_game_number' in df) | ('home_game_number' in df):
        print('You have already done this :D')
        return df
    
    df = df.reset_index().copy()
    
    n = df.shape[0]
    
    df['home_game_number'] = 0
    df['away_game_number'] = 0
    
    for g in range(n):
        df.loc[g, 'home_game_number'] = (
                np.sum(df.loc[0:g, 'home_team'] == df.loc[g, 'home_team']) +
                np.sum(df.loc[0:g, 'away_team'] == df.loc[g, 'home_team'])
                )
        df.loc[g, 'away_game_number'] = (
                np.sum(df.loc[0:g, 'away_team'] == df.loc[g, 'away_team']) +
                np.sum(df.loc[0:g, 'home_team'] == df.loc[g, 'away_team'])
                )
        
    return df

def convert_team_ids(df, teams, team_id_cols=['home_team', 'away_team']):
    '''
    Converts NHL page team_ids to a 1-31 indexing
    -----
    df - 
    teams -
    '''
    cols = ['team_id_original', 'team_id']
    for col in team_id_cols:
        df = df.merge(teams[cols], left_on=col, right_on='team_id_original')
        df = df.drop(columns=[col, 'team_id_original'])
        df = df.rename(columns={'team_id':col})
    
    return df
    

