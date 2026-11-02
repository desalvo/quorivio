# RC138 — Sovrapposizione widget, fedeltà dei risultati e wizard Kubernetes

Baseline: **RC137**, CI GitHub `41475936282` verde, commit `4b33e67ec2ee22973b557ab3ec6759bad356dedc`.

- Tutti i widget possono sovrapporsi con mouse, touch, tastiera, copia/incolla e otto maniglie. Rimangono i confini del canvas e Undo/Redo.
- I risultati live aggregati tornano direttamente nella widget Risultati della pagina del presentatore; nessuna risposta digitata viene riprodotta nelle caselle del presentatore e la widget risultati non compare sulla vista partecipante.
- Risultati offre una casella di controllo per disattivare la riscalatura automatica. Il ridimensionamento manuale la disattiva e il contenuto rimane alla dimensione impostata, scorrendo entro il riquadro senza badge fuorviante.
- I pulsanti invio delle anteprime mantengono dimensione e posizione proprie, senza allargarsi come il campo di risposta.
- Risposte testuali brevi aggregate per frequenza, soltanto etichette anonime da 1–2 parole (massimo 48 caratteri); i testi lunghi aumentano soltanto il totale.
- Il wizard ora offre `--inspect-cluster`: legge in sola lettura Deployment, ConfigMap, PVC, Ingress, ClamAV e PostgreSQL ed esporta `quorivio-cluster-discovery.json` **senza valori dei Secret**. Non applica modifiche, non rigenera credenziali e non è ancora una modalità di riconciliazione/applicazione automatica. Per installazioni esistenti proteggere Secret e PVC e valutare manualmente il diff prima di applicare manifest completi.

Esempio: `python3 tools/k8s_wizard.py --inspect-cluster --output ./quorivio-inspection --set namespace=quorivio --set name=quorivio`.

**Certificato 85,25%** (43 accettati / 17 parziali); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. RC138 non committata, CI GitHub ed evidenze indipendenti ancora da verificare. Nessun commit/push/release dell'assistente.
