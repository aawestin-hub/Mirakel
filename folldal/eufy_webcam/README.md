# Folldal Eufy webcam

Dette er et lite VPS-oppsett som:

1. logger inn i Eufy-web,
2. tar snapshot av `Folldal_Vestsiden` og `Folldal_Inngangsparti`,
3. lagrer de siste bildene lokalt,
4. og viser dem på en enkel side.

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
