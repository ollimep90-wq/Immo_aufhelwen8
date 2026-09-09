# Immo Aufhelwen — Obsidian-Skill für den Immobilienkauf

Dieses Repository enthält einen Claude-Code-Skill, der einen Obsidian-Vault als
Wissensbasis für einen Immobilienkauf führt: alle Daten zu Kaufobjekten belegt
erfassen, offene Fragen sichtbar halten und daraus Entscheidungen ableiten.

## Was der Skill tut

- **Erfassen** — Objekt-, Besichtigungs-, Dokument-, Kontakt- und
  Entscheidungsnotizen nach einem festen Frontmatter-Schema, damit alles
  auswertbar bleibt.
- **Belegen** — jede Zahl bekommt Quelle und Stand. Was nicht belegt ist, wird
  nicht ins Frontmatter geschrieben, sondern zur offenen Frage.
- **Rechnen** — Kaufnebenkosten, Annuität, Restschuld nach Zinsbindung,
  Zins-Stresstest, Kaufpreisfaktor, Brutto-/Nettorendite, Cashflow und
  Eigenkapitalrendite. Deterministisch per Skript, nicht im Kopf.
- **Entscheiden** — Suchprofil mit K.O.-Kriterien und Gewichtung, Gebotsobergrenze
  aus den eigenen Zahlen statt aus dem Angebotspreis, dokumentierte
  Entscheidungsnotizen.

## Installation

Der Skill liegt unter `.claude/skills/obsidian/` und wird von Claude Code
automatisch geladen, wenn dieses Repository das Arbeitsverzeichnis ist.

Soll er in **jedem** Projekt verfügbar sein:

```bash
mkdir -p ~/.claude/skills
cp -r .claude/skills/obsidian ~/.claude/skills/
```

### Bestehender Vault

Der Skill passt sich an einen vorhandenen Vault an, statt ihn umzubauen. Einmalig:

```bash
# nur lesen, nichts ändern — Vorschlag ansehen
python3 .claude/skills/obsidian/scripts/vault_profile.py "$OBSIDIAN_VAULT"

# nach Prüfung als Profil speichern
python3 .claude/skills/obsidian/scripts/vault_profile.py "$OBSIDIAN_VAULT" \
  --write ~/.config/claude-obsidian/vault-profile.md
```

Das Profil hält fest, in welchem Ordner die Objektnotizen liegen, woran sie
erkennbar sind und wie die Frontmatter-Felder dort tatsächlich heißen
(`kaufpreis` statt `price_asking` usw.). `vault_scan.py` und `property_calc.py`
lesen es über `--profile`. Bestehende Notizen und Ordner werden nicht umbenannt
oder verschoben; `init_vault.py` verweigert den Dienst in einem Vault, der
bereits eigene Notizen hat.

### Vault-Pfad hinterlegen

Vault-Pfad einmalig hinterlegen (sonst fragt der Skill danach):

```bash
export OBSIDIAN_VAULT="$HOME/Dokumente/Immobilien"
# oder dauerhaft:
mkdir -p ~/.config/claude-obsidian
echo "$HOME/Dokumente/Immobilien" > ~/.config/claude-obsidian/vault-path
```

**Leeren** Vault einrichten:

```bash
python3 .claude/skills/obsidian/scripts/init_vault.py "$OBSIDIAN_VAULT"
```

Danach in Obsidian das Community-Plugin **Dataview** installieren (für die
Dashboards) und `90-Meta/Suchprofil.md` ausfüllen — am besten vor dem ersten
Objekt.

## Aufbau

```
.claude/skills/obsidian/
├── SKILL.md                     Ablauf und Regeln
├── references/
│   ├── vault-structure.md       Ordnerstruktur
│   ├── frontmatter.md           Feldschema aller Notiztypen
│   ├── obsidian-syntax.md       Wikilinks, Properties, Callouts
│   ├── dataview.md              fertige Abfragen
│   ├── kaufnebenkosten-de.md    Kosten, Kennzahlen, Steuern (DE)
│   ├── due-diligence.md         Unterlagen, Prüfpunkte, Warnsignale
│   ├── decision-framework.md    Suchprofil, Scoring, Entscheidungsnotizen
│   └── rest-api.md              Local REST API (optionale Stufe 2)
├── assets/templates/            10 Notizvorlagen
└── scripts/
    ├── frontmatter.py           Frontmatter und Vault-Profil lesen
    ├── vault_profile.py         bestehenden Vault analysieren, Feldzuordnung
    ├── migrate_vault.py         lose Notizen in ein sauberes Vault überführen
    ├── vault_scan.py            alle Objekte als Tabelle/JSON
    ├── property_calc.py         Kauf-, Finanzierungs- und Renditerechnung
    └── init_vault.py            Grundgerüst — nur für leere Vaults
```

Die Skripte brauchen nur Python 3.9+ und die Standardbibliothek; PyYAML wird
genutzt, wenn vorhanden.

## Maximalgebot statt Angebotspreis

```bash
python3 .claude/skills/obsidian/scripts/property_calc.py --max-price \
  --price 800000 --bundesland Nordrhein-Westfalen --commission 3.57 \
  --rent 3200 --area 210 --equity 200000 --rate 3.7 \
  --target-cashflow 0 --target-factor 22
```

Löst für jede gesetzte Grenze den Kaufpreis, bei dem sie greift, und nennt die
strengste. Ergebnis wird abgerundet.

## Schnelltest ohne Vault

```bash
python3 .claude/skills/obsidian/scripts/property_calc.py \
  --price 485000 --area 92 --bundesland Bayern --commission 3.57 \
  --equity 120000 --rate 3.6 --rent 1250
```

## Zugriff auf den Vault

Standard ist der direkte Dateizugriff auf den Vault-Ordner — Obsidian übernimmt
externe Änderungen automatisch. Die Anbindung an ein laufendes Obsidian über das
Plugin *Local REST API* ist in `references/rest-api.md` beschrieben und als
zweite Stufe vorgesehen.

## Hinweis

Der Skill fasst deutsche Regelungen zu Kaufnebenkosten, Grunderwerbsteuer und
Abschreibung zusammen, um die richtigen Fragen stellen zu können. Steuersätze und
Gesetze ändern sich; die Angaben sind mit Stand markiert und vor Verwendung zu
prüfen. Das ist keine Rechts- oder Steuerberatung — verbindlich sind Notar,
Steuerberater, Bausachverständiger und Energieberater.
