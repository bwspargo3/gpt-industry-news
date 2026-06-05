import re
from html import escape as html_escape
from datetime import datetime
import config

# ---------------------------------------------------------------------
# UI Configurations & Tag Colors
# ---------------------------------------------------------------------

TAG_COLORS = {
    "VALUATION": "#4F46E5",   # Indigo
    "PRICING": "#059669",     # Emerald
    "ALM": "#0284C7",         # Light Blue
    "REINSURANCE": "#D97706", # Amber
    "CAPITAL": "#DC2626",     # Red
    "EXPERIENCE": "#7C3AED",  # Violet
    "REGULATORY": "#C026D3",  # Fuchsia
    "ACCOUNTING": "#475569",  # Slate
    "CARRIER": "#0D9488",     # Teal
    "GENERAL": "#94A3B8"      # Light Slate
}

# ---------------------------------------------------------------------
# Helpers & Markdown Parser
# ---------------------------------------------------------------------

def format_llm_summary(llm_summary):
    """
    Parses basic Markdown (headers, bold text, bulleted lists) generated 
    by the LLM and converts it into clean, inline-styled HTML.
    """
    lines = llm_summary.split('\n')
    formatted_lines = []
    in_list = False

    for line in lines:
        # Bold text translation via Regex
        line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line.strip())

        # List item detection
        if line.startswith("- ") or line.startswith("* "):
            if not in_list:
                formatted_lines.append("<ul style='margin-top: 8px; margin-bottom: 16px; padding-left: 24px; color: #334155; line-height: 1.6;'>")
                in_list = True
            formatted_lines.append(f"<li style='margin-bottom: 8px;'>{line[2:]}</li>")
        else:
            if in_list:
                formatted_lines.append("</ul>")
                in_list = False
            
            # Header detection
            if line.startswith("###"):
                header_text = line.replace('#', '').strip()
                formatted_lines.append(f"<h3 style='color:#0F172A; margin-top:24px; margin-bottom:10px; font-size:16px; border-bottom: 1px solid #E2E8F0; padding-bottom: 6px;'>{header_text}</h3>")
            elif line.startswith("##"):
                header_text = line.replace('#', '').strip()
                formatted_lines.append(f"<h2 style='color:#0F172A; margin-top:28px; margin-bottom:12px; font-size:18px; border-bottom: 2px solid #CBD5E1; padding-bottom: 6px;'>{header_text}</h2>")
            elif line:
                formatted_lines.append(f"<p style='margin-top:0; margin-bottom:14px; color: #334155; line-height: 1.6;'>{line}</p>")

    if in_list:
        formatted_lines.append("</ul>")

    return "".join(formatted_lines)

# ---------------------------------------------------------------------
# Market Dashboard Components
# ---------------------------------------------------------------------

def metric_tile(label, val, color="#1E293B"):
    return f"""
    <td width="33.3%" style="padding:16px 12px; background-color:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; box-shadow:0 1px 3px rgba(0,0,0,0.05); text-align:center;">
        <div style="font-size:11px; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">{label}</div>
        <div style="font-size:22px; color:{color}; font-weight:800; margin-top:6px;">{val}</div>
    </td>
    """

def alm_indicator(label, val, color="#1E293B"):
    return f"""
    <td width="25%" style="padding:12px 10px; border-right:1px solid #E2E8F0; text-align:center;">
        <div style="font-size:11px; color:#64748B; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">{label}</div>
        <div style="font-size:15px; color:{color}; font-weight:700; margin-top:4px;">{val}</div>
    </td>
    """

