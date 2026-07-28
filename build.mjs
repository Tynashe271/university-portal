import { mkdir, readFile, rm, writeFile, copyFile } from "node:fs/promises";

await rm("dist", { recursive: true, force: true });
await mkdir("dist/server", { recursive: true });
await mkdir("dist/static", { recursive: true });
await mkdir("dist/static/public", { recursive: true });
await mkdir("dist/.openai", { recursive: true });

const html = await readFile("index.html", "utf8");
const css = await readFile("styles.css", "utf8");
const js = await readFile("app.js", "utf8");

const worker = `
const files = {
  "/": { body: ${JSON.stringify(html)}, type: "text/html; charset=utf-8" },
  "/index.html": { body: ${JSON.stringify(html)}, type: "text/html; charset=utf-8" },
  "/styles.css": { body: ${JSON.stringify(css)}, type: "text/css; charset=utf-8" },
  "/app.js": { body: ${JSON.stringify(js)}, type: "text/javascript; charset=utf-8" }
};
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/public/og.png" && env.ASSETS) return env.ASSETS.fetch(request);
    const file = files[url.pathname];
    if (!file) return new Response("Not found", { status: 404 });
    return new Response(file.body, { headers: { "content-type": file.type, "cache-control": url.pathname === "/" ? "no-cache" : "public, max-age=3600", "x-content-type-options": "nosniff", "referrer-policy": "strict-origin-when-cross-origin" } });
  }
};`;

await writeFile("dist/server/index.js", worker);
await copyFile("public/og.png", "dist/static/public/og.png");
await copyFile(".openai/hosting.json", "dist/.openai/hosting.json");
console.log("Built Chongogwe High School site.");
