
if (T[cellI] >= 273.16)
	{

	// Saturation pressure at local temperature [Pa]
	psat[cellI] = 610.8*Foam::exp(-5.1421*Foam::log(T[cellI]/273.15) - 6828.77*(1/T[cellI] - 1/273.15));

	// Saturation temperature at local pressure [K]    
	Tsat[cellI] = 1730.63/(8.07131 - Foam::log10(p[cellI]*760/101325)) + 39.724;
	}

else // Extra temperature check for T > 115 is added in the main code
	{

	// Saturation pressure at local temperature [Pa]
	//psat[cellI] = Foam::exp((-2663.5/T[cellI] + 12.537)*Foam::log(10.0));
	//psat[cellI] = Foam::exp(54.842763 - 6763.22/T[cellI] - 4.210*Foam::log(T[cellI]) + 0.000367*T[cellI] + Foam::tanh(0.0415*(T[cellI] - 218.8))*(53.878 - 1331.22/T[cellI] - 9.44523*Foam::log(T[cellI]) + 0.014025*T[cellI]));
	psat[cellI] = Foam::exp(9.550426 - 5723.265/T[cellI] + 3.53068*Foam::log(T[cellI]) - 0.00728332*T[cellI]);

	// Saturation temperature at local pressure [K]
	//Tsat[cellI] = 2663.5/(12.537 - Foam::log10(p[cellI]));
	//Tsat[cellI] = 1.11164211e-3 + 9.56173207e-3*Foam::log(p[cellI]) + 0.315572925*Foam::log(p[cellI])*Foam::log(p[cellI]) + 7.37978228*Foam::log(p[cellI])*Foam::log(p[cellI])*Foam::log(p[cellI]) + 2.08416930e2*Foam::log(p[cellI])*Foam::log(p[cellI])*Foam::log(p[cellI])*Foam::log(p[cellI]);
	Tsat[cellI] = (1.814625*Foam::log(p[cellI]) + 6190.134)/(29.120 - Foam::log(p[cellI]));
	}
