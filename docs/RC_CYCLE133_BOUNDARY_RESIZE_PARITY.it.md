# RC133 — Ridimensionamento con arresto ai bordi nell'editor

2 novembre 2026. **Baseline committata verde:** RC130, GitHub Actions `41420021082`, commit `d3e89fb2f27cee0cb6aa87d57a61927cef2c874d`. Gli interventi RC131–RC133 sono cumulativi e **non ancora committati**.

## Macroarea funzionale chiusa

- **Otto maniglie per mouse/touch:** `resizeWidgetToCollisionLimit` calcola il limite della prima collisione partendo dalle dimensioni iniziali del gesto. Non rimanda il widget alla misura originaria e non attraversa widget sottili con trascinamenti veloci. Ridimensionando dai lati superiore e sinistro rimangono ancorati i bordi opposti.
- **Tastiera (Shift+frecce):** usa il medesimo controllo di collisione, mentre spostamento da tastiera (RC132) e rotazione mantengono le rispettive regole. Forme e linee possono continuare a sovrapporsi intenzionalmente.
- **Annullamento della maniglia risposta:** `pointercancel` ripristina l’altezza precedente senza salvare una modifica parziale né aggiungere una voce Undo.
- **Storico:** un gesto produce una sola voce Undo/Redo; input non finiti, rettangoli fuori canvas e situazioni inizialmente sovrapposte sono rifiutati. Le coordinate vengono ricontrollate dopo l'arrotondamento a quattro decimali.
- **CI:** sette nuovi test Node e cinque controlli Python prima di npm; aggiornato il controllo storico delle frecce per riflettere la nuova semantica, senza disabilitare alcun gate di sicurezza o pubblicazione.

## Prove e limiti

Test frontend Node locali: 209/209 PASS. Test Python mirati (tastiera, RC132, RC133): 10/10 PASS. Compilazione TypeScript/Vite completa e verifica grafica/in browser da confermare con GitHub CI. **Completamento certificato 85,25%** (43 gate accettati, 17 parziali), senza promozione arbitraria. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Le verifiche esterne di accessibilità, sicurezza/GDPR e infrastruttura restano aperte. Nessun commit, push o release eseguito dall'assistente.