def build_market_dashboard(market):
    t          = market.get("treasuries", {})
    sofr       = market.get("sofr")
    spread     = market.get("spread")
    additional = market.get("additional", {})
    macro      = market.get("macro", {})

    def tval(series):
        item = t.get(series)
        return f"{item['value']:.2f}%" if item else "N/A"

    def aval_bps(key):
        item = additional.get(key)
        if not item:
            return "N/A"
        return f"{item['value'] * 100:.0f} bps"

    def aval_pct(key, fmt="{:.2f}%"):
        item = additional.get(key)
        return fmt.format(item["value"]) if item else "N/A"

    sofr_val = f"{sofr['value']:.2f}%" if sofr else "N/A"
    spread_val = f"{spread:+.2f}%" if spread is not None else "N/A"

    # Color-coded inversion risk alert thresholds
    spread_color = "#10B981" # Green
    if spread is not None:
        if spread < -0.10:
            spread_color = "#EF4444" # Red
        elif spread < 0.15:
            spread_color = "#F59E0B" # Amber

    # Dynamic styling for equity volatility/asset matching proxies (VIX)
    vix_item = additional.get("VIX")
    vix_color = "#1E293B"
    if vix_item:
        v = vix_item["value"]
        if v > 25:
            vix_color = "#EF4444"
        elif v > 18:
            vix_color = "#F59E0B"
        else:
            vix_color = "#10B981"

    # Macro Assumption Evaluation
    def mval(key, fmt="{:.2f}%"):
        item = macro.get(key)
        return fmt.format(item["value"]) if item else "N/A"

    alm_bar = f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:16px; background-color:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; overflow:hidden;">
      <tr>
        {alm_indicator("IG OAS",         aval_bps("IG_OAS"))}
        {alm_indicator("HY OAS",         aval_bps("HY_OAS"))}
        {alm_indicator("10Y Breakeven",  aval_pct("BREAKEVEN_10Y"))}
        <td width="25%" style="padding:12px 10px; text-align:center;">
            <div style="font-size:11px; color:#64748B; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">VIX</div>
            <div style="font-size:15px; color:{vix_color}; font-weight:700; margin-top:4px;">{aval_pct("VIX", "{:.1f}")}</div>
        </td>
      </tr>
      <tr style="border-top:1px solid #E2E8F0;">
        {alm_indicator("Unemployment", mval("unemployment"))}
        {alm_indicator("30Y Mortgage", mval("mortgage_30y"))}
        <td width="25%" style="border-right:1px solid #E2E8F0;"></td>
        <td width="25%"></td>
      </tr>
    </table>
    """

    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:20px; border-collapse:separate; border-spacing:8px 8px;">
      <tr>
        {metric_tile("2Y Treasury",   tval("2Y"))}
        {metric_tile("5Y Treasury",   tval("5Y"))}
        {metric_tile("10Y Treasury",  tval("10Y"))}
      </tr>
      <tr>
        {metric_tile("30Y Treasury",  tval("30Y"))}
        {metric_tile("SOFR",          sofr_val)}
        {metric_tile("2Y/10Y Spread", spread_val, spread_color)}
      </tr>
    </table>
    {alm_bar}
    """

# ---------------------------------------------------------------------
# News Feed Components
# ---------------------------------------------------------------------

def build_tag_badges(tags):
    badges = ""
    for tag in tags:
        color = TAG_COLORS.get(tag.upper(), "#94A3B8")
        badges += f"""
        <span style="display:inline-block; background-color:{color}15; color:{color}; 
                     border: 1px solid {color}40; font-size:10px; font-weight:700; 
                     padding:2px 8px; margin-right:6px; margin-bottom:6px;
                     border-radius:12px; text-transform:uppercase; letter-spacing:0.5px;">
            {html_escape(tag)}
        </span>
        """
    return badges

