# RC224 — Menu miniature sempre accessibile e Arial predefinito in entrambi gli editor

**Base:** cumulativo RC223. Ultima full CI GitHub indipendentemente verificata completamente verde: **RC219**, run `42197607753` (14 job superati). Le RC220–224 attendono la verifica integrata. Versione invariata **0.1.0-dev**; completamento certificato **85,25%** (43 gate accettati, 17 parziali). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push o tag dell'assistente.

## Menu contestuale delle miniature

- Il menu resta in un portale `document.body`, fuori dal contenitore scrollabile delle miniature. La funzione `thumbnailMenuPosition` limita le coordinate ai bordi della finestra e calcola l'altezza massima **dalla posizione reale del menu**. È stato corretto il conflitto con la vecchia dichiarazione CSS `!important`, che annullava il limite calcolato.
- Restano in vista **Apri**, **Rinomina** e **Duplica**; l'eliminazione conserva la richiesta di conferma. Le altre voci sono raggruppate in **Crea e importa pagine**, **Ordina pagine**, **Esporta e dati**. Nessuna delle azioni precedenti viene rimossa.
- I gruppi nativi `details/summary` sono apribili con tastiera o touch. Quando il menu è troppo alto si scorre **all'interno**, senza tagliare le ultime voci. `Esc` ripristina il focus sul pulsante della miniatura; selezione multipla, scorciatoie e permessi rimangono invariati.

## Verifica Arial nel canvas di pagine e schemi

- Controllati **tutti i 20 tipi di widget** delle palette con i percorsi di inserimento, il tipo di font effettivo nel canvas e nelle viste, comprese domande e risposte, QR, statistiche, contatori e testi.
- **Titolo e footer predefiniti degli schemi** iniziano con Arial. Il titolo eredita Arial tramite lo stile predefinito del master: non si imposta forzatamente Arial come override locale, per non perdere un font personalizzato dall'utente. Il footer nasce con Arial esplicito.
- Anche i preset forme/linee sono Arial. Campi testo dell'editor e degli schemi ereditano il font effettivo della widget. I font già salvati e gli stili scelti intenzionalmente non vengono sostituiti.

## Prove e limiti

- Suite API Node **625/625**, frontend **390/390**, Python mirati **54/54**, preflight RC224 **6/6**, Node dedicati **5/5**.
- Chromium reale sul CSS rilasciato, con DOM rappresentativo, passa a **320×240**, **390×380**, **390×844**, **1440×900**. A tutti i gruppi aperti ogni voce è raggiungibile; testi nuovi negli editor mostrano Arial.
- Test sintattico TypeScript dei file modificati superato. Nuove verifiche preventive e prova Chromium in CI. Resta da eseguire la full CI React compilato/PostgreSQL della RC224 e l'accettazione manuale: non aumenta il completamento certificato di 85,25%.
