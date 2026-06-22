import { test, describe } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { execSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { join, dirname } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");

const appJs = readFileSync(join(root, "app.js"), "utf8");
const swJs = readFileSync(join(root, "service-worker.js"), "utf8");
const indexHtml = readFileSync(join(root, "index.html"), "utf8");
const manifest = JSON.parse(readFileSync(join(root, "manifest.webmanifest"), "utf8"));

// ── Bug #1: exportProfile – Anchor im DOM + setTimeout-Revoke ──────────────

describe("Bug #1 fix: exportProfile Download-Sequenz", () => {
  test("app.js hängt Link vor click() an document.body", () => {
    assert.ok(
      appJs.includes("document.body.appendChild(link)"),
      "document.body.appendChild(link) fehlt — Download auf iOS Safari/Firefox gebrochen"
    );
  });

  test("app.js entfernt Link nach click() aus document.body", () => {
    assert.ok(
      appJs.includes("document.body.removeChild(link)"),
      "document.body.removeChild(link) fehlt — DOM-Leak"
    );
  });

  test("app.js revoziert Object-URL via setTimeout, nicht synchron", () => {
    assert.ok(
      appJs.includes("window.setTimeout(() => URL.revokeObjectURL(url)"),
      "URL.revokeObjectURL() muss via setTimeout verzögert werden — synchrone Revokation bricht Download"
    );
  });
});

// ── Bug #2: persistToStorage – try/catch um localStorage.setItem ──────────

describe("Bug #2 fix: persistToStorage Safari-Private-Mode-Schutz", () => {
  test("app.js umschließt localStorage.setItem mit try/catch", () => {
    const persistFn = appJs.slice(appJs.indexOf("function persistToStorage"));
    const body = persistFn.slice(0, persistFn.indexOf("}", persistFn.indexOf("{") + 1) + 1);
    assert.ok(
      body.includes("try {"),
      "localStorage.setItem ohne try/catch — QuotaExceededError in Safari Private Mode crasht alle Formulareingaben"
    );
  });
});

// ── Bug #3: installApp – deferredInstallPrompt vor prompt() nullen ─────────

describe("Bug #3 fix: installApp Doppel-Trigger verhindert", () => {
  test("app.js nullt deferredInstallPrompt vor dem prompt()-Aufruf", () => {
    const installFn = appJs.slice(appJs.indexOf("async function installApp"));
    const closeIdx = installFn.indexOf("\nfunction ", 10);
    const body = closeIdx > 0 ? installFn.slice(0, closeIdx) : installFn.slice(0, 800);

    const nullIdx = body.indexOf("deferredInstallPrompt = null");
    const promptIdx = body.indexOf(".prompt()");
    assert.ok(nullIdx !== -1, "deferredInstallPrompt wird in installApp() nicht auf null gesetzt");
    assert.ok(promptIdx !== -1, ".prompt() nicht gefunden");
    assert.ok(
      nullIdx < promptIdx,
      "deferredInstallPrompt muss VOR .prompt() genullt werden — sonst Doppel-Trigger möglich"
    );
  });
});

// ── Bug #4: service-worker – alle Icon-PNGs in APP_SHELL ──────────────────

describe("Bug #4 fix: Service Worker APP_SHELL enthält alle Icons", () => {
  for (const icon of [
    "./icons/Icon-192.png",
    "./icons/Icon-512.png",
    "./icons/Icon-maskable-192.png",
    "./icons/Icon-maskable-512.png",
  ]) {
    test(`service-worker.js APP_SHELL enthält ${icon}`, () => {
      assert.ok(
        swJs.includes(icon),
        `${icon} fehlt in APP_SHELL — Icon lädt offline nicht`
      );
    });
  }
});

// ── Bug #5: index.html – apple-touch-icon ─────────────────────────────────

describe("Bug #5 fix: index.html enthält apple-touch-icon", () => {
  test("index.html hat <link rel='apple-touch-icon'>", () => {
    assert.ok(
      indexHtml.includes('rel="apple-touch-icon"'),
      "apple-touch-icon fehlt — iOS-Homescreen zeigt falsches oder generisches Icon"
    );
  });
});

// ── Bug #6: manifest – purpose:'any' für nicht-maskable Icons ─────────────

describe("Bug #6 fix: manifest.webmanifest Icons haben purpose:any", () => {
  test("manifest.webmanifest hat 4 Icons", () => {
    assert.equal(manifest.icons.length, 4, "Manifest sollte genau 4 Icons haben");
  });

  test("mindestens ein Icon ist als any-Variant nutzbar (purpose fehlt oder 'any')", () => {
    const anyVariants = manifest.icons.filter((i) => i.purpose !== "maskable");
    assert.ok(
      anyVariants.length > 0,
      "Kein any-Variant im Manifest — purpose-absent Icons gelten per Spec als 'any'"
    );
  });

  test("manifest hat genau 2 maskable Icons", () => {
    const maskable = manifest.icons.filter((i) => i.purpose === "maskable");
    assert.equal(maskable.length, 2, "Erwartet 2 maskable Icons (192 + 512)");
  });
});

// ──────────────────────────────────────────────────────────────
// iOS PWA-Härtung
// ──────────────────────────────────────────────────────────────

describe("index.html iOS-PWA-Meta", () => {
  test("viewport-Meta enthält viewport-fit=cover", () => {
    assert.match(indexHtml, /<meta[^>]*name="viewport"[^>]*viewport-fit=cover/);
  });

  test("viewport-Meta enthält width=device-width und initial-scale=1", () => {
    assert.match(indexHtml, /<meta[^>]*name="viewport"[^>]*width=device-width/);
    assert.match(indexHtml, /<meta[^>]*name="viewport"[^>]*initial-scale=1/);
  });

  test("apple-mobile-web-app-title ist gesetzt", () => {
    assert.match(indexHtml, /<meta[^>]*name="apple-mobile-web-app-title"[^>]*content="[^"]+"/);
  });

  test("apple-mobile-web-app-status-bar-style ist gesetzt", () => {
    assert.match(indexHtml, /<meta[^>]*name="apple-mobile-web-app-status-bar-style"[^>]*content="[^"]+"/);
  });

  test("apple-touch-icon hat sizes=\"180x180\"", () => {
    assert.match(indexHtml, /<link[^>]*rel="apple-touch-icon"[^>]*sizes="180x180"/);
  });

  test("apple-touch-icon verweist auf apple-touch-icon-180.png", () => {
    assert.match(indexHtml, /<link[^>]*rel="apple-touch-icon"[^>]*href="[^"]*apple-touch-icon-180\.png"/);
  });

  test("KEIN apple-mobile-web-app-capable (deprecated seit iOS 11.3)", () => {
    assert.doesNotMatch(indexHtml, /apple-mobile-web-app-capable/, "deprecated — darf nicht gesetzt sein");
  });

  test("keine doppelten viewport-Meta-Tags", () => {
    const matches = indexHtml.match(/<meta[^>]*name="viewport"/g) ?? [];
    assert.equal(matches.length, 1, `Genau 1 viewport-Meta erwartet, gefunden: ${matches.length}`);
  });

  test("theme-color Meta-Tag ist gesetzt", () => {
    assert.match(indexHtml, /<meta[^>]*name="theme-color"[^>]*content="[^"]+"/);
  });
});

describe("apple-touch-icon-180.png — opaques RGB", () => {
  const iconPath = join(__dirname, "..", "icons", "apple-touch-icon-180.png");

  test("apple-touch-icon-180.png existiert", () => {
    assert.ok(existsSync(iconPath), "icons/apple-touch-icon-180.png fehlt");
  });

  test("apple-touch-icon-180.png ist opakes RGB (keine Transparenz)", () => {
    const p = iconPath.replace(/\\/g, "/");
    const result = execSync(
      `python -c "from PIL import Image; img=Image.open('${p}'); d=list(img.getdata()); t=sum(1 for px in d if len(px)==4 and px[3]==0); print(t)"`,
      { encoding: "utf8" }
    ).trim();
    assert.equal(result, "0", `apple-touch-icon-180.png hat transparente Pixel: ${result}`);
  });
});

// BUG-W1: non-navigate fetch ohne .catch() → Offline-Fehler für uncached Assets
// Fix: .catch(() => new Response('Offline', {status:503})) nach fetch(request)
// Red-on-Revert: ohne .catch() schlägt dieser String-Match fehl
describe("BUG-W1 regression: service-worker fetch hat .catch() Offline-Fallback", () => {
  test("service-worker.js non-navigate fetch hat .catch() für 503 Offline-Fallback", () => {
    assert.ok(
      swJs.includes(".catch("),
      "service-worker.js non-navigate fetch muss .catch() Offline-Fallback haben — BUG-W1"
    );
    assert.ok(swJs.includes("503"), "Offline-Fallback muss HTTP 503 zurückgeben");
  });
});

describe("service-worker.js iOS-Härtung", () => {
  test("CACHE_NAME ist v3 oder höher (nach apple-touch-icon-180 Ergänzung)", () => {
    assert.match(swJs, /wsp-companion-v[3-9]/, "CACHE_NAME muss v3+ sein");
  });

  test("apple-touch-icon-180.png ist in APP_SHELL gecacht", () => {
    assert.ok(swJs.includes("apple-touch-icon-180.png"), "apple-touch-icon-180.png fehlt in APP_SHELL");
  });

  test("caches.match nutzt ignoreSearch:true (Offline-Fix bei ?-URLs)", () => {
    assert.ok(
      /caches\.match\([^)]*ignoreSearch\s*:\s*true/.test(swJs),
      "caches.match muss { ignoreSearch: true } nutzen"
    );
  });
});
