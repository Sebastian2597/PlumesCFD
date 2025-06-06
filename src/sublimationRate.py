# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 16:22:41 2025

@author: sebas
"""

def calculate(mdot_s):
    # Constants
    angstrom = 1e-10  # [m]
    m_H2O = 2.99e-26  # [kg]

    # Molecular surface density per monolayer
    number_of_molecules_in_one_layer = (1 / (3 * angstrom))**2  # [molecules/m^2]

    # Mass of one ice monolayer per m^2
    mass_of_one_layer = number_of_molecules_in_one_layer * m_H2O  # [kg/m^2]
    
    # Rate of ice layers sublimated [layers/s]
    rate_of_ice_layers_sublimated = mdot_s / mass_of_one_layer  # [layers/s]
    
    ice_layer_thickness = 3 * angstrom
    
    # Wall thickness change rate due to sublimation [m/s]
    dRw_s = ice_layer_thickness * rate_of_ice_layers_sublimated  # [m/s]

    return dRw_s

