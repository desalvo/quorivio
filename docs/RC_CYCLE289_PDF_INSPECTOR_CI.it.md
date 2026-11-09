# RC289 — Dipendenze dei controlli PDF in CI

## Evidenze

La [full CI 42666096697](https://github.com/desalvo/quorivio/actions/runs/42666096697) è fallita nel gate RC287 `test_six_published_pdfs_are_current_and_illustrated` con `ModuleNotFoundError: No module named 'fitz'`. I test anticipati RC287 e RC286 controllano i sei manuali PDF con PyMuPDF, ma l'installazione della libreria si trovava solamente nel passaggio successivo dedicato alle schermate reali.

## Correzione

Installazione di `pymupdf==1.26.7` e verifica dell'import prima dei gate documentali RC287/RC286. I controlli su immagini incorporate e acquisizioni reali restano obbligatori. Un nuovo test segnala l'assenza della dipendenza, lo spostamento sotto i gate, la perdita del vincolo di versione o la rimozione di una verifica PDF. Nessuna modifica al runtime dell'applicazione.

## Convalida

Eseguire `python3 -m unittest tools.tests.test_rc289_pdf_ci_order tools.tests.test_rc287_result_formatting tools.tests.test_rc286_authoring_manuals -q` e poi la full CI GitHub. Il superamento globale richiede una nuova esecuzione CI.
