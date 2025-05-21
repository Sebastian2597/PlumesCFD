/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | www.openfoam.com
     \\/     M anipulation  |
-------------------------------------------------------------------------------
    Copyright (C) 2011-2016 OpenFOAM Foundation
-------------------------------------------------------------------------------
License
    This file is part of OpenFOAM.
    OpenFOAM is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    OpenFOAM is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
    for more details.
    You should have received a copy of the GNU General Public License
    along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.
Application
    rhoCentralFoam_2ph
Description
    Density-based compressible flow solver based on central-upwind schemes of
    Kurganov and Tadmor, augmented to account for the non-equilibrium
    homogeneous condensation of the gaseous phase, as modelled for steam
    by Gerber and Kermani (2004).
\*---------------------------------------------------------------------------*/

#include "fvCFD.H"
#include "psiThermo.H"
#include "turbulentFluidThermoModel.H"
#include "fixedRhoFvPatchScalarField.H"
#include "directionInterpolate.H"
#include "localEulerDdtScheme.H"
#include "fvcSmooth.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

int main(int argc, char *argv[])
{
    argList::addNote
    (
        "Density-based compressible flow solver based on central-upwind"
        " schemes of Kurganov and Tadmor."
    );

    #define NO_CONTROL
    #include "postProcess.H"

    #include "addCheckCaseOptions.H"
    #include "setRootCaseLists.H"
    #include "createTime.H"
    #include "createMesh.H"
    #include "createFields.H"
    #include "createFieldRefs.H"
    #include "createTimeControls.H"

    turbulence->validate();

    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

    #include "readFluxScheme.H"

    #include "phaseChangeThermodynamics/constantsForEmpiricalEqns.H"

    const dimensionedScalar v_zero(dimVolume/dimTime, Zero);

    // Courant numbers used to adjust the time-step
    scalar CoNum = 0.0;
    scalar meanCoNum = 0.0;

    // Store cell volumes (useful later in the code)
    cellVolume.ref() = mesh.V(); // Not applicable to cells at boundaries

    Info<< "\nStarting time loop\n" << endl;

    while (runTime.run())
    {
        // --- Directed interpolation of primitive fields onto faces

        surfaceScalarField rho_pos(interpolate(rho, pos));
        surfaceScalarField rho_neg(interpolate(rho, neg));

        surfaceVectorField rhoU_pos(interpolate(rhoU, pos, U.name()));
        surfaceVectorField rhoU_neg(interpolate(rhoU, neg, U.name()));

        surfaceScalarField rhoY_pos(interpolate(rhoY, pos, Y.name()));
	surfaceScalarField rhoY_neg(interpolate(rhoY, neg, Y.name()));

        surfaceScalarField rhoN_pos(interpolate(rhoN, pos, N.name()));
	surfaceScalarField rhoN_neg(interpolate(rhoN, neg, N.name()));

        volScalarField rPsi("rPsi", 1.0/psi);
        surfaceScalarField rPsi_pos(interpolate(rPsi, pos, T.name()));
        surfaceScalarField rPsi_neg(interpolate(rPsi, neg, T.name()));

        surfaceScalarField e_pos(interpolate(e, pos, T.name()));
        surfaceScalarField e_neg(interpolate(e, neg, T.name()));

        surfaceVectorField U_pos("U_pos", rhoU_pos/rho_pos);
        surfaceVectorField U_neg("U_neg", rhoU_neg/rho_neg);

        surfaceScalarField Y_pos("Y_pos", rhoY_pos/rho_pos);
	surfaceScalarField Y_neg("Y_neg", rhoY_neg/rho_neg);

        surfaceScalarField N_pos("N_pos", rhoN_pos/rho_pos);
	surfaceScalarField N_neg("N_neg", rhoN_neg/rho_neg);

        surfaceScalarField p_pos("p_pos", rho_pos*rPsi_pos);
        surfaceScalarField p_neg("p_neg", rho_neg*rPsi_neg);

        surfaceScalarField phiv_pos("phiv_pos", U_pos & mesh.Sf());
        // Note: extracted out the orientation so becomes unoriented
        phiv_pos.setOriented(false);
        surfaceScalarField phiv_neg("phiv_neg", U_neg & mesh.Sf());
        phiv_neg.setOriented(false);

	// --- Thermophysical properties
        Cp = thermo.Cp();              // Specific heat at constant pressure
        Cv = thermo.Cv();              // Specific heat at constant volume
        gamma = thermo.gamma();        // Ratio of specific heats
        c = sqrt(gamma*rPsi);          // Speed of sound

	// Evaluate convective fluxes
        surfaceScalarField cSf_pos
        (
            "cSf_pos",
            interpolate(c, pos, T.name())*mesh.magSf()
        );

        surfaceScalarField cSf_neg
        (
            "cSf_neg",
            interpolate(c, neg, T.name())*mesh.magSf()
        );

        surfaceScalarField ap
        (
            "ap",
            max(max(phiv_pos + cSf_pos, phiv_neg + cSf_neg), v_zero)
        );

        surfaceScalarField am
        (
            "am",
            min(min(phiv_pos - cSf_pos, phiv_neg - cSf_neg), v_zero)
        );

        surfaceScalarField a_pos("a_pos", ap/(ap - am));

        surfaceScalarField amaxSf("amaxSf", max(mag(am), mag(ap)));

        surfaceScalarField aSf("aSf", am*a_pos);

        if (fluxScheme == "Tadmor")
        {
            aSf = -0.5*amaxSf;
            a_pos = 0.5;
        }

        surfaceScalarField a_neg("a_neg", 1.0 - a_pos);

        phiv_pos *= a_pos;
        phiv_neg *= a_neg;

        surfaceScalarField aphiv_pos("aphiv_pos", phiv_pos - aSf);
        surfaceScalarField aphiv_neg("aphiv_neg", phiv_neg + aSf);

        // Reuse amaxSf for the maximum positive and negative fluxes
        // estimated by the central scheme
        amaxSf = max(mag(aphiv_pos), mag(aphiv_neg));

        #include "centralCourantNo.H"
        #include "readTimeControls.H"

        if (LTS)
        {
            #include "setRDeltaT.H"
        }
        else
        {
            #include "setDeltaT.H"
        }

        ++runTime;

        Info<< "Time = " << runTime.timeName() << nl << endl;

        phi = aphiv_pos*rho_pos + aphiv_neg*rho_neg;

        phiN = aphiv_pos*rhoN_pos + aphiv_neg*rhoN_neg;

        phiY = aphiv_pos*rhoY_pos + aphiv_neg*rhoY_neg;

	surfaceVectorField phiU(aphiv_pos*rhoU_pos + aphiv_neg*rhoU_neg);
        // Note: reassembled orientation from the pos and neg parts so becomes
        // oriented
        phiU.setOriented(true);

	surfaceVectorField phiUp(phiU + (a_pos*p_pos + a_neg*p_neg)*mesh.Sf());

        surfaceScalarField phiEp
        (
            "phiEp",
            aphiv_pos*(rho_pos*(e_pos + 0.5*magSqr(U_pos)) + p_pos)
          + aphiv_neg*(rho_neg*(e_neg + 0.5*magSqr(U_neg)) + p_neg)
          + aSf*p_pos - aSf*p_neg
        );

	// --- Tranpsort properties
        volScalarField muEff("muEff", turbulence->muEff());
        volTensorField tauMC("tauMC", muEff*dev2(Foam::T(fvc::grad(U))));

        // Auxilliary terms for the source terms
        SourceMomentumFactor = -(Source_Y_nucleation +
                                  Source_Y_growth_active_coeff*rhoY)/rho;

        Source_e = -h_droplet*(Source_Y_nucleation +
                                Source_Y_growth_active_coeff*rhoY);

        // --- Solve density
        solve(fvm::ddt(rho) + fvc::div(phi) ==
        -(Source_Y_nucleation + Source_Y_growth_active_coeff*rhoY));

        // --- Solve momentum
	volVectorField Source_U("Source_U", -U*Source_Y);
	volVectorField Source_U_linear_explicit("Source_U_linear_explicit", SourceMomentumFactor*rhoU);

        solve(fvm::ddt(rhoU) + fvc::div(phiUp) ==
	Source_U - Source_U_linear_explicit + fvm::SuSp(SourceMomentumFactor, rhoU));

        U.ref() = rhoU()/rho();
        U.correctBoundaryConditions();
        rhoU.boundaryFieldRef() == rho.boundaryField()*U.boundaryField();

        if (!inviscid)
        {
            solve
            (
                fvm::ddt(rho, U) - fvc::ddt(rho, U)
              - fvm::laplacian(muEff, U)
              - fvc::div(tauMC)
            );
            rhoU = rho*U;
        }

        // --- Solve energy
        surfaceScalarField sigmaDotU
        (
            "sigmaDotU",
            (
                fvc::interpolate(muEff)*mesh.magSf()*fvc::snGrad(U)
              + fvc::dotInterpolate(mesh.Sf(), tauMC)
            )
          & (a_pos*U_pos + a_neg*U_neg)
        );

        solve
        (
            fvm::ddt(rhoE)
          + fvc::div(phiEp)
          - fvc::div(sigmaDotU)
          ==
          Source_e
        );

        e = rhoE/rho - 0.5*magSqr(U);
        e.correctBoundaryConditions();
        thermo.correct();
        rhoE.boundaryFieldRef() ==
            rho.boundaryField()*
            (
                e.boundaryField() + 0.5*magSqr(U.boundaryField())
            );

        if (!inviscid)
        {
            solve
            (
                fvm::ddt(rho, e) - fvc::ddt(rho, e)
              - fvm::laplacian(turbulence->alphaEff(), e)
            );
            thermo.correct();
            rhoE = rho*(e + 0.5*magSqr(U));
        }

	// --- Solve droplet number
	solve(fvm::ddt(rhoN) + fvc::div(phiN) == J);
	N.ref() = rhoN()/rho();
	N.correctBoundaryConditions();
	rhoN.boundaryFieldRef() == rho.boundaryField()*N.boundaryField();

	// --- Solve grain mass fraction
	volScalarField Source_Y_growth_linear_explicit("Source_Y_growth_linear_explicit", Source_Y_growth_active_coeff*rhoY);

	solve
	    (
		fvm::ddt(rhoY)
		+ fvc::div(phiY)
		==
		Source_Y
		- Source_Y_growth_linear_explicit
		+ fvm::SuSp(Source_Y_growth_active_coeff, rhoY)
            );

	Y.ref() = rhoY()/rho();

	Y.correctBoundaryConditions();

	rhoY.boundaryFieldRef() == rho.boundaryField()*Y.boundaryField();

        p.ref() = rho()/psi();
        p.correctBoundaryConditions();
        rho.boundaryFieldRef() == psi.boundaryField()*p.boundaryField();

	Mach = mag(U)/c;
	h = e + p/rho; // Specific enthalpy of gas

        turbulence->correct();

        // Transport properties
          // Plain ones, not "effective" ones as above, because the
          // nucleation model does not concern itself with turbulence artefacts
        volScalarField kappa("kappa", thermo.kappa());	// Thermal conductivity
        volScalarField mu("mu", thermo.mu());         	// Dynamic viscosity

        // Flow similarity parameters
        volScalarField Prandtl("Prandtl", thermo.Cp()*thermo.mu()/thermo.kappa()); // Prandtl number


        // -------------------------------------------------------------- //
        // -------------------------------------------------------------- //
      	// --- UPDATE THE CONSERVATION SOURCE TERMS
      	// -------------------------------------------------------------- //
        // -------------------------------------------------------------- //

        // --- Loop over all cells in the internal field
        // (i.e. cells at the boundaries not included, coming later)
        forAll(T, cellI)
        {
	  #include "phaseChangeThermodynamics/saturationProperties.H"

          // Since the conservation equations for N and Y are not directly
          // coupled, it may happen numerically that N>0 while Y=0 (or, rarely,
          // vice-versa).
          // To remedy this, here, we delete N or Y if there is an
          // inconsistency between them
          if (N[cellI]*rho[cellI]*cellVolume[cellI] > 1.0
                          && Y[cellI] > 1.00E-12)
          {
          }
          else
          {
            N[cellI] = 0.0;
            Y[cellI] = 0.0;
          }

          // Only bother with condensation checks if temperature below...
              // ...both the critical value and saturation value and also
              // higher than a minimum threshold of 273.15 for the
              // thermophysical relations
          if (T[cellI] < T_crit.value()
              && T[cellI] < Tsat[cellI]
              && T[cellI] >= 173.16)
          {
            // --- UPDATE LIQUID-RELATED THERMODYNAMIC PROPERTIES IN THE CELL

                // External file for liquid-related properties
		#include "phaseChangeThermodynamics/liquidThermophysicalProperties.H"

        //******************************************************************//
        //******************************************************************//

                // Only bother with condensation calculations if there is...
                // ...at least one liquid droplet in the current control volume
                if (N[cellI]*rho[cellI]*cellVolume[cellI] > 1.0
                                && Y[cellI] > 1.00E-12)
                {
                    // Mean radius resulting from existing droplets in the cell
                    r_droplet_actual[cellI] = Foam::pow((3.0*Y[cellI]/
                                              (4.0*pi*rho_grain.value()*
                                              N[cellI])), 1.0/3.0);

                    // Total interfacial surface area per unit mass
                    beta[cellI] = N[cellI] *
                                  4.0*pi*r_droplet_actual[cellI]*
                                  r_droplet_actual[cellI];
                }
                else // Delete the droplets in the cell
                {
                    r_droplet_actual[cellI] = 0.0;
                    beta[cellI]             = 0.0;
                    N[cellI]                = 0.0;
                    Y[cellI]                = 0.0;
                }

                // Only bother with nucleation if saturation ratio > 1
                if (S_sat[cellI] > 1.0 + SMALL)
                {
                  // Change in Gibbs free energy
                  DeltaG[cellI] =  R.value()*T[cellI]*(Foam::log(S_sat[cellI]));

                  // Critical radius
                  r_droplet_critical[cellI] = 2.0*surface_tension[cellI]/
                                                (rho_grain.value()*DeltaG[cellI]);
                }
                else // No supersaturation, set radius to 0, for convenience
                {
                  r_droplet_critical[cellI] = 0.0;
                }

                if (r_droplet_actual[cellI] >= r_droplet_critical[cellI]
                  && r_droplet_critical[cellI] > r_droplet_minimum.value())
                {

                  // Correction factor for the coefficient of
                  // thermal convection from gas to droplet
                  v_corr[cellI] = R.value()*Tsat[cellI]/(2*h_fg[cellI]) *
                       (1 - (gamma[cellI]+1)*Cp[cellI]*Tsat[cellI]/(2*gamma[cellI]*h_fg[cellI]));
                  if (v_corr[cellI] >= 1.0) // For numerical artifacts
                  {
                       v_corr[cellI] = 1.0;
                  }

                  // Mean free path
                  mean_free_path[cellI] = mu[cellI]/p[cellI] *
                                          Foam::sqrt(pi*k_B.value()*T[cellI]/(2*m_gas.value()));

                  // Knudsen number based on the droplet diameter
                  Knudsen_droplet[cellI] = mean_free_path[cellI]/
                                            (2.0*r_droplet_actual[cellI]);

                  // Rate of droplet growth
                  drdt[cellI] = kappa[cellI]*T_sc[cellI]/(rho_grain.value()*h_fg[cellI]*r_droplet_actual[cellI])*
			(1 - r_droplet_critical[cellI]/r_droplet_actual[cellI])/(1 + 3.78*(1 - v_corr[cellI])*
			Knudsen_droplet[cellI]/Prandtl[cellI]);

                  Source_Y_growth_active_coeff[cellI] =
                  3.0*drdt[cellI]*1.0/r_droplet_actual[cellI];
                }
                else
                {
                  drdt[cellI] = 0.0;
                  Source_Y_growth_active_coeff[cellI] = 0.0;
                }


        //****************************************************************//
        //****************************************************************//

                if (r_droplet_critical[cellI] > r_droplet_minimum.value())
                {
                  // Kantrowitz correction factor for the nucleation rate
                  // etaKantrowitz[cellI] = 2.0*(gamma[cellI]-1.0)/
                                         //gamma[cellI]+1.0)*
                                         //h_fg[cellI]/(R.value()*T[cellI])*
                                         //(h_fg[cellI]/
                                         //(R.value()*T[cellI]) - 0.5);
                  // if (etaKantrowitz[cellI] < 0.0 )
                  //{
                    //Info << "WARNING: Kantrowitz correction factor is negative, assumed zero" << endl;
                    //etaKantrowitz[cellI] = 0.0;
                  //}

                  // Nucleation rate of critical radius droplets,
                  // per unit volume of vapour
                  J[cellI] = Foam::sqrt(2.0*surface_tension[cellI]/(pi*
                             m_gas.value()*m_gas.value()*m_gas.value()))*
                             rho[cellI]*rho[cellI]/rho_grain.value()*
                             Foam::exp(-4.0*pi*r_droplet_critical[cellI]*
                             r_droplet_critical[cellI]*surface_tension[cellI]
                             /(3.0*k_B.value()*T[cellI]));

                  // Correction by Wölk and Strey
		  J[cellI] = J[cellI]*Foam::exp(-27.56 + 6500.0/T[cellI]);

                  // If there is at least 1 critically sized molecule generated
                  // in the cell volume over this timestep
                  if (J[cellI]*cellVolume[cellI]*
                        runTime.time().deltaT().value() > 1.0)
                  {
                  }
                  else
                  {
                    J[cellI] = 0.0;
                  }
                }
                else // Value of critical radius unphysically small
                {
                  r_droplet_critical[cellI] = 0.0;
                  J[cellI] = 0.0;
                }

        //******************************************************************//
        //*****************************************************************//

                // Contribution to the liquid mass from the
                // nucleation of new droplets
               Source_Y_nucleation[cellI] = J[cellI]*rho_grain.value()*
                                                4.0/3.0*pi*
                                                r_droplet_critical[cellI]*
                                                r_droplet_critical[cellI]*
                                                r_droplet_critical[cellI];

                // Contribution to the liquid mass from the
                // growth of existing droplets
                Source_Y_growth[cellI] = rho_grain.value()*beta[cellI]
                                                  *drdt[cellI]*rho[cellI];

                // Total (nucleation + growth) liquid mass source term
                Source_Y[cellI] = Source_Y_growth[cellI] + Source_Y_nucleation[cellI];

              }
              else // No supercooling, relevant source terms set to zero
              {
                  J[cellI]                              = 0.0;
                  Source_Y[cellI]                       = 0.0;
                  Source_Y_nucleation[cellI]            = 0.0;
                  Source_Y_growth[cellI]                = 0.0;
                  Source_Y_growth_active_coeff[cellI]   = 0.0;
                  SourceMomentumFactor[cellI]           = 0.0;
                  Source_e[cellI]                       = 0.0;
              }         // End of loop with the temperature checks
        }

        // ---------------------------------------------------------------- //
        // -------------------- END CONDENSATION MODEL -------------------- //
        // ---------------------------------------------------------------- //

        // -------------------------------------------------------------------
        // --- Update timestep
        // -------------------------------------------------------------------

        runTime.write();

        runTime.printExecutionTime(Info);
    }

    Info<< "End\n" << endl;

    return 0;
}

// ************************************************************************* //
