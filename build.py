#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build reshimu.co.il - הרב יעקב מאור, ייעוץ וספרים.

Static HTML, no framework. `pages/*.html` holds body fragments; the shared
header, nav and footer live in `_shell-head.html` / `_shell-foot.html`.

    py build/reshimu-site/build.py

LEAD_ENDPOINT is the URL the contact form POSTs to. The site is static
(GitHub Pages), so the form cannot be handled in-page - it goes to a small
Cloudflare Worker that mails the lead onward. Set it here, in one place.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = "הרב יעקב מאור"
LEAD_ENDPOINT = "https://reshimu-lead.maor0072.workers.dev/"

PAGES = {
    "index.html": ("home", f"{SITE} | ייעוץ אישי ועסקי",
                   "ייעוץ כללי בכל נושא - אישי, משפחתי ועסקי. חוכמת התורה ועקרונות "
                   "האמונה, לצד כלים מהאקדמיה וניסיון של שנים."),
    "contact.html": ("contact", f"יצירת קשר | {SITE}",
                     "שליחת בקשה לייעוץ. מלאו את הפרטים ובעז\"ה ייצרו איתכם קשר."),
    "books.html": ("books", f"הספרים | {SITE}",
                   "כוח האמונה, לחיות תומר דבורה ורק הנשמה - מהדורות אלקטרוניות "
                   "לקריאה בטלפון, ועותקים מודפסים."),
    "book-tomer-dvora.html": ("books", f"לחיות תומר דבורה | {SITE}",
                              "שלוש עשרה מידות הרחמים על פי תומר דבורה לרמ\"ק, "
                              "כדרך חיים. מהדורה אלקטרונית, 50 ש\"ח."),
    "book-koach-haemuna.html": ("books", f"כוח האמונה | {SITE}",
                                "אמונה תמימה כדרך מעשית לעבור בה ימים קשים. "
                                "מהדורה אלקטרונית, חינם."),
    "book-rak-haneshama.html": ("books", f"רק הנשמה | {SITE}",
                                "ספר קצר על נפש האדם ועל פדיון נפש. ניתן במתנה."),
}


def esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def main():
    head = (HERE / "_shell-head.html").read_text(encoding="utf-8")
    foot = (HERE / "_shell-foot.html").read_text(encoding="utf-8")
    for name, (active, title, desc) in PAGES.items():
        h = (head.replace("{{TITLE}}", esc(title)).replace("{{DESC}}", esc(desc))
                 .replace("{{LEAD_ENDPOINT}}", LEAD_ENDPOINT))
        for key in ("home", "books", "contact"):
            h = h.replace("{{NAV_%s}}" % key.upper(),
                          ' class="active"' if key == active else "")
        body = (HERE / "pages" / name).read_text(encoding="utf-8")
        (HERE / name).write_text(h + "\n" + body.rstrip() + "\n" + foot,
                                 encoding="utf-8")
        print("  " + name)
    print(f"נבנו {len(PAGES)} עמודים.")


if __name__ == "__main__":
    main()
