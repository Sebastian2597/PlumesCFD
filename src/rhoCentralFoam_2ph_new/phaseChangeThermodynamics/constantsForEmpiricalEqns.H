// ----------------------- //
// Misc properties
// ----------------------- //

	// Value of Pi
	const double pi = 3.1415926535897;

	// Boltzmann constant
	const dimensionedScalar k_B("k_B", dimensionSet(1,2,-2,-1,0,0,0), 1.38064852e-23);

	// Molecular (note: not molar) mass of H2O 
	const dimensionedScalar m_gas("m_gas", dimensionSet(1,0,0,0,0,0,0), 2.988E-26);	

	// Minimum physically meaningful radius of a H2O liduid (see documentation)
	const dimensionedScalar r_droplet_minimum("r_droplet_minimum", dimensionSet(0,1,0,0,0,0,0), 2.75E-10);	

	// Specific gas constant
	const dimensionedScalar R("R", dimensionSet(0,2,-2,-1,0,0,0), 461.52);

	// Properties at the critical point of water
	const dimensionedScalar T_crit("T_crit", dimensionSet(0,0,0,1,0,0,0), 647.096); // K
	const dimensionedScalar p_crit("p_crit", dimensionSet(1,-1,-2,0,0,0,0), 22064000.0); // Pa
	const dimensionedScalar rho_crit("rho_crit", dimensionSet(1,-3,0,0,0,0,0), 322.0); // kg/m3
	
	// Sticking coefficient
	const scalar sticking_coefficient = 1.0;
	
	// Average probability of molecule seeing wall
	const scalar p_lambda_average = 0.18756;
	
	// Exponential prefactor: vibrational frequency of ice
	const dimensionedScalar nu_s("nu_s", dimensionSet(0,0,-1,0,0,0,0), 2.29e12); // s-1

	// Binding energy of the ice
	const dimensionedScalar E_b("E_b", dimensionSet(1,2,-2,0,0,0,0), 5600 * k_B.value()); // J
	
	// Area number density of water molecules based on 3 angstrom
	const dimensionedScalar area_number_density("area_number_density", dimensionSet(0,-2,0,0,0,0,0), 1/Foam::pow((3*1e-10),2)); // m-2

// ----------------------- //
// Liquid properties
// ----------------------- //
	const dimensionedScalar rho_grain("rho_grain", dimensionSet(1,-3,0,0,0,0,0), 920.0); // kg/m3

	// Liquid surface tension
	const scalar sigma_B = 0.2358;
	const scalar sigma_b = -0.625;
	const scalar sigma_mu = 1.256;

// ----------------------- //
// Dimensioned factors that are later used to remove dimensionality from some thermophysical properties
// This is done because "for" loops are used in the code and:
//	1) OpenFOAM is sensitive to dimensional consistency (and rightly so)
//	2) OpenFOAM does not carry a parameter's dimensionality into a loop - this is inherent to how the software (and C++) is structured
// So the factors below are used to nondimensionalise some parameters that are used in loops
// ----------------------- //

    dimensionedScalar unit_Kelvin("unit_Kelvin", dimTemperature, 1.0); // To resolve dimensional inconsistencies
    dimensionedScalar unit_MPa("unit_MPa", dimPressure, 1000000.0); // To resolve dimensional inconsistencies
    dimensionedScalar unit_specific_heat("unit_specific_heat", dimensionSet(0, 2, -2, -1, 0, 0, 0), 1.0); // To resolve dimensional inconsistencies
