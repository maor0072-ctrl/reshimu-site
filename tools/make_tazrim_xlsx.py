#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""בונה את התבנית להורדה: files/tazrim-mezumanim.xlsx

    py build/reshimu-site/tools/make_tazrim_xlsx.py

התבנית נבנית מכאן ולא מומרת מקובץ 2003, ומשתי סיבות. האחת מעשית: קובץ ה-XLS
הישן נושא נתוני דוגמה, שם בנק, ו-16 גיליונות שאיש אינו צריך. השנייה היא
שמאפייני המסמך של `תקציב תזרים.xls` נושאים מחבר בשם אדם שאינו יעקב, ולכן
הפצתו כקובץ להורדה היא שאלה שאין צורך לשאול - המבנה והשיטה הם פרקטיקה
פיננסית מקובלת, והקובץ כאן נכתב מאפס לפיהם.

המבנה נגזר משתי התבניות שבארכיון הייעוץ של רשימו:
`תקציב תזרים.xls` (תחזית שנתית + טבלת עזר שממירה מכירות לתקבולים לפי תנאי
תשלום), ו-`תזרים בנק אחד.XLS` (תזרים חודשי מפורט + בלוק היתרה הריאלית).
"""
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = Path(__file__).resolve().parent.parent / "files" / "tazrim-mezumanim.xlsx"

MONTHS = ["ינואר", "פברואר", "מרץ", "אפריל", "מאי", "יוני",
          "יולי", "אוגוסט", "ספטמבר", "אוקטובר", "נובמבר", "דצמבר"]

NAVY = "1F3864"
BLUE = "2E5C8A"
LIGHT = "DCE6F1"
BAND = "F2F6FB"
TOTAL = "FFF2CC"
GREY = "808080"
RED = "C00000"

F_TITLE = Font(name="Arial", size=16, bold=True, color="FFFFFF")
F_HEAD = Font(name="Arial", size=10, bold=True, color="FFFFFF")
F_SEC = Font(name="Arial", size=11, bold=True, color=NAVY)
F_BOLD = Font(name="Arial", size=10, bold=True)
F_REG = Font(name="Arial", size=10)
F_NOTE = Font(name="Arial", size=9, italic=True, color=GREY)
F_WARN = Font(name="Arial", size=10, bold=True, color=RED)

FILL_TITLE = PatternFill("solid", fgColor=NAVY)
FILL_HEAD = PatternFill("solid", fgColor=BLUE)
FILL_LIGHT = PatternFill("solid", fgColor=LIGHT)
FILL_BAND = PatternFill("solid", fgColor=BAND)
FILL_TOTAL = PatternFill("solid", fgColor=TOTAL)

THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
NUM = "#,##0;[Red]-#,##0"
PCT = "0%"

RIGHT = Alignment(horizontal="right", vertical="center")
TOPRIGHT = Alignment(horizontal="right", vertical="top", wrap_text=True)
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)

SUM_IN = "סה" + chr(34) + "כ תקבולים"
SUM_OUT = "סה" + chr(34) + "כ תשלומים"
SUM_YEAR = "סה" + chr(34) + "כ שנה"
VAT = "מע" + chr(34) + "מ, מס הכנסה וביטוח לאומי"


def band(ws, row, first_col, last_col, fill=None, font=None, numfmt=None):
    for c in range(first_col, last_col + 1):
        cell = ws.cell(row=row, column=c)
        if fill:
            cell.fill = fill
        if font:
            cell.font = font
        if numfmt and c > first_col:
            cell.number_format = numfmt
        cell.border = BOX


def banner(ws, text, last_col):
    ws.cell(row=1, column=1, value=text).font = F_TITLE
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=last_col)
    ws.cell(row=1, column=1).alignment = RIGHT
    ws.row_dimensions[1].height = 28
    for c in range(1, last_col + 1):
        ws.cell(row=1, column=c).fill = FILL_TITLE


def note_row(ws, row, last_col, text, font):
    ws.cell(row=row, column=1, value=text).font = font
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    ws.cell(row=row, column=1).alignment = TOPRIGHT


# ---------------------------------------------------------------- גיליון ב
def sheet_sales(wb):
    """ממירה מכירות חודשיות לתקבולים לפי תנאי תשלום. מחזירה את שורת הסיכום."""
    ws = wb.create_sheet("ממכירות לתקבולים")
    ws.sheet_view.rightToLeft = True
    ws.sheet_properties.tabColor = BLUE
    banner(ws, "ממכירות לתקבולים - לפי תנאי תשלום", 14)

    note_row(ws, 2, 14,
             "מכירה אינה תקבול. לקוח שקיבל חשבונית בינואר בתנאי שוטף פלוס "
             "שישים משלם במרץ, והמשכורות של ינואר אינן מחכות. כאן ממלאים את "
             "המכירות הצפויות ואת פילוח תנאי התשלום, והתקבולים נכנסים לבד "
             "לגיליון התזרים השנתי.", F_REG)
    ws.row_dimensions[2].height = 34

    ws.cell(row=4, column=1, value="תנאי התשלום של הלקוחות")
    band(ws, 4, 1, 6, FILL_LIGHT, F_SEC)
    terms = [("משלמים שוטף, באותו חודש", 0.30),
             ("משלמים שוטף + 30", 0.50),
             ("משלמים שוטף + 60", 0.20),
             ("משלמים שוטף + 90", 0.0)]
    tr0 = 5
    for i, (label, val) in enumerate(terms):
        r = tr0 + i
        ws.cell(row=r, column=1, value=label).font = F_REG
        c = ws.cell(row=r, column=2, value=val)
        c.number_format = PCT
        c.fill = FILL_LIGHT
        band(ws, r, 1, 2)
        ws.cell(row=r, column=1).alignment = RIGHT

    r_sum = tr0 + 4
    ws.cell(row=r_sum, column=1, value="סה" + chr(34) + "כ - חייב להיות 100%")
    c = ws.cell(row=r_sum, column=2, value="=SUM(B%d:B%d)" % (tr0, tr0 + 3))
    c.number_format = PCT
    band(ws, r_sum, 1, 2, FILL_TOTAL, F_BOLD)
    chk = ws.cell(row=r_sum, column=3)
    chk.value = ('=IF(ABS(B%d-1)<0.001,"תקין","שימו לב: הפילוח אינו מסתכם ל-100 אחוז")'
                 % r_sum)
    chk.font = F_WARN

    hr = 11
    ws.cell(row=hr, column=1, value="סעיף")
    for i, m in enumerate(MONTHS):
        ws.cell(row=hr, column=2 + i, value=m)
    ws.cell(row=hr, column=14, value=SUM_YEAR)
    band(ws, hr, 1, 14, FILL_HEAD, F_HEAD)
    for c in range(1, 15):
        ws.cell(row=hr, column=c).alignment = CENTER
    ws.row_dimensions[hr].height = 22

    r = hr + 1
    ws.cell(row=r, column=1, value="מכירות בשלושת החודשים שלפני השנה")
    band(ws, r, 1, 14, FILL_LIGHT, F_SEC)
    r += 1
    prev_rows = []
    for lb in ("אוקטובר שנה קודמת", "נובמבר שנה קודמת", "דצמבר שנה קודמת"):
        ws.cell(row=r, column=1, value=lb).font = F_REG
        ws.cell(row=r, column=2).fill = FILL_LIGHT
        band(ws, r, 1, 2, None, None, NUM)
        ws.cell(row=r, column=1).alignment = RIGHT
        prev_rows.append(r)
        r += 1

    r_sales = r + 1
    ws.cell(row=r_sales, column=1,
            value="מכירות צפויות בשנה, לפי חודש החשבונית")
    for i in range(12):
        ws.cell(row=r_sales, column=2 + i).fill = FILL_LIGHT
    ws.cell(row=r_sales, column=14, value="=SUM(B%d:M%d)" % (r_sales, r_sales))
    band(ws, r_sales, 1, 14, None, F_BOLD, NUM)
    ws.cell(row=r_sales, column=1).alignment = RIGHT

    r_recv = r_sales + 2
    ws.cell(row=r_recv, column=1, value="תקבולים ממכירות - מחושב")
    pct_refs = ["$B$%d" % (tr0 + i) for i in range(4)]
    oct_p, nov_p, dec_p = ["$B$%d" % x for x in prev_rows]
    back_prev = {-1: dec_p, -2: nov_p, -3: oct_p}
    for i in range(12):
        parts = []
        for back in range(4):
            idx = i - back
            src = ("%s%d" % (get_column_letter(2 + idx), r_sales)
                   if idx >= 0 else back_prev[idx])
            parts.append("%s*%s" % (src, pct_refs[back]))
        ws.cell(row=r_recv, column=2 + i, value="=" + "+".join(parts))
    ws.cell(row=r_recv, column=14, value="=SUM(B%d:M%d)" % (r_recv, r_recv))
    band(ws, r_recv, 1, 14, FILL_TOTAL, F_BOLD, NUM)
    ws.cell(row=r_recv, column=1).alignment = RIGHT

    note_row(ws, r_recv + 2, 14,
             "השורה הזאת נכנסת לבד לשורת המכירות שבגיליון התזרים השנתי, "
             "ואין צורך להעתיק אותה.", F_NOTE)

    ws.column_dimensions["A"].width = 38
    for i in range(12):
        ws.column_dimensions[get_column_letter(2 + i)].width = 11
    ws.column_dimensions["N"].width = 13
    return r_recv


# ---------------------------------------------------------------- גיליון א
def sheet_year(wb, recv_row):
    """תחזית שנתית. A=סעיף, B..M=חודשים, N=סיכום שנה."""
    ws = wb.create_sheet("תזרים שנתי")
    ws.sheet_view.rightToLeft = True
    ws.sheet_properties.tabColor = NAVY
    banner(ws, "תזרים מזומנים - תחזית שנתית", 14)

    ws["A2"] = "שם העסק:"
    ws["A2"].font = F_BOLD
    ws["C2"] = "לשנת:"
    ws["C2"].font = F_BOLD
    for ref in ("B2", "D2"):
        ws[ref].fill = FILL_LIGHT
        ws[ref].border = BOX
    ws["F2"] = ("ממלאים רק את התאים בתכלת. כל שורה שכתוב בה סיכום, "
                "עודף או יתרה מחשבת את עצמה.")
    ws["F2"].font = F_NOTE

    hr = 4
    ws.cell(row=hr, column=1, value="סעיף")
    for i, m in enumerate(MONTHS):
        ws.cell(row=hr, column=2 + i, value=m)
    ws.cell(row=hr, column=14, value=SUM_YEAR)
    band(ws, hr, 1, 14, FILL_HEAD, F_HEAD)
    for c in range(1, 15):
        ws.cell(row=hr, column=c).alignment = CENTER
    ws.row_dimensions[hr].height = 22
    ws.freeze_panes = "B5"

    r = hr + 1
    ws.cell(row=r, column=1, value="תקבולים - כסף שנכנס בפועל")
    band(ws, r, 1, 14, FILL_LIGHT, F_SEC)
    r += 1

    first_in = r
    # **„חובות מלקוחות" הוא מלכוד כפל-ספירה, ולכן השם צר במכוון:** שורת
    # המכירות מעל כבר מכניסה את מה שנגבה מהחשבוניות של שלושת החודשים שלפני
    # השנה, לפי הפילוח בגיליון הראשון. מי שירשום כאן את אותו חוב יספור אותו
    # פעמיים. השורה נועדה רק לחוב ותיק מזה, שאינו באותם שלושה חודשים.
    incomes = [("ממכירות ומשירותים", True),
               ("גביית חוב ותיק, מלפני שלושת החודשים", False),
               ("הלוואות שנתקבלו", False),
               ("השקעת בעלים", False),
               ("מכירת רכוש קבוע", False),
               ("מענקים והחזרי מיסים", False),
               ("אחר", False)]
    for label, from_sales in incomes:
        ws.cell(row=r, column=1, value=label).font = F_REG
        for i in range(12):
            cell = ws.cell(row=r, column=2 + i)
            if from_sales:
                cell.value = ("='ממכירות לתקבולים'!%s%d"
                              % (get_column_letter(2 + i), recv_row))
                cell.fill = FILL_BAND
            else:
                cell.fill = FILL_LIGHT
        ws.cell(row=r, column=14, value="=SUM(B%d:M%d)" % (r, r))
        band(ws, r, 1, 14, None, None, NUM)
        ws.cell(row=r, column=1).alignment = RIGHT
        r += 1
    last_in = r - 1

    row_tot_in = r
    ws.cell(row=r, column=1, value=SUM_IN)
    for i in range(13):
        col = get_column_letter(2 + i)
        ws.cell(row=r, column=2 + i,
                value="=SUM(%s%d:%s%d)" % (col, first_in, col, last_in))
    band(ws, r, 1, 14, FILL_TOTAL, F_BOLD, NUM)
    r += 2

    ws.cell(row=r, column=1, value="תשלומים - כסף שיוצא בפועל")
    band(ws, r, 1, 14, FILL_LIGHT, F_SEC)
    r += 1
    first_out = r
    expenses = ["קניות, חומרי גלם ומלאי",
                "שכר עבודה כולל עלויות מעביד",
                "שכירות וארנונה",
                "חשמל, מים, תקשורת ואינטרנט",
                "אחזקה, ציוד מתכלה ותוכנות",
                "שיווק ופרסום",
                "ייעוץ, הנהלת חשבונות ומשפטי",
                "ביטוחים",
                "עמלות בנק וסליקת אשראי",
                "החזרי הלוואות - קרן וריבית",
                VAT,
                "רכישת רכוש קבוע",
                "משיכות בעלים",
                "אחר"]
    for label in expenses:
        ws.cell(row=r, column=1, value=label).font = F_REG
        for i in range(12):
            ws.cell(row=r, column=2 + i).fill = FILL_LIGHT
        ws.cell(row=r, column=14, value="=SUM(B%d:M%d)" % (r, r))
        band(ws, r, 1, 14, None, None, NUM)
        ws.cell(row=r, column=1).alignment = RIGHT
        r += 1
    last_out = r - 1

    row_tot_out = r
    ws.cell(row=r, column=1, value=SUM_OUT)
    for i in range(13):
        col = get_column_letter(2 + i)
        ws.cell(row=r, column=2 + i,
                value="=SUM(%s%d:%s%d)" % (col, first_out, col, last_out))
    band(ws, r, 1, 14, FILL_TOTAL, F_BOLD, NUM)
    r += 2

    row_net = r
    ws.cell(row=r, column=1, value="עודף או חוסר בחודש")
    for i in range(13):
        col = get_column_letter(2 + i)
        ws.cell(row=r, column=2 + i,
                value="=%s%d-%s%d" % (col, row_tot_in, col, row_tot_out))
    band(ws, r, 1, 14, FILL_TOTAL, F_BOLD, NUM)
    r += 1

    row_open = r
    ws.cell(row=r, column=1, value="יתרת פתיחה בבנק")
    ws.cell(row=r, column=2).fill = FILL_LIGHT
    for i in range(1, 12):
        ws.cell(row=r, column=2 + i,
                value="=%s%d" % (get_column_letter(1 + i), r + 1))
    band(ws, r, 1, 13, None, F_REG, NUM)
    ws.cell(row=r, column=1).alignment = RIGHT
    r += 1

    ws.cell(row=r, column=1, value="יתרת סגירה בבנק")
    for i in range(12):
        col = get_column_letter(2 + i)
        ws.cell(row=r, column=2 + i,
                value="=%s%d+%s%d" % (col, row_open, col, row_net))
    band(ws, r, 1, 13, FILL_TOTAL, F_BOLD, NUM)
    r += 2

    note_row(ws, r, 14,
             "השורה שקובעת היא יתרת הסגירה: חודש אחד שלילי הוא החודש שבו "
             "ייגמר הכסף, גם אם השנה כולה מסתיימת ברווח. זה מה שתזרים נועד "
             "להראות, ודוח רווח והפסד אינו מראה.", F_WARN)
    ws.row_dimensions[r].height = 32

    ws.column_dimensions["A"].width = 34
    for i in range(12):
        ws.column_dimensions[get_column_letter(2 + i)].width = 11
    ws.column_dimensions["N"].width = 13
    return ws


# ---------------------------------------------------------------- גיליון ג
def sheet_month(wb):
    ws = wb.create_sheet("תזרים חודשי מפורט")
    ws.sheet_view.rightToLeft = True
    banner(ws, "תזרים חודשי מפורט - תנועה אחר תנועה", 8)

    for col, label, val in ((1, "חודש:", None), (3, "בנק:", None),
                            (5, "יתרת פתיחה:", 0)):
        ws.cell(row=2, column=col, value=label).font = F_BOLD
        cell = ws.cell(row=2, column=col + 1, value=val)
        cell.fill = FILL_LIGHT
        cell.border = BOX
        if val is not None:
            cell.number_format = NUM

    hr = 4
    heads = ["תאריך", "תיאור התנועה", "לקוח או מוטב", "אמצעי תשלום",
             "אסמכתא", "תשלום שיוצא", "תקבול שנכנס", "יתרה"]
    for i, h in enumerate(heads):
        ws.cell(row=hr, column=1 + i, value=h)
    band(ws, hr, 1, 8, FILL_HEAD, F_HEAD)
    for c in range(1, 9):
        ws.cell(row=hr, column=c).alignment = CENTER
    ws.row_dimensions[hr].height = 22
    ws.freeze_panes = "A5"

    first = hr + 1
    rows = 45
    for k in range(rows):
        r = first + k
        for c in range(1, 8):
            cell = ws.cell(row=r, column=c)
            cell.fill = FILL_LIGHT if k % 2 == 0 else FILL_BAND
            cell.border = BOX
            if c in (6, 7):
                cell.number_format = NUM
        # יתרה מצטברת מהפתיחה ולא שרשרת של H שמעל. **זה לא עניין של טעם:**
        # בשרשרת, הוספת שורה באמצע הטבלה משאירה את התא החדש ריק, והיתרה בכל
        # השורות שמתחתיו נשברת; מחיקת שורה מייצרת #REF. בנוסחה המצטברת אקסל
        # מרחיב את הטווחים לבד, ושורה שנוספה או נמחקה אינה שוברת דבר.
        bal = ws.cell(row=r, column=8)
        bal.value = ("=$F$2+SUM($G$%d:G%d)-SUM($F$%d:F%d)"
                     % (first, r, first, r))
        bal.number_format = NUM
        bal.border = BOX
    last = first + rows - 1

    r = last + 2
    rng = (first, last)
    for label, formula in (("יתרת פתיחה", "=$F$2"),
                           (SUM_IN, "=SUM(G%d:G%d)" % rng),
                           (SUM_OUT, "=SUM(F%d:F%d)" % rng),
                           ("יתרת סגירה",
                            "=$F$2+SUM(G%d:G%d)-SUM(F%d:F%d)" % (rng + rng))):
        ws.cell(row=r, column=2, value=label).font = F_BOLD
        c = ws.cell(row=r, column=4, value=formula)
        c.number_format = NUM
        band(ws, r, 2, 4, FILL_TOTAL if "סגירה" in label else None, F_BOLD, NUM)
        ws.cell(row=r, column=2).alignment = RIGHT
        r += 1

    r += 1
    ws.cell(row=r, column=2, value="היתרה הריאלית - לא מה שכתוב בבנק")
    band(ws, r, 2, 4, FILL_LIGHT, F_SEC)
    r += 1
    base = r
    for label in ("יתרת הבנק לפי דף החשבון",
                  "בניכוי חיובים שנרשמו וטרם נפרעו",
                  "בתוספת תקבולים שהתקבלו וטרם זוכו"):
        ws.cell(row=r, column=2, value=label).font = F_REG
        c = ws.cell(row=r, column=4, value=0)
        c.number_format = NUM
        c.fill = FILL_LIGHT
        band(ws, r, 2, 4, None, None, NUM)
        ws.cell(row=r, column=2).alignment = RIGHT
        r += 1
    ws.cell(row=r, column=2, value="היתרה הריאלית").font = F_BOLD
    c = ws.cell(row=r, column=4,
                value="=D%d-D%d+D%d" % (base, base + 1, base + 2))
    c.number_format = NUM
    band(ws, r, 2, 4, FILL_TOTAL, F_BOLD, NUM)
    r += 2

    ws.cell(row=r, column=2,
            value="זו ההבחנה שהחזיקה את רוב העסקים שעבדתי איתם: היתרה "
                  "שמופיעה בבנק אינה הכסף שיש. שיק שנתת וטרם נפרע הוא כסף "
                  "שאינו שלך, והפרש של כמה אלפים כאן הוא ההבדל בין יתרה "
                  "חיובית לחריגה.").font = F_WARN
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=8)
    ws.cell(row=r, column=2).alignment = TOPRIGHT
    ws.row_dimensions[r].height = 32

    for i, w in enumerate([11, 30, 22, 16, 14, 14, 14, 14]):
        ws.column_dimensions[get_column_letter(1 + i)].width = w
    return ws


# ---------------------------------------------------------------- גיליון ד
def sheet_help(wb):
    ws = wb.create_sheet("איך משתמשים")
    ws.sheet_view.rightToLeft = True
    ws.sheet_properties.tabColor = RED
    banner(ws, "תזרים מזומנים - תבנית לעסק קטן", 6)

    blocks = [
        ("סדר העבודה, ואין לדלג עליו", None),
        ("1. ממכירות לתקבולים",
         "ממלאים את פילוח תנאי התשלום של הלקוחות, את המכירות של שלושת "
         "החודשים שלפני השנה, ואת המכירות הצפויות בכל חודש. התקבולים "
         "מחושבים לבד."),
        ("2. תזרים שנתי",
         "ממלאים יתרת פתיחה בבנק בינואר, ואת שאר התקבולים והתשלומים "
         "הצפויים. שורת המכירות מגיעה לבד מהגיליון הקודם ואין לדרוס אותה."),
        ("3. תזרים חודשי מפורט",
         "אחרי שהחודש התחיל רושמים בו תנועה אחר תנועה ומשווים לתחזית. זה "
         "הגיליון שאומר אם התחזית הייתה נכונה, וממנו לומדים לתחזית הבאה."),
        ("שלוש אמירות שהתבנית בנויה עליהן", None),
        ("רווח אינו מזומן",
         "אפשר להיות רווחי על הנייר ולא להצליח לשלם משכורות, כי הלקוחות "
         "משלמים בשוטף פלוס תשעים והספקים אינם מחכים. זו הסיבה שעסקים "
         "רווחיים נסגרים, וזו הסיבה שצריך תזרים ולא רק דוח רווח והפסד."),
        ("מכירה אינה תקבול",
         "חשבונית שיצאה בינואר בתנאי שוטף פלוס שישים היא כסף שנכנס במרץ. "
         "הגיליון הראשון קיים בדיוק בשביל הפער הזה, והוא הפער שרוב "
         "התחזיות מדלגות עליו."),
        ("היתרה בבנק אינה הכסף שיש",
         "שיק שנתת וטרם נפרע הוא כסף שאינו שלך, ותקבול שהופקד וטרם זוכה "
         "אינו זמין. בלוק היתרה הריאלית שבגיליון החודשי מחשב את זה, "
         "וההפרש הוא ההבדל בין יתרה חיובית לחריגה."),
        ("מה למלא ומה לא", None),
        ("תאים בתכלת", "אלה תאי קלט, ורק אותם ממלאים."),
        ("תאים בצהוב", "מחושבים. אין לכתוב בהם, אחרת הנוסחה נמחקת."),
        ("הוספת שורת סעיף",
         "אפשר להוסיף שורות באמצע הטבלה, לא בסופה, כדי שנוסחאות הסיכום "
         "ייכללו אותן מעצמן."),
        ("שורה חדשה בתזרים החודשי",
         "בשורה שנוספה עמודת היתרה נשארת ריקה, כי אקסל אינו מעתיק נוסחה "
         "לשורה חדשה. גוררים את תא היתרה מהשורה שמעל אל השורה החדשה והכול "
         "חוזר למקומו. שאר השורות והסיכומים נשארים נכונים גם בלי זה."),
        ("לא לספור חוב פעמיים",
         "שורת המכירות בתזרים השנתי כבר מכניסה את מה שייגבה מהחשבוניות של "
         "שלושת החודשים שלפני השנה. שורת גביית החוב הוותיק נועדה רק לחוב "
         "מלפני כן, ולא לאותם חודשים."),
    ]
    r = 3
    for title, body in blocks:
        if body is None:
            ws.cell(row=r, column=1, value=title).font = F_SEC
            band(ws, r, 1, 6, FILL_LIGHT, F_SEC)
            r += 1
            continue
        ws.cell(row=r, column=1, value=title).font = F_BOLD
        ws.cell(row=r, column=1).alignment = TOPRIGHT
        c = ws.cell(row=r, column=2, value=body)
        c.font = F_REG
        c.alignment = TOPRIGHT
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
        ws.row_dimensions[r].height = 48
        r += 1

    r += 1
    note_row(ws, r, 6,
             "התבנית חופשית לשימוש. מי שרוצה שנעבור על המספרים שלו יחד, "
             "או שצריך גם תוכנית עסקית - הרב יעקב מאור, רשימו, "
             "reshimu.co.il, 052-8395189.",
             Font(name="Arial", size=10, bold=True, color=NAVY))
    ws.row_dimensions[r].height = 30

    ws.column_dimensions["A"].width = 30
    for col in "BCDEF":
        ws.column_dimensions[col].width = 18
    return ws


def main():
    wb = Workbook()
    wb.remove(wb.active)
    sheet_help(wb)
    recv_row = sheet_sales(wb)
    sheet_year(wb, recv_row)
    sheet_month(wb)
    wb.properties.title = "תזרים מזומנים - תבנית לעסק קטן"
    wb.properties.creator = "הרב יעקב מאור, רשימו - reshimu.co.il"
    wb.properties.lastModifiedBy = "רשימו"
    wb.properties.description = (
        "תבנית תזרים מזומנים לעסק קטן: תחזית שנתית, המרת מכירות לתקבולים "
        "לפי תנאי תשלום, ותזרים חודשי מפורט עם חישוב היתרה הריאלית.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    print("נכתב:", OUT, OUT.stat().st_size, "bytes")
    print("גיליונות:", [s.title for s in wb.worksheets])


if __name__ == "__main__":
    main()