def build_impact_section(category_buckets, level, min_score=0, require_tags=None):
    impact_color = {
        "HIGH":   "#DC2626", # Deep Red
        "MEDIUM": "#D97706", # Amber
        "LOW":    "#059669", # Emerald
    }[level]

    rows = ""

    for category, articles in category_buckets.items():
        matching = [
            a for a in articles
            if a.get("impact") == level
            and a.get("score", 0) >= min_score
            and (
                require_tags is None
                or any(t in a.get("tags", []) for t in require_tags)
            )
        ]

        if not matching:
            continue

        rows += f"""
        <tr>
            <td style="padding:24px 0 12px 0; font-size:18px; font-weight:800; color:#0F172A; border-bottom:2px solid #E2E8F0;">
                {html_escape(category)}
            </td>
        </tr>
        """

        for idx, article in enumerate(matching[:config.MAX_ARTICLES_PER_SECTION]):
            tags     = article.get("tags", ["GENERAL"])
            tag_html = build_tag_badges(tags)
            date_str = html_escape(article.get("date", ""))
            source   = html_escape(article.get("source", ""))
            snippet  = html_escape(article.get("snippet", ""))
            
            # Add a faint alternating background color for better visual separation
            bg_color = "#FFFFFF" if idx % 2 == 0 else "#F8FAFC"

            rows += f"""
            <tr>
                <td style="padding:20px 16px; background-color:{bg_color}; border-bottom:1px solid #F1F5F9; border-radius:6px;">
                    <div style="margin-bottom:8px;">{tag_html}</div>
                    <div style="font-weight:700; color:#1E293B; font-size:15px; line-height:1.4;">
                        <a href="{article['url']}" style="color:#2563EB; text-decoration:none;">
                            {html_escape(article['title'])}
                        </a>
                    </div>
                    <div style="color:#475569; font-size:13px; margin-top:8px; line-height:1.6;">
                        {snippet}
                    </div>
                    <div style="color:#94A3B8; font-size:11px; margin-top:10px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">
                        {source} &nbsp;&bull;&nbsp; {date_str}
                    </div>
                </td>
            </tr>
            """

    if not rows:
        return ""

    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:40px;">
        <tr>
            <td style="background-color:{impact_color}10; color:{impact_color}; padding:14px 20px; font-weight:800; font-size:15px; border-left:4px solid {impact_color}; border-radius:0 6px 6px 0; letter-spacing:1px;">
                {level} IMPACT DEVELOPMENTS
            </td>
        </tr>
        {rows}
    </table>
    """

# ---------------------------------------------------------------------
# Main Execution / Assembly
# ---------------------------------------------------------------------

def build_email_html(market_data, category_buckets, llm_summary):
    dashboard_html = build_market_dashboard(market_data)
    
    high_impact = build_impact_section(category_buckets, "HIGH")
    med_impact  = build_impact_section(category_buckets, "MEDIUM")
    low_impact  = build_impact_section(
        category_buckets, "LOW", 
        min_score=config.LOW_IMPACT_MIN_SCORE, 
        require_tags=config.LOW_IMPACT_ALLOWED_TAGS
    )

    formatted_summary = format_llm_summary(llm_summary)

    today = datetime.utcnow().strftime("%A, %B %d, %Y")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Actuarial Intelligence Briefing</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin:0; padding:30px 10px; background-color:#F1F5F9; color:#0F172A;">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width:760px; margin:0 auto; background-color:#FFFFFF; border-radius:12px; box-shadow:0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05); border-collapse:collapse; overflow:hidden;">
            
            <tr>
                <td style="background-color:#0F172A; padding:32px 40px; text-align:left; border-bottom:4px solid #3B82F6;">
                    <h1 style="color:#F8FAFC; margin:0; font-size:26px; font-weight:800; letter-spacing:-0.5px;">Actuarial Intelligence Briefing</h1>
                    <p style="color:#94A3B8; margin:8px 0 0 0; font-size:14px; font-weight:500; letter-spacing:0.5px;">ARC | Springline &nbsp;&bull;&nbsp; {today}</p>
                </td>
            </tr>
            
            <tr>
                <td style="padding:10px 32px 24px 32px; background-color:#F8FAFC; border-bottom:1px solid #E2E8F0;">
                    {dashboard_html}
                </td>
            </tr>
            
            <tr>
                <td style="padding:32px 40px;">
                    {formatted_summary}
                </td>
            </tr>
            
            <tr>
                <td style="padding:0 40px 40px 40px;">
                    {high_impact}
                    {med_impact}
                    {low_impact}
                </td>
            </tr>
            
            <tr>
                <td style="background-color:#F8FAFC; border-top:1px solid #E2E8F0; padding:24px 40px; text-align:center; font-size:12px; color:#64748B; font-weight:500; line-height:1.6;">
                    <strong>Actuarial Resources Corporation</strong> &nbsp;&bull;&nbsp; Internal Consulting Briefing Pipeline<br>
                    <span style="font-size:11px; color:#94A3B8;">Sources: Google News, NAIC LATF, SOA, AAA, LIMRA, ThinkAdvisor, AM Best, SEC EDGAR</span>
                </td>
            </tr>
            
        </table>
    </body>
    </html>
    """
