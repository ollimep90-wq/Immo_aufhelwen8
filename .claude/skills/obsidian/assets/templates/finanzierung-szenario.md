---
type: finanzierung-szenario
object:
name: Basis
created:

equity:
price_override:
renovation_cost: 0

interest_rate_pct:
repayment_pct: 2.0
fixed_years: 10
stress_rate_pct: 6.0
finance_side_costs: false

grunderwerbsteuer_pct:
notary_pct: 1.5
land_register_pct: 0.5
commission_pct:

rent_used_month:
vacancy_pct: 3.0
maintenance_eur_m2a: 12.0
management_eur_month: 30.0
hausgeld_non_apportionable_month:
---

# Szenario %% Name %% — [[ ]]

> [!note] Hier stehen ausschließlich **Annahmen**. Fakten gehören in die Objektnotiz.

## Begründung der Annahmen

| Annahme | Wert | Woher |
|---|---|---|
| Sollzins |  | %% Bankangebot vom …, Vergleichsportal, Schätzung %% |
| Eigenkapital |  | %% nach Abzug der Liquiditätsreserve %% |
| Renovierungskosten |  | %% Angebot, Erfahrungswert, grobe Schätzung %% |
| Miete |  | %% Mietvertrag, Mietspiegel, Vergleichsangebote %% |

## Ergebnis

%% Ausgabe von:
python3 property_calc.py <objektnotiz> --scenario <diese notiz> --markdown
Mit Datum. Bei geänderten Annahmen neu rechnen, alte Rechnung datiert stehen lassen. %%

## Bewertung

%% Trägt das? Was passiert im Stressfall? Wo ist die Schmerzgrenze? %%
