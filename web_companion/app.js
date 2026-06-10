const STORAGE_KEY = "winstorepackager-companion-profile";
const PROFILE_FORMAT = "winstorepackager-project-v1";
const PROFILE_VERSION = 1;

const form = document.getElementById("profileForm");
const importProfileButton = document.getElementById("importProfileButton");
const exportProfileButton = document.getElementById("exportProfileButton");
const installAppButton = document.getElementById("installAppButton");
const profileFileInput = document.getElementById("profileFileInput");
const resetButton = document.getElementById("resetButton");
const copyManifestButton = document.getElementById("copyManifestButton");
const manifestPreview = document.getElementById("manifestPreview");
const jsonPreview = document.getElementById("jsonPreview");
const summaryList = document.getElementById("summaryList");
const iconUpload = document.getElementById("iconUpload");
const iconPreview = document.getElementById("iconPreview");
const iconStatus = document.getElementById("iconStatus");
const protocolStatus = document.getElementById("protocolStatus");
const installState = document.getElementById("installState");
const connectivityState = document.getElementById("connectivityState");
const swState = document.getElementById("swState");
const runtimeMode = document.getElementById("runtimeMode");
const cacheState = document.getElementById("cacheState");
const installHint = document.getElementById("installHint");

let deferredInstallPrompt = null;

init();

function init() {
  hydrateFromStorage();
  refreshViews();
  refreshEnvironment();

  form.addEventListener("input", onFormChanged);
  form.addEventListener("change", onFormChanged);

  importProfileButton.addEventListener("click", () => profileFileInput.click());
  exportProfileButton.addEventListener("click", exportProfile);
  installAppButton.addEventListener("click", installApp);
  profileFileInput.addEventListener("change", importProfile);
  resetButton.addEventListener("click", resetProfile);
  copyManifestButton.addEventListener("click", copyManifest);
  iconUpload.addEventListener("change", handleIconUpload);

  window.addEventListener("online", refreshEnvironment);
  window.addEventListener("offline", refreshEnvironment);
  window.addEventListener("beforeinstallprompt", handleBeforeInstallPrompt);
  window.addEventListener("appinstalled", handleAppInstalled);

  const displayModeQuery = window.matchMedia("(display-mode: standalone)");
  if (typeof displayModeQuery.addEventListener === "function") {
    displayModeQuery.addEventListener("change", refreshEnvironment);
  } else if (typeof displayModeQuery.addListener === "function") {
    displayModeQuery.addListener(refreshEnvironment);
  }

  registerServiceWorker();
}

function onFormChanged() {
  persistToStorage();
  refreshViews();
}

function buildProfile() {
  return {
    format: PROFILE_FORMAT,
    schema_version: PROFILE_VERSION,
    project_root: valueOf("projectRoot") || ".",
    metadata: {
      app_name: valueOf("appName"),
      publisher_display: valueOf("publisherDisplay"),
      identity_name: valueOf("identityName"),
      version: valueOf("version") || "1.0.0.0",
    },
    paths: {
      script_path: valueOf("scriptPath"),
      icon_path: valueOf("iconPath"),
      source_path: valueOf("sourcePath"),
      installer_path: valueOf("installerPath"),
      output_dir: valueOf("outputDir"),
      exe_name: valueOf("exeName"),
    },
    store: {
      privacy_url: valueOf("privacyUrl"),
      support_url: valueOf("supportUrl"),
      capabilities: splitCommaList(valueOf("capabilities")),
      category: valueOf("category"),
      age_rating: valueOf("ageRating"),
      description: valueOf("description"),
      changelog: valueOf("changelog"),
    },
    documents: {
      readme: valueOf("readme"),
      license_files: splitLineList(valueOf("licenseFiles")),
      license_text_entries: splitLicenseBlocks(valueOf("licenseTexts")),
    },
    settings: {
      enable_i18n: document.getElementById("enableI18n").checked,
    },
  };
}

