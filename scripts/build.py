"""Build src/ from content/ and templates/. Standard library only.

    python scripts/build.py            # pages, sitemap, CV html (+ PDF when a browser is found)
    python scripts/build.py --no-pdf   # skip the PDF step

Inputs:  content/profile.json, content/strings.json,
         src/data/leetcode.json, src/data/github.json (both produced by the fetch scripts)
Outputs: src/index.html, src/uk/index.html, src/cv.html, src/uk/cv.html,
         src/cv-en.pdf, src/cv-uk.pdf, src/sitemap.xml
"""
import html
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT, TEMPLATES, SRC = ROOT / "content", ROOT / "templates", ROOT / "src"
LANGS = ["en", "uk"]
TODAY = date.today().isoformat()

# ---------------------------------------------------------------- icons
ICONS = {
    "database": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/></svg>',
    "code": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m8 8-4 4 4 4M16 8l4 4-4 4M14 4l-4 16"/></svg>',
    "building": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18M5 21V7l7-4 7 4v14M9 21v-5h6v5"/></svg>',
    "graduation": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 10 12 5 2 10l10 5 10-5zM6 12v5c0 1.7 2.7 3 6 3s6-1.3 6-3v-5"/></svg>',
    "github": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 .5C5.7.5.5 5.7.5 12c0 5.1 3.3 9.4 7.9 10.9.6.1.8-.2.8-.6v-2c-3.2.7-3.9-1.4-3.9-1.4-.5-1.3-1.3-1.7-1.3-1.7-1-.7.1-.7.1-.7 1.2.1 1.8 1.2 1.8 1.2 1 1.8 2.7 1.3 3.4 1 .1-.8.4-1.3.7-1.6-2.6-.3-5.3-1.3-5.3-5.7 0-1.3.4-2.3 1.2-3.1-.1-.3-.5-1.5.1-3.1 0 0 1-.3 3.2 1.2a11 11 0 0 1 5.8 0c2.2-1.5 3.2-1.2 3.2-1.2.6 1.6.2 2.8.1 3.1.8.8 1.2 1.8 1.2 3.1 0 4.4-2.7 5.4-5.3 5.7.4.4.8 1.1.8 2.2v3.2c0 .3.2.7.8.6 4.6-1.5 7.9-5.8 7.9-10.9C23.5 5.7 18.3.5 12 .5z"/></svg>',
    "linkedin": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6.9 8.5H3.3V21h3.6V8.5zM5.1 3a2.1 2.1 0 1 0 0 4.2 2.1 2.1 0 0 0 0-4.2zM21 13.3c0-3.6-1.9-5.2-4.5-5.2-2.1 0-3 1.1-3.5 1.9V8.5H9.4V21H13v-6.9c0-1.8.5-3 2.2-3s2.2 1.4 2.2 3V21H21v-7.7z"/></svg>',
    "leetcode": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 4 6.5 11.5a3 3 0 0 0 0 4.2l3.3 3.3a3 3 0 0 0 4.2 0L17 16M10 13h10"/></svg>',
    "gift": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 12v9H4v-9M2 7h20v5H2zM12 21V7M12 7c-2-3-6-3-6 0h6zm0 0c2-3 6-3 6 0h-6z"/></svg>',
    "image": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="m3 16 5-5 4 4 3-3 6 6"/><circle cx="16" cy="8" r="1.5"/></svg>',
    "cube": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2 3 7v10l9 5 9-5V7zM3 7l9 5 9-5M12 12v10"/></svg>',
    "lock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg>',
    "swap": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7h16M4 17h16M8 3 4 7l4 4M16 13l4 4-4 4"/></svg>',
    "snake": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6h10a3 3 0 0 1 0 6H8a3 3 0 0 0 0 6h12"/><circle cx="20" cy="18" r="1" fill="currentColor"/></svg>',
    "star": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="m12 2 3 6.6 7 .8-5.2 4.8 1.4 7L12 17.8 5.8 21.2l1.4-7L2 9.4l7-.8z"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17 17 7M8 7h9v9"/></svg>',
    "right": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M5 12h14M14 7l5 5-5 5"/></svg>',
}

