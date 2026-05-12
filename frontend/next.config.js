/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  distDir: 'out',
  images: {
    unoptimized: true
  },
  // API calls will be proxied or use full URL in production
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL + '/api/:path*' || 'http://localhost:8000/api/:path*'
      }
    ];
  }
};

module.exports = nextConfig;
