import {clsx, type ClassValue} from 'clsx';
import {twMerge} from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Extract bundle name from bundle string (e.g., 'cask "google-chrome"' -> 'google-chrome')
export const extractBundleName = (bundle: string): string | null => {
  const match = bundle.match(/^(brew|cask|mas)\s+"([^"]+)"/);
  return match ? match[2] : null;
};
