import { test, describe } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
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

  test("alle nicht-maskable Icons haben purpose:'any'", () => {
    const nonMaskable = manifest.icons.filter((i) => i.purpose !== "maskable");
    for (const icon of nonMaskable) {
      assert.equal(
        icon.purpose,
        "any",
        `Icon ${icon.src} (${icon.sizes}) hat kein 'purpose: any'`
      );
    }
  });

  test("manifest hat genau 2 maskable Icons", () => {
    const maskable = manifest.icons.filter((i) => i.purpose === "maskable");
    assert.equal(maskable.length, 2, "Erwartet 2 maskable Icons (192 + 512)");
  });
});
