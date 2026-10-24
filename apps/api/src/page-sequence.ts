/** Require an exact, bounded permutation of the pages belonging to this session. */
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
export function validPageOrder(requested: unknown, existing: readonly string[]): requested is string[] {
  if (!Array.isArray(requested) || requested.length !== existing.length || requested.length > 500) return false;
  const allowed = new Set(existing);
  if (allowed.size !== existing.length) return false;
  const seen = new Set<string>();
  for (const id of requested) {
    if (typeof id !== 'string' || !UUID.test(id) || !allowed.has(id) || seen.has(id)) return false;
    seen.add(id);
  }
  return true;
}
