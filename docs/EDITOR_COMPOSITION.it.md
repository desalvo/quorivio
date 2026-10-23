# Composizione dell'editor — ciclo accorpato (23/10/2026)

Il canvas 16:9 dispone ora di aggancio facoltativo alla griglia del 5% durante trascinamento/ridimensionamento (disattivato per impostazione predefinita), duplicazione di ciascun widget con un nuovo ID e comandi per spostarlo davanti o dietro agli altri. I controlli sono visibili al passaggio del puntatore o al focus, e sempre sui dispositivi touch. Riutilizzano l'array di widget e il salvataggio esistente, senza migrazioni dello schema.

**Limiti:** l'ordine dei livelli dipende dall'ordine nell'array. La copia mantiene le impostazioni e viene spostata di cinque punti percentuali quando possibile. La griglia non è persistita nel layout e non modifica la precisione degli spostamenti da tastiera. Non è implementata la risoluzione automatica delle collisioni con widget ruotati. Restano da verificare interazioni browser/touch e tecnologie assistive. I test statici non sono collaudi E2E.

La matrice RC complessiva rimane invariata fino a collaudi browser/database. Vedere `RC_GATE_MATRIX.json` e `DEVELOPMENT_STATUS.it.md`.
