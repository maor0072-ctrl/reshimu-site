// reshimu-lead - צד השרת של reshimu.co.il.
//
// שני מסלולים:
//   kind ריק  - טופס יצירת הקשר לייעוץ. שולח את הפנייה במייל ליעקב.
//   kind=book - בקשת ספר מעמוד הספר. שולחת את הספר לפונה **אוטומטית**,
//               ובמקביל מודיעה ליעקב מי ביקש.
//
// למה בכלל: האתר סטטי (GitHub Pages) ולכן אין לו צד שרת. הפונקציה הזאת היא
// כל צד השרת, והיא רצה על Cloudflare Workers בחינם. המייל נשלח דרך Composio
// אל חשבון הג'ימייל שכבר מחובר ל-AIOS, כך ששום שירות טפסים חיצוני לא רואה
// את הלידים.
//
// COMPOSIO_API_KEY מוזרק כסוד של ה-Worker ואינו נמצא בקוד.

const ALLOWED = [
  "https://reshimu.co.il",
  "https://www.reshimu.co.il",
  "http://127.0.0.1:8902",
];
const TO = "maor0072@gmail.com";
const FROM = "הרב יעקב מאור <maor0072@gmail.com>";
const COMPOSIO_USER = "maor0072@gmail.com";
const GMAIL_ACCOUNT = "ca_NGVDA1Vrsmz0";

const BOOK_PHONE = "https://reshimu.co.il/files/koach-haemuna-phone.pdf";
const BOOK_DESKTOP = "https://reshimu.co.il/files/koach-haemuna.pdf";
const BOOK_PAGE = "https://reshimu.co.il/book-koach-haemuna.html";
const DONATE = "https://nedar.im/7009579";

function cors(origin) {
  const allow = ALLOWED.includes(origin) ? origin : ALLOWED[0];
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
  };
}

