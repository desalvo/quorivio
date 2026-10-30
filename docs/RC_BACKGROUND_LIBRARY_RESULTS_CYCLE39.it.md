# RC ciclo 39 — libreria sfondi e visualizzazione risultati

Gli sfondi vengono caricati dal presentatore e conservati nella sua libreria personale. Presentatori che collaborano almeno in una sessione possono scegliere le immagini altrui anche nelle proprie presentazioni: quando ne usano una, il server crea una copia autonoma nella loro libreria prima di applicarla alla sessione. Il background della pagina resta un asset indipendente, così duplicazioni ed esportazioni della sessione non dipendono più dalla disponibilità dell'account sorgente.

Il menu contestuale del canvas e la finestra delle impostazioni usano entrambi la libreria. Il colore CSS bianco predefinito non sovrascrive l'immagine di sfondo. La visualizzazione dei risultati è impostata nella domanda/quiz/sondaggio collegato e non nel widget Risultati; la nuvola è animata con rispetto per le preferenze di accessibilità.

**Limiti di verifica:** test locali, non collaudo PostgreSQL 18 + Chromium + multiutente. Lo score RC resta 80,75%. Da validare in CI e manualmente dopo il commit. Nessuna dichiarazione di conformità GDPR/AGID finale.
