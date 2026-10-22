# Sequenza grafica delle pagine — trascinamento

Nell'elenco delle pagine il presentatore può trascinare una pagina sopra una diversa posizione. Il riordino si salva attraverso `PUT /api/sessions/:id/pages/order`, già dotato di verifica delle autorizzazioni e transazione PostgreSQL. Gli ID delle pagine rimangono invariati: le risposte e la pagina attiva non vengono spostate tra oggetti. Sono disponibili anche i pulsanti Su/Giù, utili da tastiera e su dispositivi che non supportano il drag-and-drop HTML5. Le sessioni chiuse non permettono riordini.

È stato aggiunto un modulo puro di ordinamento, con quattro test per movimenti avanti, indietro, senza modifiche e ID non validi. Questa implementazione **non** costituisce ancora un canvas di posizionamento libero, né include la vista anteprima delle pagine, la creazione attraverso drag-and-drop dalla palette, o il collaudo multi-browser/PostgreSQL.
