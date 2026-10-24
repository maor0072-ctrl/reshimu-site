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
                   "ייעוץ אישי, משפחתי ועסקי, ותשתיות בינה מלאכותית לעסק. חוכמת התורה "
                   "ועקרונות האמונה לצד כלים מהאקדמיה וניסיון משנת 2001."),
    "contact.html": ("contact", f"יצירת קשר | {SITE}",
                     "יצירת קשר לייעוץ אישי ועסקי או לייעוץ בינה מלאכותית לעסק. "
                     "משאירים פרטים ובעז\"ה חוזרים אליכם."),
    "ai.html": ("ai", f"בינה מלאכותית | {SITE}",
                "מערכות בינה מלאכותית שנבנו ועובדות בפועל - מסך הכיתה, אתרים, "
                "מרכז פיקוד מהטלפון - ושיעור על בינה מלאכותית שמועבר דרך המערכת עצמה."),
    "ai-asakim.html": ("ai", f"בינה מלאכותית לעסקים קטנים - ייעוץ ואוטומציות | {SITE}",
                       "איפה בינה מלאכותית באמת חוסכת זמן וכסף בעסק קטן, מה זה אוטומציות "
                       "לעסקים, מה זה סוכן AI, ומאיפה מתחילים בלי לשרוף תקציב."),
    "ai-horaa.html": ("ai", f"בינה מלאכותית למורים - כלים, כללים ושימוש בכיתה | {SITE}",
                      "מה באמת חוסך זמן למורה בהכנת שיעור, מה מותר ומה אסור להכניס לכלי "
                      "בינה מלאכותית לפי כללי משרד החינוך, ואיך נראית מערכת שנבנתה לכיתה."),
    "kita.html": ("ai", f"מסך הכיתה | {SITE}",
                  "המורה או המרצה שולט מהטלפון במסך הגדול בחדר, בלי התקנה ובלי כבל, "
                  "ופניו אל הכיתה כל הזמן."),
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
                                "מדריך מעשי בהלכות אבלות ובהבנת סוד הנשמה. מהדורה אלקטרונית, בקרוב."),
    "terms.html": ("", f"תקנון ותנאי שימוש | {SITE}",
                    "תנאי השימוש באתר ובמהדורות האלקטרוניות של הספרים."),
    "privacy.html": ("", f"מדיניות פרטיות | {SITE}",
                      "אילו פרטים נאספים באתר, מה נעשה בהם, והזכויות שלך."),
    "refund.html": ("", f"ביטולים והחזרות | {SITE}",
                     "החזר כספי מלא תוך 14 יום, בלי צורך בנימוק."),
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
        for key in ("home", "ai", "books", "contact"):
            h = h.replace("{{NAV_%s}}" % key.upper(),
                          ' class="active"' if key == active else "")
        body = (HERE / "pages" / name).read_text(encoding="utf-8")
        (HERE / name).write_text(h + "\n" + body.rstrip() + "\n" + foot,
                                 encoding="utf-8")
        print("  " + name)
    print(f"נבנו {len(PAGES)} עמודים.")


if __name__ == "__main__":
    main()
