#!/usr/bin/env python3
"""Purchase and financing math for a German residential property.

Reads an Obsidian property note (type: objekt) and, optionally, a financing
scenario note (type: finanzierung-szenario). Every input can be overridden on the
command line, so the script also works without any vault at all.

    python3 property_calc.py OBJ-2026-001.md --scenario Szenario-Basis.md
    python3 property_calc.py --price 485000 --bundesland Bayern --area 92 \
        --equity 120000 --rate 3.6 --rent 1250

Deliberately shows which figures are inputs, which are defaults and which are
derived. Standard library only.

Rates and conventional planning values: see references/kaufnebenkosten-de.md.
This is a calculator, not tax or legal advice.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from frontmatter import as_number, field, load_profile, read_note  # noqa: E402

# Grunderwerbsteuer per Bundesland, in percent.
# Stand: model knowledge as of May 2026 — VERIFY before relying on it.
# Keep in sync with references/kaufnebenkosten-de.md.
GREST_RATES: dict[str, float] = {
    "baden-württemberg": 5.0,
    "bayern": 3.5,
    "berlin": 6.0,
    "brandenburg": 6.5,
    "bremen": 5.0,
    "hamburg": 5.5,
    "hessen": 6.0,
    "mecklenburg-vorpommern": 6.0,
    "niedersachsen": 5.0,
    "nordrhein-westfalen": 6.5,
    "rheinland-pfalz": 5.0,
    "saarland": 6.5,
    "sachsen": 5.5,
    "sachsen-anhalt": 5.0,
    "schleswig-holstein": 6.5,
    "thüringen": 5.0,
}
GREST_ASOF = "Kenntnisstand Mai 2026 — Satz vor Verwendung prüfen"

# Common abbreviations. Without these a note saying "NW" silently produced a
# 0 % rate, and the resulting purchase costs looked plausible.
GREST_ALIASES: dict[str, str] = {
    "bw": "baden-württemberg", "baden-wuerttemberg": "baden-württemberg",
    "by": "bayern", "be": "berlin", "bb": "brandenburg", "hb": "bremen",
    "hh": "hamburg", "he": "hessen",
    "mv": "mecklenburg-vorpommern",
    "ni": "niedersachsen", "nds": "niedersachsen",
    "nw": "nordrhein-westfalen", "nrw": "nordrhein-westfalen",
    "rp": "rheinland-pfalz", "sl": "saarland", "sn": "sachsen",
    "st": "sachsen-anhalt", "sachsen anhalt": "sachsen-anhalt",
    "sh": "schleswig-holstein", "th": "thüringen", "thueringen": "thüringen",
}


def grest_rate(bundesland: str) -> float | None:
    """Rate for a Bundesland, accepting full names and usual abbreviations."""
    key = str(bundesland).strip().lower()
    key = GREST_ALIASES.get(key, key)
    return GREST_RATES.get(key)

DEFAULTS = {
    "notary_pct": 1.5,
    "land_register_pct": 0.5,
    "repayment_pct": 2.0,
    "fixed_years": 10,
    "stress_rate_pct": 6.0,
    "vacancy_pct": 3.0,
    "maintenance_eur_m2a": 12.0,
    "management_eur_month": 30.0,
}

MAX_MONTHS = 600  # 50 years; anything longer is not a plan


# --------------------------------------------------------------------------- #
# formatting
# --------------------------------------------------------------------------- #
def eur(value: float | None, decimals: int = 0) -> str:
    if value is None:
        return "—"
    if value == 0:
        value = 0.0  # avoid rendering "-0 €"
    text = f"{value:,.{decimals}f}"
    text = text.replace(",", "\x00").replace(".", ",").replace("\x00", ".")
    return f"{text} €"


def pct(value: float | None, decimals: int = 2) -> str:
    if value is None:
        return "—"
    return f"{value:.{decimals}f}".replace(".", ",") + " %"


def num(value: float | None, decimals: int = 1) -> str:
    if value is None:
        return "—"
    return f"{value:.{decimals}f}".replace(".", ",")


# --------------------------------------------------------------------------- #
# finance
# --------------------------------------------------------------------------- #
def amortize(loan: float, rate_pct: float, repayment_pct: float, months: int
             ) -> dict[str, Any]:
    """German Annuitätendarlehen: constant annuity, monthly interest on the
    remaining balance. Reports the state after `months` payments and the month in
    which the loan is fully repaid if the conditions stayed unchanged."""
    annuity_year = loan * (rate_pct + repayment_pct) / 100.0
    monthly = annuity_year / 12.0
    monthly_rate = rate_pct / 100.0 / 12.0

    balance = loan
    interest_paid = 0.0
    principal_paid = 0.0
    balance_at_months = loan
    payoff_month: int | None = None

    for month in range(1, MAX_MONTHS + 1):
        interest = balance * monthly_rate
        principal = monthly - interest
        # principal <= 0 means the annuity does not cover the interest: the
        # balance stays flat or grows. Keep simulating so the interest actually
        # paid during the fixed period is reported correctly.
        principal = min(principal, balance)
        balance -= principal
        if month <= months:
            interest_paid += interest
            principal_paid += principal
            balance_at_months = balance
        if balance <= 1e-9:
            payoff_month = month
            break

    if months == 0:
        balance_at_months = loan
    elif payoff_month is not None and payoff_month <= months:
        balance_at_months = 0.0

    return {
        "annuity_year": annuity_year,
        "monthly_payment": monthly,
        "remaining_balance": balance_at_months,
        "interest_paid": interest_paid,
        "principal_paid": principal_paid,
        "payoff_months": payoff_month,
        "never_amortizes": payoff_month is None,
    }


def annuity_payment(balance: float, rate_pct: float, months: int) -> float:
    """Monthly payment that fully repays `balance` over `months` at `rate_pct`."""
    if months <= 0:
        return balance
    monthly_rate = rate_pct / 100.0 / 12.0
    if monthly_rate == 0:
        return balance / months
    return balance * monthly_rate / (1 - (1 + monthly_rate) ** (-months))


# --------------------------------------------------------------------------- #
# input assembly
# --------------------------------------------------------------------------- #
class Inputs:
    def __init__(self) -> None:
        self.values: dict[str, Any] = {}
        self.origin: dict[str, str] = {}
        self.warnings: list[str] = []
        self.notes: list[str] = []

    def set(self, key: str, value: Any, origin: str) -> None:
        if value is None:
            return
        self.values[key] = value
        self.origin[key] = origin

    def get(self, key: str) -> Any:
        return self.values.get(key)

    def default(self, key: str) -> None:
        if key not in self.values and key in DEFAULTS:
            self.values[key] = DEFAULTS[key]
            self.origin[key] = "Standardwert"

    def warn(self, message: str) -> None:
        if message not in self.warnings:
            self.warnings.append(message)

    def clone_with_price(self, price: float) -> "Inputs":
        """A throwaway copy for solving — warnings are discarded, not repeated."""
        copy = Inputs()
        copy.values = dict(self.values)
        copy.origin = dict(self.origin)
        copy.values["price_override"] = price
        copy.origin["price_override"] = "Suchlauf"
        return copy


NOTE_FIELDS = {
    "price_asking": "price_asking",
    "price_offered": "price_offered",
    "price_agreed": "price_agreed",
    "living_area_m2": "living_area_m2",
    "plot_area_m2": "plot_area_m2",
    "bundesland": "bundesland",
    "commission_pct": "commission_pct",
    "hausgeld_month": "hausgeld_month",
    "hausgeld_reserve_share_month": "hausgeld_reserve_share_month",
    "grundsteuer_year": "grundsteuer_year",
    "rent_cold_month": "rent_cold_month",
    "rent_potential_month": "rent_potential_month",
    "parking_price": "parking_price",
    "year_built": "year_built",
    "property_type": "property_type",
    "usage_intent": "usage_intent",
}

SCENARIO_FIELDS = [
    "equity", "price_override", "interest_rate_pct", "repayment_pct",
    "fixed_years", "stress_rate_pct", "finance_side_costs", "renovation_cost",
    "grunderwerbsteuer_pct", "notary_pct", "land_register_pct", "commission_pct",
    "rent_used_month", "vacancy_pct", "maintenance_eur_m2a", "living_area_m2",
    "management_eur_month", "hausgeld_non_apportionable_month",
]

TEXT_FIELDS = {"bundesland", "property_type", "usage_intent"}


def collect(args: argparse.Namespace) -> Inputs:
    data = Inputs()
    profile = load_profile(args.profile)

    if args.note:
        fm, _ = read_note(args.note)
        known_types = set(profile.get("object_type_values") or []) | {"objekt"}
        if fm.get("type") is not None and fm.get("type") not in known_types:
            data.warn(f"Notiz hat type: {fm.get('type')!r}, erwartet wurde eines von "
                      f"{sorted(known_types)}.")
        label = f"Objektnotiz ({Path(args.note).name})"
        for key, canonical in NOTE_FIELDS.items():
            raw = field(fm, canonical, profile)
            value = raw if key in TEXT_FIELDS else as_number(raw)
            data.set(key, value, label)
        for key in ("id", "title", "data_asof"):
            data.set(key, field(fm, key, profile), label)
        if profile:
            data.notes.append(f"Vault-Profil verwendet: {profile.get('_path')}")

    if args.scenario:
        fm, _ = read_note(args.scenario)
        fm = {k: v for k, v in fm.items()}
        label = f"Szenario ({Path(args.scenario).name})"
        for name in SCENARIO_FIELDS:
            if name not in fm:
                continue
            raw = fm.get(name)
            value = raw if isinstance(raw, bool) else as_number(raw)
            data.set(name, value, label)
        data.set("scenario_name", fm.get("name"), label)

    cli = {
        "price_override": args.price, "living_area_m2": args.area,
        "bundesland": args.bundesland, "equity": args.equity,
        "interest_rate_pct": args.rate, "repayment_pct": args.repayment,
        "fixed_years": args.fixed_years, "stress_rate_pct": args.stress_rate,
        "commission_pct": args.commission, "renovation_cost": args.renovation,
        "rent_used_month": args.rent, "grunderwerbsteuer_pct": args.grest,
        "hausgeld_month": args.hausgeld,
        "hausgeld_non_apportionable_month": args.hausgeld_nonapportionable,
    }
    for key, value in cli.items():
        data.set(key, value, "CLI-Argument")

    for key in DEFAULTS:
        data.default(key)
    return data


# --------------------------------------------------------------------------- #
# the calculation
# --------------------------------------------------------------------------- #
def compute(data: Inputs) -> dict[str, Any]:
    out: dict[str, Any] = {"warnings": data.warnings, "inputs": {}, "origin": data.origin}
    used_defaults: set[str] = set()

    def use(key: str) -> Any:
        """Read a value and remember it if it came from a default."""
        if data.origin.get(key) == "Standardwert":
            used_defaults.add(key)
        return data.get(key)

    # --- price ------------------------------------------------------------- #
    price = None
    for key in ("price_override", "price_agreed", "price_offered", "price_asking"):
        if data.get(key) is not None:
            price = float(data.get(key))
            out["price_basis"] = key
            break
    if price is None:
        raise SystemExit("Kein Kaufpreis gefunden. --price setzen oder "
                         "price_asking/price_agreed in der Objektnotiz pflegen.")
    if out["price_basis"] == "price_asking":
        data.warn("Gerechnet wird mit dem Angebotspreis (price_asking), "
                  "nicht mit einem verhandelten Preis.")

    area = data.get("living_area_m2")
    if area is None:
        data.warn("Keine Wohnfläche (living_area_m2) — €/m² und Instandhaltung "
                  "können nicht berechnet werden.")

    # --- side costs -------------------------------------------------------- #
    grest = data.get("grunderwerbsteuer_pct")
    if grest is None:
        bundesland = data.get("bundesland")
        if bundesland:
            grest = grest_rate(bundesland)
            if grest is None:
                data.warn(f"Bundesland {bundesland!r} unbekannt — "
                          "Grunderwerbsteuer bitte mit --grest setzen.")
            else:
                data.origin["grunderwerbsteuer_pct"] = f"Tabelle Bundesland ({bundesland})"
        else:
            data.warn("Kein Bundesland gesetzt — Grunderwerbsteuer fehlt in der "
                      "Rechnung. bundesland im Frontmatter ergänzen oder --grest setzen.")
    if grest is None:
        grest = 0.0

    notary = float(use("notary_pct"))
    land_register = float(use("land_register_pct"))
    commission = data.get("commission_pct")
    if commission is None:
        commission = 0.0
        data.warn("Keine Maklerprovision (commission_pct) — es wird mit 0 % "
                  "gerechnet. Provisionsfrei? Sonst Käuferanteil inkl. USt eintragen.")
    commission = float(commission)

    grest_eur = price * grest / 100.0
    notary_eur = price * notary / 100.0
    land_register_eur = price * land_register / 100.0
    commission_eur = price * commission / 100.0
    side_costs = grest_eur + notary_eur + land_register_eur + commission_eur
    side_pct = (side_costs / price * 100.0) if price else 0.0

    renovation = float(data.get("renovation_cost") or 0.0)
    total_investment = price + side_costs + renovation

    if data.get("parking_price"):
        data.warn(f"parking_price = {eur(float(data.get('parking_price')))} ist "
                  "gesetzt und wurde NICHT automatisch addiert — prüfen, ob der "
                  "Stellplatz im Kaufpreis enthalten ist.")

    out["costs"] = {
        "price": price, "grest_pct": grest, "grest_eur": grest_eur,
        "notary_pct": notary, "notary_eur": notary_eur,
        "land_register_pct": land_register, "land_register_eur": land_register_eur,
        "commission_pct": commission, "commission_eur": commission_eur,
        "side_costs": side_costs, "side_costs_pct": side_pct,
        "renovation": renovation, "total_investment": total_investment,
        "price_per_m2": price / area if area else None,
        "total_per_m2": total_investment / area if area else None,
    }

    # --- financing --------------------------------------------------------- #
    equity = data.get("equity")
    rate = data.get("interest_rate_pct")
    financing: dict[str, Any] | None = None
    if equity is not None and rate is not None:
        equity = float(equity)
        rate = float(rate)
        repayment = float(use("repayment_pct"))
        fixed_years = int(float(use("fixed_years")))
        loan = total_investment - equity

        if loan <= 0:
            financing = {"loan": 0.0, "no_loan": True,
                         "equity_left": equity - total_investment}
        else:
            if equity < side_costs and not data.get("finance_side_costs"):
                data.warn(
                    f"Eigenkapital ({eur(equity)}) deckt die Kaufnebenkosten "
                    f"({eur(side_costs)}) nicht. Banken finanzieren diese in der "
                    "Regel nicht mit.")
            plan = amortize(loan, rate, repayment, fixed_years * 12)
            ltv = loan / price * 100.0
            if plan["never_amortizes"]:
                data.warn("Bei diesem Zins und dieser Tilgung sinkt die Restschuld "
                          "nie — Tilgungssatz erhöhen.")
            if ltv > 100:
                data.warn(f"Beleihungsauslauf {pct(ltv)} des Kaufpreises: die "
                          "Nebenkosten werden mitfinanziert. Das akzeptieren viele "
                          "Banken nicht, und es verteuert den Zins deutlich.")
            elif ltv > 90:
                data.warn(f"Beleihungsauslauf {pct(ltv)} — hoher Zinsaufschlag zu "
                          "erwarten.")

            remaining = plan["remaining_balance"]
            payoff_months = plan["payoff_months"]
            # A Volltilger repays within the fixed-rate period: there is no
            # follow-up financing at all, so the rate stress test does not apply.
            # A rounding residual well under a percent of the loan counts as repaid.
            fully_repaid = remaining <= max(1000.0, loan * 0.005)
            if payoff_months:
                remaining_months = max(payoff_months - fixed_years * 12, 12)
            else:
                remaining_months = 25 * 12
            stress_rate = float(use("stress_rate_pct"))
            stress_payment = (annuity_payment(remaining, stress_rate, remaining_months)
                              if remaining > 0 else 0.0)

            financing = {
                "fully_repaid_at_fix_end": fully_repaid,
                "equity": equity, "loan": loan, "ltv_pct": ltv,
                "interest_rate_pct": rate, "repayment_pct": repayment,
                "fixed_years": fixed_years,
                "annuity_year": plan["annuity_year"],
                "monthly_payment": plan["monthly_payment"],
                "interest_paid_fixed": plan["interest_paid"],
                "principal_paid_fixed": plan["principal_paid"],
                "remaining_balance": remaining,
                "payoff_months": payoff_months,
                "payoff_years": payoff_months / 12.0 if payoff_months else None,
                "stress_rate_pct": stress_rate,
                "stress_months": remaining_months,
                "stress_monthly_payment": stress_payment,
                "stress_delta": stress_payment - plan["monthly_payment"],
                "no_loan": False,
            }
    else:
        missing = [n for n, v in (("equity", equity), ("interest_rate_pct", rate))
                   if v is None]
        data.notes.append("Finanzierung übersprungen — fehlt: " + ", ".join(missing))
    out["financing"] = financing

    # --- rental ------------------------------------------------------------ #
    rent = data.get("rent_used_month")
    if rent is None:
        rent = data.get("rent_cold_month")
        if rent is not None:
            data.origin["rent_used_month"] = data.origin.get("rent_cold_month", "Objektnotiz")
    rental: dict[str, Any] | None = None
    if rent:
        rent = float(rent)
        annual_rent = rent * 12.0
        vacancy = annual_rent * float(use("vacancy_pct")) / 100.0

        non_app = data.get("hausgeld_non_apportionable_month")
        if non_app is not None:
            operating = float(non_app) * 12.0
            operating_label = ("nicht umlagefähiges Hausgeld "
                               f"({eur(float(non_app))}/Monat)")
        else:
            maintenance = (float(use("maintenance_eur_m2a")) * area) if area else 0.0
            management = float(use("management_eur_month")) * 12.0
            operating = maintenance + management
            operating_label = (
                f"Instandhaltung {eur(maintenance)} + Verwaltung {eur(management)}")
            if area is None:
                data.warn("Ohne Wohnfläche wurde die Instandhaltungspauschale mit "
                          "0 € angesetzt — die Nettorendite ist damit zu hoch.")
            if data.get("hausgeld_month") and non_app is None:
                data.warn("hausgeld_month ist bekannt, der nicht umlagefähige Anteil "
                          "aber nicht. Ersatzweise wurden Pauschalen verwendet — den "
                          "echten Split aus dem Wirtschaftsplan nachtragen.")

        noi = annual_rent - vacancy - operating
        rental = {
            "rent_month": rent, "annual_rent": annual_rent,
            "factor": price / annual_rent,
            "gross_yield_pct": annual_rent / price * 100.0,
            "vacancy": vacancy, "operating": operating,
            "operating_label": operating_label, "noi": noi,
            "net_yield_pct": noi / total_investment * 100.0,
        }
        if financing and not financing.get("no_loan"):
            cashflow = noi - financing["annuity_year"]
            rental["cashflow_year"] = cashflow
            rental["cashflow_month"] = cashflow / 12.0
            rental["roe_pct"] = (cashflow / financing["equity"] * 100.0
                                 if financing["equity"] else None)
            rental["break_even_rent_month"] = (
                (financing["annuity_year"] + operating)
                / (1 - float(use("vacancy_pct")) / 100.0) / 12.0)
            if financing.get("fully_repaid_at_fix_end"):
                rental["stress_cashflow_month"] = rental["cashflow_month"]
            else:
                stress_cashflow = noi - financing["stress_monthly_payment"] * 12.0
                rental["stress_cashflow_month"] = stress_cashflow / 12.0
    out["rental"] = rental

    # --- own use ----------------------------------------------------------- #
    own: dict[str, Any] | None = None
    if (financing and not financing.get("no_loan")
            and data.get("usage_intent") != "kapitalanlage"):
        hausgeld = data.get("hausgeld_month")
        grundsteuer = data.get("grundsteuer_year")
        burden = financing["monthly_payment"]
        parts = [f"Rate {eur(financing['monthly_payment'])}"]
        if hausgeld:
            burden += float(hausgeld)
            parts.append(f"Hausgeld {eur(float(hausgeld))}")
        if grundsteuer:
            burden += float(grundsteuer) / 12.0
            parts.append(f"Grundsteuer {eur(float(grundsteuer) / 12.0)}")
        own = {
            "monthly_burden": burden, "parts": parts,
            "stress_burden": burden - financing["monthly_payment"]
                             + financing["stress_monthly_payment"],
        }
        if not hausgeld:
            data.notes.append("Eigennutzer-Belastung ohne Hausgeld/Nebenkosten "
                              "gerechnet — hausgeld_month ergänzen.")
    out["own_use"] = own

    out["defaults_used"] = sorted(used_defaults)
    out["meta"] = {
        "id": data.get("id"), "title": data.get("title"),
        "scenario": data.get("scenario_name"), "data_asof": data.get("data_asof"),
        "grest_asof": GREST_ASOF,
    }
    out["inputs"] = data.values
    out["notes"] = data.notes
    return out


# --------------------------------------------------------------------------- #
# solving for the maximum price
# --------------------------------------------------------------------------- #
def metric_at(data: Inputs, price: float, name: str) -> float | None:
    """Evaluate one metric at a hypothetical purchase price."""
    result = compute(data.clone_with_price(price))
    if name == "total_investment":
        return result["costs"]["total_investment"]
    if name == "factor":
        return result["rental"]["factor"] if result["rental"] else None
    if name == "cashflow_month":
        rental, fin = result["rental"], result["financing"]
        if not rental or not fin:
            return None
        # Below the equity line there is no loan and therefore no debt service —
        # the cashflow is simply the net operating income. Keeps the curve
        # monotonic across the whole search range.
        if fin.get("no_loan"):
            return rental["noi"] / 12.0
        return rental.get("cashflow_month")
    if name == "monthly_payment":
        fin = result["financing"]
        if not fin:
            return None
        return 0.0 if fin.get("no_loan") else fin["monthly_payment"]
    raise ValueError(name)


def solve_price(data: Inputs, name: str, target: float,
                lo: float = 10_000.0, hi: float = 5_000_000.0) -> float | None:
    """Bisect for the price at which `name` hits `target`. All four metrics are
    monotonic in the price, so a sign change between the bounds is the answer."""
    try:
        f_lo = metric_at(data, lo, name)
        f_hi = metric_at(data, hi, name)
    except SystemExit:
        return None
    if f_lo is None or f_hi is None:
        return None
    f_lo -= target
    f_hi -= target
    if f_lo == 0:
        return lo
    if f_lo * f_hi > 0:
        return None  # the constraint never binds inside the search range
    for _ in range(60):
        mid = (lo + hi) / 2
        f_mid = metric_at(data, mid, name)
        if f_mid is None:
            return None
        f_mid -= target
        if f_lo * f_mid <= 0:
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
        if hi - lo < 5:
            break
    # A maximum is rounded DOWN — the conservative direction for a ceiling.
    return float(int((lo + hi) / 2 / 100) * 100)


def max_price_report(data: Inputs, args: argparse.Namespace) -> str:
    constraints: list[tuple[str, str, float]] = []
    if args.max_total is not None:
        constraints.append(("total_investment", args.max_total,
                            f"Gesamtinvestition ≤ {eur(args.max_total)}"))
    if args.target_factor is not None:
        constraints.append(("factor", args.target_factor,
                            f"Kaufpreisfaktor ≤ {num(args.target_factor)}"))
    if args.target_cashflow is not None:
        constraints.append(("cashflow_month", args.target_cashflow,
                            f"Cashflow ≥ {eur(args.target_cashflow, 2)}/Monat"))
    if args.max_burden is not None:
        constraints.append(("monthly_payment", args.max_burden,
                            f"Rate ≤ {eur(args.max_burden, 2)}/Monat"))
    # the tuples above are (metric, target, label) — reorder for readability
    constraints = [(m, label, target) for m, target, label in constraints]

    if not constraints:
        raise SystemExit(
            "--max-price braucht mindestens eine Grenze:\n"
            "  --max-total EUR         maximale Gesamtinvestition\n"
            "  --target-factor N       höchster akzeptierter Kaufpreisfaktor\n"
            "  --target-cashflow EUR   mindestens dieser Cashflow pro Monat\n"
            "  --max-burden EUR        höchste monatliche Rate")

    lines = ["Maximalgebot — aus den eigenen Zahlen, nicht aus dem Angebotspreis", ""]
    results: list[tuple[str, float | None]] = []
    for metric, label, target in constraints:
        price = solve_price(data, metric, target)
        results.append((label, price))
        if price is None:
            lines.append(f"- {label}: nicht bestimmbar "
                         "(fehlende Eingaben oder Grenze wird nie erreicht)")
        else:
            lines.append(f"- {label}  →  Kaufpreis bis **{eur(price)}**")

    valid = [(label, price) for label, price in results if price is not None]
    lines.append("")
    if valid:
        label, price = min(valid, key=lambda r: r[1])
        lines.append(f"**Bindende Grenze: {label} → Maximalgebot {eur(price)}**")
        if args.price is not None:
            delta = args.price - price
            if delta > 0:
                lines.append(f"Gefordert werden {eur(args.price)} — das sind "
                             f"{eur(delta)} über der eigenen Grenze "
                             f"({pct(delta / price * 100, 1)}).")
            else:
                lines.append(f"Gefordert werden {eur(args.price)} — das liegt "
                             f"{eur(-delta)} unter der eigenen Grenze.")
    else:
        lines.append("Keine Grenze war berechenbar — fehlende Eingaben ergänzen.")
    lines += ["", "Vor dem ersten Gespräch mit Datum in der Objektnotiz festhalten "
              "und danach nur bei geänderten **Fakten** korrigieren."]
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# reporting
# --------------------------------------------------------------------------- #
def render(result: dict[str, Any], markdown: bool) -> str:
    c = result["costs"]
    f = result["financing"]
    r = result["rental"]
    o = result["own_use"]
    meta = result["meta"]
    lines: list[str] = []
    h1 = "## " if markdown else ""
    rule = "" if markdown else "-" * 62

    title = meta.get("title") or meta.get("id") or "Objekt"
    header = f"{title}"
    if meta.get("scenario"):
        header += f" — Szenario: {meta['scenario']}"
    lines += [f"{h1}Wirtschaftlichkeit — {header}", ""]

    basis = {"price_override": "Szenario-Override", "price_agreed": "vereinbarter Preis",
             "price_offered": "abgegebenes Gebot", "price_asking": "Angebotspreis"}
    lines += [f"{h1}Kaufpreis und Nebenkosten", ""]
    lines += [f"- Kaufpreis ({basis[result['price_basis']]}): **{eur(c['price'])}**"]
    if c["grest_pct"]:
        lines += [f"- Grunderwerbsteuer {pct(c['grest_pct'], 1)}: {eur(c['grest_eur'])}"]
    else:
        lines += ["- Grunderwerbsteuer: **unbekannt, mit 0 € gerechnet** — "
                  "bundesland setzen oder --grest angeben"]
    lines += [f"- Notar {pct(c['notary_pct'], 1)}: {eur(c['notary_eur'])}"]
    lines += [f"- Grundbuch {pct(c['land_register_pct'], 1)}: {eur(c['land_register_eur'])}"]
    lines += [f"- Maklerprovision {pct(c['commission_pct'])}: {eur(c['commission_eur'])}"]
    lines += [f"- **Kaufnebenkosten gesamt: {eur(c['side_costs'])}** "
              f"({pct(c['side_costs_pct'], 1)} des Kaufpreises)"]
    if c["renovation"]:
        lines += [f"- Renovierung/Sanierung: {eur(c['renovation'])}"]
    lines += [f"- **Gesamtinvestition: {eur(c['total_investment'])}**"]
    if c["price_per_m2"]:
        lines += [f"- Preis je m²: {eur(c['price_per_m2'])} "
                  f"(inkl. Nebenkosten {eur(c['total_per_m2'])})"]
    lines += [""]

    if f and f.get("no_loan"):
        lines += [f"{h1}Finanzierung", "",
                  f"- Kein Darlehen nötig; Eigenkapital reicht, es bleiben "
                  f"{eur(f['equity_left'])} übrig.", ""]
    elif f:
        lines += [f"{h1}Finanzierung", ""]
        lines += [f"- Eigenkapital: {eur(f['equity'])}"]
        lines += [f"- Darlehen: **{eur(f['loan'])}** "
                  f"(Beleihungsauslauf {pct(f['ltv_pct'], 1)} des Kaufpreises)"]
        lines += [f"- Sollzins {pct(f['interest_rate_pct'])}, anfängliche Tilgung "
                  f"{pct(f['repayment_pct'])}, Zinsbindung {f['fixed_years']} Jahre"]
        lines += [f"- **Monatliche Rate: {eur(f['monthly_payment'], 2)}** "
                  f"(Annuität {eur(f['annuity_year'])}/Jahr)"]
        lines += [f"- In der Zinsbindung: Zinsen {eur(f['interest_paid_fixed'])}, "
                  f"Tilgung {eur(f['principal_paid_fixed'])}"]
        lines += [f"- **Restschuld nach {f['fixed_years']} Jahren: "
                  f"{eur(f['remaining_balance'])}**"]
        if f["payoff_years"]:
            lines += [f"- Vollständig getilgt nach {num(f['payoff_years'])} Jahren "
                      "(ohne Sondertilgung, bei gleichbleibendem Zins)"]
        else:
            lines += ["- Vollständige Tilgung wird bei diesen Konditionen nicht erreicht."]
        if f.get("fully_repaid_at_fix_end"):
            lines += ["- **Keine Anschlussfinanzierung**: das Darlehen ist am Ende "
                      "der Zinsbindung vollständig getilgt. Ein Zinsänderungsrisiko "
                      "besteht nicht."]
        else:
            sign = "+" if f["stress_delta"] >= 0 else "-"
            lines += [f"- Stresstest Anschluss zu {pct(f['stress_rate_pct'], 1)}: Rate "
                      f"**{eur(f['stress_monthly_payment'], 2)}** "
                      f"({sign}{eur(abs(f['stress_delta']), 2)}/Monat), Restschuld "
                      f"getilgt über {f['stress_months'] // 12} Jahre"]
        lines += [""]

    if r:
        lines += [f"{h1}Vermietung", ""]
        lines += [f"- Nettokaltmiete: {eur(r['rent_month'])}/Monat = "
                  f"{eur(r['annual_rent'])}/Jahr"]
        lines += [f"- **Kaufpreisfaktor: {num(r['factor'])}** "
                  f"(Bruttomietrendite {pct(r['gross_yield_pct'])})"]
        lines += [f"- Nicht umlagefähig: {r['operating_label']}; "
                  f"Mietausfallwagnis {eur(r['vacancy'])}"]
        lines += [f"- Reinertrag (NOI): {eur(r['noi'])}/Jahr → "
                  f"**Nettomietrendite {pct(r['net_yield_pct'])}** "
                  "(auf die Gesamtinvestition)"]
        if "cashflow_month" in r:
            lines += [f"- **Cashflow vor Steuern: {eur(r['cashflow_month'], 2)}/Monat** "
                      f"({eur(r['cashflow_year'])}/Jahr)"]
            if r.get("roe_pct") is not None:
                lines += [f"- Eigenkapitalrendite: {pct(r['roe_pct'])}"]
            lines += [f"- Break-even-Miete (Cashflow 0): "
                      f"{eur(r['break_even_rent_month'])}/Monat"]
            if not (f or {}).get("fully_repaid_at_fix_end"):
                lines += [f"- Cashflow im Zins-Stressfall: "
                          f"{eur(r['stress_cashflow_month'], 2)}/Monat"]
        lines += [""]

    if o:
        lines += [f"{h1}Eigennutzung", ""]
        lines += [f"- Monatliche Belastung: **{eur(o['monthly_burden'], 2)}** "
                  f"({' + '.join(o['parts'])})"]
        if not (f or {}).get("fully_repaid_at_fix_end"):
            lines += [f"- Im Zins-Stressfall: {eur(o['stress_burden'], 2)}/Monat"]
        lines += [""]

    if result["warnings"]:
        lines += [f"{h1}Warnungen", ""]
        lines += [f"- ⚠️ {w}" for w in result["warnings"]]
        lines += [""]
    if result["notes"]:
        lines += [f"- ℹ️ {n}" for n in result["notes"]] + [""]

    lines += [f"{h1}Grundlagen", ""]
    if result["defaults_used"]:
        lines += ["- Standardwerte verwendet für: "
                  + ", ".join(result["defaults_used"])]
    lines += [f"- Grunderwerbsteuer-Tabelle: {meta['grest_asof']}"]
    if meta.get("data_asof"):
        lines += [f"- Objektdaten Stand: {meta['data_asof']}"]
    lines += ["- Definitionen: references/kaufnebenkosten-de.md. "
              "Keine Steuer- oder Rechtsberatung."]
    if rule:
        return rule + "\n" + "\n".join(lines) + "\n" + rule
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Kaufneben-, Finanzierungs- und Renditerechnung.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    p.add_argument("note", nargs="?", help="Pfad zur Objektnotiz (type: objekt)")
    p.add_argument("--scenario", help="Pfad zur Finanzierungs-Szenario-Notiz")
    p.add_argument("--profile", help="Pfad zum Vault-Profil (Feldnamen des Nutzers); "
                                     "ohne Angabe wird automatisch gesucht")
    p.add_argument("--price", type=float, help="Kaufpreis (überschreibt die Notiz)")
    p.add_argument("--area", type=float, help="Wohnfläche in m²")
    p.add_argument("--bundesland")
    p.add_argument("--grest", type=float, help="Grunderwerbsteuer in %%")
    p.add_argument("--commission", type=float, help="Maklerprovision Käuferanteil in %%")
    p.add_argument("--equity", type=float, help="Eigenkapital")
    p.add_argument("--rate", type=float, help="Sollzins p. a. in %%")
    p.add_argument("--repayment", type=float, help="anfängliche Tilgung in %%")
    p.add_argument("--fixed-years", type=int)
    p.add_argument("--stress-rate", type=float, help="Anschlusszins für den Stresstest")
    p.add_argument("--renovation", type=float, help="Renovierungskosten")
    p.add_argument("--rent", type=float, help="Nettokaltmiete pro Monat")
    p.add_argument("--hausgeld", type=float, help="Hausgeld pro Monat (gesamt)")
    p.add_argument("--hausgeld-nonapportionable", type=float,
                   help="nicht umlagefähiger Hausgeld-Anteil pro Monat")
    p.add_argument("--max-price", action="store_true",
                   help="rückwärts rechnen: welcher Kaufpreis passt zu den Grenzen?")
    p.add_argument("--max-total", type=float, help="Grenze: Gesamtinvestition")
    p.add_argument("--target-factor", type=float, help="Grenze: Kaufpreisfaktor")
    p.add_argument("--target-cashflow", type=float,
                   help="Grenze: Cashflow pro Monat (0 = kostenneutral)")
    p.add_argument("--max-burden", type=float, help="Grenze: Monatsrate")
    p.add_argument("--json", action="store_true", help="Rohdaten als JSON ausgeben")
    p.add_argument("--markdown", action="store_true",
                   help="Ausgabe mit Überschriften, zum Einfügen in die Notiz")
    args = p.parse_args()

    if not args.note and args.price is None and not args.max_price:
        p.error("Entweder eine Objektnotiz oder --price angeben.")

    data = collect(args)
    if args.max_price:
        print(max_price_report(data, args))
        if args.price is None and args.note is None:
            return 0
        print("\n" + "-" * 62 + "\n")

    result = compute(data)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    else:
        print(render(result, args.markdown))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
