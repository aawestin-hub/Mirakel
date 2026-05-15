import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const baseUrl = process.env.EUFY_BASE_URL ?? 'https://mysecurity.eufylife.com';
const loginUrl = process.env.EUFY_LOGIN_URL ?? `${baseUrl}/#/login?type=/`;
const outputDir = path.resolve(__dirname, process.env.EUFY_OUTPUT_DIR ?? './public');
const stateDir = path.resolve(__dirname, process.env.EUFY_STATE_DIR ?? './state');
const storageStatePath = path.join(stateDir, 'storage-state.json');
const cameraNames = (process.env.EUFY_CAMERA_NAMES ?? 'Folldal_Vestsiden,Folldal_Inngangsparti')
  .split(',')
  .map((value) => value.trim())
  .filter(Boolean);
const email = process.env.EUFY_EMAIL ?? '';
const password = process.env.EUFY_PASSWORD ?? '';

function slugify(value) {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

async function pathExists(targetPath) {
  try {
    await fs.access(targetPath);
    return true;
  } catch {
    return false;
  }
}

async function ensureDirectories() {
  await fs.mkdir(outputDir, { recursive: true });
  await fs.mkdir(stateDir, { recursive: true });
}

async function loginIfNeeded(page, context) {
  await page.goto(loginUrl, { waitUntil: 'networkidle' });

  const emailField = page.locator('input[type="email"], input[placeholder*="mail" i], input[autocomplete="username"]').first();
  const passwordField = page.locator('input[type="password"], input[autocomplete="current-password"]').first();

  if ((await emailField.count()) === 0 || (await passwordField.count()) === 0) {
    return;
  }

  if (!email || !password) {
    throw new Error('Missing EUFY_EMAIL or EUFY_PASSWORD. Set them in the environment before running capture.');
  }

  await emailField.fill(email);
  await passwordField.fill(password);

  const submitButton = page
    .locator('button:has-text("Log In"), button:has-text("Login"), button:has-text("Sign In"), .ant-btn-primary')
    .first();
  await submitButton.click();

  await page.waitForURL((url) => !url.toString().includes('/login'), { timeout: 90_000 });
  await context.storageState({ path: storageStatePath });
}

async function openCameraPage(page) {
  await page.goto(`${baseUrl}/#/camera`, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('.camera-item', { timeout: 90_000 });
}

async function activateCamera(page, cameraName) {
  const cameraCard = page.locator('.camera-item', { hasText: cameraName }).first();
  await cameraCard.waitFor({ state: 'visible', timeout: 90_000 });
  await cameraCard.locator('.camera-main-inner').click();

  await page.waitForFunction(
    (name) => {
      const cards = Array.from(document.querySelectorAll('.camera-item'));
      const card = cards.find((entry) => entry.textContent?.includes(name));
      const video = card?.querySelector('video');
      if (!video) {
        return false;
      }
      const style = window.getComputedStyle(video);
      return style.display !== 'none' && video.clientWidth > 0 && video.clientHeight > 0;
    },
    cameraName,
    { timeout: 90_000 }
  );

  return cameraCard;
}

async function captureCamera(page, cameraName) {
  const cameraCard = await activateCamera(page, cameraName);
  const fileName = `${slugify(cameraName)}.jpg`;
  const absolutePath = path.join(outputDir, fileName);

  await cameraCard.locator('.camera-main').screenshot({
    path: absolutePath,
    type: 'jpeg',
    quality: 85,
  });

  return {
    name: cameraName,
    file: fileName,
  };
}

async function writeMetadata(cameras) {
  const metadataPath = path.join(outputDir, 'metadata.json');
  const metadata = {
    updatedAt: new Date().toISOString(),
    cameras,
  };

  await fs.writeFile(metadataPath, `${JSON.stringify(metadata, null, 2)}\n`, 'utf8');
}

async function main() {
  await ensureDirectories();

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext(
    (await pathExists(storageStatePath))
      ? { storageState: storageStatePath, viewport: { width: 1600, height: 1200 } }
      : { viewport: { width: 1600, height: 1200 } }
  );
  const page = await context.newPage();

  try {
    await loginIfNeeded(page, context);
    await openCameraPage(page);

    const capturedCameras = [];
    for (const cameraName of cameraNames) {
      capturedCameras.push(await captureCamera(page, cameraName));
    }

    await context.storageState({ path: storageStatePath });
    await writeMetadata(capturedCameras);
  } finally {
    await context.close();
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
