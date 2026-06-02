import re
from datetime import datetime

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def html_escape(text):
    if not text:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

# ---------------------------------------------------------------------
# Market Dashboard — expanded with credit spreads, VIX, breakeven
# ---------------------------------------------------------------------

def build_market_dashboard(market):

    t          = market.get("treasuries", {})
    sofr       = market.get("sofr")
    spread     = market.get("spread")
    additional = market.get("additional", {})

    def tval(series):
        item = t.get(series)
        return f"{item['value']:.2f}%" if item else "N/A"

    def aval(key, fmt="{:.2f}", suffix=""):
        item = additional.get(key)
        if not item:
            return "N/A"
        try:
            return fmt.format(item["value"]) + suffix
        except Exception:
            return "N/A"

    sofr_val = (
        f"{sofr['value']:.2f}%"
        if sofr else "N/A"
    )

    spread_val = (
        f"{spread:+.2f}%"
        if spread is not None else "N/A"
    )

    spread_color = "#4CAF50"
    if spread is not None:
        if spread < -0.10:
            spread_color = "#E53935"
        elif spread < 0.15:
            spread_color = "#FFB300"

    # ALM indicators
    ig_val  = aval("IG_OAS",        "{:.0f}",  " bps")
    hy_val  = aval("HY_OAS",        "{:.0f}",  " bps")
    be_val  = aval("BREAKEVEN_10Y", "{:.2f}",  "%")
    vix_val = aval("VIX",           "{:.1f}",  "")

    vix_item  = additional.get("VIX")
    vix_color = "#9CB7D7"
    if vix_item:
        v = vix_item["value"]
        if v > 25:
            vix_color = "#E53935"
        elif v > 18:
            vix_color = "#FFB300"
        else:
            vix_color = "#4CAF50"

    alm_bar = f"""
    <table width="100%" cellpadding="0" cellspacing="0"
           style="margin-top:8px;border-collapse:collapse;
                  border-top:1px solid #1E3A5F;">
      <tr>
        {alm_indicator("IG OAS",         ig_val)}
        {alm_indicator("HY OAS",         hy_val)}
        {alm_indicator("10Y Breakeven",  be_val)}
        {alm_indicator("VIX",            vix_val, vix_color)}
      </tr>
    </table>
    """

    return f"""
    <table width="100%" cellpadding="0" cellspacing="0"
           style="margin-top:15px;border-collapse:collapse;">
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

def metric_tile(label, value, value_color="#FFFFFF"):
    return f"""
    <td width="33%"
        style="background:#13294B;border:1px solid #23406C;
               padding:16px;text-align:center;">
        <div style="color:#8FAFD6;font-size:11px;
                    text-transform:uppercase;letter-spacing:1px;
                    font-family:Arial;">
            {label}
        </div>
        <div style="color:{value_color};font-size:26px;
                    font-weight:bold;margin-top:8px;font-family:Arial;">
            {value}
        </div>
    </td>
    """

def alm_indicator(label, value, value_color="#9CB7D7"):
    """
    Compact single-line indicator for the ALM bar below the main tiles.
    """
    return f"""
    <td style="background:#0D2340;padding:10px 16px;text-align:center;
               border-right:1px solid #1E3A5F;">
        <span style="color:#8FAFD6;font-size:10px;
                     text-transform:uppercase;letter-spacing:1px;
                     font-family:Arial;">
            {label}&nbsp;
        </span>
        <span style="color:{value_color};font-size:14px;
                     font-weight:bold;font-family:Arial;">
            {value}
        </span>
    </td>
    """



# ---------------------------------------------------------------------
# Impact Articles — with tag badges and noise filtering
# ---------------------------------------------------------------------

TAG_COLORS = {
    "VALUATION":  "#1565C0",
    "PRICING":    "#6A1B9A",
    "ALM":        "#00695C",
    "REINSURANCE":"#4E342E",
    "CAPITAL":    "#B71C1C",
    "EXPERIENCE": "#E65100",
    "REGULATORY": "#283593",
    "ACCOUNTING": "#37474F",
    "CARRIER":    "#1B5E20",
    "GENERAL":    "#757575",
    "RESEARCH": "#4527A0",  # deep purple

}

def build_tag_badges(tags):
    html = ""
    for tag in tags:
        color = TAG_COLORS.get(tag, "#757575")
        html += f"""<span style="
            background:{color};color:white;font-size:9px;
            font-weight:bold;padding:2px 6px;border-radius:3px;
            margin-right:4px;letter-spacing:0.5px;font-family:Arial;
        ">{tag}</span>"""
    return html

