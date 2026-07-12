import anthropic
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

INDUSTRIES = [
    "Finance and banking",
    "Cosmetics and beauty",
    "Liquor, wine and beverages",
    "Korea general news and business",
]

INDUSTRY_ICONS = {
    "Finance and banking": "💰",
    "Cosmetics and beauty": "💄",
    "Liquor, wine and beverages": "🍷",
    "Korea general news and business": "🇰🇷",
}


def get_news_summary(client, industry):
    prompt = f"""Search the web for the 3 most recent and relevant news articles about "{industry}" from the past 3 days. If nothing from past 3 days, use past week.

For each article provide:
1. A clear article title
2. A 2-3 sentence summary in natural English suitable for a business English learner
3. The same summary in natural Korean

Respond ONLY in this exact JSON format, no extra text:
{{
  "articles": [
    {{"title": "...", "english": "...", "korean": "..."}},
    {{"title": "...", "english": "...", "korean": "..."}},
    {{"title": "...", "english": "...", "korean": "..."}}
  ]
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )

    full_text = "".join(
        block.text for block in response.content if hasattr(block, "text")
    )
    clean = full_text.replace("```json", "").replace("```", "").strip()
    start = clean.index("{")
    end = clean.rindex("}") + 1
    import json
    return json.loads(clean[start:end])


def build_html_email(all_summaries):
    today = datetime.now().strftime("%B %d, %Y")
    sections = ""

    for industry, data in all_summaries.items():
        icon = INDUSTRY_ICONS.get(industry, "📰")
        articles_html = ""
        for i, article in enumerate(data.get("articles", []), 1):
            articles_html += f"""
            <div style="margin-bottom:20px; padding:16px; background:#f9f9f7; border-left:4px solid #c0392b; border-radius:4px;">
              <div style="font-size:11px; color:#c0392b; font-weight:600; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:6px;">Article {i}</div>
              <div style="font-size:15px; font-weight:600; color:#1f2a3c; margin-bottom:12px;">{article['title']}</div>
              <table style="width:100%; border-collapse:collapse;">
                <tr>
                  <td style="width:50%; padding-right:10px; vertical-align:top;">
                    <div style="font-size:11px; color:#888; font-weight:600; margin-bottom:6px; text-transform:uppercase;">English</div>
                    <div style="font-size:13px; color:#4a5468; line-height:1.6;">{article['english']}</div>
                  </td>
                  <td style="width:50%; padding-left:10px; vertical-align:top; border-left:1px solid #e2d8c2;">
                    <div style="font-size:11px; color:#888; font-weight:600; margin-bottom:6px; text-transform:uppercase;">Korean</div>
                    <div style="font-size:13px; color:#4a5468; line-height:1.6;">{article['korean']}</div>
                  </td>
                </tr>
              </table>
            </div>"""

        sections += f"""
        <div style="margin-bottom:36px;">
          <div style="font-size:18px; font-weight:700; color:#1f2a3c; margin-bottom:16px; padding-bottom:10px; border-bottom:2px solid #e2d8c2;">
            {icon} {industry}
          </div>
          {articles_html}
        </div>"""

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; background:#f0ebe0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <div style="max-width:680px; margin:0 auto; padding:24px 16px;">

    <div style="background:#1f2a3c; border-radius:8px 8px 0 0; padding:28px 32px;">
      <div style="font-size:22px; font-weight:700; color:#fffaf4; margin-bottom:4px;">Daily English KR</div>
      <div style="font-size:13px; color:#c9d2e3;">Industry News Summary · {today}</div>
    </div>

    <div style="background:#fffdf8; border-radius:0 0 8px 8px; padding:32px;">
      <div style="font-size:13px; color:#4a5468; margin-bottom:28px; padding:12px 16px; background:#f6f1e6; border-radius:4px;">
        안녕하세요! 오늘의 산업별 뉴스 요약입니다. Here are your top 3 news summaries for each industry. You can do it! 💪
      </div>

      {sections}

      <div style="border-top:1px solid #e2d8c2; padding-top:20px; margin-top:8px; text-align:center;">
        <div style="font-size:12px; color:#888;">Daily English KR · No boring grammar, just REAL English</div>
        <div style="margin-top:8px;">
          <a href="https://www.youtube.com/@DailyEnglishKR" style="font-size:12px; color:#c0392b; text-decoration:none;">YouTube 채널 보기 ▶</a>
        </div>
      </div>
    </div>
  </div>
</body>
</html>"""


def send_email(html_content):
    sender = os.environ["GMAIL_ADDRESS"]
    receiver = os.environ["RECEIVER_EMAIL"]
    password = os.environ["GMAIL_APP_PASSWORD"]

    today = datetime.now().strftime("%b %d")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📰 Daily English KR — Industry News ({today})"
    msg["From"] = f"Daily English KR <{sender}>"
    msg["To"] = receiver

    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
    print("Email sent successfully!")


def main():
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    all_summaries = {}

    for industry in INDUSTRIES:
        print(f"Fetching news for: {industry}...")
        try:
            data = get_news_summary(client, industry)
            all_summaries[industry] = data
            print(f"  Got {len(data.get('articles', []))} articles")
        except Exception as e:
            print(f"  Error for {industry}: {e}")
            all_summaries[industry] = {"articles": []}

    html = build_html_email(all_summaries)
    send_email(html)


if __name__ == "__main__":
    main()
