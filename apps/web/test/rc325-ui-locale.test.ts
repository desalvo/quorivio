import assert from 'node:assert/strict';
import test from 'node:test';
import {translateUiText} from '../src/ui-locale.ts';
test('IT/EN UI menu and admin labels have deterministic translations',()=>{
 assert.equal(translateUiText('Impostazioni server','en'),'Server settings');
 assert.equal(translateUiText('  Gestione utenti ','en'),'  User management ');
 assert.equal(translateUiText('Nuova pagina prima','en'),'New page before');
 assert.equal(translateUiText('Spazio disco e allarmi','en'),'Disk space and alerts');
 assert.equal(translateUiText('Rinomina pagine selezionate (R)','en'),'Rename selected pages (R)');
 assert.equal(translateUiText('Nuova pagina prima','it'),'Nuova pagina prima');
});
test('unrecognized strings and user-authored content are never machine-translated',()=>{
 assert.equal(translateUiText('Conference 2026 preliminary notes','en'),'Conference 2026 preliminary notes');
 assert.equal(translateUiText('Sessione privata 123','en'),'Sessione privata 123');
});