function applyProfile(profile) {
  if (profile.format !== PROFILE_FORMAT || profile.schema_version !== PROFILE_VERSION) {
    throw new Error("Unbekanntes Projektprofilformat.");
  }

  setValue("projectRoot", profile.project_root || ".");
  setValue("appName", profile.metadata?.app_name || "");
  setValue("publisherDisplay", profile.metadata?.publisher_display || "");
  setValue("identityName", profile.metadata?.identity_name || "");
  setValue("version", profile.metadata?.version || "1.0.0.0");
  setValue("category", profile.store?.category || "Developer Tools");
  setValue("ageRating", profile.store?.age_rating || "3+");
  setValue("capabilities", (profile.store?.capabilities || []).join(", "));
  setValue("privacyUrl", profile.store?.privacy_url || "");
  setValue("supportUrl", profile.store?.support_url || "");
  setValue("scriptPath", profile.paths?.script_path || "");
  setValue("iconPath", profile.paths?.icon_path || "");
  setValue("sourcePath", profile.paths?.source_path || "");
  setValue("installerPath", profile.paths?.installer_path || "");
  setValue("outputDir", profile.paths?.output_dir || "");
  setValue("exeName", profile.paths?.exe_name || "");
  setValue("description", profile.store?.description || "");
  setValue("readme", profile.documents?.readme || "");
  setValue("changelog", profile.store?.changelog || "");
  setValue("licenseFiles", (profile.documents?.license_files || []).join("\n"));
  setValue("licenseTexts", (profile.documents?.license_text_entries || []).join("\n---\n"));
  document.getElementById("enableI18n").checked = Boolean(profile.settings?.enable_i18n);
}

function refreshViews() {
  const profile = buildProfile();
  jsonPreview.textContent = JSON.stringify(profile, null, 2);
  manifestPreview.textContent = buildManifestPreview(profile);
  renderSummary(profile);
}

function renderSummary(profile) {
  const rows = [
    ["App", profile.metadata.app_name || "offen"],
    ["Version", profile.metadata.version || "offen"],
    ["Kategorie", profile.store.category || "offen"],
    ["Freigabe", profile.store.age_rating || "offen"],
    ["Capabilities", profile.store.capabilities.join(", ") || "keine"],
    ["i18n", profile.settings.enable_i18n ? "aktiv" : "aus"],
  ];

  summaryList.innerHTML = rows
    .map(([term, value]) => `<dt>${escapeHtml(term)}</dt><dd>${escapeHtml(value)}</dd>`)
    .join("");
}

function buildManifestPreview(profile) {
  const appName = profile.metadata.app_name || "MyApp";
  const identityName = profile.metadata.identity_name || appName.replace(/\s+/g, "");
  const displayName = profile.metadata.publisher_display || "Your Studio";
  const description = profile.store.description || "Beschreibung ergänzen";
  const capabilities = profile.store.capabilities.length
    ? profile.store.capabilities.map((cap) => `    <Capability Name="${escapeAttribute(cap)}" />`).join("\n")
    : "    <Capability Name=\"internetClient\" />";

  return `<?xml version="1.0" encoding="utf-8"?>
<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
         xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10">
  <Identity Name="${escapeAttribute(identityName)}"
            Publisher="CN=DEIN-PUBLISHER-ID"
            Version="${escapeAttribute(profile.metadata.version || "1.0.0.0")}" />
  <Properties>
    <DisplayName>${escapeXml(appName)}</DisplayName>
    <PublisherDisplayName>${escapeXml(displayName)}</PublisherDisplayName>
    <Description>${escapeXml(description)}</Description>
    <Logo>icons\\icon_50x50.png</Logo>
  </Properties>
  <Dependencies>
    <TargetDeviceFamily Name="Windows.Desktop" MinVersion="10.0.17763.0" MaxVersionTested="10.0.19041.0" />
  </Dependencies>
  <Capabilities>
${capabilities}
  </Capabilities>
  <Applications>
    <Application Id="${escapeAttribute(identityName)}App"
                 Executable="${escapeAttribute(profile.paths.exe_name || `${appName}.exe`)}"
                 EntryPoint="Windows.FullTrustApplication">
      <uap:VisualElements DisplayName="${escapeAttribute(appName)}"
                          Description="${escapeAttribute(description)}"
                          Square150x150Logo="icons\\icon_150x150.png"
                          Square44x44Logo="icons\\icon_44x44.png"
                          BackgroundColor="transparent">
        <uap:DefaultTile Wide310x150Logo="icons\\icon_310x150.png" />
      </uap:VisualElements>
    </Application>
  </Applications>
</Package>`;
}

