# Quorivio RC264 — Test PDF senza Pillow nel preflight CI

Il run GitHub Actions [42496843522](https://github.com/desalvo/quorivio/actions/runs/42496843522) del commit RC263 (`8749af933ffbd13de5aaf139b6d38e8884e9f3a5`) ha fallito prima dell'installazione delle dipendenze Python. I test RC261 creavano un PNG tramite un renderer simulato, ma invocavano comunque `_verify_png`, che richiede Pillow. Il runner non aveva `PIL`, generando anche un `UnboundLocalError` nell'espressione `except`.

La RC264 usa nei due test di **staging su filesystem** una verifica deterministica dei byte PNG sintetici, mantenendo il controllo della pubblicazione atomica e dei manifest. Un test negativo dedicato conferma che `_verify_png` fallisce esplicitamente quando Pillow non è disponibile. Nel convertitore di produzione resta obbligatoria la decodifica completa (entrambe `Image.verify()` e `Image.load()`) insieme a tutti i controlli di header, chunk, CRC, dimensione e terminazione. Nessun bypass di sicurezza. I test dopo l'installazione delle dipendenze continuano a esercitare le conversioni PDF/PPTX reali.

Per riprodurre la condizione del runner privo di librerie esterne:

```bash
python3 -S -m unittest -q tools.tests.test_rc264_pillow_independent_ci tools.tests.test_rc261_conversion_mount_and_zlib tools.tests.test_rc263_kube_defaults_and_ci tools.tests.test_rc262_disk_monitor_wizard
```

La CI mantiene le scansioni Trivy HIGH/CRITICAL. Non è necessario ripetere alcuna patch Kubernetes: la sonda PostgreSQL e i manifest sono già sincronizzati. L'operatore deve attendere la full CI e la pubblicazione delle nuove immagini prima di aggiornare l'applicazione.
