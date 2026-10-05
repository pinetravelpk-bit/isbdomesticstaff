# ISB Domestic Staff — isbdomesticstaff.pk

Home page for **ISB Domestic Staff**, a domestic staffing agency in Islamabad & Rawalpindi
(maids, housekeepers, cooks, drivers, babysitters, patient care, watchmen, office staff).

Plain static site — HTML + CSS + vanilla JS, no build step.

```
index.html            page markup (icons are an inline SVG sprite)
assets/css/style.css  styles, animations, responsive breakpoints
assets/js/main.js     preloader, typing effect, particles, scroll reveal, counters,
                      testimonial slider, 3D tilt, WhatsApp enquiry form
assets/img/           logo
deploy/               nginx config + VPS setup/update scripts
```

## Run locally

Open `index.html` in a browser, or `python3 -m http.server 8080` and visit http://localhost:8080.

## Edit common things

| What                      | Where                                                        |
|---------------------------|--------------------------------------------------------------|
| Phone / WhatsApp number   | `index.html` (search `0310 521 4309`, `923105214309`) and `WHATSAPP` in `assets/js/main.js` |
| Typing words in hero      | `words` array in `assets/js/main.js`                         |
| Colours                   | `:root` variables at the top of `assets/css/style.css`       |
| Photos                    | `<img src>` in `index.html`                                  |

## Images

Photos are free stock images from [Unsplash](https://unsplash.com/license) (free for commercial
use, no attribution required), loaded from the Unsplash CDN. If a photo ever fails to load, the
script swaps in a matching drawn illustration so the layout never breaks. To self-host, download
the photos into `assets/img/` and update the `src` paths.

## Deploy to the VPS (Ubuntu, nginx)

This runs as its **own nginx site** next to anything else on the server.

1. **DNS** — at your domain registrar, point `A` records for `@` and `www` of
   `isbdomesticstaff.pk` to the VPS IP.
2. **Setup** — in the Hostinger *Web console* (or `ssh root@<VPS-IP>`):
   ```bash
   curl -fsSL -o setup.sh https://raw.githubusercontent.com/pinetravelpk-bit/isbdomesticstaff/main/deploy/setup.sh  # public repo only
   bash setup.sh
   ```
   For a private repo, paste the contents of `deploy/setup.sh` into a file on the server instead.
   The first run prints a **deploy key** — add it on GitHub under
   *Repo → Settings → Deploy keys*, then run `bash setup.sh` again. It installs nginx + certbot,
   clones the site to `/var/www/isbdomesticstaff`, enables the nginx site and issues the free
   HTTPS certificate.
3. **Updates** — after pushing changes to GitHub:
   ```bash
   bash /var/www/isbdomesticstaff/deploy/update.sh
   ```
