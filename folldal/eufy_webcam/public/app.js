const updatedAtElement = document.getElementById('updated-at');
const cameraGridElement = document.getElementById('camera-grid');

function formatTimestamp(value) {
  const timestamp = new Date(value);
  return new Intl.DateTimeFormat('nb-NO', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(timestamp);
}

async function loadMetadata() {
  const response = await fetch(`metadata.json?ts=${Date.now()}`, { cache: 'no-store' });
  if (!response.ok) {
    throw new Error('Fant ingen metadata ennå.');
  }
  return response.json();
}

function renderCameras(metadata) {
  updatedAtElement.textContent = `Sist oppdatert: ${formatTimestamp(metadata.updatedAt)}`;
  cameraGridElement.innerHTML = metadata.cameras
    .map(
      (camera) => `
        <article class="camera-card">
          <h2>${camera.name}</h2>
          <img src="${camera.file}?ts=${Date.now()}" alt="${camera.name}">
        </article>
      `
    )
    .join('');
}

async function main() {
  try {
    const metadata = await loadMetadata();
    renderCameras(metadata);
  } catch (error) {
    updatedAtElement.textContent = 'Ingen bilder er hentet ennå.';
    cameraGridElement.innerHTML = `<p class="empty">${error.message}</p>`;
  }
}

main();