def build_impact_section(
    category_buckets,
    level,
    min_score=0,
    require_tags=None,
):
    from config import (
        LOW_IMPACT_ALLOWED_TAGS,
        LOW_IMPACT_MIN_SCORE,
    )

    impact_color = {
        "HIGH":   "#C62828",
        "MEDIUM": "#EF6C00",
        "LOW":    "#2E7D32",
    }[level]

    rows = ""

    for category, articles in category_buckets.items():

        matching = [
            a for a in articles
            if a.get("impact") == level
            and a.get("score", 0) >= min_score
            and (
                require_tags is None
                or any(
                    t in a.get("tags", [])
                    for t in require_tags
                )
            )
        ]

        if not matching:
            continue

        rows += f"""
        <tr>
            <td style="padding:12px 0;font-size:18px;font-weight:bold;
                       color:#13294B;border-bottom:1px solid #EEEEEE;">
                {html_escape(category)}
            </td>
        </tr>
        """

        for article in matching[:5]:

            tags     = article.get("tags", ["GENERAL"])
            tag_html = build_tag_badges(tags)
            date_str = html_escape(article.get("date", ""))
            source   = html_escape(article.get("source", ""))

            rows += f"""
            <tr>
                <td style="padding:12px 0;border-bottom:1px solid #F2F2F2;">

                    <div style="margin-bottom:5px;">{tag_html}</div>

                    <div style="font-weight:600;color:#1F3A60;font-size:14px;">
                        <a href="{article['url']}"
                           style="color:#1F3A60;text-decoration:none;">
                            {html_escape(article['title'])}
                        </a>
                    </div>

                    <div style="color:#888;font-size:11px;margin-top:4px;">
                        {source} &nbsp;·&nbsp; {date_str}
                    </div>

                </td>
            </tr>
            """

    if not rows:
        return ""

    return f"""
    <table width="100%" cellpadding="0" cellspacing="0"
           style="margin-top:25px;">
        <tr>
            <td style="background:{impact_color};color:white;
                       padding:12px 18px;font-weight:bold;
                       font-size:16px;border-radius:6px;">
                {level} IMPACT DEVELOPMENTS
            </td>
        </tr>
        {rows}
    </table>
    """

# ---------------------------------------------------------------------
# Action Items
# ---------------------------------------------------------------------

def build_action_panel(summary):

    lines      = summary.splitlines()
    collecting = False
    items      = []

    for line in lines:
        if "Action Items for This Week" in line:
            collecting = True
            continue
        if collecting:
            if not line.strip():
                continue
            if line.startswith("**") and line.strip().endswith("**"):
                break
            items.append(line.strip())

    if not items:
        return ""

    html = ""
    for item in items[:8]:
        html += f"""
        <li style="margin-bottom:8px;">{html_escape(item)}</li>
        """

    return f"""
    <div style="background:#FFF9E6;border-left:5px solid #FFB300;
                padding:20px;margin-top:25px;">
        <div style="font-weight:bold;font-size:16px;color:#13294B;
                    margin-bottom:10px;">
            Action Items for This Week
        </div>
        <ul>{html}</ul>
    </div>
    """

# ---------------------------------------------------------------------
# Conversation Starters
# ---------------------------------------------------------------------

def build_conversation_starters(summary):

    lines      = summary.splitlines()
    collecting = False
    blocks     = []
    current    = []

    for line in lines:
        if "Conversation Starters" in line:
            collecting = True
            continue
        if collecting:
            if line.startswith("**") and line.strip().endswith("**"):
                break
            if line.strip().startswith("- TOPIC:"):
                if current:
                    blocks.append("\n".join(current))
                current = [line.strip()]
            elif current:
                current.append(line.strip())

    if current:
        blocks.append("\n".join(current))

    if not blocks:
        return ""

    cards = ""

    for block in blocks[:5]:

        topic = what = why = relevant = ""

        for line in block.splitlines():
            if line.startswith("- TOPIC:"):
                topic   = line.replace("- TOPIC:", "").strip()
            elif line.startswith("WHAT TO SAY:"):
                what    = line.replace("WHAT TO SAY:", "").strip()
            elif line.startswith("WHY NOW:"):
                why     = line.replace("WHY NOW:", "").strip()
            elif line.startswith("RELEVANT TO:"):
                relevant = line.replace("RELEVANT TO:", "").strip()

        if not topic:
            continue

        cards += f"""
        <div style="border:1px solid #D0E4F7;border-radius:6px;
                    padding:16px;margin-bottom:14px;background:#F7FBFF;">

            <div style="font-weight:bold;font-size:14px;
                        color:#0D3B6E;margin-bottom:8px;">
                💬 {html_escape(topic)}
            </div>

            <div style="font-size:13px;color:#333;
                        line-height:1.6;margin-bottom:8px;">
                {html_escape(what)}
            </div>

            <div style="font-size:11px;color:#666;margin-top:6px;">
                <strong>Why now:</strong> {html_escape(why)}
            </div>

            <div style="font-size:11px;color:#666;margin-top:3px;">
                <strong>Relevant to:</strong> {html_escape(relevant)}
            </div>

        </div>
        """

    if not cards:
        return ""

    return f"""
    <div style="margin-top:25px;border-left:5px solid #1565C0;
                background:#EEF5FF;padding:20px;">
        <div style="font-weight:bold;font-size:16px;color:#13294B;
                    margin-bottom:14px;">
            Conversation Starters for Client Calls This Week
        </div>
        {cards}
    </div>
    """

