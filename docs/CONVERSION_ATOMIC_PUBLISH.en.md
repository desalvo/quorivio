# Conversion safety / Sicurezza conversione

The worker now rejects ambiguous PDF/PPTX inputs and writes the completed manifest inside temporary staging before publishing the rendered page directory. Confirm this behavior using a real converter container and PDF/PPTX uploads. Existing orphaned job locks must be recovered manually only with all workers stopped.
