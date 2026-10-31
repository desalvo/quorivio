# RC77 — Campagna RC automatica sempre non pubblicante

La CI standard `41209516202` è verde sul commit `e4f24a9fb8a36ef0b96ddb20b755a5a2f9335343`. Le campagne estese `41210085593` e `41210395340` si sono fermate al controllo iniziale: il runner esponeva `RC_CAMPAIGN_PUBLISH=true` anche se l'utente dichiara di aver selezionato soltanto `rc_acceptance_suite`. La API pubblica della run non espone gli input originali, perciò non è possibile attribuire con certezza l'origine di true. Il riepilogo 1/11 è una conseguenza del blocco iniziale.

Quando `rc_acceptance_suite=true`, l'ambiente del test usa sempre `RC_CAMPAIGN_PUBLISH=false` e `RC_CAMPAIGN_STRICT=false`. Le condizioni dei job pubblicazione e strict escludono esplicitamente la campagna; lo script per risolvere i tag Docker blocca separatamente qualsiasi tentativo di pubblicare durante una campagna. Test di sicurezza eseguiti all'inizio della CI controllano tutte e tre le protezioni.

La pubblicazione manuale vera resta disponibile solo fuori dalla campagna e con consenso separato. La RC strict resta bloccata da verifiche esterne. Dopo il commit di RC77, avviare una **nuova** workflow_dispatch con `rc_acceptance_suite=true` (non Re-run jobs su una run precedente). Non dichiarare verde la campagna finché non è stata eseguita e controllata.
