# RC176 — Ordine di lettura accessibile e tre modalità partecipante realmente distinte

**Data:** 04/11/2026. **Base cumulativa:** RC175. Versione `0.1.0-dev`, licenza EUPL-1.2.

## Problemi chiusi nel codice

1. Nella sessione reale, il footer veniva spostato visivamente in fondo tramite `order` CSS; l'ordine DOM/Tab e quello dei lettori di schermo rimanevano invece l'ordine sorgente, potenzialmente errato. L'helper `participantReadingWidgets()` crea un documento effettivamente ordinato: posizione dall'alto verso il basso, da sinistra a destra per righe uguali, footer sempre ultimo. Le forme/linee decorative e gli elementi privati del presentatore non hanno nodi nel documento accessibile. Non modifica l'ordine né i livelli grafici della diapositiva 16:9 o dello smartphone personalizzato.
2. Il test Chromium/PostgreSQL della sessione reale richiedeva erroneamente `.stage-phone` dopo aver selezionato «Lettura accessibile». Il test ora seleziona **tre pulsanti diversi** e verifica rispettivamente `.stage-fidelity`, `.stage-phone` e `.stage-reading`, compreso il background bianco, il footer nel DOM, i controlli da almeno 44px in lettura e la corrispondenza delle coordinate normalizzate tra desktop e smartphone 16:9. Verifica inoltre che i widget riservati al presentatore non producano spazi nel layout smartphone.
3. Una prova indipendente Chromium esegue l'helper TypeScript autentico e applica il `style.css` distribuito ai suoi widget: verifiche su larghezze 1280, 390 e 320 px. Il test è inserito nel job CI esistente e un preflight Python con mutazioni negative impedisce di confondere nuovamente le modalità.

## Risultati locali verificati

- Web Node: **313/313**, API Node: **588/588**.
- Python selezionati: **25/25**; test nuovo RC176 **5/5** e test Node nuovo RC176 **4/4**.
- Chromium CSS/DOM: RC174 geometria, RC175 media, RC176 ordine lettura, tre larghezze: **PASS**.
- Parsing/transpile TypeScript delle tre unità aggiornate: nessun errore sintattico.

## Limiti e gate

L'esecuzione reale **React + PostgreSQL autenticata**, la build Vite e la CI GitHub sull'attuale sorgente **non sono state eseguite**. `npm ci --offline` non trova i tarball necessari; il registry DNS non è raggiungibile in questo ambiente. Le prove Chromium locali non costituiscono certificazione WCAG/AGID o dispositivo fisico. Il gate A4 resta **parziale** fino a prova indipendente e approvazione assistive-tech.

**Completamento globale certificato invariato: 85,25% (43 accettati, 17 parziali).** Non alterare la matrice per assegnare crediti non comprovati. `rc_strict=false`, `publish_image=false`, `publish_latest=false`; nessun commit, push, tag, deploy o pubblicazione automatica.
