import assert from 'node:assert/strict';
import {test} from 'node:test';
import {backgroundUploadError} from '../src/background-upload-error.ts';
test('background rejection reports actionable status without leaking server HTML',()=>{
 assert.match(backgroundUploadError(413,'invalid_upload_size'),/File troppo grande/);
 assert.match(backgroundUploadError(415,'unsupported_background_media'),/JPG/);
 assert.match(backgroundUploadError(409,'session_closed'),/sessione è chiusa/);
 assert.match(backgroundUploadError(403,''),/permessi/);
 assert.match(backgroundUploadError(500,'<script>unsafe</script>'),/HTTP 500/);
 assert.doesNotMatch(backgroundUploadError(400,'<script>unsafe</script>'),/script|unsafe/);
});

test('Kubernetes upload failures provide distinct safe actions',()=>{
 assert.match(backgroundUploadError(503,'antivirus_unavailable'),/ClamAV|Kubernetes/);
 assert.match(backgroundUploadError(507,'background_storage_unavailable'),/Volume|PVC/);
 assert.match(backgroundUploadError(503,'background_database_unavailable'),/PostgreSQL/);
 assert.match(backgroundUploadError(500,'background_processing_failed'),/background_upload_failed/);
 assert.match(backgroundUploadError(415,'invalid_media_signature'),/formato/);
 assert.doesNotMatch(backgroundUploadError(503,'private_name'),/private_name/);
});
