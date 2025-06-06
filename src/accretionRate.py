# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 15:15:12 2025

@author: sebas
"""

def calculate(mdot_a):
    # Constants
    angstrom = 1e-10 # [m]
    m_H2O = 2.988e-26 # [kg]
      
    # Molecular surface density per monolayer
    number_of_molecules_in_one_layer = (1 / (3 * angstrom)) ** 2 # [molecules/m^2]
    
    # Mass of one ice monolayer per m^2
    mass_of_one_layer = number_of_molecules_in_one_layer * m_H2O # [kg/m^2]
    
    # Rate of ice layers accreted [layers/s]
    rate_of_ice_layers_accreted = mdot_a / mass_of_one_layer # [layers/s]
    
    ice_layer_thickness = 3 * angstrom # [m]
    
    # Wall thickness change rate due to accretion [m/s]
    dRw_a = ice_layer_thickness * rate_of_ice_layers_accreted # [m/s]
    
    return dRw_a