# ---------------------------------------------------------------- helpers
def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def L(v, lang):
    """Pick the language variant of a bilingual value; plain values pass through."""
    if isinstance(v, dict) and lang in v:
        return v[lang]
    return v


def esc(s):
    return html.escape(str(s), quote=True)


def fmt(s, **kw):
    for k, v in kw.items():
        s = s.replace("{" + k + "}", str(v))
    return s


def chip(item):
    core = item.endswith("*")
    name = item.rstrip("*")
    return f'<span class="tag{" k" if core else ""}">{esc(name)}</span>'


def render(template, ctx):
    missing = set()

    def sub(m):
        key = m.group(1)
        if key in ctx:
            return str(ctx[key])
        missing.add(key)
        return ""
    out = re.sub(r"\{\{(\w+)\}\}", sub, template)
    if missing:
        print(f"  warning: no value for {sorted(missing)}")
    return out


def human_date(iso, lang):
    y, m, d = (int(x) for x in iso.split("-"))
    months = {
        "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
        "uk": ["січня", "лютого", "березня", "квітня", "травня", "червня", "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"],
    }[lang]
    return f"{d} {months[m - 1]} {y}"


# ---------------------------------------------------------------- page pieces
def section_list(t):
    items = [("experience", t["list_experience"]), ("skills", t["list_skills"]),
             ("projects", t["list_projects"]), ("activity", t["list_activity"]), ("contact", t["list_contact"])]
    out = []
    for i, (sid, label) in enumerate(items):
        out.append(f'<a href="#{sid}" class="res-item" style="--i:{i}"><span>{esc(label)}<span class="n">/ {i + 1:02d}</span></span>'
                   f'<span class="dots"><span></span><span></span><span></span></span><span class="arrow">{ICONS["right"]}</span></a>')
    return "\n".join(out)


def focus_cards(profile, lang):
    return "\n".join(
        f'<div class="clay info"><span class="ic-head">{ICONS[f["icon"]]}{esc(f["name"])}</span><p>{esc(L(f["text"], lang))}</p></div>'
        for f in profile["focus"])


def experience_cards(profile, lang, t):
    out = []
    for e in profile["experience"]:
        when = f'{e["from"]} – {e["to"] or t["cv_now"] if lang == "uk" else e["to"] or "now"}'
        tags = "".join(f'<span class="tag{" k" if tag in e.get("core", []) else ""}">{esc(tag)}</span>' for tag in e["tags"])
        out.append(f'''<article class="clay xp reveal">
        <div class="head"><span class="icon" aria-hidden="true">{ICONS[e["icon"]]}</span><h3>{esc(L(e["role"], lang))}</h3><span class="when">{when}</span></div>
        <div class="co">{esc(L(e["company"], lang))}</div>
        <p>{esc(L(e["text"], lang))}</p>
        <div class="tag-row">{tags}</div>
      </article>''')
    return "\n".join(out)


def skill_rows(profile, lang):
    return "\n".join(
        f'<div class="skill-row"><div class="g">{esc(L(g["group"], lang))}</div><div class="tag-row">{"".join(chip(i) for i in g["items"])}</div></div>'
        for g in profile["skills"])


def project_cards(profile, lang, gh):
    out = []
    for p in profile["projects"]:
        stars = gh.get("repos", {}).get(p["repo"], {}).get("stars", p["stars"])
        tags = "".join(chip(i) for i in p["tags"])
        out.append(f'''<a class="clay proj" href="https://github.com/{p["repo"]}" data-repo="{p["repo"]}">
        <div class="head"><span class="icon">{ICONS[p["icon"]]}</span><h3>{esc(p["name"])}</h3><span class="stars">{ICONS["star"]}<span data-field="stars">{stars}</span></span></div>
        <p>{esc(L(p["about"], lang))}</p>
        <div class="tag-row">{tags}</div>
      </a>''')
    return "\n".join(out)


def contact_links(profile):
    return "\n".join(f'<a class="cl" href="{esc(l["url"])}">{esc(l["label"])}<span class="dot">{ICONS["arrow"]}</span></a>' for l in profile["links"])


def social_buttons(profile):
    return "\n".join(f'<a href="{esc(l["url"])}" class="social-btn" aria-label="{esc(l["label"])}">{ICONS[l["icon"]]}</a>' for l in profile["links"])


