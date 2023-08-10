#!/usr/bin/env python
import logging
import os

import click
import numpy
from openeye import oechem
from openff.toolkit.topology import Molecule
from openff.toolkit.typing.engines import smirnoff
from openff.toolkit.utils import GLOBAL_TOOLKIT_REGISTRY, OpenEyeToolkitWrapper
from openmmforcefields.generators import GAFFTemplateGenerator
from simtk import openmm, unit
from simtk.openmm.app import ForceField


def run_openmm(molecule: Molecule, system: openmm.System):
    """
    Minimize molecule with the specified system and return the optimized
    positions.
    """

    # Make sure we consistently only use OE in this script
    for toolkit in GLOBAL_TOOLKIT_REGISTRY.registered_toolkits:
        if isinstance(toolkit, OpenEyeToolkitWrapper):
            continue
        GLOBAL_TOOLKIT_REGISTRY.deregister_toolkit(toolkit)

    integrator = openmm.VerletIntegrator(0.1 * unit.femtoseconds)

    platform = openmm.Platform.getPlatformByName("Reference")

    openmm_context = openmm.Context(system, integrator, platform)
    openmm_context.setPositions(
        molecule.conformers[0].value_in_unit(unit.nanometer)
    )

    openmm.LocalEnergyMinimizer.minimize(openmm_context, 5.0e-9, 1500)

    conformer = openmm_context.getState(getPositions=True).getPositions(
        asNumpy=True
    )
    energy = openmm_context.getState(getEnergy=True).getPotentialEnergy()

    return conformer, energy.value_in_unit(unit.kilocalories_per_mole)


@click.command()
@click.option("--input-sdf", type=click.Path(exists=True, dir_okay=False))
@click.option("--force-field", type=click.Path(exists=False, dir_okay=False))
@click.option("--output", type=click.Path(exists=False, dir_okay=False))
@click.option("--force-field-type", default="SMIRNOFF")
def main(input_sdf, force_field, force_field_type, output):
    failed = False
    with oechem.oemolistream(input_sdf) as input_stream, oechem.oemolostream(
        output
    ) as output_stream:
        try:
            for oe_molecule in input_stream.GetOEGraphMols():
                oe_molecule = oechem.OEGraphMol(oe_molecule)
                oechem.OE3DToInternalStereo(oe_molecule)

                oe_data = {
                    pair.GetTag(): pair.GetValue()
                    for pair in oechem.OEGetSDDataPairs(oe_molecule)
                }

                off_molecule = Molecule.from_openeye(
                    oe_molecule, allow_undefined_stereo=True
                )

                off_molecule._conformers = [
                    numpy.array(
                        [
                            oe_molecule.GetCoords()[i]
                            for i in range(off_molecule.n_atoms)
                        ]
                    )
                    * unit.angstrom
                ]

                if force_field_type.lower() == "smirnoff":
                    smirnoff_force_field = smirnoff.ForceField(
                        force_field, allow_cosmetic_attributes=True
                    )

                    if (
                        "Constraints"
                        in smirnoff_force_field.registered_parameter_handlers
                    ):
                        smirnoff_force_field.deregister_parameter_handler(
                            "Constraints"
                        )

                    omm_system = smirnoff_force_field.create_openmm_system(
                        off_molecule.to_topology()
                    )

                elif force_field_type.lower() == "gaff":
                    force_field = ForceField()

                    generator = GAFFTemplateGenerator(
                        molecules=off_molecule, forcefield=force_field
                    )

                    force_field.registerTemplateGenerator(generator.generator)

                    omm_system = force_field.createSystem(
                        off_molecule.to_topology().to_openmm(),
                        nonbondedCutoff=0.9 * unit.nanometer,
                        constraints=None,
                    )

                else:
                    raise NotImplementedError()

                new_conformer, energy = run_openmm(off_molecule, omm_system)

                off_molecule._conformers = [new_conformer]
                oe_molecule = off_molecule.to_openeye()

                oechem.OESetSDData(oe_molecule, "Energy FFXML", str(energy))

                for key, value in oe_data.items():
                    oechem.OESetSDData(oe_molecule, key, value)

                oechem.OEWriteMolecule(output_stream, oe_molecule)

        except BaseException:
            logging.exception(
                f"failed to minimize {input_sdf} with {force_field}"
            )
            failed = True

    if failed and os.path.isfile(output):
        os.unlink(output)


if __name__ == "__main__":
    main()