function exportProfile() {
  const profile = buildProfile();
  const blob = new Blob([JSON.stringify(profile, null, 2)], {
    type: "application/json;charset=utf-8",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "winstorepackager-project-v1.json";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

async function importProfile(event) {
  const [file] = event.target.files || [];
  if (!file) {
    return;
  }

  try {
    const text = await file.text();
    const profile = JSON.parse(text);
    applyProfile(profile);
    persistToStorage();
    refreshViews();
  } catch (error) {
    window.alert(`Projektprofil konnte nicht geladen werden:\n${error.message}`);
  } finally {
    profileFileInput.value = "";
  }
}

function resetProfile() {
  if (!window.confirm("Lokales Profil und Vorschau zurücksetzen?")) {
    return;
  }
  localStorage.removeItem(STORAGE_KEY);
  form.reset();
  setValue("projectRoot", ".");
  setValue("version", "1.0.0.0");
  setValue("category", "Developer Tools");
  setValue("ageRating", "3+");
  setValue("changelog", "Version 1.0.0.0\n- ");
  document.getElementById("enableI18n").checked = true;
  iconPreview.hidden = true;
  iconPreview.removeAttribute("src");
  setChip(iconStatus, "Noch kein Icon geladen", "neutral");
  refreshViews();
}

async function copyManifest() {
  try {
    await navigator.clipboard.writeText(manifestPreview.textContent);
    copyManifestButton.textContent = "Manifest kopiert";
    window.setTimeout(() => {
      copyManifestButton.textContent = "Manifest kopieren";
    }, 1400);
  } catch (error) {
    window.alert(`Manifest konnte nicht kopiert werden:\n${error.message}`);
  }
}

function persistToStorage() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(buildProfile()));
  } catch (_) {}
}

function hydrateFromStorage() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return;
  }

  try {
    applyProfile(JSON.parse(raw));
  } catch (error) {
    localStorage.removeItem(STORAGE_KEY);
  }
}

function handleIconUpload(event) {
  const [file] = event.target.files || [];
  if (!file) {
    return;
  }

  const imageUrl = URL.createObjectURL(file);
  const image = new Image();
  image.onload = () => {
    iconPreview.src = imageUrl;
    iconPreview.hidden = false;
    if (image.width >= 310 && image.height >= 310) {
      setChip(iconStatus, `Icon ok: ${image.width}×${image.height}px`, "success");
    } else {
      setChip(iconStatus, `Zu klein: ${image.width}×${image.height}px`, "warning");
    }
  };
  image.onerror = () => {
    URL.revokeObjectURL(imageUrl);
    setChip(iconStatus, "Icon konnte nicht gelesen werden", "warning");
  };
  image.src = imageUrl;
}

