# Quorivio 0.1.0-dev — accessibilità della prova e avanzamento RC verificato

Data: 28 ottobre 2026. Ultimo commit dichiarato dall'utente: `a32ef78902a656262d346a0fa622604a4deda405`. Il precedente cumulativo relativo alle statistiche delle domande sul tema **non è ancora stato committato**: il prossimo messaggio di commit deve comprenderlo.

## Modifiche

- Tutte le anteprime (presentatore, partecipante, affiancata) condividono `activateRehearsalDialog`: alla loro apertura il focus va al pulsante Chiudi; Tab e Maiusc+Tab mantengono il focus sui controlli visibili e attivi; Esc chiude l'anteprima e restituisce il focus al pulsante di provenienza.
- Blocca lo scorrimento della pagina sottostante e ripristina l'impostazione precedente alla chiusura. Rimuove gli handler quando l'anteprima viene smontata; evita la doppia gestione di Esc.
- Nuova prova Chromium reale, senza accesso di rete, che trasforma il modulo TypeScript effettivo ed esegue i controlli su viewport 1440×900 e 390×844. Inclusa nella Full CI opt-in dopo il controllo delle proporzioni affiancate.

## Verifiche locali

Build completa backend/frontend TypeScript+Vite **PASS**, **468/468 test Node API**, **50/50 frontend**, **921/921 Python**. Verifiche Chromium isolate di focus, anteprima affiancata/reazioni, geometria editor/anteprima/partecipanti e WYSIWYG tutte **PASS**. L'ambiente blocca il browser dell'app su localhost (`ERR_BLOCKED_BY_ADMINISTRATOR`): i test offline non sostituiscono i flussi autenticati PostgreSQL né il collaudo fisico o con screen reader. La nuova Full CI GitHub è ancora da eseguire.

## Progresso con evidenze verificabili: 56,0% → 60,0%

Scomposti quattro gate tecnici con prove GitHub **già eseguite**, senza approvare automaticamente le richieste residue:

- `B1-WS`, peso 2: CI 40638652838, due repliche WebSocket/PostgreSQL e privacy; restano prove di carico prolungato e recupero.
- `C2-TLS`, peso 2: CI 40638652838, MFA email PostgreSQL e SMTP TLS locale; restano provider SMTP reali e deliverability.
- `D2-DR`, peso 2: CI 40638652838, backup e ripristino PostgreSQL 18 con integrità; restano obiettivi RPO/RTO in produzione, cifratura e rotazione chiavi.
- `D3-IMAGE`, peso 2: multiarchitettura Buildx CI 40595463258, build e scansioni CI 40638652838; restano ARM64 nativo, Podman rootless e cluster Kubernetes HA.

I quattro gate genitori restano **parziali** con peso ridotto di 2 ciascuno. Formula invariata: accettato 100% del peso, parziale 50%. Risultato: **25 gate, 8 accettati e 17 parziali; 60,0%**. Il nuovo test della finestra non riceve punti RC prima della conferma GitHub. **La RC non è pronta** e il gate rigoroso resta bloccato.

## Da fare

Dopo il commit dell'utente, eseguire CI standard e CI estesa manuale con `browser_test=true`, `publish_image=false`. Provare navigazione da tastiera nell'app reale; accettazione visiva indipendente dei widget e statistiche collegate; Firefox/WebKit, hardware fisico e NVDA/VoiceOver/TalkBack; SMTP esterni, disaster recovery operativo, ARM64/Podman/Kubernetes, verifiche GDPR/AGID. Nessun commit, push, tag, rilascio o Docker push effettuati.
