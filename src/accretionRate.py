# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 15:15:12 2025

@author: sebas
"""

#import numpy as np

def calculate(mdot_a):
    
    angstrom = 1e-10 # [m]
    m_H2O = 2.988e-26 # [kg]
      
    number_of_molecules_in_one_layer = (1 / (3 * angstrom)) ** 2 # [-]
    
    mass_of_one_layer = number_of_molecules_in_one_layer * m_H2O # [kg]
    
    rate_of_ice_layers_accreted = mdot_a / mass_of_one_layer # [layers/s]
    
    ice_layer_thickness = 3 * angstrom # [m]
    
    dRw_a = ice_layer_thickness * rate_of_ice_layers_accreted # [m/s]
    
    return dRw_a

# def calculate(T, rho, velocity_mag, cell_length, cell_height):
    
#     angstrom = 1e-10 # [m]
#     k_b = 1.380649e-23 # [J/K]
#     m_H2O = 2.99e-26 # [kg]
    
#     V_th = np.sqrt((8 * k_b * T) / (np.pi * m_H2O)) # [m/s]
    
#     mdot = rho * V_th # [kg/(m^2 s)]
    
#     dt = cell_length / velocity_mag # [s]
    
#     f_accretion = V_th * dt / cell_height # [-]
    
#     S_stick = 1 # [-]
    
#     mdot_a = S_stick * mdot * f_accretion
    
#     number_of_molecules_in_one_layer = (1 / (3 * angstrom)) ** 2 # [-]
    
#     mass_of_one_layer = number_of_molecules_in_one_layer * m_H2O # [kg]
    
#     rate_of_ice_layers_accreted = mdot_a / mass_of_one_layer # [layers/s]
    
#     ice_layer_thickness = 3 * angstrom # [m]
    
#     dRw_a = ice_layer_thickness * rate_of_ice_layers_accreted # [m/s]
    
#     return dRw_a, mdot_a
