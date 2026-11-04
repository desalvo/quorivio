# RC173 — Presentazione reale: fedeltà partecipanti, accessibilità e gradimento

**Baseline:** RC172 cumulativa ottenuta da RC171. **Versione:** 0.1.0-dev (invariata); licenza EUPL-1.2 invariata. Nessun commit, push, tag o rilascio automatico.

## Correzioni applicate

1. **Doppio sfondo eliminato.** La pagina HTML del partecipante non disegna più lo sfondo della slide; lo sfondo è applicato al solo canvas interno 16:9. In precedenza lo stesso asset appariva anche sul contenitore esterno, dando l'impressione di una pagina sotto alla pagina.
2. **Tre modalità indipendenti.** I controlli partecipante «Diapositiva 16:9», «Layout smartphone» e «Lettura accessibile» hanno stati separati. La prima non passa automaticamente alle coordinate smartphone alle larghezze ridotte. La seconda usa gli override della pagina mobile. La terza dispone linearmente gli elementi leggibili, senza importare lo sfondo grafico o le forme decorative della slide.
3. **Resa 16:9 mobile.** La fedeltà geometrica (coordinate percentuali, rotazione, proporzioni) prevale sulle vecchie regole di impilamento mobile; i minimi touch 44px rimangono nella modalità accessibile, mentre non distorcono il canvas 16:9 ridotto. Il testo può risultare piccolo in questa modalità: usare «Lettura accessibile» per una lettura e interazione ingrandita.
4. **Editor gradimento.** Un solo componente genera commento e valori 0–9. Il titolo viene renderizzato dal corpo del widget fuori dalla modalità modifica; mentre si modifica il testo, il titolo è gestito dal campo editabile, non da due sovrapposizioni.
5. **Risultati privati senza riempimenti orfani.** I risultati e il conteggio partecipanti sono esclusi *prima* della disposizione; gli eventuali rettangoli senza didascalia che coincidono per posizione e dimensione con un widget risultati vengono esclusi solo nella vista partecipante. Forme nominate o lontane restano visibili. Rimosso anche un fallback legacy che stampava statistiche sotto la pagina quando il progetto non aveva widget.
6. Conservate la risoluzione degli schemi e le personalizzazioni smartphone introdotte in RC171/RC172; il presenter e il salvataggio del layout non vengono mutati dalla policy pubblica.

## Controlli

- Node frontend: **302/302 PASS**, inclusi 6 nuovi test RC173. Due vecchi test che imponevano la specifica stringa JSX del precedente titolo duplicato sono stati aggiornati al nuovo contratto.
- TypeScript/Vite: non compilato in questo ambiente perché mancano dipendenze npm e definizioni `vite/client`. Il messaggio del compilatore è TS2688; non va interpretato come errore del sorgente.
- Test Chromium su React autenticato con le cinque riproduzioni reali, CI completa, PostgreSQL, Firefox, Safari/WebKit, smartphone e lettori schermo: **ancora da eseguire e validare**.
- Completamento RC **85,25%** (43 gate accettati, 17 parziali), invariato perché nessun gate è promosso sulla sola evidenza locale. RC non ancora certificata.

Impostazioni release consigliate: `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Non pubblicare né effettuare commit prima di confermare la CI e le prove visive.
