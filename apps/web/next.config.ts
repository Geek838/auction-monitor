import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  devIndicators: false,
  // CPU-only local vision has a finite 180s backend deadline plus inventory work.
  // Next's default 30s rewrite timeout would terminate those valid local requests.
  experimental: { proxyTimeout: 210_000 },
  async rewrites() {
    const backend = (process.env.API_BASE_URL ?? 'http://127.0.0.1:8000').replace(/\/$/, '');
    return [{ source: '/api/v1/:path*', destination: `${backend}/api/v1/:path*` }];
  },
};
export default nextConfig;
