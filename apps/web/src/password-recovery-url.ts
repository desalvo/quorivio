/**
 * Remove a one-time password recovery bearer token from the visible address
 * before users can navigate away, copy the URL, or trigger link previews.
 * The token is kept only in React component state; it is never persisted.
 */
export function consumeRecoveryTokenFromUrl(
  location: Pick<Location, 'href'>,
  history: Pick<History, 'replaceState' | 'state'>,
): string {
  const url = new URL(location.href);
  // The fragment format prevents exposure in access logs and on the initial
  // document request. Legacy query-format reset links must still work for
  // tokens emailed before this change; remove BOTH forms if present.
  const fragment = url.hash.startsWith('#reset_token=')
    ? new URLSearchParams(url.hash.slice(1)) : null;
  const hasFragmentToken = fragment?.has('reset_token') ?? false;
  if (!hasFragmentToken && !url.searchParams.has('reset_token')) return '';
  const token = (hasFragmentToken ? fragment?.get('reset_token') : url.searchParams.get('reset_token')) || '';
  url.searchParams.delete('reset_token');
  if (hasFragmentToken && fragment) {
    fragment.delete('reset_token');
    const remaining = fragment.toString();
    url.hash = remaining ? `#${remaining}` : '';
  }
  // Preserve unrelated query parameters and fragments without forwarding the
  // credential to history, storage, analytics, or external navigation.
  history.replaceState(history.state, '', url.protocol === 'about:'
    ? url.href : `${url.pathname}${url.search}${url.hash}`);
  return token;
}
