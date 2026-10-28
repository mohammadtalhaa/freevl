import data from "@/lib/legacy/premium-voices.json";
import LegacyPage from "@/components/LegacyPage";

export const metadata = {
  title: data.title,
  description: data.description || undefined,
  alternates: { canonical: data.ogUrl },
  openGraph: {
    title: data.ogTitle || data.title,
    description: data.ogDescription || data.description || undefined,
    url: data.ogUrl,
    images: data.ogImage ? [{ url: data.ogImage }] : undefined,
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: data.ogTitle || data.title,
    description: data.ogDescription || data.description || undefined,
    images: data.ogImage ? [data.ogImage] : undefined,
  },
};

export default function Page() {
  return (
    <>
      {data.jsonLd.map((ld, i) => (
        <script key={i} type="application/ld+json" dangerouslySetInnerHTML={{ __html: ld }} />
      ))}
      <LegacyPage data={data} />
    </>
  );
}
