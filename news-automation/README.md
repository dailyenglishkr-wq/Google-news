# Daily English KR — Automated News Summary

Sends an email every Monday, Wednesday, and Friday at 8am Korea time with top 3 news articles for Finance, Cosmetics, Liquor & Wine, and Korea General — in English and Korean side by side.

## Setup (one time only)

### Step 1 — Get a Gmail App Password
1. Go to your Google account → Security
2. Turn on 2-Step Verification (if not already on)
3. Search for "App Passwords" → create one → name it "GitHub News Bot"
4. Copy the 16-character password it gives you

### Step 2 — Add secrets to GitHub
In your GitHub repository go to Settings → Secrets and variables → Actions → New repository secret. Add these 4 secrets:

| Name | Value |
|------|-------|
| ANTHROPIC_API_KEY | Your Anthropic API key |
| GMAIL_ADDRESS | Your Gmail address |
| GMAIL_APP_PASSWORD | The 16-character App Password from Step 1 |
| RECEIVER_EMAIL | The email address to send summaries to |

### Step 3 — Upload these files to GitHub
Upload everything to your repository keeping the same folder structure.

### Step 4 — Test it
Go to Actions tab in GitHub → "Industry News Summary Email" → "Run workflow" → Run it manually to confirm the email arrives.

After that it runs automatically every Mon/Wed/Fri at 8am KST. Done!
