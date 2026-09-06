// reshimu-lead - מקבל פניות מטופס יצירת הקשר של reshimu.co.il ושולח אותן במייל.
//
// למה בכלל: האתר סטטי (GitHub Pages) ולכן אין לו צד שרת שיטפל בטופס.
// הפונקציה הזאת היא כל צד השרת, והיא רצה על Cloudflare Workers בחינם.
// המייל נשלח דרך Composio אל חשבון הג'ימייל שכבר מחובר ל-AIOS, כך ששום
// שירות טפסים חיצוני לא רואה את הלידים.
//
// COMPOSIO_API_KEY מוזרק כסוד של ה-Worker ואינו נמצא בקוד.

const ALLOWED = [
  "https://reshimu.co.il",
  "https://www.reshimu.co.il",
  "http://127.0.0.1:8902",
];
const TO = "maor0072@gmail.com";
const COMPOSIO_USER = "maor0072@gmail.com";
const GMAIL_ACCOUNT = "ca_NGVDA1Vrsmz0";

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

    for (const f of ["name", "phone", "email", "subject"]) {
      if (!d[f] || !String(d[f]).trim())
        return new Response("missing " + f, { status: 400, headers });
    }
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(String(d.email).trim()))
      return new Response("bad email", { status: 400, headers });

    const body =
      `<div dir="rtl" style="font-family:Arial,sans-serif;font-size:15px;line-height:1.7">` +
      `<h2 style="margin:0 0 14px">פנייה חדשה מהאתר</h2>` +
      `<table style="border-collapse:collapse">` +
      row("שם ומשפחה", d.name) +
      row("טלפון", d.phone) +
      row("דוא\"ל", d.email) +
      row("שם העסק", d.business) +
      row("תחום עיסוק", d.field) +
      row("הופנה על ידי", d.referrer) +
      `</table>` +
      `<p style="margin:18px 0 6px;color:#4a453e">נושא הפנייה:</p>` +
      `<div style="background:#f3ece0;border-right:4px solid #b08434;padding:14px 18px;` +
      `border-radius:8px;white-space:pre-wrap">${esc(d.subject)}</div>` +
      `<p style="margin-top:22px;font-size:13px;color:#8a8478">` +
      `נשלח מטופס יצירת הקשר ב-reshimu.co.il</p></div>`;

    // בניית ה-MIME בעצמנו, ולא דרך GMAIL_SEND_EMAIL.
    // הסיבה: הכלי המובנה שולח את הגוף בלי להצהיר על קידוד, וג'ימייל מפרש
    // אותו כ-ASCII - מה שהופך כל אות עברית לג'יבריש. כאן הכותרת מקודדת
    // ב-RFC 2047 והגוף ב-base64 עם charset=UTF-8 מפורש, ואז אין לג'ימייל
    // מה לנחש.
    const b64 = (str) => {
      const bytes = new TextEncoder().encode(str);
      let bin = "";
      for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
      return btoa(bin);
    };
    const subject = `פנייה מהאתר: ${d.name}`;
    const mime = [
      `To: ${TO}`,
      `Reply-To: ${String(d.email).trim()}`,
      `Subject: =?UTF-8?B?${b64(subject)}?=`,
      "MIME-Version: 1.0",
      'Content-Type: text/html; charset="UTF-8"',
      "Content-Transfer-Encoding: base64",
      "",
      b64(body),
    ].join("\r\n");
    const raw = b64(mime).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

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
    let ok = res.ok;
    if (ok) {
      const out = await res.json().catch(() => null);
      ok = out && out.status >= 200 && out.status < 300;
      if (!ok) console.log("gmail rejected", JSON.stringify(out).slice(0, 400));
    }
    if (!ok) {
      console.log("send failed", res.status);
      return new Response("send failed", { status: 502, headers });
    }
    return new Response("ok", { status: 200, headers });
  },
};