def jsonld_person(profile, site):
    return json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "Person", "@id": f"{site}#person", "name": profile["name"]["en"], "alternateName": [profile["handle"], profile["name"]["uk"]],
         "url": site, "image": profile["avatar"], "jobTitle": profile["role"]["en"],
         "worksFor": {"@type": "Organization", "name": "Medical Plaza"},
         "alumniOf": {"@type": "CollegeOrUniversity", "name": "Donbas State Engineering Academy"},
         "address": {"@type": "PostalAddress", "addressLocality": "Dnipro", "addressCountry": "UA"},
         "knowsAbout": ["C#", ".NET", "ASP.NET", "WPF", "T-SQL", "MS SQL Server", "REST API"],
         "sameAs": [l["url"] for l in profile["links"]]},
        {"@type": "WebSite", "@id": f"{site}#site", "url": site, "name": profile["handle"], "author": {"@id": f"{site}#person"}, "inLanguage": ["en", "uk"]},
    ]}, ensure_ascii=False)


# ---------------------------------------------------------------- pages
def build_index(lang, profile, strings, lc, gh):
    t = strings[lang]
    site = profile["site"]
    root = "" if lang == "en" else "../"
    name = L(profile["name"], lang)
    role = L(profile["role"], lang)
    exp0 = profile["experience"][0]
    solved = lc.get("solved", {})
    langs = lc.get("languages", {})
    ctx = dict(t)
    ctx.update({
        "lang": lang, "root": root, "site": site, "repo": profile["repo"], "year": date.today().year,
        "canonical": site if lang == "en" else site + "uk/",
        "alt_href": ("uk/" if lang == "en" else "../"), "alt_lang": "uk" if lang == "en" else "en",
        "og_locale": "en_US" if lang == "en" else "uk_UA",
        "handle": profile["handle"], "name": esc(name), "avatar": profile["avatar"], "github_url": profile["links"][0]["url"],
        "eyebrow": esc(fmt(t["eyebrow"], name=name, handle=profile["handle"])),
        "headline_1": esc(profile["headline"][lang][0]), "headline_2": esc(profile["headline"][lang][1]), "headline_3": esc(profile["headline"][lang][2]),
        "intro": esc(L(profile["intro"], lang)),
        "profile_role": esc(fmt(t["profile_role"], role=L(exp0["role"], lang), company=L(exp0["company"], lang).split(",")[0])),
        "icon_database": ICONS["database"], "icon_github": ICONS["github"],
        "section_list": section_list(t), "focus_cards": focus_cards(profile, lang), "experience_cards": experience_cards(profile, lang, t),
        "social_buttons": social_buttons(profile), "skill_rows": skill_rows(profile, lang), "project_cards": project_cards(profile, lang, gh),
        "contact_links": contact_links(profile),
        "cv_href": f"{root}cv-{lang}.pdf",
        "lc_all": solved.get("all", 0), "lc_mssql": langs.get("MS SQL Server", 0), "lc_cs": langs.get("C#", 0),
        "stat_solved": esc(fmt(t["stat_solved"], easy=solved.get("easy", 0), medium=solved.get("medium", 0), hard=solved.get("hard", 0))),
        "stat_cs": esc(fmt(t["stat_cs"], mysql=langs.get("MySQL", 0))),
        "jsonld": jsonld_person(profile, site),
        "i18n_json": json.dumps({k: v for k, v in t.items()}, ensure_ascii=False),
    })
    out = render((TEMPLATES / "index.html").read_text(encoding="utf-8"), ctx)
    target = SRC / ("index.html" if lang == "en" else "uk/index.html")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(out, encoding="utf-8")
    print(f"  {target.relative_to(ROOT)}")


