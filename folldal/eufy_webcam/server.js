import fs from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const publicDir = path.join(__dirname, 'public');
const port = Number(process.env.PORT ?? 8787);

const contentTypes = new Map([
  ['.html', 'text/html; charset=utf-8'],
  ['.js', 'text/javascript; charset=utf-8'],
  ['.css', 'text/css; charset=utf-8'],
  ['.json', 'application/json; charset=utf-8'],
  ['.jpg', 'image/jpeg'],
  ['.jpeg', 'image/jpeg'],
  ['.png', 'image/png'],
]);

async function serveFile(filePath, response) {
  const extension = path.extname(filePath).toLowerCase();
  const contentType = contentTypes.get(extension) ?? 'application/octet-stream';
  const file = await fs.readFile(filePath);
  response.writeHead(200, { 'Content-Type': contentType, 'Cache-Control': 'no-store' });
  response.end(file);
}

const server = http.createServer(async (request, response) => {
  try {
    const requestedPath = request.url === '/' ? '/index.html' : request.url ?? '/index.html';
    const safePath = requestedPath.split('?')[0];
    const filePath = path.join(publicDir, safePath);
    await serveFile(filePath, response);
  } catch {
    response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
    response.end('Not found');
  }
});

server.listen(port, () => {
  console.log(`Eufy webcam page available on port ${port}`);
});
