import type { NextConfig } from "next";

// GitHub Pages serves project sites from /<repo-name>/, so production builds
// need a basePath. Local `npm run dev` keeps serving from the root.
const repo = "tampa-bay-lightning-tracker";
const isProd = process.env.NODE_ENV === "production";

const nextConfig: NextConfig = {
  output: "export", // build plain static files into ./out (no server needed)
  basePath: isProd ? `/${repo}` : "",
  images: { unoptimized: true }, // Next's image optimizer needs a server
  trailingSlash: true,
};

export default nextConfig;
