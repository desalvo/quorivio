# Assets and reports — presenter procedures (0.1.0-dev)

1. Sign in with an approved presenter account and select an authorized session.
2. Under **Session assets**, choose a PNG, JPEG, GIF, WebP, PDF, MP4 or WebM file. The default per-file limit is 100 MB. The backend checks size, declared media type and binary signature; it may reject the file.
3. Use **Refresh assets** to display the inventory, open an authenticated link or delete an unneeded attachment. Do not share this link with participants: it is restricted to authenticated presenters. The UI is not yet a complete visual media editor.
4. Under **Session data**, select **Aggregate JSON report and audit**. The report includes session metadata, activities, valid/invalidated vote totals, invalidation audit and file hashes. It excludes media bytes and participant identities; it is not a complete backup.
5. As platform administrator, adjust **Upload limit (MB)** in **Administration**. For Kubernetes deployments regenerate and apply Ingress manifests using the wizard. Set coherent ingress, backend and storage quotas.

**Not yet available:** full instance/database+media backup/restore, streaming ingestion, malware scanning, shared S3 storage, complete drag-and-drop media editing, guaranteed orphan-file cleanup. This is not yet production validated for arbitrary untrusted content.
