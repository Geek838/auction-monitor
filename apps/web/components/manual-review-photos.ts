export type LocalPhoto = {
  photo_id: string;
  sha256: string;
  width: number;
  height: number;
  label: string;
  preview_url: string;
  original_size: number;
};

export const PHOTO_LIMIT = 6;
export const FILE_LIMIT = 8 * 1024 * 1024;
export const TOTAL_LIMIT = 24 * 1024 * 1024;
const MAX_PIXELS = 20_000_000;

function dimensions(bytes: Uint8Array): { width: number; height: number } {
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const png = [137, 80, 78, 71, 13, 10, 26, 10].every((value, index) => bytes[index] === value);
  if (png && bytes.length >= 33) {
    if (view.getUint32(8) !== 13 || view.getUint32(12) !== 0x49484452) throw new Error('The PNG header is invalid.');
    let offset = 8;
    while (offset + 12 <= bytes.length) {
      const length = view.getUint32(offset);
      if (length > bytes.length - offset - 12) throw new Error('The PNG file is incomplete.');
      if (view.getUint32(offset + 4) === 0x6163544c) throw new Error('Animated images are not supported. Choose a single PNG or JPEG photo.');
      offset += length + 12;
      if (view.getUint32(offset - length - 8) === 0x49454e44) break;
    }
    return { width: view.getUint32(16), height: view.getUint32(20) };
  }
  if (bytes[0] === 0xff && bytes[1] === 0xd8) {
    let offset = 2;
    while (offset + 3 < bytes.length) {
      if (bytes[offset++] !== 0xff) throw new Error('The JPEG header is invalid.');
      while (bytes[offset] === 0xff) offset++;
      const marker = bytes[offset++];
      if (marker === 0xd9 || marker === 0xda) break;
      if (marker === 0x01 || (marker >= 0xd0 && marker <= 0xd7)) continue;
      if (offset + 2 > bytes.length) break;
      const length = view.getUint16(offset);
      if (length < 2 || offset + length > bytes.length) throw new Error('The JPEG file is incomplete.');
      if ([0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf].includes(marker)) {
        if (length < 8) throw new Error('The JPEG dimensions are invalid.');
        return { width: view.getUint16(offset + 5), height: view.getUint16(offset + 3) };
      }
      offset += length;
    }
  }
  throw new Error('Choose a valid, single-frame PNG or JPEG photo.');
}

export async function preparePhoto(file: File, label: string): Promise<LocalPhoto> {
  if (file.size === 0 || file.size > FILE_LIMIT) throw new Error('Each photo must be between 1 byte and 8 MiB.');
  const bytes = new Uint8Array(await file.arrayBuffer());
  const declared = dimensions(bytes);
  if (declared.width < 1 || declared.height < 1 || declared.width * declared.height > MAX_PIXELS) {
    throw new Error('Each photo must be no larger than 20 megapixels.');
  }
  const original = URL.createObjectURL(file);
  const image = new Image();
  try {
    image.src = original;
    await image.decode();
    if (image.naturalWidth * image.naturalHeight > MAX_PIXELS || !image.naturalWidth || !image.naturalHeight) {
      throw new Error('Each photo must be no larger than 20 megapixels.');
    }
    const ratio = Math.min(1, 2048 / Math.max(image.naturalWidth, image.naturalHeight));
    const width = Math.max(1, Math.round(image.naturalWidth * ratio));
    const height = Math.max(1, Math.round(image.naturalHeight * ratio));
    const canvas = document.createElement('canvas');
    canvas.width = width; canvas.height = height;
    const context = canvas.getContext('2d');
    if (!context) throw new Error('This browser could not prepare the photo.');
    context.drawImage(image, 0, 0, width, height);
    const normalized = await new Promise<Blob>((resolve, reject) => canvas.toBlob(blob => blob ? resolve(blob) : reject(new Error('The photo could not be prepared.')), 'image/png'));
    const digest = await crypto.subtle.digest('SHA-256', await normalized.arrayBuffer());
    const sha256 = Array.from(new Uint8Array(digest), value => value.toString(16).padStart(2, '0')).join('');
    return { photo_id: crypto.randomUUID(), sha256, width, height, label, preview_url: URL.createObjectURL(normalized), original_size: file.size };
  } catch (error) {
    throw error instanceof Error && error.name !== 'EncodingError' ? error : new Error('This photo could not be decoded. Choose a valid PNG or JPEG.');
  } finally {
    image.src = ''; URL.revokeObjectURL(original);
  }
}
