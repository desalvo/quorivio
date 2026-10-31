# RC83 instradamento degli eventi del menu contestuale

La CI estesa 41232865276 ha confermato `canvas_background_menu_open=True` dopo un vero clic destro Chromium sul widget, malgrado il calcolo di coordinate verificabili da Playwright. Il problema è nella gestione reale dell'interfaccia, non soltanto nel selettore del test.

In RC83 `.widget-canvas` gestisce il `contextmenu` **in cattura**. Il widget viene individuato prima dal target DOM e, se l'evento è stato ritargettizzato, tramite i rettangoli reali dei widget. L'identificativo è verificato nei widget della pagina prima di aprire `Azioni widget`. Un punto libero continua ad aprire il menu dello sfondo. Nessun clic forzato o sintetico, nessuna promozione dei gate.

Copertura: 3 test Node e nuovi controlli Python. Servono nuova CI GitHub e prove reali Chromium/Firefox/WebKit/TypeScript per confermare completamente il comportamento.
