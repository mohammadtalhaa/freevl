/** @type {import('next').NextConfig} */
const legacyRedirects = [
  ["index.html", "/"],
  ["about.html", "/about"],
  ["ai-voices.html", "/ai-voices"],
  ["premium-voices.html", "/premium-voices"],
  ["realistic-voices.html", "/realistic-voices"],
  ["faqs.html", "/faqs"],
  ["contact.html", "/contact"],
  ["feature-requests.html", "/feature-requests"],
  ["privacy.html", "/privacy"],
  ["terms.html", "/terms"],
  ["disclaimers.html", "/disclaimers"],
  ["sitemap.html", "/sitemap"],
  ["admin.html", "/admin"],
];

const nextConfig = {
  // The legacy scripts attach window handlers and run boot() on load.
  // Strict Mode double-invokes effects in development, which would run
  // those scripts twice, so it stays off for this migrated site.
  reactStrictMode: false,
  async redirects() {
    return [
      ...legacyRedirects.map(([source, destination]) => ({
        source: `/${source}`,
        destination,
        permanent: true,
      })),
      {
        source: "/:path*",
        has: [{ type: "host", value: "www.freevoicelabs.com" }],
        destination: "https://freevoicelabs.com/:path*",
        permanent: true,
      },
    ];
  },
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
        ],
      },
      {
        source: "/(favicon.ico|logo.png|og-image.png|apple-touch-icon.png|shared.css)",
        headers: [{ key: "Cache-Control", value: "public, max-age=31536000, immutable" }],
      },
    ];
  },
};

export default nextConfig;
