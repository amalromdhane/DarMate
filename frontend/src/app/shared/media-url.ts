import { Img } from '../models';
export function mediaUrl(i: Img): string | null {
  const raw = i.url ?? i.path;
  if (!raw) return null;
  if (raw.startsWith('http') || raw.startsWith('/media/')) return raw;
  return '/media/' + raw.replace(/^\/+/, '');
}
export function mediaUrls(images?: Img[]): string[] {
  return (images ?? []).map(mediaUrl).filter((u): u is string => !!u);
}