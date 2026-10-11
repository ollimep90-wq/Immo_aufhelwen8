/* Fragen des Risiko-Kurzchecks. Auswahl aus dem Excel-Prototyp (Masterarbeit, Jan. 2026),
 * Stand 10.10.2026. Kennzeichnung je Frage:
 *   quelle: "Prototyp <Nr>"            wörtlich übernommen
 *           "Prototyp <Nr>, angepasst" zweiter Satz auf die Antwortskala umformuliert
 *           "neu"                      nicht im Prototyp
 * Unfall nur noch aus k8: k1/k2 (Bandscheibe, Sehen) sind keine Unfälle; Gewichtung mit Jan klären.
 * Gewichte je Thema 0..3. Grundlage sind die Block-Gewichte des Prototyps, zusammengefasst
 * zu Themen. Abweichungen und offene Punkte: Beratung/Prototyp_Analyse.md, Befunde 10–13 und 16.
 * filter: nur zeigen, wenn zutreffend (kinder, tier, eigentum, familie)
 */
(function (root) {
  const THEMEN = {
    arbeitskraft: "Ihre Arbeitskraft",
    familie:      "Ihre Familie, falls Ihnen etwas passiert",
    kinder:       "Absicherung Ihrer Kinder",
    gesundheit:   "Gesundheit und Krankenhaus",
    unfall:       "Unfall",
    haftung:      "Schäden an anderen (Haftpflicht)",
    recht:        "Rechtsstreit",
    hausrat:      "Ihre Einrichtung (Hausrat)",
    gebaeude:     "Ihr Haus (Wohngebäude)",
    tier:         "Ihr Haustier"
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
      text: "Stellen Sie sich vor, Sie haben einen Bandscheibenvorfall und dürfen 12 Monate nicht arbeiten. Wie wirkt sich das auf Ihr Einkommen und Ihren Alltag aus?",
      gewichte: { arbeitskraft: 3, gesundheit: 2 } },
    { id: "k2", block: 1, quelle: "Prototyp 1.2.0.2, angepasst",
      text: "Stellen Sie sich vor, Ihr Sehvermögen verschlechtert sich stark und Ihr Beruf funktioniert so nicht mehr. Wie hart würde Sie das treffen?",
      gewichte: { arbeitskraft: 3, gesundheit: 2 } },
    { id: "k3", block: 2, quelle: "Prototyp 2.3.0.1, angepasst",
      text: "Stellen Sie sich vor, Ihr Körper „zieht die Notbremse“ und Sie können monatelang nicht arbeiten, etwa wegen Erschöpfung. Wie hart würde Sie das finanziell treffen?",
      gewichte: { arbeitskraft: 3, gesundheit: 1 } },
    { id: "k4", block: 3, quelle: "Prototyp 3.0.0.1, angepasst",
      text: "Stellen Sie sich vor, Sie können Ihren heutigen Beruf nicht mehr ausüben und ein anderer Job bringt deutlich weniger ein. Wie hart würde Sie das treffen?",
      gewichte: { arbeitskraft: 3 } },
    { id: "k5", block: 4, quelle: "Prototyp 4.0.0.1, angepasst",
      text: "Stellen Sie sich vor, Ihr Einkommen fällt weg, aber Ihre festen Ausgaben laufen weiter. Wie hart würde Sie das treffen?",
      gewichte: { arbeitskraft: 2, familie: 3 } },
    { id: "k6", block: 4, quelle: "Prototyp 4.0.0.2/4.0.0.3, angepasst", filter: "familie",
      text: "Stellen Sie sich vor, Ihnen passiert etwas und Ihre Familie müsste ohne Ihr Einkommen auskommen, Kredite inklusive. Wie hart würde es Ihre Familie treffen?",
      gewichte: { familie: 3 } },
    { id: "k7", block: 5, quelle: "Prototyp 5.1.1.1, angepasst", filter: "kinder",
      text: "Stellen Sie sich vor, Ihr Kind muss für mehrere Wochen ins Krankenhaus und Sie möchten die ganze Zeit dabei sein. Wie stark würden die Zusatzkosten Sie belasten?",
      gewichte: { kinder: 3, gesundheit: 3 } },
    { id: "k8", block: 5, quelle: "Prototyp 5.1.2.1, angepasst", filter: "kinder",
      text: "Stellen Sie sich vor, Ihr Kind hat nach einem Unfall dauerhafte Folgen und braucht Hilfsmittel oder Umbauten. Wie hart würde Sie das finanziell treffen?",
      gewichte: { kinder: 3, unfall: 3 } },
    { id: "k9", block: 5, quelle: "Prototyp 5.2.0.1, angepasst", filter: "tier",
      text: "Stellen Sie sich vor, Ihr Tier braucht eine OP für 6.000 bis 10.000 €. Wie stark würde Sie das belasten?",
      gewichte: { tier: 3 } },
    { id: "k10", block: 10, quelle: "neu",
      text: "Stellen Sie sich vor, Sie verursachen aus Versehen einen Unfall, bei dem jemand schwer verletzt wird, und sollen Schadenersatz zahlen. Wie hart würde Sie das treffen?",
      gewichte: { haftung: 3 } },
    { id: "k11", block: 6, quelle: "Prototyp 6.0.0.2, angepasst",
      text: "Stellen Sie sich vor, Sie geraten in einen langen Streit mit Vermieter oder Arbeitgeber. Wie stark würden Anwalts- und Gerichtskosten Sie belasten?",
      gewichte: { recht: 3 } },
    { id: "k12", block: 7, quelle: "Prototyp 7.1.0.1, angepasst",
      text: "Stellen Sie sich vor, ein Küchengerät fängt nachts Feuer und der Rauch zerstört Möbel, Kleidung und Elektronik. Wie hart würde es Sie treffen, alles neu zu kaufen?",
      gewichte: { hausrat: 3 } },
    { id: "k13", block: 8, quelle: "Prototyp 8.4.0.1, angepasst", filter: "eigentum",
      text: "Stellen Sie sich vor, Starkregen drückt Wasser in Keller oder Erdgeschoss. Wie hart würden Sanierung, Trocknung und Ersatz Sie treffen?",
      gewichte: { gebaeude: 3 } },
    { id: "k14", block: 8, quelle: "Prototyp 8.2.0.1, angepasst", filter: "eigentum",
      text: "Stellen Sie sich vor, ein Brand macht Ihr Haus monatelang unbewohnbar und Sie zahlen Miete und Kredit gleichzeitig. Wie hart würde Sie das treffen?",
      gewichte: { gebaeude: 3, familie: 2 } }
    /* Prototyp 9.0.0.4 („Ich habe schon erlebt, dass mein Körper anders reagiert hat …“)
     * bewusst NICHT übernommen: fragt nach eigener Gesundheitserfahrung (Art. 9 DSGVO).
     * Entscheidung laut Bedarfsanalyse: keine Gesundheitsdaten im Vorab-Check. */
  ];

  const api = { THEMEN, SKALA, SKALA_ZUSTIMMUNG, FRAGEN };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.Fragen = api;
})(this);
