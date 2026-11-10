import { Pipe, PipeTransform } from '@angular/core';
const L: Record<string, string> = { PENDING: 'En attente', ACCEPTED: 'Acceptée', REJECTED: 'Refusée', CANCELLED: 'Annulée', CONFIRMED: 'Confirmée', ACTIVE: 'Actif', SUSPENDED: 'Suspendu', BANNED: 'Banni', PUBLISHED: 'Publiée',AVAILABLE: 'Disponible', DRAFT: 'Brouillon', RENTED: 'Louée', PROPOSED: 'Proposée', VERIFIED: 'Vérifié', OPEN: 'Ouvert', RESOLVED: 'Résolu' };
@Pipe({ name: 'statusLabel', standalone: true })
export class StatusLabelPipe implements PipeTransform { transform(v: string | undefined): string { return v ? L[v] ?? v : ''; } }
