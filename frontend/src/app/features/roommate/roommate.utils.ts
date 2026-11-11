export const SCHEDULES: Record<string, string> = {
  EARLY: '🌅 Lève-tôt',
  NIGHT: '🌙 Couche-tard',
  FLEXIBLE: '🔄 Flexible',
};

export function initials(name: string): string {
  return (name || '?').split(' ').map(p => p[0]).join('').slice(0, 2).toUpperCase();
}