{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import re\
from datetime import datetime\
\
# ---------------------------------------------------------------------\
# Helpers\
# ---------------------------------------------------------------------\
\
def html_escape(text):\
\
    if not text:\
        return ""\
\
    return (\
        str(text)\
        .replace("&", "&amp;")\
        .replace("<", "&lt;")\
        .replace(">", "&gt;")\
    )\
\
# ---------------------------------------------------------------------\
# Market Dashboard\
# ---------------------------------------------------------------------\
\
def build_market_dashboard(market):\
\
    t = market.get("treasuries", \{\})\
\
    sofr = market.get("sofr")\
\
    spread = market.get("spread")\
\
    def val(series):\
\
        item = t.get(series)\
\
        if not item:\
            return "N/A"\
\
        return f"\{item['value']:.2f\}%"\
\
    sofr_val = (\
        f"\{sofr['value']:.2f\}%"\
        if sofr\
        else "N/A"\
    )\
\
    spread_val = (\
        f"\{spread:+.2f\}%"\
        if spread is not None\
        else "N/A"\
    )\
\
    spread_color = "#4CAF50"\
\
    if spread is not None:\
\
        if spread < -0.10:\
            spread_color = "#E53935"\
\
        elif spread < 0.15:\
            spread_color = "#FFB300"\
\
    return f"""\
    <table width="100%" cellpadding="0" cellspacing="0"\
           style="margin-top:15px;border-collapse:collapse;">\
      <tr>\
\
        \{metric_tile("2Y Treasury", val("2Y"))\}\
        \{metric_tile("5Y Treasury", val("5Y"))\}\
        \{metric_tile("10Y Treasury", val("10Y"))\}\
\
      </tr>\
\
      <tr>\
\
        \{metric_tile("30Y Treasury", val("30Y"))\}\
        \{metric_tile("SOFR", sofr_val)\}\
        \{metric_tile("2Y/10Y Spread", spread_val, spread_color)\}\
\
      </tr>\
    </table>\
    """\
\
def metric_tile(label, value, value_color="#FFFFFF"):\
\
    return f"""\
    <td width="33%"\
        style="\
            background:#13294B;\
            border:1px solid #23406C;\
            padding:16px;\
            text-align:center;\
        ">\
\
        <div style="\
            color:#8FAFD6;\
            font-size:11px;\
            text-transform:uppercase;\
            letter-spacing:1px;\
            font-family:Arial;\
        ">\
            \{label\}\
        </div>\
\
        <div style="\
            color:\{value_color\};\
            font-size:26px;\
            font-weight:bold;\
            margin-top:8px;\
            font-family:Arial;\
        ">\
            \{value\}\
        </div>\
\
    </td>\
    """\
\
# ---------------------------------------------------------------------\
# Impact Articles\
# ---------------------------------------------------------------------\
\
def build_impact_section(category_buckets, level):\
\
    impact_color = \{\
\
        "HIGH": "#C62828",\
        "MEDIUM": "#EF6C00",\
        "LOW": "#2E7D32"\
\
    \}[level]\
\
    rows = ""\
\
    for category, articles in category_buckets.items():\
\
        matching = [\
\
            a for a in articles\
            if a.get("impact") == level\
\
        ]\
\
        if not matching:\
            continue\
\
        rows += f"""\
        <tr>\
            <td style="\
                padding:12px 0;\
                font-size:18px;\
                font-weight:bold;\
                color:#13294B;\
                border-bottom:1px solid #EEEEEE;\
            ">\
                \{category\}\
            </td>\
        </tr>\
        """\
\
        for article in matching[:5]:\
\
            rows += f"""\
            <tr>\
                <td style="\
                    padding:12px 0;\
                    border-bottom:1px solid #F2F2F2;\
                ">\
\
                    <div style="\
                        font-weight:600;\
                        color:#1F3A60;\
                        font-size:14px;\
                    ">\
                        <a href="\{article['url']\}"\
                           style="\
                               color:#1F3A60;\
                               text-decoration:none;\
                           ">\
                            \{html_escape(article['title'])\}\
                        </a>\
                    </div>\
\
                    <div style="\
                        color:#888;\
                        font-size:11px;\
                        margin-top:5px;\
                    ">\
                        \{article['source']\}\
                    </div>\
\
                </td>\
            </tr>\
            """\
\
    if not rows:\
        return ""\
\
    return f"""\
    <table width="100%" cellpadding="0" cellspacing="0"\
           style="margin-top:25px;">\
\
        <tr>\
            <td style="\
                background:\{impact_color\};\
                color:white;\
                padding:12px 18px;\
                font-weight:bold;\
                font-size:16px;\
                border-radius:6px;\
            ">\
                \{level\} IMPACT DEVELOPMENTS\
            </td>\
        </tr>\
\
        \{rows\}\
\
    </table>\
    """\
\
# ---------------------------------------------------------------------\
# Action Items\
# ---------------------------------------------------------------------\
\
def build_action_panel(summary):\
\
    action_lines = []\
\
    lines = summary.splitlines()\
\
    collecting = False\
\
    for line in lines:\
\
        if "Action Items" in line:\
\
            collecting = True\
\
            continue\
\
        if collecting:\
\
            if not line.strip():\
                continue\
\
            if line.startswith("**"):\
                break\
\
            action_lines.append(line)\
\
    if not action_lines:\
\
        return ""\
\
    html = ""\
\
    for item in action_lines[:8]:\
\
        html += f"""\
        <li style="margin-bottom:8px;">\
            \{html_escape(item)\}\
        </li>\
        """\
\
    return f"""\
    <div style="\
        background:#FFF9E6;\
        border-left:5px solid #FFB300;\
        padding:20px;\
        margin-top:25px;\
    ">\
\
        <div style="\
            font-weight:bold;\
            font-size:16px;\
            color:#13294B;\
            margin-bottom:10px;\
        ">\
            Action Items For Actuaries\
        </div>\
\
        <ul>\
            \{html\}\
        </ul>\
\
    </div>\
    """\
\
# ---------------------------------------------------------------------\
# Consulting Opportunities\
# ---------------------------------------------------------------------\
\
def build_consulting_panel(opportunities):\
\
    if not opportunities:\
        return ""\
\
    rows = ""\
\
    for item in opportunities:\
\
        rows += f"""\
        <li style="margin-bottom:8px;">\
            \{html_escape(item)\}\
        </li>\
        """\
\
    return f"""\
    <div style="\
        background:#EEF7FF;\
        border-left:5px solid #1E88E5;\
        padding:20px;\
        margin-top:25px;\
    ">\
\
        <div style="\
            font-weight:bold;\
            font-size:16px;\
            color:#13294B;\
            margin-bottom:10px;\
        ">\
            Consulting Opportunities\
        </div>\
\
        <ul>\
            \{rows\}\
        </ul>\
\
    </div>\
    """\
\
# ---------------------------------------------------------------------\
# Executive Summary\
# ---------------------------------------------------------------------\
\
def format_summary(summary):\
\
    summary = html_escape(summary)\
\
    summary = re.sub(\
\
        r"\\*\\*(.*?)\\*\\*",\
\
        r"<h3 style='color:#13294B;'>\\1</h3>",\
\
        summary\
\
    )\
\
    summary = summary.replace(\
        "\\n",\
        "<br>"\
    )\
\
    return summary\
\
# ---------------------------------------------------------------------\
# Main Email Builder\
# ---------------------------------------------------------------------\
\
def build_email_html(\
    summary,\
    market,\
    category_buckets,\
    consulting_opportunities\
):\
\
    today = datetime.utcnow().strftime(\
        "%A, %B %d, %Y"\
    )\
\
    dashboard = build_market_dashboard(\
        market\
    )\
\
    high_section = build_impact_section(\
        category_buckets,\
        "HIGH"\
    )\
\
    medium_section = build_impact_section(\
        category_buckets,\
        "MEDIUM"\
    )\
\
    low_section = build_impact_section(\
        category_buckets,\
        "LOW"\
    )\
\
    summary_html = format_summary(\
        summary\
    )\
\
    action_panel = build_action_panel(\
        summary\
    )\
\
    consulting_panel = build_consulting_panel(\
        consulting_opportunities\
    )\
\
    return f"""\
<!DOCTYPE html>\
<html>\
\
<head>\
<meta charset="utf-8">\
<meta name="viewport"\
      content="width=device-width, initial-scale=1.0">\
</head>\
\
<body style="\
    margin:0;\
    padding:0;\
    background:#EDF1F5;\
    font-family:Arial, sans-serif;\
">\
\
<table width="100%"\
       cellpadding="0"\
       cellspacing="0">\
\
<tr>\
<td align="center">\
\
<table width="900"\
       cellpadding="0"\
       cellspacing="0"\
       style="\
           background:white;\
           margin-top:25px;\
           margin-bottom:25px;\
           box-shadow:0 2px 12px rgba(0,0,0,.08);\
       ">\
\
<tr>\
<td style="\
    background:#0B1F3A;\
    padding:35px;\
">\
\
<div style="\
    color:white;\
    font-size:34px;\
    font-weight:bold;\
">\
Life & Annuity Actuarial Intelligence\
</div>\
\
<div style="\
    color:#9CB7D7;\
    margin-top:10px;\
">\
Executive Daily Briefing\
</div>\
\
<div style="\
    color:#9CB7D7;\
    margin-top:5px;\
    font-size:12px;\
">\
\{today\}\
</div>\
\
\{dashboard\}\
\
</td>\
</tr>\
\
<tr>\
<td style="padding:35px;">\
\
<div style="\
    font-size:28px;\
    color:#13294B;\
    font-weight:bold;\
    margin-bottom:20px;\
">\
Executive Summary\
</div>\
\
<div style="\
    line-height:1.8;\
    color:#333;\
    font-size:14px;\
">\
\{summary_html\}\
</div>\
\
\{action_panel\}\
\
\{consulting_panel\}\
\
\{high_section\}\
\
\{medium_section\}\
\
\{low_section\}\
\
</td>\
</tr>\
\
<tr>\
<td style="\
    background:#F6F8FA;\
    padding:20px;\
    text-align:center;\
    color:#777;\
    font-size:11px;\
">\
\
Generated by Life & Annuity Intelligence Platform\
\
<br><br>\
\
Sources:\
Google News \'95 SOA \'95 AAA \'95 LIMRA \'95 ThinkAdvisor \'95\
AM Best \'95 S&P \'95 Moody's \'95 Fitch \'95 SEC EDGAR\
\
</td>\
</tr>\
\
</table>\
\
</td>\
</tr>\
\
</table>\
\
</body>\
</html>\
"""}