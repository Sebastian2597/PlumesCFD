psat_lg[cellI] = 610.8*Foam::exp(-5.1421*Foam::log(T[cellI]/273.15) - 6828.77*(1/T[cellI] - 1/273.15)); // to calculate supersaturation

if (T[cellI] >= 273.16)
	{

	// Saturation pressure at local temperature [Pa]
	psat[cellI] = psat_lg[cellI];

	// Saturation temperature at local pressure [K]    
	Tsat[cellI] = 1730.63/(8.07131 - Foam::log10(p[cellI]*760/101325)) + 39.724;
	}

else // Extra temperature check for T > 173.16 is added in the main code
	{

	// Saturation pressure at local temperature [Pa]
	psat[cellI] = Foam::exp((-2663.5/T[cellI] + 12.537)*Foam::log(10.0));

	// Saturation temperature at local pressure [K]
	Tsat[cellI] = 2663.5/(12.537 - Foam::log10(p[cellI]));
	}
