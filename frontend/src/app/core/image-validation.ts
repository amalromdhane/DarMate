export const IMAGE_RULES = {
  maxFiles: 5,
  maxBytes: 5 * 1024 * 1024,
  extensions: ['jpg', 'jpeg', 'png', 'webp'],
  minWidth: 640, minHeight: 480,
  maxWidth: 6000, maxHeight: 6000,
};

async function hasImageSignature(file: File): Promise<boolean> {
  const b = new Uint8Array(await file.slice(0, 12).arrayBuffer());
  const jpeg = b[0] === 0xFF && b[1] === 0xD8 && b[2] === 0xFF;
  const png  = b[0] === 0x89 && b[1] === 0x50 && b[2] === 0x4E && b[3] === 0x47;
  const webp = b[0] === 0x52 && b[1] === 0x49 && b[2] === 0x46 && b[3] === 0x46 &&
               b[8] === 0x57 && b[9] === 0x45 && b[10] === 0x42 && b[11] === 0x50;
  return jpeg || png || webp;
}

function dimensions(file: File): Promise<{ w: number; h: number }> {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => { resolve({ w: img.naturalWidth, h: img.naturalHeight }); URL.revokeObjectURL(url); };
    img.onerror = () => { reject(); URL.revokeObjectURL(url); };
    img.src = url;
  });
}

export async function validateImages(picked: File[], currentCount: number)
  : Promise<{ accepted: File[]; errors: string[] }> {
  const R = IMAGE_RULES;
  const accepted: File[] = [];
  const errors: string[] = [];
  const room = R.maxFiles - currentCount;

  if (room <= 0) return { accepted, errors: [`Maximum ${R.maxFiles} images par annonce.`] };

  for (const f of picked) {
    if (accepted.length >= room) {
      errors.push(`Maximum ${R.maxFiles} images : les fichiers en trop ont été ignorés.`);
      break;
    }
    const ext = f.name.split('.').pop()?.toLowerCase() ?? '';
    if (!R.extensions.includes(ext)) { errors.push(`${f.name} : seules les images JPG, PNG et WebP sont acceptées.`); continue; }
    if (f.size > R.maxBytes)         { errors.push(`${f.name} : plus de ${R.maxBytes / 1024 / 1024} Mo.`); continue; }
    if (!(await hasImageSignature(f))) { errors.push(`${f.name} : ce fichier n'est pas une vraie image.`); continue; }
    try {
      const { w, h } = await dimensions(f);
      if (w < R.minWidth || h < R.minHeight) { errors.push(`${f.name} : trop petite (${w}×${h}, minimum ${R.minWidth}×${R.minHeight}).`); continue; }
      if (w > R.maxWidth || h > R.maxHeight) { errors.push(`${f.name} : trop grande (${w}×${h}, maximum ${R.maxWidth}×${R.maxHeight}).`); continue; }
    } catch {
      errors.push(`${f.name} : image illisible.`); continue;
    }
    accepted.push(f);
  }
  return { accepted, errors };
}