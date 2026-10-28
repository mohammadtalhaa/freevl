"use client";

import { useEffect, useRef } from "react";

/**
 * Renders one migrated legacy page.
 *
 * The page's original CSS and body HTML are rendered server-side (so the
 * content is in the HTML Vercel serves, not fetched after load), and the
 * page's original scripts are injected once, after mount, in their original
 * order. Injected classic scripts execute in global scope exactly like the
 * original <script> tags did, and the scripts expose their onclick handlers
 * on window, so the studio, auth, checkout and admin behaviour is preserved.
 *
 * Navigation between pages is a full page load (the original <a> links),
 * not Next.js client-side navigation, because the legacy scripts boot once
 * per page load. That is intentional for this migration.
 */
export default function LegacyPage({ data }) {
  const ran = useRef(false);

  useEffect(() => {
    if (ran.current) return;
    ran.current = true;
    data.scripts.forEach((s) => {
      const el = document.createElement("script");
      if (s.src) {
        el.src = s.src;
        el.async = !!s.async;
        el.crossOrigin = "anonymous";
      } else {
        el.textContent = s.content;
      }
      document.body.appendChild(el);
    });
  }, [data]);

  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: data.css }} />
      <div id={data.bodyId || undefined} dangerouslySetInnerHTML={{ __html: data.bodyHtml }} />
    </>
  );
}
