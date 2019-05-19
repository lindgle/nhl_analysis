# -*- coding: utf-8 -*-
"""
Created on Sun May 12 19:54:57 2019

@author: Leevi
"""

from pystan import stan

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
        matrix[n_match_days, nteams] eta_a
    }
    transformed parameters{
        matrix[n_match_days, nteams] a; // Team abilities
        row_vector<lower=0>[n_teams] sigma_a; // Game-to-game variation
        a[1] = b_prev * prev_perf + sigma_a0 * eta_a[1]; // Initial abilities at week 1
        sigma_a = tau_a * sigma_a_raw;
        for (d in 2:n_match_days) {
            a[w] = a[w-1] + sigma_a .* eta_a[w];
        }
    }
    model {
        vector[ngames] a_diff
        // Priors
        nu ~ gamma(2, 0.1);
        b_prev ~ normal(0, 1);
        sigma_a0 ~ normal(0, 1);
        sigma_y ~ normal(0, 5);
        b_home ~ normal(0, 1);
        sigma_a_raw ~ normal(0, 1);
        tau_a ~ cauchy(0, 1);
        to_vector(eta_a) ~ normal(0, 1)
        // Likelihood
        for (g in 1:ngames) {
            a_diff[g] = a[home_match_day[g], home_team[g]] - a[away_match_day[g], away_team[g]];
        }
        score_diff ~ student_t(nu, a_diff + b_home, sigma_y)
    }
    '''