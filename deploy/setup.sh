#!/usr/bin/env bash
# One-time setup of isbdomesticstaff.pk on an Ubuntu VPS (run as root).
#   bash setup.sh
# Safe to re-run. Adds a separate nginx site; does not touch other sites on the server.
set -euo pipefail

DOMAIN="isbdomesticstaff.pk"
REPO="git@github.com:pinetravelpk-bit/isbdomesticstaff.git"
WEBROOT="/var/www/isbdomesticstaff"
KEY="/root/.ssh/isbdomesticstaff_deploy"
EMAIL="${EMAIL:-pinetravel.pk@gmail.com}"

echo "==> Checking web server"
if ss -ltnp 2>/dev/null | grep -q ':80 ' && ! ss -ltnp | grep ':80 ' | grep -q nginx; then
  echo "!! Port 80 is used by something other than nginx:"
  ss -ltnp | grep ':80 '
  echo "   This script configures nginx. Stop here and share the output above."
  exit 1
fi

echo "==> Installing packages"
apt-get update -y
apt-get install -y nginx git certbot python3-certbot-nginx

echo "==> GitHub deploy key"
mkdir -p /root/.ssh && chmod 700 /root/.ssh
if [ ! -f "$KEY" ]; then
  ssh-keygen -t ed25519 -N "" -C "isbdomesticstaff-vps" -f "$KEY"
fi
grep -q "Host github-isb" /root/.ssh/config 2>/dev/null || cat >> /root/.ssh/config <<CFG
Host github-isb
  HostName github.com
  User git
  IdentityFile $KEY
  IdentitiesOnly yes
CFG
ssh-keyscan -t ed25519 github.com >> /root/.ssh/known_hosts 2>/dev/null
CLONE_URL="${REPO/git@github.com:/github-isb:}"

if ! git ls-remote "$CLONE_URL" >/dev/null 2>&1; then
  echo
  echo "!! Add this key to GitHub, then run this script again:"
  echo "   Repo -> Settings -> Deploy keys -> Add deploy key (read-only is fine)"
  echo
  cat "$KEY.pub"
  echo
  exit 1
fi

echo "==> Fetching site"
git config --global --get-all safe.directory | grep -qx "$WEBROOT" || git config --global --add safe.directory "$WEBROOT"
if [ -d "$WEBROOT/.git" ]; then
  git -C "$WEBROOT" pull --ff-only
else
  rm -rf "$WEBROOT"
  git clone "$CLONE_URL" "$WEBROOT"
fi
chown -R www-data:www-data "$WEBROOT"

echo "==> nginx site"
cp "$WEBROOT/deploy/nginx-isbdomesticstaff.conf" "/etc/nginx/sites-available/$DOMAIN"
ln -sf "/etc/nginx/sites-available/$DOMAIN" "/etc/nginx/sites-enabled/$DOMAIN"
nginx -t
systemctl reload nginx

if command -v ufw >/dev/null && ufw status | grep -q active; then
  ufw allow 'Nginx Full' || true
fi

echo "==> HTTPS certificate"
SERVER_IP=$(curl -4 -s https://ifconfig.me || true)
DNS_IP=$(getent ahostsv4 "$DOMAIN" | awk 'NR==1{print $1}')
if [ -n "$DNS_IP" ] && [ "$DNS_IP" = "$SERVER_IP" ]; then
  certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos -m "$EMAIL" --redirect
else
  echo "!! $DOMAIN points to '${DNS_IP:-nothing}', this server is '$SERVER_IP'."
  echo "   Point the DNS A records (@ and www) to $SERVER_IP, wait a few minutes, then run:"
  echo "   certbot --nginx -d $DOMAIN -d www.$DOMAIN --redirect -m $EMAIL --agree-tos"
fi

echo "==> Done. Site files: $WEBROOT"
