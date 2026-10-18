# Changelog

## 0.2.0

### Added
- Tax years 2014–2026, each with its own tariffs from the Wet MRB 1994 text and opcenten from CBS StatLine 80889ned, instead of a base tariff corrected with inflation (#10).
- `calculate_yearly_tax()`, which gives the yearly amount, including the kwarttarief that is paid once per year.
- `calculate_breakdown()` and `TaxBreakdown`, `TaxRule`: the parts of the tax (base, brandstoftoeslag, fijnstoftoeslag, opcenten, discount, rule) (#20).
- `from_kenteken()`: build a `Car` or `Motorcycle` from the RDW open data, including LPG G3 installations (#21, #45).
- Command line interface: `mrb` or `python -m motorrijtuigenbelasting` (#22).
- `EnergySource.WATERSTOF`: hydrogen cars pay no brandstoftoeslag and get the zero emission discount (#13).
- `Province` enum, and `PROVINCES` and `SUPPORTED_YEARS` constants (#24).
- Dates: `manufacturing_year` and `year` accept a `datetime.date`, so the oldtimer rule applies from the exact day a vehicle turns 40 (#15).
- `scripts/add_year.py` and `scripts/check_opcenten.py` to add and verify a tax year (#27).

### Changed
- **Weights are massa rijklaar**, as in the kentekenregister and the law since 1 July 2026. Pass massa rijklaar for every year.
- **`year` and `province` are keyword arguments** of `calculate_total_tax`, `calculate_yearly_tax`, `calculate_quarterly_tax` and `calculate_opcenten`. Positional calls still work with a `DeprecationWarning` and will stop working in a later release (#23).
- `is_historic(year)` and `is_kwarttarief(year)` take the year. `set_calculation_year()` and `calculation_year` are removed.
- `EnergySource.LPG.value` is `"lpg"`; it was an alias of `EnergySource.OVERIGE`.
- Vehicle types implement `tax_components()` instead of `calculate_base_tax()`.
- Province names are normalised (`"Noord Holland"` works). Unknown provinces and years raise a `KeyError` that lists the valid values.
- Invalid weights and energy sources raise `ValueError`. Weights may have decimals.
- Requires Python 3.10 or newer.

### Fixed
- The kwarttarief is the previous year's quarterly tariff plus this year's opcenten, paid once per year, up to the maximum (art. 84a).
- No inflation correction on top of tariffs that already include it.
- The fijnstoftoeslag only applies from 2020 (#12).
- Limburg opcenten 2025: 85.8 instead of 88.5 (#35).
- Electric motorcycles pay the full tariff from 2026.
- The package can be built and installed: `tax_data.json` is included in the wheel.

## 0.1.0

Initial release.
