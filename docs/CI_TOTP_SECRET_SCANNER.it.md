# Segnalazione GitGuardian: vettori TOTP di test

Nel test `apps/api/test/totp.test.ts` era presente in forma letterale la codifica Base32 di un vettore pubblico di RFC 6238. Non è una chiave di un account Quorivio o di un sistema di produzione, ma uno scanner può interpretare la stringa come un segreto.

La stringa letterale è stata rimossa e il vettore pubblico viene costruito a runtime a partire dalla sequenza di byte descritta nell'RFC; gli altri test usano byte casuali e non inseriscono password o chiavi fisse nel repository. Il valore atteso RFC rimane verificato.

**Azioni nell'interfaccia GitGuardian:** classificare la segnalazione originale come *test data / false positive*, se l'interfaccia lo consente, dopo aver verificato che il rilevamento riguardi unicamente la chiave pubblica di test. Se il valore fosse stato usato fuori dai test o come chiave di un servizio reale, ruotare immediatamente tale segreto. Rimuovere la stringa dall'HEAD non la elimina dalla cronologia Git; riscrivere la cronologia richiede una decisione esplicita e coordinata.

**CI:** ripetere il controllo del secret scanner sul nuovo commit. Verifiche locali: 82 test Node e 40 Python superati; i risultati della nuova GitHub Actions non sono ancora disponibili.
