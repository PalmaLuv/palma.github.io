## Alexander Kolyasa — portfolio

[![uk-UA](https://img.shields.io/badge/lang-uk--UA-blue)](README.uk-UA.md)

**Live:** [palmaluv.github.io/palma.github.io](https://palmaluv.github.io/palma.github.io/) · Ukrainian: [/uk/](https://palmaluv.github.io/palma.github.io/uk/)

Portfolio of a .NET and T-SQL developer. One JSON file describes the person; a small Python script turns it into the site in two languages and a CV in HTML and PDF. Plain HTML, CSS and JavaScript on the page; no framework, no npm.

![Screenshot](./.github/img/image.png)

### What is on the page

- **Command palette.** `Ctrl K` jumps to sections, opens links, switches the theme or language, downloads the CV.
- **Activity calendars.** LeetCode submissions and GitHub contributions by day, GitHub style, one card each, refreshed nightly.
- **CV.** Generated from the same data as the page, English and Ukrainian, as HTML and PDF.
- **English and Ukrainian.** Two static pages with `hreflang`, not a client-side switch.
- **404.** Snake, in JavaScript, after the C++ repository.

### Layout

```
content/
  profile.json         the person: name, roles, experience, skills, projects, in en and uk
  strings.json         every UI string, in en and uk
templates/             index.html, cv.html
scripts/
  build.py             content + templates + data -> src/ (standard library only)
  fetch-leetcode.py    LeetCode GraphQL -> src/data/leetcode.json
  fetch-github.py      GitHub GraphQL (or the public contributions page) -> src/data/github.json
src/                   the built site, published as-is to GitHub Pages
  index.html, uk/, cv.html, uk/cv.html, 404.html
  css/main.css, js/site.js, data/
drafts/                earlier design directions, not deployed
.github/workflows/refresh-and-deploy.yml
```

### Editing

Change `content/*.json`, then rebuild:

```
python scripts/build.py
```

The PDF step looks for Chrome or Edge and skips itself when neither is installed; the workflow always produces it. Preview with the bundled server, which serves `404.html` for missing paths the way GitHub Pages does:

```
python scripts/serve.py
```

### How it updates itself

The workflow runs nightly, on every push to `main` and on demand. It pulls both calendars, rebuilds the site, commits `src/` when the numbers changed, and publishes `src/` to the `gh-pages` branch that GitHub Pages serves. LeetCode does not allow browser requests from other sites, which is why the calendars are fetched server-side and shipped as JSON.

### Design

Composition follows a minimal editorial hero: one large headline with inline elements, a pill header, a hairline section list and a few cards. Dark theme by default with a light toggle; the choice is remembered. Fonts: Manrope and JetBrains Mono.
