# Quorivio 0.1.0-dev — RC cycle 28

## Risultato della CI dopo il commit del ciclo 27

GitHub Actions [40980312270](https://github.com/desalvo/quorivio/actions/runs/40980312270): **sei job su sette superati**. Qualità (`123818832091`), build container (`123820527899`), OCI AMD64 e ARM64 via QEMU (`123820527902`), manifest Kubernetes (`123820527914`), Firefox/WebKit (`123820527976`), runtime KIND a nodo singolo (`123820528118`) sono **SUCCESS**. Pubblicazione non eseguita.

Il collaudo Podman rootless (`123820527939`) è **FAILURE**: `unknown mount option "uid=1000"` (uscita 125). La costruzione dell'immagine Podman era riuscita; l'avvio dell'applicazione è stato bloccato dal montaggio `--tmpfs` prima che Quorivio potesse essere verificato. Questo non prova un malfunzionamento del servizio né un esito positivo del suo runtime rootless.

## Correzione

La sintassi tmpfs di Docker `uid=1000,gid=1000` è stata sostituita con la sintassi supportata da Podman: `--mount type=tmpfs,destination=/app/assets,tmpfs-size=268435456,tmpfs-mode=0700,U=true`. `U=true` associa la proprietà del tmpfs all'utente non-root configurato nell'immagine; non è abilitato nessun privilegio aggiuntivo e la rete resta isolata. Prima dell'API un contenitore temporaneo con la **stessa immagine** e lo **stesso mount** verifica apertura, scrittura, lettura ed eliminazione di un file a permessi stretti usando l'effettivo UID non-root. Un errore interrompe il test e impedisce di dichiarare il PASS. I segreti effimeri restano nascosti e la pulizia automatica rimane attiva.

Riferimento: [manuale ufficiale Podman](https://docs.podman.io/en/latest/markdown/podman-run.1.html), opzioni tmpfs `U`/`tmpfs-mode`/`tmpfs-size`.

## Gate e verifica

**79,0% invariato** (30 accettati, 17 parziali). Il successo remoto OCI AMD64/ARM64 e KIND è nuova prova valida limitata ai rispettivi ambienti CI, ma il gate D3 resta parziale finché Podman, ingress produttivo, storage RWX multi-nodo e hardware ARM64 nativo non sono validati. La nuova correzione Podman è verificata **solo in locale** tramite controlli di sintassi e contratti; nessun runtime Podman reale è disponibile nell'ambiente di sviluppo. Le prove esterne di accessibilità, GDPR e AGID restano aperte. Non viene dichiarata la RC pronta.

Dopo il commit del package ciclo 28, lanciare la workflow manuale con `rootless_podman_test=true`, `runtime_arch_test=true`, `browser_test=true`, `cross_browser_test=true`, `kubernetes_runtime_test=true`, `publish_image=false`, `publish_latest=false`, `rc_strict=false`. Nessun commit, push o pubblicazione automatici.

**Test locali / local tests:** 1,177 Python (1 skipped), 474 API Node, 65 web Node; build TypeScript non verificata per dipendenze npm locali incomplete; l’ultima CI GitHub del ciclo 27 ha compilato con successo.
