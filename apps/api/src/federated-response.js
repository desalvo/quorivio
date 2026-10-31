/** Fail-closed bounded JSON decoder for untrusted identity-provider responses.
 * Checking response.text().length after downloading the full body is NOT a
 * memory limit. Consume a streaming response with a hard byte budget instead.
 * Tokens and provider claims must never be echoed in errors or logs.
 */
/** @param {Response} response @param {number} maxBytes @returns {Promise<Record<string, unknown>>} */
export async function boundedFederatedJson(response, maxBytes) {
 if (!Number.isSafeInteger(maxBytes) || maxBytes < 1 || maxBytes > 262144)
  throw new RangeError('invalid federated response limit');
 if (!response.body) throw new Error('federated_empty_response');
 const declared = response.headers.get('content-length');
 if (declared !== null && /^\d+$/.test(declared) && Number(declared) > maxBytes)
  throw new Error('federated_response_too_large');
 const reader = response.body.getReader();
 const chunks = [];
 let length = 0;
 let fullyRead = false;
 try {
  while (true) {
   const {done, value} = await reader.read();
   if (done) { fullyRead = true; break; }
   length += value.byteLength;
   if (length > maxBytes) throw new Error('federated_response_too_large');
   chunks.push(value);
  }
 } finally {
  if (!fullyRead) await reader.cancel().catch(() => {});
  reader.releaseLock();
 }
 let decoded;
 try {
  const bytes = new Uint8Array(length);
  let offset = 0;
  for (const chunk of chunks) {bytes.set(chunk, offset); offset += chunk.byteLength;}
  decoded = JSON.parse(new TextDecoder('utf-8', {fatal: true}).decode(bytes));
 } catch {throw new Error('federated_invalid_json');}
 if (!decoded || typeof decoded !== 'object' || Array.isArray(decoded))
  throw new Error('federated_invalid_json');
 return decoded;
}
