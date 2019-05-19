# -*- coding: utf-8 -*-
"""
Created on Sun May 12 20:32:30 2019

@author: Leevi
"""
#%%
from nhl_api import NHLapi
from nhl_functions import prev_season_ability, game_number, convert_team_ids
import pandas as pd
pd.set_option('display.max_columns', 12)
pd.set_option('display.width', 700)

api = NHLapi()

#%%
df1718 = api.get_games(start='2017-10-01', end='2018-05-01')
df1718 = df1718.query('game_type == "R"')
df1819 = api.get_games(start='2018-10-01', end='2019-05-01')
df1819 = df1819.query('game_type == "R"')

teams = api.get_teams()

standings = api.get_standings(season=20172018)
standings['score'] = prev_season_ability(standings.points)
#%%

df = game_number(df1819)
df = convert_team_ids(df, teams)
df['goal_diff'] = df['home_team_score'] - df['away_team_score']


df.head()

#%%
standings = standings.merge(teams, on='team_id_original').sort_values('team_id')

#%%
from pystan import StanModel
model_code = '''
    data{
        int<lower=1> nteams; // Number of teams        
        int<lower=1> ngames; // Number of games
        int<lower=1> n_match_days; // Number of match days
        int<lower=1> home_match_day[ngames]; // Match day number for home team
        int<lower=1> away_match_day[ngames]; // Match day number for away team
        int<lower=1, upper=nteams> home_team[ngames]; // Home team ID (1,...,31)
        int<lower=1, upper=nteams> away_team[ngames]; // Away team ID (1,...,31)
        vector[ngames] goal_diff; // home_goals - away_goals
        row_vector[nteams] prev_perf; // Score between 1 and -1
    }
    parameters {
        real b_home; // Home game effect
        real b_prev; // Regression coef b_prev
        real<lower=0> sigma_a0; //Ability variation (first game)
        real<lower=0> tau_a; // Hyper-param. for game-to-game variation
        real<lower=1> nu; // t_dist degrees of freedom
        real<lower=0> sigma_y; // score diff variation
        row_vector<lower=0>[nteams] sigma_a_raw; //game-to-game variation
        matrix[n_match_days, nteams] eta_a;
    }
    transformed parameters{
        matrix[n_match_days, nteams] a; // Team abilities
        row_vector<lower=0>[nteams] sigma_a; // Game-to-game variation
        a[1] = b_prev * prev_perf + sigma_a0 * eta_a[1]; // Initial abilities at week 1
        sigma_a = tau_a * sigma_a_raw;
        if (n_match_days >= 2)
            for (d in 2:n_match_days) {
                a[d] = a[d-1] + sigma_a .* eta_a[d];
            }
    }
    model {
        vector[ngames] a_diff;
        // Priors
        nu ~ gamma(2, 0.1);
        b_prev ~ normal(0, 1);
        sigma_a0 ~ normal(0, 1);
        sigma_y ~ normal(0, 5);
        b_home ~ normal(0, 1);
        sigma_a_raw ~ normal(0, 1);
        tau_a ~ cauchy(0, 1);
        to_vector(eta_a) ~ normal(0, 1);
        // Likelihood
        for (g in 1:ngames) {
            a_diff[g] = a[home_match_day[g], home_team[g]] - a[away_match_day[g], away_team[g]];
        }
        goal_diff ~ student_t(nu, a_diff + b_home, sigma_y);
    }
    '''

sm = StanModel(model_code=model_code)

#%%
sub_df = df.query('home_game_number == 1 | away_game_number == 1')
ngames = sub_df.shape[0]
nteams = standings.shape[0]
n_match_days = 2

data = {'nteams': nteams,
         'ngames': ngames,
         'n_match_days': n_match_days,
         'home_match_day': sub_df['home_game_number'].values,
         'away_match_day': sub_df['away_game_number'].values,
         'home_team': sub_df['home_team'].values,
         'away_team': sub_df['away_team'].values,
         'goal_diff': sub_df['goal_diff'].values,
         'prev_perf': standings['score']}

fit = sm.sampling(data=data, iter=1000, chains=4)


