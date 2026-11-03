# RC141 — Modifica del voto, risultati adattivi e coerenza grafica delle quattro viste

Base: cumulativo RC140 con correzione TypeScript, successivo al commit RC140 (`2612d704ac9ea886a3770e7eab9148a3f2186876`). La correzione della compilazione RC140 è inclusa. Nessun commit/push/rilascio da parte dell'assistente.

## Interventi

- **Gradimento**: un solo voto per `(attività, partecipante, widget)`; mentre la pagina è corrente e aperta, selezionare un nuovo punteggio aggiorna lo stesso record. Ripetere lo stesso voto non incrementa i conteggi. L'interfaccia evidenzia la scelta e impedisce invii concorrenti. La prova affiancata rispecchia la modifica del voto; l'API verifica lo stato della sessione e della pagina.
- **Risultati**: nuova opzione **Solo risultati**, non selezionata per default, per eliminare titolo e intestazione della domanda lasciando visibili soltanto i risultati aggregati. Le statistiche non sono pubblicate nei widget dei partecipanti.
- **Risposte e nuvola**: una risposta e il conteggio in parentesi quadre formano una singola unità visiva. Con l'adattamento automatico attivo, niente scrollbar interna: i risultati sono misurati e ridotti proporzionalmente all'arrivo di nuovi valori. Con adattamento manualmente disabilitato resta possibile scegliere lo scorrimento e il ritaglio. Per elenchi molto lunghi l'ingrandimento del widget migliora la leggibilità.
- **Reazioni**: otto emoji identiche con componente condiviso nelle viste editor, presentatore, prova affiancata e partecipante. Il titolo nascosto resta nascosto in tutte le viste, incluso l'editor.
- **Risposte multiple**: nell'editor checkbox e radio native disabilitate con le stesse misure, allineamento e tipografia delle anteprime. L'interazione rimane naturalmente diversa nelle diverse viste.

## Verifiche e limiti

Suite Node e test di regressione RC141; Chromium CSS a 1440/390 px su quattro superfici sintetiche; parsing TypeScript e inventario integrale. La build Vite completa, il collaudo autentico su Kubernetes e l'accettazione RC esterna restano da confermare. Il test sintetico non certifica l'identità pixel-per-pixel di tutte le pagine effettive. Nessuna modifica a Secret/PVC/deploy/autorizzazioni.

Completamento certificato invariato **85,25% (43 gate accettati / 17 parziali)**. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
