# Folldal Eufy webcam

Dette er et lite VPS-oppsett som:

1. logger inn i Eufy-web,
2. tar snapshot av `Folldal_Vestsiden` og `Folldal_Inngangsparti`,
3. lagrer de siste bildene lokalt,
4. og viser dem på en enkel side.

Det kan også kjøres gratis via **GitHub Actions + GitHub Pages**.

## Filer

- `capture.js` - henter nye bilder fra Eufy
- `server.js` - serverer den enkle nettsiden
- `public/` - statisk side + siste bilder
- `deploy/` - systemd-filer og oppsettsskript
- `.env.example` - miljøvariabler som må fylles ut

## Rask start på VPS

```bash
cd /opt
git clone <repo-url> folldal-eufy-webcam
cd folldal-eufy-webcam/folldal/eufy_webcam
bash deploy/setup-vps.sh /opt/folldal-eufy-webcam
cp .env.example .env
```

Fyll deretter inn Eufy-bruker og passord i `.env`.

## Systemd

Kopier filene i `deploy/` til `/etc/systemd/system/`, og kjør:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now eufy-web.service
sudo systemctl enable --now eufy-capture.timer
sudo systemctl start eufy-capture.service
```

## GitHub Actions + Pages

Workflowen ligger i `.github/workflows/eufy-webcam.yml`.

For å bruke den må repoet ha disse GitHub Secrets:

- `EUFY_STORAGE_STATE_B64` **eller**
- `EUFY_EMAIL`
- `EUFY_PASSWORD`
- `EUFY_SAFETY_PIN`

`EUFY_SAFETY_PIN` er sikkerhetskoden Eufy ber om for **Web Portal Access** før livebildet kan åpnes i nettleseren.

Deretter må GitHub Pages være slått på for repoet med **Build and deployment source = GitHub Actions**.

Workflowen:

1. kjører daglig rundt lokal tid 12 i Norge,
2. logger inn i Eufy,
3. lager nye bilder og metadata,
4. og publiserer `public/` til GitHub Pages.
