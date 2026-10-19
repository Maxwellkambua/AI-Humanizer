# AI Humanizer (essay mode)

Rewrites AI-drafted essays so they read like natural human writing — while
preserving every citation, quotation, and factual claim.

**Positioning:** this is a style-and-clarity editor for *your own drafts*,
not a detector-evasion tool. The verification pass is a feature, not an
afterthought.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env — set GROQ_API_KEY (free at console.groq.com) or GEMINI_API_KEY