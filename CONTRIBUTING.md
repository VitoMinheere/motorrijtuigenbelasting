# Contributing

## Development setup

```bash
git clone https://github.com/VitoMinheere/motorrijtuigenbelasting.git
cd motorrijtuigenbelasting
pip install -e .[dev]
```

Before opening a pull request, run the same checks as CI:

```bash
coverage run -m unittest discover -s tests && coverage report
ruff check .
black --check .
mypy
```

## Adding a new tax year

Every January the tariffs, opcenten and some percentages change. All of them live in `motorrijtuigenbelasting/data/tax_data.json`; the code normally does not need to change.

1. **Wait for the sources.** The law version of 1 January must be on wetten.overheid.nl, and CBS must have published the opcenten for the new year (usually in January).
2. **Parse the year:**
   ```bash
   python scripts/add_year.py 2027            # prints the parsed values
   python scripts/add_year.py 2027 --write    # adds them to tax_data.json
   ```
   The script reads art. 23, 23b, 25, 31 and 84a from `https://wetten.overheid.nl/BWBR0006324/2027-01-01` and the opcenten from CBS StatLine table [80889ned](https://opendata.cbs.nl/statline/#/CBS/nl/dataset/80889ned/table). If the law changed its wording the script stops with an error. Then read the article and update the parser or enter the values by hand.
3. **Check the result:**
   - Add the tabelcorrectiefactor of the new year to `TABELCORRECTIEFACTOR` in `tests/test_tax_data.py`. It is published in the Rijksoverheid overview "Belangrijkste wijzigingen belastingen <year>".
   - Run `python scripts/add_year.py --check 2027` and `python scripts/check_opcenten.py`.
   - Run the tests. If a table changed by more than the tabelcorrectiefactor, find out why in the law and add it to `OTHER_CHANGES` with an explanation.
4. **Add test cases** for the new year to `TOTAL_TAX` in `tests/test_car.py` and `tests/test_motorcycle.py`. Check at least a few with the Belastingdienst calculator ("Motorrijtuigenbelasting berekenen" on belastingdienst.nl), and say which ones in a comment.
5. **Regenerate the example output** with `python scripts/generate_output.py benzine`. A test fails when `output/benzine.json` is out of date.
6. **Update the README** year range.

### Things to look out for
- New percentages in art. 23b (zero emission), e.g. 70% in 2026–2028 and 75% in 2029.
- Changes in what counts as massa rijklaar or eigen massa (see the README).
- A law version that changes mid-year (wetten.overheid.nl shows "Geldend van ... t/m ..."). Compare both versions with the parser.
