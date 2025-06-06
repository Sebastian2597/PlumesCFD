// Auxilliary nondimensional term
scalar Tterm = max(0.0, 1.0 - T[cellI]/T_crit.value()); // max used to avoid negatives

S_sat[cellI] = p[cellI]/psat_lg[cellI]; // supersaturation ratio

if (T[cellI] > 273.16)
	{
	// ----------------------- //
	// Surface tension
	// ----------------------- //

	surface_tension[cellI] = sigma_B*Foam::pow(Tterm, sigma_mu)*(1.0 + sigma_b*Tterm);


	// ----------------------- //
	// Vaporization
	// ----------------------- //

	// Latent heat release upon droplet condensation
	h_fg[cellI] = 2.257E6;

	// Degree of supercooling
	T_sc[cellI] = Tsat[cellI] - T[cellI];

	// Specific enthalpy of the liquid phase
	h_liquid[cellI] = h[cellI] - h_fg[cellI];

	// Droplet total enthalpy
	h_droplet[cellI] = h_liquid[cellI] + 0.5*magSqr(U[cellI]);

	}
else if (T[cellI] < 273.16 && T[cellI] >= 173.16) // Different set of thermophysical properties for temperature range below the freezing point
	{
	// Only (presumably) valid for extremely rapid expansions (e.g., supersonic micronozzles)

	surface_tension[cellI] = 93.6635e-03 + 9.133e-06*T[cellI] - 2.75e-07*T[cellI]*T[cellI];
	h_fg[cellI] = 2.836E6;

	// Degree of supercooling
	T_sc[cellI] = Tsat[cellI] - T[cellI];

	// Specific enthalpy of the solid phase
	h_liquid[cellI] = h[cellI] - h_fg[cellI];

	// Droplet total enthalpy
	h_droplet[cellI] = h_liquid[cellI] + 0.5*magSqr(U[cellI]);

	}
