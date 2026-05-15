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
const storageStateBase64 = process.env.EUFY_STORAGE_STATE_B64 ?? '';
const safetyPin = process.env.EUFY_SAFETY_PIN ?? '';

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

async function seedStorageStateFromEnvironment() {
  if (!storageStateBase64 || (await pathExists(storageStatePath))) {
    return;
  }

  const decodedState = Buffer.from(storageStateBase64, 'base64').toString('utf8');
  await fs.writeFile(storageStatePath, decodedState, 'utf8');
}

function emailLocator(page) {
  return page.locator('input[type="email"], input[placeholder*="mail" i], input[autocomplete="username"]').first();
}

function passwordLocator(page) {
  return page.locator('input[type="password"], input[autocomplete="current-password"]').first();
}

async function loginIfNeeded(page, context) {
  const emailField = emailLocator(page);
  const passwordField = passwordLocator(page);

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

async function ensureAuthenticated(page, context) {
  await page.goto(`${baseUrl}/#/camera`, { waitUntil: 'domcontentloaded' });
  await page.waitForLoadState('networkidle');

  if ((await emailLocator(page).count()) > 0 && (await passwordLocator(page).count()) > 0) {
    await loginIfNeeded(page, context);
    await page.goto(`${baseUrl}/#/camera`, { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('networkidle');
  }

  await page.waitForSelector('.camera-item', { timeout: 90_000 });
}

async function dismissVisibleModal(page) {
  const modalResult = await page.evaluate((pin) => {
    const isVisible = (element) => {
      if (!(element instanceof HTMLElement)) {
        return false;
      }
      const style = window.getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return (
        style.display !== 'none' &&
        style.visibility !== 'hidden' &&
        rect.width > 0 &&
        rect.height > 0
      );
    };

    const setNativeValue = (input, value) => {
      const descriptor = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value');
      descriptor?.set?.call(input, value);
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
      input.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true, key: value }));
    };

    const modals = Array.from(document.querySelectorAll('.ant-modal-wrap, .liveViewAccess-content'));
    const visibleModal = modals.find(isVisible);
    if (!(visibleModal instanceof HTMLElement)) {
      return { handled: false, text: '', requiresPin: false };
    }

    const modalText = visibleModal.textContent?.trim().slice(0, 500) ?? '';
    const pinInputs = Array.from(visibleModal.querySelectorAll('input')).filter(
      (element) => element instanceof HTMLInputElement && isVisible(element)
    );

    if (pinInputs.length > 0) {
      if (!pin) {
        return {
          handled: false,
          text: modalText,
          requiresPin: true,
        };
      }

      const singleCharacterInputs = pinInputs.every((input) => input.maxLength === 1 || input.maxLength === 0);
      if (singleCharacterInputs && pinInputs.length >= pin.length) {
        pinInputs.slice(0, pin.length).forEach((input, index) => {
          input.focus();
          setNativeValue(input, pin[index] ?? '');
        });
      } else {
        const firstInput = pinInputs[0];
        firstInput.focus();
        setNativeValue(firstInput, '');
        setNativeValue(firstInput, pin);
      }
    }

    const buttons = Array.from(visibleModal.querySelectorAll('button')).filter(isVisible);
    const preferredKeywords = ['allow', 'confirm', 'continue', 'ok', 'yes', 'agree', 'enable', 'start'];
    const selectedButton =
      buttons.find((button) => {
        const label = button.textContent?.trim().toLowerCase() ?? '';
        return preferredKeywords.some((keyword) => label.includes(keyword));
      }) ?? buttons.at(-1);

    if (!(selectedButton instanceof HTMLElement)) {
      return {
        handled: false,
        text: modalText,
        requiresPin: pinInputs.length > 0 && !pin,
      };
    }

    const buttonText = selectedButton.textContent?.trim() ?? '';
    selectedButton.click();

    return {
      handled: true,
      buttonText,
      text: modalText,
      requiresPin: false,
    };
  }, safetyPin);

  if (modalResult.requiresPin) {
    throw new Error(
      `Eufy live view requires a Safety PIN. Set EUFY_SAFETY_PIN before running capture. Modal text: ${modalResult.text}`
    );
  }

  if (modalResult.handled) {
    console.log(`Dismissed modal with button "${modalResult.buttonText}".`);
    await page.waitForTimeout(2_000);
  }

  return modalResult;
}

async function clickCameraCard(page, cameraName) {
  await page.evaluate((name) => {
    const cards = Array.from(document.querySelectorAll('.camera-item'));
    const card = cards.find((entry) => entry.textContent?.includes(name));
    const target = card?.querySelector('.camera-main-inner');
    if (!(target instanceof HTMLElement)) {
      throw new Error(`Camera card not found for ${name}`);
    }
    target.click();
  }, cameraName);
}

async function waitForCameraMedia(page, cameraName, timeout) {
  try {
    await page.waitForFunction(
      (name) => {
        const cards = Array.from(document.querySelectorAll('.camera-item'));
        const card = cards.find((entry) => entry.textContent?.includes(name));
        const media = card?.querySelector('video, canvas, img');
        if (!(media instanceof HTMLElement)) {
          return false;
        }
        const style = window.getComputedStyle(media);
        return style.display !== 'none' && media.clientWidth > 0 && media.clientHeight > 0;
      },
      cameraName,
      { timeout }
    );
    return true;
  } catch (error) {
    if (error instanceof Error && error.name === 'TimeoutError') {
      return false;
    }
    throw error;
  }
}

async function activateCamera(page, cameraName) {
  const cameraCard = page.locator('.camera-item', { hasText: cameraName }).first();
  await cameraCard.waitFor({ state: 'visible', timeout: 90_000 });
  await dismissVisibleModal(page);
  await clickCameraCard(page, cameraName);
  await dismissVisibleModal(page);

  if (!(await waitForCameraMedia(page, cameraName, 30_000))) {
    const modalResult = await dismissVisibleModal(page);
    await clickCameraCard(page, cameraName);

    if (!(await waitForCameraMedia(page, cameraName, 60_000))) {
      const modalDetails = modalResult.text ? ` Modal text: ${modalResult.text}` : '';
      throw new Error(`Timed out waiting for live media for ${cameraName}.${modalDetails}`);
    }
  }

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
  await seedStorageStateFromEnvironment();

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext(
    (await pathExists(storageStatePath))
      ? { storageState: storageStatePath, viewport: { width: 1600, height: 1200 } }
      : { viewport: { width: 1600, height: 1200 } }
  );
  const page = await context.newPage();

  try {
    await ensureAuthenticated(page, context);

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
