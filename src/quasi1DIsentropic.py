import numpy as np
from scipy.optimize import fsolve

# Constants
gamma = 1.333
R = 461.52
T0 = 273.16
p0 = 611.657

def area_mach_relation(M, A_Astar):
    term1 = (2 / (gamma + 1)) * (1 + ((gamma - 1) / 2) * M**2)
    term2 = (gamma + 1) / (2 * (gamma - 1))
    return A_Astar - (1 / M) * term1**term2

def compute_mach_from_area_ratio(A_Astar, subsonic=True):
    M_guess = 0.2 if subsonic else 2.0
    M_solution, = fsolve(area_mach_relation, M_guess, args=(A_Astar))
    return M_solution

def isentropic_properties(M):
    T_T0 = 1 / (1 + ((gamma - 1) / 2) * M**2)
    p_p0 = T_T0**(gamma / (gamma - 1))
    return T_T0, p_p0

def velocity_magnitude(T, M):
    c = np.sqrt(gamma * T * R)
    U = c * M
    return U

def compute_flow_variables(wall_coordinates_x, wall_coordinates_y, cell_centers_x, gamma=1.333, R=461.52, T0=273.16, p0=611.657):
    x = wall_coordinates_x
    y = wall_coordinates_y
    A = 2 * y
    
    dA_dx = np.gradient(A, x)
    throat_index = np.argmin(A)
    A_star = A[throat_index]
    A_ratio = A / A_star
    Mach = np.zeros_like(A)

    for i in range(0, throat_index + 1):
        Mach[i] = compute_mach_from_area_ratio(A_ratio[i], subsonic=True)

    regime = "supersonic"
    for i in range(throat_index + 1, len(A)):
        if regime == "supersonic":
            Mach[i] = compute_mach_from_area_ratio(A_ratio[i], subsonic=False)
            if dA_dx[i] < 0:
                regime = "subsonic"
        else:
            Mach[i] = compute_mach_from_area_ratio(A_ratio[i], subsonic=True)
            if dA_dx[i] > 0:
                regime = "supersonic"

    T_T0, p_p0 = isentropic_properties(Mach)
    T = T_T0 * T0
    p = p_p0 * p0
    velocity = velocity_magnitude(T, Mach)

    # Interpolate onto cell_centers_x
    p_interp = np.interp(cell_centers_x, x, p)
    T_interp = np.interp(cell_centers_x, x, T)
    Mach_interp = np.interp(cell_centers_x, x, Mach)
    velocity_interp = np.interp(cell_centers_x, x, velocity)

    return p_interp, T_interp, Mach_interp, velocity_interp
