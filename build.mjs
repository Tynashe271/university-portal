import { mkdir, readFile, rm, writeFile, copyFile } from "node:fs/promises";

await rm("dist", { recursive: true, force: true });
await mkdir("dist/server", { recursive: true });
await mkdir("dist/static", { recursive: true });
await mkdir("dist/static/public", { recursive: true });
await mkdir("dist/.openai", { recursive: true });

const css = await readFile("styles.css", "utf8");
const js = await readFile("app.js", "utf8");
const portalCss = await readFile("portal.css", "utf8");
const portalJs = await readFile("portal.js", "utf8");
const pages = ["index.html", "about.html", "academics.html", "student-life.html", "admissions.html", "news.html", "contact.html", "application.html", "student-portal.html"];
const pageFiles = Object.fromEntries(await Promise.all(pages.map(async name => [name, await readFile(name, "utf8")])));
const routes = Object.fromEntries(Object.entries(pageFiles).flatMap(([name, body]) => {
  const route = name === "index.html" ? "/" : `/${name}`;
  return [[route, { body, type: "text/html; charset=utf-8" }], [`/${name}`, { body, type: "text/html; charset=utf-8" }]];
}));

const worker = `
const files = {
  ...${JSON.stringify(routes)},
  "/styles.css": { body: ${JSON.stringify(css)}, type: "text/css; charset=utf-8" },
  "/app.js": { body: ${JSON.stringify(js)}, type: "text/javascript; charset=utf-8" },
  "/portal.css": { body: ${JSON.stringify(portalCss)}, type: "text/css; charset=utf-8" },
  "/portal.js": { body: ${JSON.stringify(portalJs)}, type: "text/javascript; charset=utf-8" }
};
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/public/og.png" && env.ASSETS) return env.ASSETS.fetch(request);
    const file = files[url.pathname];
    if (!file) return new Response("Not found", { status: 404 });
    return new Response(file.body, { headers: { "content-type": file.type, "cache-control": url.pathname === "/" || url.pathname.startsWith("/portal.") ? "no-cache" : "public, max-age=3600", "x-content-type-options": "nosniff", "referrer-policy": "strict-origin-when-cross-origin" } });
  }
};`;

await writeFile("dist/server/index.js", worker);
await copyFile("public/og.png", "dist/static/public/og.png");
await copyFile(".openai/hosting.json", "dist/.openai/hosting.json");
console.log("Built Anyschool High School site.");
