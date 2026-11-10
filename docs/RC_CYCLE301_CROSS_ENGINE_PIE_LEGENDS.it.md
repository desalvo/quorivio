# RC301 — Legende risultati leggibili su più browser

**Baseline:** commit di pubblicazione main `7c1046a16203`, con sorgenti RC300 già verificati dalla full CI `f27525c9b09e`.

## Correzione visibile

Le etichette lunghe delle opzioni nei grafici a torta smartphone vanno finalmente **a capo su più righe** invece di essere tagliate con i puntini. Le percentuali mantengono una riga leggibile distinta. Si applica ai risultati condivisi nell'editor, nell'anteprima presentatore e nelle varianti pubbliche che usano lo stesso componente.

## Validazione aggiunta

- Usa il vero modulo TypeScript di produzione `resultPieLayout` con dodici opzioni, quote molto piccole e una configurazione con percentuali disabilitate.
- Verifica i CSS realmente distribuiti con Chromium, Firefox e WebKit nativi su desktop, smartphone 390/360px e layout Smartphone nell'editor desktop.
- Misura a browser l'andata a capo, font percentuali almeno 14px, overflow assente, rapporto SVG, legenda accessibile e soppressione delle callout SVG troppo piccole; nessuna percentuale deve apparire se disabilitata.
- Chromium obbligatorio su PR; Firefox e WebKit nativi nella full CI. Screenshot degli errori esclusivamente con dati sintetici pubblici.
- Controllo sintattico e contrattuale prima di npm.

## Limiti RC

Questa prova automatica non equivale a voti reali su Firefox/WebKit, NVDA/VoiceOver/TalkBack, Safari fisico o convalida esterna AGID. Rimane **85,25% (43 accepted, 17 partial)**; la RC stretta richiede ancora l'approvazione indipendente dei gate A4/B3 e degli altri collaudi esterni. Nessun tag.

**Messaggio merge suggerito:** `fix: wrap long pie legends and validate Firefox WebKit accessibility`
