import contextlib
import io
import unittest

from motorrijtuigenbelasting.__main__ import main


def run(*argv: str) -> str:
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        main(list(argv))
    return output.getvalue()


def run_error(*argv: str) -> str:
    errors = io.StringIO()
    with contextlib.redirect_stderr(errors), expect_usage_error():
        main(list(argv))
    return errors.getvalue()


@contextlib.contextmanager
def expect_usage_error():
    try:
        yield
    except SystemExit as exit:
        assert exit.code == 2
    else:
        raise AssertionError("expected SystemExit")


class TestCli(unittest.TestCase):
    def test_car(self):
        output = run(
            "--weight", "1300", "--province", "noord-holland", "--year", "2026"
        )
        self.assertEqual(output, "€ 172 per three months\n")

    def test_yearly_with_breakdown(self):
        output = run(
            "--weight", "820",
            "--fuel", "diesel",
            "--diesel-particles",
            "--province", "Noord Holland",
            "--year", "2026",
            "--breakdown",
            "--yearly",
        )  # fmt: skip
        self.assertIn("fijnstoftoeslag: € 28.89", output)
        self.assertTrue(output.endswith("€ 788 per year\n"))

    def test_motorcycle_kwarttarief(self):
        output = run(
            "--vehicle", "motorcycle",
            "--province", "gelderland",
            "--year", "2026",
            "--first-use", "1987",
            "--yearly",
        )  # fmt: skip
        self.assertEqual(output, "€ 37 per year\n")

    def test_dates(self):
        output = run(
            "--weight", "820",
            "--fuel", "diesel",
            "--province", "noord-holland",
            "--first-use", "1986-11-15",
            "--year", "2026-11-15",
        )  # fmt: skip
        self.assertEqual(output, "€ 0 per three months\n")

    def test_errors(self):
        self.assertIn(
            "Unknown province",
            run_error("--weight", "1300", "--province", "mars", "--year", "2026"),
        )
        self.assertIn(
            "No tax data for 2010",
            run_error("--weight", "1300", "--province", "utrecht", "--year", "2010"),
        )
        self.assertIn(
            "--weight is required", run_error("--province", "utrecht", "--year", "2026")
        )