def build_cv(lang, profile, strings, lc, make_pdf):
    t = strings[lang]
    now_word = t["cv_now"]
    work = [e for e in profile["experience"] if e["icon"] != "graduation"]
    edu = [e for e in profile["experience"] if e["icon"] == "graduation"]

    def xp(e):
        tags = "".join(f'<span class="tag{" k" if tag in e.get("core", []) else ""}">{esc(tag)}</span>' for tag in e["tags"])
        return (f'<div class="xp"><div class="when">{e["from"]} – {e["to"] or now_word}</div><div><h3>{esc(L(e["role"], lang))}</h3>'
                f'<div class="co">{esc(L(e["company"], lang))}</div><p>{esc(L(e["text"], lang))}</p><div class="tags">{tags}</div></div></div>')

    def skill(g):
        items = ", ".join(f"<b>{esc(i[:-1])}</b>" if i.endswith("*") else esc(i) for i in g["items"])
        return f'<dt>{esc(L(g["group"], lang))}</dt><dd>{items}</dd>'

    def proj(p):
        return f'<div class="proj"><b>{esc(p["name"])}</b><span>{esc(p["language"] or "")}{" · " if p["language"] else ""}{p["stars"]} ★</span><p>{esc(L(p["about"], lang))}</p></div>'

    solved, langs = lc.get("solved", {}), lc.get("languages", {})
    ctx = dict(t, lang=lang, name=esc(L(profile["name"], lang)), role=esc(L(profile["role"], lang)), city=esc(L(profile["city"], lang)), site=profile["site"],
               cv_links="".join(f'<b>{esc(l["label"])}</b>{esc(l["url"].replace("https://", "").rstrip("/"))}<br>' for l in profile["links"]) + f'<b>Web</b>{esc(profile["site"].replace("https://", "").rstrip("/"))}',
               about_paragraphs="".join(f"<p>{esc(p)}</p>" for p in L(profile["about"], lang)),
               cv_experience_items="".join(xp(e) for e in work), cv_education_items="".join(xp(e) for e in edu),
               cv_skill_rows="".join(skill(g) for g in profile["skills"]), cv_project_items="".join(proj(p) for p in profile["projects"][:4]),
               stat_line=f'LeetCode: {solved.get("all", 0)} solved, {langs.get("MS SQL Server", 0)} in MS SQL Server')
    out = render((TEMPLATES / "cv.html").read_text(encoding="utf-8"), ctx)
    target = SRC / ("cv.html" if lang == "en" else "uk/cv.html")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(out, encoding="utf-8")
    print(f"  {target.relative_to(ROOT)}")
    if make_pdf:
        pdf = SRC / f"cv-{lang}.pdf"
        if print_pdf(target, pdf):
            print(f"  {pdf.relative_to(ROOT)}")
        else:
            print(f"  no headless browser found, {pdf.name} not produced (the workflow makes it)")


def find_browser():
    candidates = [
        "google-chrome", "chromium-browser", "chromium", "microsoft-edge",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for c in candidates:
        if Path(c).exists() or shutil.which(c):
            return c
    return None


def print_pdf(html_path, pdf_path):
    browser = find_browser()
    if not browser:
        return False
    cmd = [browser, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
           "--run-all-compositor-stages-before-draw", "--virtual-time-budget=6000",
           f"--print-to-pdf={pdf_path}", html_path.resolve().as_uri()]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=90)
        return pdf_path.exists()
    except Exception as e:
        print(f"  pdf failed: {e}")
        return False


def build_sitemap(profile):
    site = profile["site"]
    urls = [(site, TODAY, "weekly", "1.0"), (site + "uk/", TODAY, "weekly", "0.9")]
    body = "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod><changefreq>{c}</changefreq><priority>{p}</priority></url>\n" for u, d, c, p in urls)
    (SRC / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n', encoding="utf-8")
    print("  src/sitemap.xml")


def main():
    make_pdf = "--no-pdf" not in sys.argv
    profile = load(CONTENT / "profile.json")
    strings = load(CONTENT / "strings.json")
    lc = load(SRC / "data" / "leetcode.json") if (SRC / "data" / "leetcode.json").exists() else {}
    gh = load(SRC / "data" / "github.json") if (SRC / "data" / "github.json").exists() else {}
    (SRC / "data").mkdir(parents=True, exist_ok=True)
    print("build:")
    for lang in LANGS:
        build_index(lang, profile, strings, lc, gh)
    for lang in LANGS:
        build_cv(lang, profile, strings, lc, make_pdf)
    build_sitemap(profile)
    print("done")


if __name__ == "__main__":
    main()
