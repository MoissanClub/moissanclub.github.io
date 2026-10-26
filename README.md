# Moissan Club website

A small, self-contained Hugo site for **https://moissan.org/**. No theme download, Ruby, Node.js, Sass, or npm packages are needed. GitHub Actions builds the site using pinned Hugo **0.168.0**.

## Content and URLs

```text
content/
├── _index.md                         → /
├── projects.md                       → /projects/
└── newsletter/
    ├── _index.md                     → /newsletter/
    └── 2026-10-26-welcome/
        └── index.md                  → /newsletter/welcome/
```

- `content/_index.md` controls the homepage's headline, introduction, and body.
- `content/projects.md` is the editable Projects page.
- `content/newsletter/_index.md` introduces the automatically generated archive.
- Each newsletter issue is a **leaf page bundle**: one folder containing `index.md` and any images or downloads for that issue. Use `_index.md` only for the home or section/archive page; use `index.md` for an individual issue.
- The folder's date prefix is for your convenience. **Hugo reads the post date from front matter, not from the folder name.** Dates control the archive's newest-first order.
- The banner is the provided original image, copied to `static/images/moissan-banner.jpeg`. Its URL is `/images/moissan-banner.jpeg`.

## Add a newsletter from GitHub or any text editor

1. Copy `content/newsletter/2026-10-26-welcome/index.md` into a new folder, for example `content/newsletter/2026-11-02-robot-update/index.md`.
2. Change the title, date, description, author, and slug. Remove `example: true` and the sample body.
3. Write the communication in Markdown. For an issue-specific image, put `photo.jpg` beside `index.md` and reference it with `![Useful description](photo.jpg)`.
4. Set `draft: false` when ready. Commit to `main`, or open and merge a pull request. The workflow checks the site and publishes changes from `main`.

```yaml
---
title: "A robot update"
date: 2026-11-02T09:00:00-08:00
slug: "robot-update"
description: "What we tried and what we learned."
author: "Moissan Club"
draft: false
---

Your communication starts here.
```

This produces **https://moissan.org/newsletter/robot-update/**. Use a date at or before the actual publishing time. Drafts and future-dated posts are excluded from the production build; a future date alone does not schedule a GitHub Actions run.

You can keep drafts with `draft: true`. The included example has `example: true`, which adds a visible “Example issue” label. Remove or replace it before announcing the new site.

If you optionally use Hugo locally, a bundle archetype is included:

```sh
hugo new content --kind newsletter newsletter/robot-update
```

## Customize post URLs

The site-wide rule in `hugo.toml` is:

```toml
[permalinks.page]
  newsletter = '/newsletter/:slug/'
```

Set an explicit `slug` for every issue. Changing the title, date, or folder name then leaves its URL intact. Keep slugs unique across the newsletter section.

For a date-based structure, change the rule to:

```toml
[permalinks.page]
  newsletter = '/newsletter/:year/:month/:slug/'
```

Hugo fills the year and month from the issue's front matter date. Changing this rule changes existing issue URLs, so decide on the structure before sharing links.

To override the entire path for one issue, add:

```yaml
url: "/announcements/robot-update/"
```

`url` wins over both the permalink rule and `slug`. To preserve an old URL after a change, add its previous path:

```yaml
aliases:
  - "/newsletter/old-robot-update/"
```

Hugo generates an HTML redirect page at the alias. This is a browser redirect, not an HTTP 301. The newsletter archive, RSS, and sitemap automatically link to the new canonical URL.

## Publishing on GitHub Pages

1. In the repository's **Settings → Pages**, choose **GitHub Actions** as Source.
2. In the **MoissanClub organization → Settings → Pages**, verify `moissan.org` using GitHub's generated DNS TXT record. Keep the verification record.
3. In the repository's **Settings → Pages**, set **Custom domain** to `moissan.org` before changing the website's DNS.
4. In Namecheap **Domain List → Manage → Advanced DNS**, replace the old root website-forwarding rule and Google Sites `www` record with:

   | Type | Host | Value |
   | --- | --- | --- |
   | A | `@` | `185.199.108.153` |
   | A | `@` | `185.199.109.153` |
   | A | `@` | `185.199.110.153` |
   | A | `@` | `185.199.111.153` |
   | CNAME | `www` | `moissanclub.github.io` |

   A five-minute TTL is suitable for the cutover. Preserve your nameservers, MX, SPF, DKIM, DMARC, and Google verification records. Optional IPv6 addresses are in the linked GitHub instructions. Recheck GitHub's published addresses when making DNS changes. Configure the exact hosts above rather than pointing a wildcard to Pages.

5. After GitHub's DNS check and certificate succeed, enable **Enforce HTTPS**. DNS and HTTPS availability can take up to 24 hours. `https://www.moissan.org/` will redirect to the canonical `https://moissan.org/`.

The workflow intentionally respects `baseURL` in `hugo.toml`; it does not substitute the temporary `github.io` URL. A `CNAME` file is not required for a custom GitHub Actions deployment: set the domain in repository Pages settings. This setup does not configure GitHub settings or DNS automatically.

Pull requests run the build and link/feed checks without deployment. Pushes to `main` publish the site. Publishing a post **does not send email**: continue sending announcements through the existing Google Group. A Groups subscription URL is not configured because it has not been supplied; the site uses the published contact address instead.

RSS is available at **https://moissan.org/newsletter/index.xml**.

## Optional local preview

Editing and publishing through GitHub requires no local Hugo installation. With the same Hugo version installed, these commands are optional:

```sh
hugo server --disableFastRender
```

Open the Local URL printed by Hugo. To build exactly as CI does:

```sh
hugo --gc --minify --panicOnWarning
python3 scripts/check_site.py
```

`public/` and generated caches are ignored and should not be committed. Site templates live in `layouts/`; the stylesheet is `assets/css/main.css`. The site has no client-side JavaScript or external font dependencies.

## References

- [Hugo page bundles](https://gohugo.io/content-management/page-bundles/)
- [Hugo URL management](https://gohugo.io/content-management/urls/)
- [Hugo permalink configuration](https://gohugo.io/configuration/permalinks/)
- [Hugo deployment to GitHub Pages](https://gohugo.io/host-and-deploy/deploy-to-github-pages/)
- [GitHub custom-domain configuration](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
- [GitHub domain verification](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages)

Initial project descriptions and contact information are based on the existing [Moissan Club website](https://www.moissan.org/projects) and the linked public repositories. The sample newsletter is illustrative content, not a record of an event.