# ---------------------------------------------------------------------
# Consulting Opportunities
# ---------------------------------------------------------------------

def build_consulting_panel(opportunities):

    if not opportunities:
        return ""

    rows = ""
    for item in opportunities:
        rows += f"""
        <li style="margin-bottom:8px;">{html_escape(item)}</li>
        """

    return f"""
    <div style="background:#EEF7FF;border-left:5px solid #1E88E5;
                padding:20px;margin-top:25px;">
        <div style="font-weight:bold;font-size:16px;color:#13294B;
                    margin-bottom:10px;">
            Consulting Opportunities
        </div>
        <ul>{rows}</ul>
    </div>
    """

# ---------------------------------------------------------------------
# Executive Summary Formatter
# ---------------------------------------------------------------------

def format_summary(summary):

    # Extract only the top sections for the summary panel —
    # stop before the article-level sections begin
    stop_sections = [
        "Valuation & Reserving",
        "Regulatory Developments",
        "Accounting & LDTI",
        "Mortality & Experience",
        "Reinsurance Market",
        "Capital & Risk",
        "Annuity Market",
        "Life Product Developments",
        "Investments & ALM",
        "Carrier Intelligence",
        "SOA / AAA Research",
        "Conversation Starters",
        "Action Items",
        "Consulting Opportunities",
    ]

    lines  = summary.splitlines()
    output = []

    for line in lines:
        # Stop at the first section that belongs in article area
        if any(
            f"**{sec}" in line or f"**{sec}**" in line
            for sec in stop_sections
        ):
            break
        output.append(line)

    truncated = "\n".join(output).strip()

    # Render markdown bold as h3
    truncated = html_escape(truncated)
    truncated = re.sub(
        r"\*\*(.*?)\*\*",
        r"<h3 style='color:#13294B;margin-top:20px;'>\1</h3>",
        truncated,
    )
    truncated = truncated.replace("\n", "<br>")

    return truncated

# ---------------------------------------------------------------------
# Main Email Builder
# ---------------------------------------------------------------------

def build_email_html(
    summary,
    market,
    category_buckets,
    consulting_opportunities,
):
    from config import LOW_IMPACT_ALLOWED_TAGS, LOW_IMPACT_MIN_SCORE

    today = datetime.utcnow().strftime("%A, %B %d, %Y")

    dashboard = build_market_dashboard(market)

    high_section = build_impact_section(
        category_buckets, "HIGH",
    )

    medium_section = build_impact_section(
        category_buckets, "MEDIUM",
    )

    # LOW section: filtered — only actuarially-tagged articles
    # above the minimum score threshold
    low_section = build_impact_section(
        category_buckets, "LOW",
        min_score=LOW_IMPACT_MIN_SCORE,
        require_tags=LOW_IMPACT_ALLOWED_TAGS,
    )

    summary_html        = format_summary(summary)
    action_panel        = build_action_panel(summary)
    conversation_panel  = build_conversation_starters(summary)
    consulting_panel    = build_consulting_panel(consulting_opportunities)

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#EDF1F5;font-family:Arial,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0">
<tr><td align="center">

<table width="900" cellpadding="0" cellspacing="0"
       style="background:white;margin-top:25px;margin-bottom:25px;
              box-shadow:0 2px 12px rgba(0,0,0,.08);">

<!-- HEADER -->
<tr>
<td style="background:#0B1F3A;padding:35px;">
    <div style="color:white;font-size:34px;font-weight:bold;">
        Life &amp; Annuity Actuarial Intelligence
    </div>
    <div style="color:#9CB7D7;margin-top:6px;font-size:13px;">
        ARC | Springline &nbsp;·&nbsp; Executive Daily Briefing
    </div>
    <div style="color:#9CB7D7;margin-top:4px;font-size:12px;">
        {today}
    </div>
    {dashboard}
</td>
</tr>

<!-- EXECUTIVE SUMMARY -->
<tr>
<td style="padding:35px;">

    <div style="font-size:28px;color:#13294B;font-weight:bold;
                margin-bottom:20px;">
        Executive Summary
    </div>

    <div style="line-height:1.8;color:#333;font-size:14px;">
        {summary_html}
    </div>

    {action_panel}

    {conversation_panel}

    {consulting_panel}

    {high_section}

    {medium_section}

    {low_section}

</td>
</tr>

<!-- FOOTER -->
<tr>
<td style="background:#F6F8FA;padding:20px;text-align:center;
           color:#777;font-size:11px;">

    Generated by Life &amp; Annuity Intelligence Platform
    &nbsp;·&nbsp; ARC | Springline

    <br><br>

    Sources: Google News &nbsp;·&nbsp; NAIC LATF &nbsp;·&nbsp;
    SOA &nbsp;·&nbsp; AAA &nbsp;·&nbsp; LIMRA &nbsp;·&nbsp;
    ThinkAdvisor &nbsp;·&nbsp; AM Best &nbsp;·&nbsp;
    Federal Register &nbsp;·&nbsp; SEC EDGAR

</td>
</tr>

</table>
</td></tr>
</table>

</body>
</html>
"""
