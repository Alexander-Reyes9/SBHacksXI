/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',  // Enable static exports
  images: {
    unoptimized: true,
  },
  basePath: '/SBHacksXI', // Your repository name
  assetPrefix: '/SBHacksXI/', // Your repository name with trailing slash
}

module.exports = nextConfig
