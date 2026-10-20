import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Auction Intelligence — Listing identity',
  description: 'Verify an auction listing identity with clearly labeled demonstration data.',
};
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
