export const metadata = {
  metadataBase: new URL("https://freevoicelabs.com"),
  title: {
    default: "AI Voice Generator — Neural TTS, Voice Cloning & Podcast Studio | Free Voice Labs",
  },
  description:
    "Free AI voice generator with neural TTS, voice cloning, and podcast mode. 320+ voices, 90+ languages.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://api.fontshare.com/v2/css?f[]=clash-display@400,500,600,700&display=swap"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
        <link rel="dns-prefetch" href="https://mohammadtalhaa-free-voice-labs-backend.hf.space" />
      </head>
      <body>{children}</body>
    </html>
  );
}
