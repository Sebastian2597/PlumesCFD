// Auxilliary nondimensional term
scalar Tterm = max(0.0, 1.0 - T[cellI]/T_crit.value()); // max used to avoid negatives
rho_grain[cellI] = 916.7-0.175*(T[cellI]-273.15)-5.0e-4*(T[cellI]-273.15)*(T[cellI]-273.15); // kg/m3

S_sat[cellI] = p[cellI]/psat[cellI]; // supersaturation ratio

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
	h_fg[cellI] = (6763.22/(T[cellI]*T[cellI]) - 4.21/T[cellI] + 0.000367 + (0.0415*(53.878-1331.22/T[cellI] + 0.014025*T[cellI] - 9.44523*Foam::log(T[cellI]))/((Foam::cosh((0.0415*(T[cellI] - 218.8))))*(Foam::cosh((0.0415*(T[cellI] - 218.8))))))+(0.014025+1331.22/(T[cellI]*T[cellI])-9.44523/T[cellI])*Foam::tanh(0.0415*(T[cellI] - 218.8)))*R.value()*T[cellI]*T[cellI]; // J/kg

	// Degree of supercooling
	T_sc[cellI] = Tsat[cellI] - T[cellI];

	// Specific enthalpy of the liquid phase
	h_liquid[cellI] = h[cellI] - h_fg[cellI];

	// grain total enthalpy
	h_grain[cellI] = h_liquid[cellI] + 0.5*magSqr(U[cellI]);

	}
else if (T[cellI] < 273.16 && T[cellI] >= 100.0) // Different set of thermophysical properties for temperature range below the freezing point
	{

	surface_tension[cellI] = 93.6635e-03 + 9.133e-06*T[cellI] - 2.75e-07*T[cellI]*T[cellI];
	h_fg[cellI] = (46782.5 + 35.8925*T[cellI] - 0.07414*T[cellI]*T[cellI] + 541.5*Foam::exp(-(T[cellI]/123.75)*(T[cellI]/123.75)))/m_molar.value(); // J/mol

	// Degree of supercooling
	T_sc[cellI] = Tsat[cellI] - T[cellI];

	// Specific enthalpy of the solid phase
	h_liquid[cellI] = h[cellI] - h_fg[cellI];

	// grain total enthalpy
	h_grain[cellI] = h_liquid[cellI] + 0.5*magSqr(U[cellI]);

	}
