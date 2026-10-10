/* Fragen des Risiko-Kurzchecks. Auswahl aus dem Excel-Prototyp (Masterarbeit, Jan. 2026),
 * Stand 10.10.2026. Kennzeichnung je Frage:
 *   quelle: "Prototyp <Nr>"            wörtlich übernommen
 *           "Prototyp <Nr>, angepasst" zweiter Satz auf die Antwortskala umformuliert
 *           "neu"                      nicht im Prototyp
 * Gewichte je Thema 0..3. Grundlage sind die Block-Gewichte des Prototyps, zusammengefasst
 * zu Themen. Abweichungen und offene Punkte: Beratung/Prototyp_Analyse.md, Befunde 10–13 und 16.
 * filter: nur zeigen, wenn zutreffend (kinder, tier, eigentum, familie)
 */
(function (root) {
  const THEMEN = {
    arbeitskraft: "Deine Arbeitskraft",
    familie:      "Deine Familie, falls dir etwas passiert",
    kinder:       "Absicherung deiner Kinder",
    gesundheit:   "Gesundheit und Krankenhaus",
    unfall:       "Unfall",
    haftung:      "Schäden an anderen (Haftpflicht)",
    recht:        "Rechtsstreit",
    hausrat:      "Deine Einrichtung (Hausrat)",
    gebaeude:     "Dein Haus (Wohngebäude)",
    tier:         "Dein Haustier"
  };

  const SKALA = [
    { wert: 4, text: "Existenzbedrohend" },
    { wert: 3, text: "Stark belastend" },
    { wert: 2, text: "Spürbar" },
    { wert: 1, text: "Kaum" },
    { wert: 0, text: "Gar nicht" },
    { wert: null, text: "Trifft nicht zu" }
  ];
  const SKALA_ZUSTIMMUNG = [
    { wert: 4, text: "Stimme voll zu" },
    { wert: 3, text: "Eher ja" },
    { wert: 2, text: "Teils, teils" },
    { wert: 1, text: "Eher nein" },
    { wert: 0, text: "Stimme nicht zu" },
    { wert: null, text: "Trifft nicht zu" }
  ];

  const FRAGEN = [
    { id: "k1", block: 1, quelle: "Prototyp 1.1.0.1",
      text: "Stell dir vor, du hast einen Bandscheibenvorfall und darfst 12 Monate nicht arbeiten. Wie wirkt sich das auf dein Einkommen und deinen Alltag aus?",
      gewichte: { arbeitskraft: 3, unfall: 2, gesundheit: 2 } },
    { id: "k2", block: 1, quelle: "Prototyp 1.2.0.2, angepasst",
      text: "Stell dir vor, dein Sehvermögen verschlechtert sich stark und dein Beruf funktioniert so nicht mehr. Wie hart würde dich das treffen?",
      gewichte: { arbeitskraft: 3, unfall: 2, gesundheit: 2 } },
    { id: "k3", block: 2, quelle: "Prototyp 2.3.0.1, angepasst",
      text: "Stell dir vor, dein Körper „zieht die Notbremse“ und du kannst monatelang nicht arbeiten, etwa wegen Erschöpfung. Wie hart würde dich das finanziell treffen?",
      gewichte: { arbeitskraft: 3, gesundheit: 1 } },
    { id: "k4", block: 3, quelle: "Prototyp 3.0.0.1, angepasst",
      text: "Stell dir vor, du kannst deinen heutigen Beruf nicht mehr ausüben und ein anderer Job bringt deutlich weniger ein. Wie hart würde dich das treffen?",
      gewichte: { arbeitskraft: 3 } },
    { id: "k5", block: 4, quelle: "Prototyp 4.0.0.1, angepasst",
      text: "Stell dir vor, dein Einkommen fällt weg, aber die Fixkosten laufen weiter. Wie hart würde dich das treffen?",
      gewichte: { arbeitskraft: 2, familie: 3 } },
    { id: "k6", block: 4, quelle: "Prototyp 4.0.0.2/4.0.0.3, angepasst", filter: "familie",
      text: "Stell dir vor, dir passiert etwas und deine Familie müsste ohne dein Einkommen auskommen, Kredite inklusive. Wie hart würde es sie treffen?",
      gewichte: { familie: 3 } },
    { id: "k7", block: 5, quelle: "Prototyp 5.1.1.1, angepasst", filter: "kinder",
      text: "Stell dir vor, dein Kind muss für mehrere Wochen ins Krankenhaus und du willst bessere Unterbringung und Betreuung. Wie stark würden dich die Zusatzkosten belasten?",
      gewichte: { kinder: 3, gesundheit: 3 } },
    { id: "k8", block: 5, quelle: "Prototyp 5.1.2.1, angepasst", filter: "kinder",
      text: "Stell dir vor, dein Kind verliert durch einen Unfall dauerhaft die Beweglichkeit eines Arms oder Beins und braucht Hilfsmittel und Umbauten. Wie hart würde euch das finanziell treffen?",
      gewichte: { kinder: 3, unfall: 3 } },
    { id: "k9", block: 5, quelle: "Prototyp 5.2.0.1, angepasst", filter: "tier",
      text: "Stell dir vor, dein Tier braucht eine OP für 6.000 bis 10.000 €. Wie stark würde dich das belasten?",
      gewichte: { tier: 3 } },
    { id: "k10", block: 10, quelle: "neu",
      text: "Stell dir vor, du verursachst aus Versehen einen Unfall, bei dem jemand schwer verletzt wird, und sollst Schadenersatz zahlen. Wie hart würde dich das treffen?",
      gewichte: { haftung: 3 } },
    { id: "k11", block: 6, quelle: "Prototyp 6.0.0.2, angepasst",
      text: "Stell dir vor, du gerätst in einen langen Streit mit Vermieter oder Arbeitgeber. Wie stark würden dich Anwalts- und Gerichtskosten belasten?",
      gewichte: { recht: 3 } },
    { id: "k12", block: 7, quelle: "Prototyp 7.1.0.1, angepasst",
      text: "Stell dir vor, ein Küchengerät fängt nachts Feuer und der Rauch zerstört Möbel, Kleidung und Elektronik. Wie hart würde es dich treffen, alles neu zu kaufen?",
      gewichte: { hausrat: 3 } },
    { id: "k13", block: 8, quelle: "Prototyp 8.4.0.1, angepasst", filter: "eigentum",
      text: "Stell dir vor, Starkregen drückt Wasser in Keller oder Erdgeschoss. Wie hart würden dich Sanierung, Trocknung und Ersatz treffen?",
      gewichte: { gebaeude: 3 } },
    { id: "k14", block: 8, quelle: "Prototyp 8.2.0.1, angepasst", filter: "eigentum",
      text: "Stell dir vor, ein Brand macht dein Haus monatelang unbewohnbar und du zahlst Miete und Kredit gleichzeitig. Wie hart würde dich das treffen?",
      gewichte: { gebaeude: 3, familie: 2 } }
    /* Prototyp 9.0.0.4 („Ich habe schon erlebt, dass mein Körper anders reagiert hat …“)
     * bewusst NICHT übernommen: fragt nach eigener Gesundheitserfahrung (Art. 9 DSGVO).
     * Entscheidung laut Bedarfsanalyse: keine Gesundheitsdaten im Vorab-Check. */
  ];

  const api = { THEMEN, SKALA, SKALA_ZUSTIMMUNG, FRAGEN };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.Fragen = api;
})(this);
