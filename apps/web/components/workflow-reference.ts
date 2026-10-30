/** Navigation convenience only. The backend remains the identity authority. */
export type WorkflowPageProps = { searchParams: Promise<Record<string, string | string[] | undefined>> };

export function workflowReference(value: unknown): string {
  if (typeof value !== 'string' || !value || value.length > 2048 || /[\s\\\x00-\x1f\x7f]/.test(value)) return '';
  // Check the unnormalized path: URL() must not hide dot segments or encoded paths.
  const raw = /^https:\/\/([^/?#]+)([^?#]*)/i.exec(value);
  if (!raw || !/^(?:(?:www\.|m\.)?(?:copart|iaai)\.com)(?::443)?$/i.test(raw[1]) || raw[2].includes('%')) return '';
  try {
    const parsed = new URL(value);
    if (parsed.protocol !== 'https:' || parsed.username || parsed.password || parsed.port) return '';
    const copart = ['copart.com', 'www.copart.com', 'm.copart.com'].includes(parsed.hostname);
    const iaai = ['iaai.com', 'www.iaai.com', 'm.iaai.com'].includes(parsed.hostname);
    const path = copart ? /^\/(?:[a-z]{2}\/)?lot\/[0-9]+(?:\/[A-Za-z0-9_-]+)?\/?$/i
      : /^\/(?:[a-z]{2}(?:-[a-z]{2})?\/)?VehicleDetail\/[A-Za-z0-9-]+(?:~[A-Za-z]{2})?\/?$/i;
    if ((!copart && !iaai) || !path.test(raw[2])) return '';
    return `https://${parsed.hostname}${raw[2].replace(/\/$/, '')}`;
  } catch { return ''; }
}

export function workflowHref(path: string, reference: string): string {
  const safe = workflowReference(reference);
  return safe ? `${path}?${new URLSearchParams({ reference: safe })}` : path;
}