async function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) {
    setChip(swState, "Service Worker fehlt", "warning");
    cacheState.textContent = "Browser ohne Service-Worker-Support.";
    installHint.textContent = "Installieren nur in modernen Browsern möglich.";
    return;
  }

  if (window.location.protocol === "file:") {
    setChip(swState, "Service Worker blockiert", "warning");
    cacheState.textContent = "Dateimodus erlaubt kein Caching.";
    installHint.textContent = "Für PWA-Funktionen localhost oder https nutzen.";
    return;
  }

  try {
    const registration = await navigator.serviceWorker.register("./service-worker.js");
    if (registration.installing) {
      setChip(swState, "Service Worker installiert", "accent");
    } else {
      setChip(swState, "Service Worker aktiv", "success");
    }
    cacheState.textContent = "App-Shell wird lokal zwischengespeichert.";
    await navigator.serviceWorker.ready;
    setChip(swState, "Service Worker bereit", "success");
  } catch (error) {
    setChip(swState, "Service Worker fehlgeschlagen", "warning");
    cacheState.textContent = `Registrierung fehlgeschlagen: ${error.message}`;
  } finally {
    refreshEnvironment();
  }
}

function handleBeforeInstallPrompt(event) {
  event.preventDefault();
  deferredInstallPrompt = event;
  installAppButton.hidden = false;
  installAppButton.disabled = false;
  setChip(installState, "Installierbar", "accent");
  installHint.textContent = "Install-Dialog ist bereit.";
}

async function installApp() {
  if (!deferredInstallPrompt) {
    installHint.textContent = "Kein Install-Dialog verfügbar. Nutze localhost oder den Browser-Menüpunkt.";
    return;
  }

  const prompt = deferredInstallPrompt;
  deferredInstallPrompt = null;
  installAppButton.hidden = true;
  prompt.prompt();
  const choice = await prompt.userChoice;
  if (choice.outcome === "accepted") {
    setChip(installState, "Installation bestätigt", "success");
    installHint.textContent = "Der Browser installiert jetzt den Companion.";
  } else {
    setChip(installState, "Installation abgebrochen", "warning");
    installHint.textContent = "Der Dialog wurde geschlossen. Er kann später erneut erscheinen.";
  }
}

function handleAppInstalled() {
  deferredInstallPrompt = null;
  installAppButton.hidden = true;
  setChip(installState, "Installiert", "success");
  installHint.textContent = "Companion läuft jetzt auch als installierte App.";
  refreshEnvironment();
}

function refreshEnvironment() {
  const fileMode = window.location.protocol === "file:";
  const standalone = isStandaloneMode();
  const online = navigator.onLine;

  if (fileMode) {
    setChip(protocolStatus, "Dateimodus", "warning");
  } else {
    setChip(protocolStatus, "Lokalserver", "success");
  }

  if (standalone) {
    runtimeMode.textContent = "Installierte App";
  } else if (fileMode) {
    runtimeMode.textContent = "Lokale Datei";
  } else {
    runtimeMode.textContent = "Browser-Tab";
  }

  if (standalone) {
    setChip(installState, "Installiert", "success");
  } else if (deferredInstallPrompt) {
    setChip(installState, "Installierbar", "accent");
  } else if (fileMode) {
    setChip(installState, "Nicht installierbar", "warning");
  } else {
    setChip(installState, "Nicht installiert", "neutral");
  }

  setChip(connectivityState, online ? "Online" : "Offline", online ? "success" : "warning");
}

function isStandaloneMode() {
  return window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
}

function setChip(element, text, kind) {
  element.textContent = text;
  element.className = `status-chip ${kind}`;
}

function valueOf(id) {
  return document.getElementById(id).value.trim();
}

function setValue(id, value) {
  document.getElementById(id).value = value;
}

function splitCommaList(value) {
  return value
    .split(",")
    .map((entry) => entry.trim())
    .filter(Boolean);
}

function splitLineList(value) {
  return value
    .split(/\r?\n/)
    .map((entry) => entry.trim())
    .filter(Boolean);
}

function splitLicenseBlocks(value) {
  return value
    .split(/\n---\n/g)
    .map((entry) => entry.trim())
    .filter(Boolean);
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function escapeXml(value) {
  return escapeHtml(value)
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");
}

function escapeAttribute(value) {
  return escapeXml(value || "");
}
