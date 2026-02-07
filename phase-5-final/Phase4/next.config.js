// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: (config) => {
    // Important: return the modified config
    return config;
  },
};

module.exports = nextConfig;