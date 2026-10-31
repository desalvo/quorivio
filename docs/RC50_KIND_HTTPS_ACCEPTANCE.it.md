# Collaudo HTTPS reale in KIND (ciclo 50)

## Obiettivo

Passare da test di sola attestazione TLS nei manifest a richieste HTTPS reali attraverso ingress **NGINX** e **HAProxy Technologies** con un client che verifica i certificati. Il test è separato dalla precedente accettazione HTTP, usa soltanto un cluster KIND effimero e non esegue pubblicazioni.

## Avvio GitHub Actions

Nell'esecuzione manuale del workflow selezionare `kubernetes_tls_test=true`, `publish_image=false`, `rc_strict=false`. Gli altri toggle possono rimanere falsi: il workflow avvia due job indipendenti con la matrice `nginx, haproxytech`, dopo il gate standard. Non usare gli hash dei test precedenti come prova di questo nuovo ambito.

## Cosa viene effettivamente verificato

1. Generazione di un certificato RSA/SHA-256 con SAN DNS per `quorivio-multi.example.invalid`, validità di un giorno e Secret Kubernetes TLS nello stesso namespace dell'applicazione.
2. Il wizard configura lo schema pubblico `https://`, l'Ingress richiama esattamente il Secret TLS e il client `node:https` usa `rejectUnauthorized=true`, una CA esplicitamente ancorata e SNI coerente.
3. Su entrambi i pod Quorivio: lettura HTTPS, rifiuto virtual host sconosciuto, rifiuto del certificato autofirmato quando il trust non è configurato.
4. Dopo l'eliminazione controllata di un pod, l'altro resta raggiungibile via HTTPS e la nuova coppia di repliche è pronta.

La chiave privata esiste soltanto nella directory temporanea del runner e nel Secret del cluster KIND effimero; l'output non deve mai stampare Secret, valori degli header o contenuti delle risposte.

## Limiti

La radice di fiducia è di test, non pubblica; entrambi i worker sono container sullo stesso host Docker. Lo storage condiviso è ancora un bind temporaneo, non CSI/NFS/CephFS. Nessun attestato di HA/TLS pubblico, host fisici indipendenti o sicurezza enterprise. La percentuale ufficiale RC resta 81,25 fino ai job verdi e a una riconciliazione senza doppio conteggio.
