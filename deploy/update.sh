#!/usr/bin/env bash
# Pull the latest site from GitHub and refresh nginx (run as root on the VPS).
set -euo pipefail
WEBROOT=/var/www/isbdomesticstaff
DOMAIN=isbdomesticstaff.pk
# files are owned by www-data; let root's git work in this folder
git config --global --get-all safe.directory | grep -qx "$WEBROOT" || git config --global --add safe.directory "$WEBROOT"
git -C "$WEBROOT" pull --ff-only
chown -R www-data:www-data "$WEBROOT"
# keep nginx config in sync, but never overwrite certbot's HTTPS edits
if ! grep -q "listen 443" "/etc/nginx/sites-available/$DOMAIN" 2>/dev/null; then
  cp "$WEBROOT/deploy/nginx-isbdomesticstaff.conf" "/etc/nginx/sites-available/$DOMAIN"
fi
nginx -t && systemctl reload nginx
echo "Updated: $(git -C "$WEBROOT" log -1 --format='%h %s')"
