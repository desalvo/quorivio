# OAuth federato e sottogate C3-AUTO — 28 ottobre 2026

L'ultimo commit confermato è `a32ef78902a656262d346a0fa622604a4deda405`.

**Punteggio ufficiale 67,0% (+1)**: la Full CI 40638652838 aveva già passato test Node per OIDC PKCE/state, HTTPS, token RS256/JWKS, registrazione provider, durata delle claim, stato OAuth social e scope Facebook. Solo queste evidenze autorizzano `C3-AUTO` (2 punti); il genitore `C3` passa da 6 a 4 punti e rimane parziale. 32 gate, 15 accettati, 17 parziali, peso totale 100.

**Hardening nuovo, NON ancora accettato in CI:** callback rigorosa per provider, POST invece di query di Facebook con secret, token Facebook esclusivamente nell'header Bearer, `appsecret_proof` conservato, niente redirect nei fetch di OAuth/OIDC. Test mock offline aggiunti; l'integrazione reale con Google/GitHub/Facebook richiede credenziali/tenant di prova ed è ancora aperta.

**Prossima azione:** commit cumulativo a cura dell'utente e Full CI `browser_test=true`, `publish_image=false`. Nessun gate indipendente è stato promosso né si è dichiarata pronta la release candidate.
