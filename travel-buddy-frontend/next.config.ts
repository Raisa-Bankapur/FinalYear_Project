import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  distDir: ".next-release",
  turbopack: {
    root: __dirname,
  },
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "source.unsplash.com",
      },
    ],
  },
};

export default nextConfig;
