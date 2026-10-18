"""Command line interface.

Example: python -m motorrijtuigenbelasting --weight 1300 --fuel benzine --province noord-holland
"""

import argparse
import datetime

from . import PROVINCES, Car, EnergySource, Motorcycle, from_kenteken
from .vehicles.base import Moment

VEHICLES = {"car": Car, "motorcycle": Motorcycle}


def moment(value: str) -> Moment:
    """A year like 2026 or a date like 2026-11-15."""
    if value.isdigit():
        return int(value)
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"expected a year or a date (YYYY-MM-DD), got {value!r}"
        ) from None


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mrb",
        description="Calculate the Dutch motorrijtuigenbelasting.",
    )
    parser.add_argument(
        "--kenteken",
        help="look up the vehicle in the RDW open data, instead of the options below",
    )
    parser.add_argument("--vehicle", choices=VEHICLES, default="car")
    parser.add_argument(
        "--weight",
        type=float,
        help="massa rijklaar in kg from the kentekenregister, required for a car",
    )
    parser.add_argument(
        "--fuel",
        choices=[source.value for source in EnergySource],
        default=EnergySource.BENZINE.value,
    )
    parser.add_argument(
        "--province",
        required=True,
        help=f"one of {', '.join(PROVINCES)}",
    )
    parser.add_argument(
        "--year",
        type=moment,
        default=datetime.date.today().year,
        help="year or date (YYYY-MM-DD) to calculate, defaults to this year",
    )
    parser.add_argument(
        "--first-use",
        type=moment,
        help="datum eerste toelating, a year or a date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--low-co2",
        action="store_true",
        help="CO2 emission above 0 and at most 50 g/km (cars only)",
    )
    parser.add_argument(
        "--diesel-particles",
        action="store_true",
        help="particle emission above the Euro 5 limit (diesel cars only)",
    )
    parser.add_argument(
        "--yearly", action="store_true", help="show the amount per year"
    )
    parser.add_argument(
        "--breakdown", action="store_true", help="show how the amount is built up"
    )
    return parser


def build_vehicle(args: argparse.Namespace):
    if args.vehicle == "car":
        return Car(
            weight=args.weight,
            energy_source=args.fuel,
            manufacturing_year=args.first_use,
            co2_emissions=args.low_co2,
            diesel_particles=args.diesel_particles,
        )
    return Motorcycle(
        weight=args.weight or 0,
        energy_source=args.fuel,
        manufacturing_year=args.first_use,
    )


def main(argv: list[str] | None = None) -> int:
    arguments = parser()
    args = arguments.parse_args(argv)
    if not args.kenteken and args.vehicle == "car" and args.weight is None:
        arguments.error("--weight is required for a car")
    try:
        vehicle = from_kenteken(args.kenteken) if args.kenteken else build_vehicle(args)
        breakdown = vehicle.calculate_breakdown(year=args.year, province=args.province)
    except (KeyError, ValueError, NotImplementedError, OSError) as error:
        arguments.error(error.args[0] if error.args else str(error))

    if args.breakdown:
        print(f"Rule: {breakdown.rule.value} (tariff of {breakdown.tariff_year})")
        for name, amount in breakdown.components.items():
            print(f"  {name}: € {amount:.2f}")
        print(f"  opcenten: € {breakdown.opcenten:.2f}")
        print(f"  emission factor: {breakdown.emission_factor:g}")
        if breakdown.maximum is not None:
            print(f"  maximum per year: € {breakdown.maximum:.2f}")

    if args.yearly:
        print(f"€ {breakdown.per_year} per year")
    else:
        print(f"€ {breakdown.per_three_months} per three months")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
