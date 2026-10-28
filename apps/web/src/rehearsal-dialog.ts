/**
 * Keyboard lifecycle for the presenter/participant rehearsal overlay.
 * Keep this DOM-only so the same focus behavior is testable in a real offline
 * Chromium browser without bypassing the full application's access checks.
 * Screen-reader and physical-device acceptance remain separate RC gates.
 */
const FOCUSABLE = [
  'a[href]',
  'button:not([disabled])',
  'input:not([disabled])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
].join(',');

function visibleFocusTargets(root: HTMLElement): HTMLElement[] {
  return Array.from(root.querySelectorAll<HTMLElement>(FOCUSABLE)).filter(element =>
    !element.closest('[inert], [aria-hidden="true"], [hidden]') &&
    !element.matches(':disabled') &&
    !element.hidden &&
    element.getClientRects().length > 0 &&
    getComputedStyle(element).visibility !== 'hidden' &&
    getComputedStyle(element).display !== 'none',
  );
}

/** Focus the Close action, constrain Tab/Shift+Tab, and restore the invoker.
 * Caller MUST invoke cleanup when the React overlay unmounts. */
export function activateRehearsalDialog(root: HTMLElement, onClose: () => void): () => void {
  const invoker = document.activeElement instanceof HTMLElement ? document.activeElement : null;
  const priorOverflow = document.body.style.overflow;
  document.body.style.overflow = 'hidden';
  // A modal must isolate the background from pointer, keyboard AND assistive
  // navigation. aria-modal alone does not make underlying DOM inaccessible.
  // Inert only siblings on the path from the overlay to <body>; inerting the
  // application root would also disable the dialog itself.
  const modal = root.closest<HTMLElement>('[role="dialog"][aria-modal="true"]') ?? root;
  // Capture each background element at most once. React can create new
  // siblings (notifications, external portals) while the dialog is mounted;
  // those must not escape the modal's accessible/keyboard isolation.
  const background = new Map<HTMLElement, {inert: boolean; ariaHidden: string | null}>();
  const isolateBackground = (): void => {
    let child: HTMLElement | null = modal;
    while (child && child !== document.body) {
      const parent: HTMLElement | null = child.parentElement;
      if (!parent) break;
      for (const sibling of Array.from(parent.children)) {
        if (sibling === child || !(sibling instanceof HTMLElement) || background.has(sibling)) continue;
        background.set(sibling, {inert: sibling.inert, ariaHidden: sibling.getAttribute('aria-hidden')});
        sibling.inert = true;
        sibling.setAttribute('aria-hidden', 'true');
      }
      child = parent;
    }
  };
  isolateBackground();
  const backgroundObserver = new MutationObserver(() => {
    if (modal.isConnected) isolateBackground();
  });
  backgroundObserver.observe(document.body, {subtree: true, childList: true});
  const closeButton = root.querySelector<HTMLElement>('button[aria-label="Chiudi anteprima"]');
  (closeButton ?? visibleFocusTargets(root)[0] ?? root).focus();

  const onKeyDown = (event: KeyboardEvent): void => {
    // Escape during IME composition cancels input; do not close the preview.
    if (event.isComposing || event.keyCode === 229) return;
    if (event.key === 'Escape') {
      event.preventDefault();
      event.stopPropagation();
      onClose();
      return;
    }
    if (event.key !== 'Tab') return;
    const targets = visibleFocusTargets(root);
    if (!targets.length) {
      event.preventDefault();
      root.focus();
      return;
    }
    const first = targets[0];
    const last = targets[targets.length - 1];
    const active = document.activeElement;
    if (!(active instanceof HTMLElement) || !root.contains(active) || !targets.includes(active)) {
      event.preventDefault();
      (event.shiftKey ? last : first).focus();
    } else if (event.shiftKey && active === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && active === last) {
      event.preventDefault();
      first.focus();
    }
  };
  document.addEventListener('keydown', onKeyDown, true);
  return () => {
    document.removeEventListener('keydown', onKeyDown, true);
    backgroundObserver.disconnect();
    for (const [node, previous] of background) {
      node.inert = previous.inert;
      const ariaHidden = previous.ariaHidden;
      if (ariaHidden === null) node.removeAttribute('aria-hidden');
      else node.setAttribute('aria-hidden', ariaHidden);
    }
    document.body.style.overflow = priorOverflow;
    if (document.fullscreenElement === root) void document.exitFullscreen().catch(() => {});
    if (invoker?.isConnected) invoker.focus();
  };
}
