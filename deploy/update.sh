#!/usr/bin/env bash
# Pull the latest site from GitHub (run as root on the VPS).
set -euo pipefail
git -C /var/www/isbdomesticstaff pull --ff-only
chown -R www-data:www-data /var/www/isbdomesticstaff
echo "Updated: $(git -C /var/www/isbdomesticstaff log -1 --format='%h %s')"
