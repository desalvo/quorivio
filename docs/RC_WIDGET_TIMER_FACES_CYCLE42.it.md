# Timer artistici e precedenza riempimenti — ciclo 42

Il presentatore sceglie il **Quadrante timer** dalle proprietà di un widget Timer o Quiz a tempo. Opzioni: **Clessidra**, **Orologio circolare**, **Digitale**. La scelta persiste nel JSON della pagina, viene validata dall’API e si riflette in editor, anteprima affiancata e pagina pubblica; un vecchio widget senza impostazione mantiene la clessidra. La progressione è calcolata dal tempo reale e non è un’animazione fittizia. Lo stato urgente usa un colore di avviso vicino alla scadenza.

La trasparenza, il riempimento solido, il gradiente e l’immagine scelti manualmente prevalgono sui temi artistici. `fillOpacity=0` non deve lasciar vedere un gradiente decorativo. Lo stato `Riduci movimento` disabilita i movimenti ornamentali ma non altera cifre, precisione del conto o leggibilità.

**Collaudo dopo il commit:** verificare in Chromium, Firefox e WebKit i tre quadranti nei quattro contesti, la modifica del timer in fase di anteprima, `fillOpacity=0`, selezione del gradiente e un'immagine privata di riempimento. Accertare inoltre che le scelte restino dopo salvataggio e riapertura e che non vengano pubblicati asset non autorizzati. Nessuna certificazione formale RC aggiunta al solo test locale.
