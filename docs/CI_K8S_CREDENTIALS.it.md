# Accettazione credenziali Kubernetes in CI

Due nuove installazioni generate dal wizard devono utilizzare segreti diversi; il confronto integrale tra directory indipendenti è scorretto e può esporre password nei log. Eseguire `python3 tools/check_k8s_generation.py` per verificare la stabilità dopo rigenerazione nella stessa directory, l’unicità delle credenziali tra installazioni nuove e i permessi riservati. Il controllo usa directory temporanee e non esegue deployment. Rimane da confermare la nuova CI GitHub.
