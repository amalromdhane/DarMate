import { AbstractControl, ValidationErrors } from '@angular/forms';


export const adultValidator = (c: AbstractControl): ValidationErrors | null => {
  if (!c.value) return null;
  const d = new Date(c.value), t = new Date();
  if (isNaN(d.getTime()) || d > t) return { future: true };
  let age = t.getFullYear() - d.getFullYear();
  if (t.getMonth() < d.getMonth() || (t.getMonth() === d.getMonth() && t.getDate() < d.getDate())) age--;
  return age >= 18 && age <= 120 ? null : { minor: true };
};


export const maxBirthDate = (): string => {
  const d = new Date();
  d.setFullYear(d.getFullYear() - 18);
  return d.toISOString().slice(0, 10);
};