const esc = (s) =>
  String(s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

function row(label, value) {
  if (!value) return "";
  return `<tr><td style="padding:6px 14px 6px 0;color:#4a453e;white-space:nowrap">${label}</td>` +
         `<td style="padding:6px 0;color:#1c1a17"><strong>${esc(value)}</strong></td></tr>`;
}

const b64 = (str) => {
  const bytes = new TextEncoder().encode(str);
  let bin = "";
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
  return btoa(bin);
};

// בניית ה-MIME בעצמנו, ולא דרך GMAIL_SEND_EMAIL.
// הסיבה: הכלי המובנה שולח את הגוף בלי להצהיר על קידוד, וג'ימייל מפרש אותו
// כ-ASCII - מה שהופך כל אות עברית לג'יבריש. כאן הכותרת מקודדת ב-RFC 2047
// והגוף ב-base64 עם charset=UTF-8 מפורש, ואז אין לג'ימייל מה לנחש.
function mime({ to, replyTo, subject, html }) {
  const lines = [`To: ${to}`, `From: ${encodeHeader(FROM)}`];
  if (replyTo) lines.push(`Reply-To: ${replyTo}`);
  lines.push(
    `Subject: =?UTF-8?B?${b64(subject)}?=`,
    "MIME-Version: 1.0",
    'Content-Type: text/html; charset="UTF-8"',
    "Content-Transfer-Encoding: base64",
    "",
    b64(html)
  );
  return b64(lines.join("\r\n"))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

// שם תצוגה בעברית בכותרת From חייב להיות מקודד; כתובת הדואר עצמה נשארת כמות שהיא.
function encodeHeader(v) {
  const m = /^(.*?)\s*<([^>]+)>$/.exec(v);
  if (!m) return v;
  return `=?UTF-8?B?${b64(m[1])}?= <${m[2]}>`;
}

async function sendMail(env, raw) {
  const res = await fetch(
    "https://backend.composio.dev/api/v3/tools/execute/proxy",
    {
      method: "POST",
      headers: {
        "x-api-key": env.COMPOSIO_API_KEY,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: COMPOSIO_USER,
        connected_account_id: GMAIL_ACCOUNT,
        endpoint: "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
        method: "POST",
        body: { raw },
      }),
    }
  );
  // ה-proxy מחזיר את תשובת ג'ימייל עטופה: {data, status, headers}.
  // 200 של ה-proxy עצמו לא מעיד על הצלחה - צריך לבדוק את status שבפנים.
  if (!res.ok) {
    console.log("proxy failed", res.status);
    return false;
  }
  const out = await res.json().catch(() => null);
  const ok = out && out.status >= 200 && out.status < 300;
  if (!ok) console.log("gmail rejected", JSON.stringify(out).slice(0, 400));
  return ok;
}

function bookHtml(name) {
  return (
    `<div dir="rtl" style="font-family:Arial,sans-serif;font-size:16px;line-height:1.8;color:#1c1a17">` +
    `<p>שלום ${esc(name)},</p>` +
    `<p>תודה שביקשת את הספר. הנה הוא, במתנה גמורה.</p>` +
    `<p style="margin:26px 0">` +
    `<a href="${BOOK_PHONE}" style="background:#b08434;color:#fff;text-decoration:none;` +
    `padding:13px 26px;border-radius:8px;display:inline-block;margin-left:10px;` +
    `font-weight:bold">להורדה לטלפון</a>` +
    `<a href="${BOOK_DESKTOP}" style="background:#f3ece0;color:#1c1a17;text-decoration:none;` +
    `padding:13px 26px;border-radius:8px;display:inline-block;font-weight:bold">להורדה למחשב</a>` +
    `</p>` +
    `<p style="font-size:14px;color:#4a453e">מהדורת הטלפון עומדה בעמוד קטן כדי שהאותיות ייצאו גדולות במסך. מהדורת המחשב היא בגודל A4.</p>` +
    `<p>זה ספר קליל שמלמד את העקרונות לפיהם העולם מתנהל. אל תאמין למה שכתוב &mdash; תנסה את זה בעצמך, או תבדוק את החיים שלך אחורנית, ותראה איך הכל אמת.</p>` +
    `<p>אפשר וכדאי להעביר את הקישור הלאה: <a href="${BOOK_PAGE}">${BOOK_PAGE}</a></p>` +
    `<hr style="border:0;border-top:1px solid #e5ddd0;margin:28px 0">` +
    `<p>העמותה שלי עוסקת בתמיכה במשפחות יתומים ואלמנות, בהלומי קרב, בנזקקים ובלומדי תורה. לפני החג אנחנו מבקשים מהציבור לתרום. כל שקל הולך ממש לקודש הקודשים, בלי דמי תיווך לאיש.</p>` +
    `<p><a href="${DONATE}" style="background:#b08434;color:#fff;text-decoration:none;` +
    `padding:12px 24px;border-radius:8px;display:inline-block;font-weight:bold">לתרומה לעמותה</a></p>` +
    `<p style="font-size:14px;color:#4a453e">בכרטיס אשראי או בביט, העברה חד פעמית או הוראת קבע.</p>` +
    `<p style="margin-top:28px">שנה טובה וגמר חתימה טובה, לך ולכל בני משפחתך!</p>` +
    `<p>באהבה,<br>יעקב מאור<br>0528395189</p>` +
    `</div>`
  );
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const headers = cors(origin);

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers });
    if (request.method !== "POST")
      return new Response("method not allowed", { status: 405, headers });

    let d;
    try {
      d = await request.json();
    } catch {
      return new Response("bad json", { status: 400, headers });
    }

    // מלכודת הספאם: שדה שאדם אמיתי לעולם לא רואה ולכן לא ממלא.
    // מחזירים 200 בכוונה - בוט שמקבל שגיאה מנסה שוב, בוט שמקבל אישור הולך.
    if (d.website) return new Response("ok", { status: 200, headers });

    const isBook = d.kind === "book";
    const required = isBook ? ["name", "email"] : ["name", "phone", "email", "subject"];
    for (const f of required) {
      if (!d[f] || !String(d[f]).trim())
        return new Response("missing " + f, { status: 400, headers });
    }
    const email = String(d.email).trim();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email))
      return new Response("bad email", { status: 400, headers });

    if (isBook) {
      // הספר לפונה - זה העיקר, ולכן הוא נשלח ראשון.
      const okBook = await sendMail(
        env,
        mime({
          to: email,
          subject: `הספר "כוח האמונה" - במתנה`,
          html: bookHtml(d.name),
        })
      );

      // ההודעה ליעקב. נושא קבוע ומובחן, כדי שאפשר יהיה לסנן ולתייג בג'ימייל.
      // לא נשלח ל-info@reshimu.co.il בכוונה: הכתובת מועברת חזרה לאותה תיבת
      // ג'ימייל, וג'ימייל מדכא עותק של הודעה שהוא עצמו שלח - ההתראה הייתה
      // נעלמת לתיקיית "נשלחו" בלבד.
      const notice =
        `<div dir="rtl" style="font-family:Arial,sans-serif;font-size:15px;line-height:1.7">` +
        `<h2 style="margin:0 0 14px">הספר נשלח למבקש</h2>` +
        `<table style="border-collapse:collapse">` +
        row("שם ומשפחה", d.name) +
        row("דוא\"ל", email) +
        row("טלפון", d.phone) +
        row("הספר", d.book || "כוח האמונה") +
        row("סטטוס המשלוח", okBook ? "נשלח בהצלחה" : "נכשל - צריך לשלוח ידנית") +
        `</table>` +
        `<p style="margin-top:22px;font-size:13px;color:#8a8478">` +
        `נשלח אוטומטית מעמוד הספר ב-reshimu.co.il</p></div>`;
      await sendMail(
        env,
        mime({
          to: TO,
          replyTo: email,
          subject: `הורדת הספר: ${d.name}`,
          html: notice,
        })
      );

      if (!okBook) return new Response("send failed", { status: 502, headers });
      return new Response("ok", { status: 200, headers });
    }

    const body =
      `<div dir="rtl" style="font-family:Arial,sans-serif;font-size:15px;line-height:1.7">` +
      `<h2 style="margin:0 0 14px">פנייה חדשה מהאתר</h2>` +
      `<table style="border-collapse:collapse">` +
      row("שם ומשפחה", d.name) +
      row("טלפון", d.phone) +
      row("דוא\"ל", email) +
      row("שם העסק", d.business) +
      row("תחום עיסוק", d.field) +
      row("הופנה על ידי", d.referrer) +
      `</table>` +
      `<p style="margin:18px 0 6px;color:#4a453e">נושא הפנייה:</p>` +
      `<div style="background:#f3ece0;border-right:4px solid #b08434;padding:14px 18px;` +
      `border-radius:8px;white-space:pre-wrap">${esc(d.subject)}</div>` +
      `<p style="margin-top:22px;font-size:13px;color:#8a8478">` +
      `נשלח מטופס יצירת הקשר ב-reshimu.co.il</p></div>`;

    const ok = await sendMail(
      env,
      mime({
        to: TO,
        replyTo: email,
        subject: `פנייה מהאתר: ${d.name}`,
        html: body,
      })
    );
    if (!ok) return new Response("send failed", { status: 502, headers });
    return new Response("ok", { status: 200, headers });
  },
};
