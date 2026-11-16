# Blog writing guide (isbdomesticstaff.pk)

Used by the scheduled job that publishes one post every 6 hours.

## Publishing steps
1. `python3 scripts/build_blog.py --next` → the next pending topic (title, slug, category). If it prints `NONE`, stop.
2. Write the article body to `content/blog/<slug>.html` (HTML fragment, see format below).
3. `python3 scripts/build_blog.py --publish <slug> "<meta description>"` → marks it published and rebuilds `blog/`, `sitemap.xml`, `robots.txt`.
4. Commit everything and push to `main`. The VPS pulls `main` automatically.

## Content rules
- The page H1 is the topic title exactly; the build script adds it. Do not put an `<h1>` in the fragment.
- 1,800–2,200 words of original writing in clear, simple English for families in Islamabad/Rawalpindi.
  Never copy or lightly rephrase earlier posts in `content/blog/`; give each post its own angle, structure, examples and FAQ.
- Target keyword = the topic title. Use it in the first paragraph, in at least two `<h2>` headings (naturally),
  and 4–8 times overall. Weave in related/LSI phrases (synonyms, roles, sectors, salary, verification, live-in/live-out, etc.).
- Local relevance: mention real sectors/areas where natural (F-6, F-7, G-11, E-11, DHA, Bahria Town, Saddar, Satellite Town, Chaklala, Gulraiz…).
- No invented statistics, prices or quotes presented as fact. For salaries, give hedged typical ranges in PKR
  ("roughly", "depending on experience and hours") and recommend confirming current rates with ISB Domestic Staff.
- Internal links: link to `/` (home) and 1–3 relevant earlier posts as `/blog/<slug>/` (only ones already published).
- End with a short section on how ISB Domestic Staff helps (verified staff, fast hiring, replacement guarantee,
  office in Chandni Chowk, Rawalpindi, phone/WhatsApp <a href="tel:+923105214309">0310 521 4309</a>), then the FAQ.
- Meta description: 140–160 characters, includes the keyword, written for clicks.

## Fragment format
```html
<p class="lead">Opening paragraph with the keyword…</p>
<h2>…</h2><p>…</p>
<h3>…</h3><p>…</p>
<ul><li>…</li></ul>   <ol><li>…</li></ol>
<table><thead><tr><th>…</th></tr></thead><tbody><tr><td>…</td></tr></tbody></table>   (optional)
<div class="callout"><strong>Tip:</strong> …</div>   (optional)
<section class="faq">
  <h2>Frequently Asked Questions</h2>
  <h3>Question?</h3>
  <p>Answer in one paragraph.</p>
  … 4–6 questions …
</section>
```
Use only these tags: p, h2, h3, ul, ol, li, strong, em, a, table, thead, tbody, tr, th, td, div.callout, section.faq.
