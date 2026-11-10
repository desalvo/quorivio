# RC299 — Voti reali, grafico live e riservatezza

**Base:** RC298 integrata in main a 9df7c1ce48e1; [full CI 42874569129](https://github.com/desalvo/quorivio/actions/runs/42874569129) post-merge verde.

## Implementazione sul branch RC299

- Tooltip delle fette SVG con testo reale della risposta, conteggio effettivo e singolare/plurale corretto; la percentuale compare esclusivamente quando abilitata. Dimensione torta e geometria del tasto R invariati.
- Test Chromium/PostgreSQL obbligatorio su frontend compilato, sessione effimera autenticata e **tre browser partecipanti indipendenti** (desktop/smartphone), accesso tramite la pagina pubblica e voto reale dai controlli React: alfa, beta, alfa.
- La verifica PostgreSQL deve contare tre risposte e lo **schermo live del presentatore** deve visualizzare 2/1/0, etichette originali, percentuali 67% / 33% e conteggi coerenti. Non si usano le statistiche simulate delle anteprime.
- La pagina del partecipante non può mostrare le widget di risultati riservate; richiesta non autorizzata alle statistiche private = HTTP 401. Errori JavaScript bloccanti.
- Preflight prima di npm e test reale browser dopo PostgreSQL/Chromium, prima di acquisire screenshot e creare manuali.

## Limiti della certificazione

La CI del nuovo branch deve risultare verde prima di ogni merge. Punteggio ufficiale invariato **85,25% (43 accepted, 17 partial)** in attesa dell'accettazione A4/B3 su dispositivi e ausili fisici. Non autorizzati tag, pubblicazione o RC strict. Ancora necessari NVDA, VoiceOver, TalkBack, tastiera e prova indipendente di utenti reali. Versione 0.1.0-dev.

**Titolo merge suggerito:** `test: verify real participant votes in live PostgreSQL result pies`
