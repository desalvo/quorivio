# Quorivio RC118 — Verifica della percentuale localizzata

La run `41332909058` è fallita in quattro controlli storici della documentazione: le intestazioni attive italiane RC117 indicavano `85.25%` invece di `85,25%`. Il test Chromium non è stato avviato, quindi il bug dell'Undo va ancora certificato.

RC118 corregge le intestazioni italiane e inglesi, conserva integralmente gli inventari storici e rafforza il controllo anticipato: la percentuale è calcolata dal registro dei gate e verificata nel formato richiesto dalla lingua. I test negativi bloccano percentuali mancanti, obsolete o con separatore sbagliato. Nessuna modifica alla logica applicativa o ai gate certificati. Serve la full CI GitHub.
