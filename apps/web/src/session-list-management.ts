/** Owner-only list actions use the authenticated /sessions access_role, never a guessed owner. */
export type ListedSessionAction = Pick<{
  id: string;
  status: string;
  access_role: 'owner' | 'collaborator';
}, 'id' | 'status' | 'access_role'>;

export function canResetListedSession(session: ListedSessionAction): boolean {
  return session.access_role === 'owner' &&
    (session.status === 'active' || session.status === 'paused' || session.status === 'closed');
}

export function canDeleteListedSession(session: ListedSessionAction): boolean {
  return session.access_role === 'owner';
}
