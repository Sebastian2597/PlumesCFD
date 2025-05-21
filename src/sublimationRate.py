#import numpy as np

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
    
    # Wall thickness change rate [m/s]
    dRw_s = ice_layer_thickness * rate_of_ice_layers_sublimated  # [m/s]

    return dRw_s

# def calculate(T_wall, cell_area):
#     # Constants
#     angstrom = 1e-10  # [m]
#     m_H2O = 2.99e-26  # [kg]
#     k_b = 1.380649e-23  # [J/K]
#     nu = 2.29e12  # [s^-1]
#     Ea = 5600 * k_b  # Convert activation energy [K] to [J]

#     # Molecular surface density per monolayer
#     number_of_molecules_in_one_layer = (1 / (3 * angstrom))**2  # [molecules/m^2]

#     # Mass of one ice monolayer per m^2
#     mass_of_one_layer = number_of_molecules_in_one_layer * m_H2O  # [kg/m^2]

#     # Sublimation mass flux [kg/m^2/s]
#     mdot_s = - nu * number_of_molecules_in_one_layer * m_H2O * np.exp(-Ea / (k_b * T_wall))

#     # Wall thickness change rate [m/s]
#     ice_layer_thickness = 3 * angstrom
#     rate_of_ice_layers_sublimated = mdot_s / mass_of_one_layer  # [layers/s]
#     dRw_s = ice_layer_thickness * rate_of_ice_layers_sublimated  # [m/s]

#     return dRw_s, mdot_s

