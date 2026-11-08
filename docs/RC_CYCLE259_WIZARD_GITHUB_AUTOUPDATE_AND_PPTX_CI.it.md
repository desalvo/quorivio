# RC259 — Wizard Kubernetes auto-aggiornante e riconciliazione PPTX CI

**Origine:** full CI RC258 [42480854048](https://github.com/desalvo/quorivio/actions/runs/42480854048), commit `64744e1bb3aec55ba7de4482ed9a05640b4a5376`. Il job "Kubernetes wizard and worker integration tests" ha eseguito 2.325 test Python; l'unico fallimento era `test_pptx_text_style_is_applied_on_presenter_projection`, che pretendeva il vecchio frammento di sorgente `const textStyle={fontFamily:widget.style?.fontFamily`. Il renderer usa correttamente `explicitWidgetFontFamily(...)` per mantenere le scelte personalizzate e ignorare `undefined`/valori non validi. Aggiornato il test senza toccare il renderer, più gate anticipato RC259.

## File singolo, versione e aggiornamento automatico

`tools/k8s_wizard.py` è un file standalone: libreria standard Python 3, `kubectl` necessario solo per operazioni di cluster, nessuna dipendenza dalle directory del repository. Versione incorporata `0.1.0-dev-rc259`.

Al **primo avvio operativo** di ogni comando, il wizard consulta esclusivamente `https://raw.githubusercontent.com/desalvo/quorivio/main/tools/k8s_wizard.py` su HTTPS. Scarica un file limitato a 2 MiB, ne verifica UTF-8, sintassi Python, versione in forma `0.1.0-dev-rcN`, presenza degli helper standalone e provenienza GitHub. Non installa versioni precedenti; quando la versione è nuova o il contenuto della versione corrente è cambiato, scrive nella **stessa directory** tramite file temporaneo con permessi preservati e sostituzione atomica, poi riavvia l'interprete con gli **stessi argomenti**, evitando aggiornamenti ricorsivi. Nessuna operazione `kubectl` viene eseguita prima del controllo.

```bash
# Solo versione installata (nessuna rete, nessun kubectl)
python3 ./k8s_wizard.py --version

# Verifica/aggiorna da GitHub e termina, senza generare manifest né chiamare kubectl
python3 ./k8s_wizard.py --self-update-only

# Normale: aggiornamento+riavvio automatici prima dell'operazione sul cluster
python3 ./k8s_wizard.py --inspect-cluster \
  --set namespace=quorivio --set name=quorivio --output ./cluster-inventory

# Modalità offline esplicita (NON garantisce la versione GitHub più recente)
python3 ./k8s_wizard.py --no-self-update --version
python3 ./k8s_wizard.py --no-self-update --upgrade-converter \
  --set namespace=quorivio --set name=quorivio \
  --converter-image desalvo/quorivio-converter:latest --output ./converter-plan
```

**Sicurezza / disponibilità:** se GitHub non è raggiungibile o l'aggiornamento non può essere completato, un comando operativo termina **prima** di toccare il cluster (fail-closed); il tecnico può optare esplicitamente per `--no-self-update`, dopo aver verificato localmente la versione. `--version` e `--help` funzionano sempre offline. Una copia **non committata** più recente del file non viene sovrascritta da `main` ancora alla RC precedente. Una sorgente GitHub senza marcatore di versione viene ignorata per evitare downgrade. Non sono disponibili aggiornamenti silenziosi da URL arbitrari o da fork: la fonte è codificata nel wizard. Le modifiche sul cluster restano esplicite e protette dalla verifica del Deployment/contesto.

**Collaudi:** test senza accesso a GitHub: update atomico, versioni, no downgrade, URL ridiretto non fidato, errore di rete, file malformati, file symlink e read-only, riavvio con argv invariato, esecuzione con sola copia del file. Verifiche Node su Arial/Georgia; build e suite del progetto. Inventario RC258 storico conservato, nuovo inventario RC259. La full CI RC259 va eseguita dopo il commit. **85,25%** (43 gate accettati, 17 parziali), `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
