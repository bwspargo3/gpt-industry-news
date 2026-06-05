import re
from html import escape as html_escape
from datetime import datetime

import config
from market_data import safe_pct, safe_val

# ---------------------------------------------------------------------
# Tag badge colors
# ---------------------------------------------------------------------

TAG_COLORS = {
    "VALUATION":   "#4F46E5",
    "PRICING":     "#059669",
    "ALM":         "#0284C7",
    "REINSURANCE": "#D97706",
    "CAPITAL":     "#DC2626",
    "EXPERIENCE":  "#7C3AED",
    "REGULATORY":  "#C026D3",
    "ACCOUNTING":  "#475569",
    "CARRIER":     "#0D9488",
    "GENERAL":     "#94A3B8",
    "RESEARCH":    "#4527A0",
}

# ---------------------------------------------------------------------
# Markdown → HTML (summary body only)
# ---------------------------------------------------------------------

def format_llm_summary(text):
    lines   = text.split("\n")
    out     = []
    in_list = False

    for line in lines:
        line = re.sub(
            r"\*\*(.*?)\*\*",
            r"<strong>\1</strong>",
            line.strip()
        )

        if line.startswith("- ") or line.startswith("* "):
            if not in_list:
                out.append(
                    "<ul style='margin:8px 0 16px 0;padding-left:22px;"
                    "color:#334155;line-height:1.7;'>"
                )
                in_list = True
            out.append(f"<li style='margin-bottom:6px;'>{line[2:]}</li>")

        else:
            if in_list:
                out.append("</ul>")
                in_list = False

            if line.startswith("### "):
                h = line[4:]
                out.append(
                    f"<h3 style='color:#0F172A;font-size:15px;"
                    f"font-weight:700;margin:22px 0 8px 0;"
                    f"padding-bottom:4px;border-bottom:1px solid #E2E8F0;'>"
                    f"{h}</h3>"
                )
            elif line.startswith("## "):
                h = line[3:]
                out.append(
                    f"<h2 style='color:#0F172A;font-size:17px;"
                    f"font-weight:800;margin:28px 0 10px 0;"
                    f"padding-bottom:5px;border-bottom:2px solid #CBD5E1;'>"
                    f"{h}</h2>"
                )
            elif line:
                out.append(
                    f"<p style='margin:0 0 12px 0;color:#334155;"
                    f"line-height:1.7;font-size:14px;'>{line}</p>"
                )

    if in_list:
        out.append("</ul>")

    return "".join(out)

# ---------------------------------------------------------------------
# Market Dashboard
# ---------------------------------------------------------------------

def _tile(label, value, color="#1E293B"):
    return (
        f"<td width='33.3%' style='padding:14px 10px;"
        f"background:#FFFFFF;border:1px solid #E2E8F0;"
        f"border-radius:6px;text-align:center;"
        f"box-shadow:0 1px 3px rgba(0,0,0,.04);'>"
        f"<div style='font-size:10px;color:#64748B;font-weight:700;"
        f"text-transform:uppercase;letter-spacing:.6px;'>{label}</div>"
        f"<div style='font-size:20px;color:{color};font-weight:800;"
        f"margin-top:5px;'>{value}</div>"
        f"</td>"
    )


def _alm(label, value, color="#334155"):
    return (
        f"<td style='padding:10px 14px;text-align:center;"
        f"border-right:1px solid #E2E8F0;'>"
        f"<div style='font-size:10px;color:#64748B;font-weight:600;"
        f"text-transform:uppercase;letter-spacing:.6px;'>{label}</div>"
        f"<div style='font-size:14px;color:{color};font-weight:700;"
        f"margin-top:3px;'>{value}</div>"
        f"</td>"
    )


def build_market_dashboard(market):
    t    = market.get("treasuries", {})
    sofr = market.get("sofr")
    sprd = market.get("spread")
    add  = market.get("additional", {})

    spread_val   = (
        f"{sprd:+.2f}%" if sprd is not None else "N/A"
    )
    spread_color = (
        "#EF4444" if sprd is not None and sprd < -0.10 else
        "#F59E0B" if sprd is not None and sprd < 0.15  else
        "#10B981"
    )

    ig  = add.get("IG_OAS")         # already in bps after market_data conversion
    hy  = add.get("HY_OAS")         # already in bps
    be  = add.get("BREAKEVEN_10Y")
    vix = add.get("VIX")

    ig_val  = safe_val(ig,  "{:.0f}", " bps") if ig  else "N/A"
    hy_val  = safe_val(hy,  "{:.0f}", " bps") if hy  else "N/A"
    be_val  = safe_pct(be)
    vix_val = safe_val(vix, "{:.1f}")

    vix_color = (
        "#EF4444" if vix and vix["value"] > 25 else
        "#F59E0B" if vix and vix["value"] > 18 else
        "#10B981"
    )

    tiles = (
        f"<table width='100%' cellpadding='0' cellspacing='0'"
        f" style='border-collapse:separate;border-spacing:6px 6px;"
        f"margin-top:16px;'>"
        f"<tr>"
        f"{_tile('2Y Treasury',   safe_pct(t.get('2Y')))}"
        f"{_tile('5Y Treasury',   safe_pct(t.get('5Y')))}"
        f"{_tile('10Y Treasury',  safe_pct(t.get('10Y')))}"
        f"</tr><tr>"
        f"{_tile('30Y Treasury',  safe_pct(t.get('30Y')))}"
        f"{_tile('SOFR',          safe_pct(sofr))}"
        f"{_tile('2Y/10Y Spread', spread_val, spread_color)}"
        f"</tr></table>"
    )

    alm_bar = (
        f"<table width='100%' cellpadding='0' cellspacing='0'"
        f" style='margin-top:8px;background:#F8FAFC;"
        f"border:1px solid #E2E8F0;border-radius:6px;'>"
        f"<tr>"
        f"{_alm('IG OAS',        ig_val)}"
        f"{_alm('HY OAS',        hy_val)}"
        f"{_alm('10Y Breakeven', be_val)}"
        f"<td style='padding:10px 14px;text-align:center;'>"
        f"<div style='font-size:10px;color:#64748B;font-weight:600;"
        f"text-transform:uppercase;letter-spacing:.6px;'>VIX</div>"
        f"<div style='font-size:14px;color:{vix_color};font-weight:700;"
        f"margin-top:3px;'>{vix_val}</div>"
        f"</td>"
        f"</tr></table>"
    )

    return tiles + alm_bar

# ---------------------------------------------------------------------
# Tag Badges
# ---------------------------------------------------------------------

def build_tag_badges(tags):
    out = ""
    for tag in tags:
        color = TAG_COLORS.get(tag.upper(), "#94A3B8")
        out += (
            f"<span style='display:inline-block;background:{color}18;"
            f"color:{color};border:1px solid {color}50;font-size:9px;"
            f"font-weight:700;padding:2px 7px;margin-right:5px;"
            f"margin-bottom:4px;border-radius:10px;"
            f"text-transform:uppercase;letter-spacing:.4px;'>"
            f"{html_escape(tag)}</span>"
        )
    return out

# ---------------------------------------------------------------------
# Article Impact Sections
# ---------------------------------------------------------------------

def build_impact_section(category_buckets, level,
                          min_score=0, require_tags=None):
    color_map = {
        "HIGH":   "#DC2626",
        "MEDIUM": "#D97706",
        "LOW":    "#059669",
    }
    bar_color = color_map[level]
    rows      = ""

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

        rows += (
            f"<tr><td style='padding:20px 0 8px 0;font-size:16px;"
            f"font-weight:800;color:#0F172A;"
            f"border-bottom:2px solid #E2E8F0;'>"
            f"{html_escape(category)}</td></tr>"
        )

        for i, a in enumerate(matching[:config.MAX_ARTICLES_PER_SECTION]):
            bg       = "#FFFFFF" if i % 2 == 0 else "#F8FAFC"
            tag_html = build_tag_badges(a.get("tags", ["GENERAL"]))
            snippet  = html_escape(a.get("snippet") or "")
            title    = html_escape(a.get("title") or "No title")
            source   = html_escape(a.get("source") or "")
            date     = html_escape(a.get("date") or "")
            url      = a.get("url") or "#"

            rows += (
                f"<tr><td style='padding:16px;background:{bg};"
                f"border-bottom:1px solid #F1F5F9;border-radius:4px;'>"
                f"<div style='margin-bottom:6px;'>{tag_html}</div>"
                f"<div style='font-weight:700;font-size:14px;line-height:1.4;'>"
                f"<a href='{url}' style='color:#2563EB;text-decoration:none;'>"
                f"{title}</a></div>"
                + (
                    f"<div style='color:#475569;font-size:13px;"
                    f"margin-top:6px;line-height:1.6;'>{snippet}</div>"
                    if snippet else ""
                )
                + f"<div style='color:#94A3B8;font-size:11px;"
                f"margin-top:8px;font-weight:600;"
                f"text-transform:uppercase;letter-spacing:.4px;'>"
                f"{source}&nbsp;&bull;&nbsp;{date}</div>"
                f"</td></tr>"
            )


    if not rows:
        return ""

    return (
        f"<table width='100%' cellpadding='0' cellspacing='0'"
        f" style='margin-top:32px;'>"
        f"<tr><td style='background:{bar_color}12;color:{bar_color};"
        f"padding:12px 18px;font-weight:800;font-size:13px;"
        f"border-left:4px solid {bar_color};"
        f"border-radius:0 4px 4px 0;letter-spacing:.8px;'>"
        f"{level} IMPACT DEVELOPMENTS</td></tr>"
        f"{rows}</table>"
    )

# ---------------------------------------------------------------------
# Main Email Builder
# ---------------------------------------------------------------------

def build_email_html(market_data, category_buckets, llm_summary):
    today     = datetime.utcnow().strftime("%A, %B %d, %Y")
    dashboard = build_market_dashboard(market_data)

    high = build_impact_section(category_buckets, "HIGH")
    med  = build_impact_section(category_buckets, "MEDIUM")
    low  = build_impact_section(
        category_buckets, "LOW",
        min_score=config.LOW_IMPACT_MIN_SCORE,
        require_tags=config.LOW_IMPACT_ALLOWED_TAGS,
    )

    summary_html = format_llm_summary(llm_summary)

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>Life &amp; Annuity Intelligence</title>
</head>
<body style="margin:0;padding:24px 8px;background:#F1F5F9;
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0">
<tr><td align="center">
<table width="780" cellpadding="0" cellspacing="0"
  style="background:#FFFFFF;border-radius:10px;
  box-shadow:0 4px 20px rgba(0,0,0,.08);overflow:hidden;">

  <!-- HEADER -->
  <tr>
    <td style="background:#0F172A;padding:28px 36px;
      border-bottom:3px solid #3B82F6;">
      <div style="color:#F8FAFC;font-size:24px;font-weight:800;
        letter-spacing:-.3px;">
        Life &amp; Annuity Actuarial Intelligence
      </div>
      <div style="color:#94A3B8;font-size:12px;margin-top:5px;
        font-weight:500;letter-spacing:.4px;">
        Daily Briefing &nbsp;&bull;&nbsp; {today}
      </div>
    </td>
  </tr>

  <!-- MARKET DASHBOARD -->
  <tr>
    <td style="padding:20px 36px 24px 36px;background:#F8FAFC;
      border-bottom:1px solid #E2E8F0;">
      {dashboard}
    </td>
  </tr>

  <!-- EXECUTIVE SUMMARY -->
  <tr>
    <td style="padding:32px 36px 8px 36px;">
      <div style="font-size:20px;font-weight:800;color:#0F172A;
        margin-bottom:20px;padding-bottom:10px;
        border-bottom:2px solid #E2E8F0;">
        Today's Briefing
      </div>
      {summary_html}
    </td>
  </tr>

  <!-- ARTICLE FEED -->
  <tr>
    <td style="padding:8px 36px 36px 36px;">
      {high}
      {med}
      {low}
    </td>
  </tr>

  <!-- FOOTER -->
  <tr>
    <td style="background:#F8FAFC;border-top:1px solid #E2E8F0;
      padding:20px 36px;text-align:center;
      font-size:11px;color:#64748B;line-height:1.7;">
      Life &amp; Annuity Actuarial Intelligence &nbsp;&bull;&nbsp;
      Daily Briefing<br>
      <span style="color:#94A3B8;font-size:10px;">
        Sources: NAIC LATF &nbsp;&bull;&nbsp; SOA &nbsp;&bull;&nbsp;
        LIMRA &nbsp;&bull;&nbsp; AM Best &nbsp;&bull;&nbsp;
        The Actuary Magazine &nbsp;&bull;&nbsp; Carrier Management
        &nbsp;&bull;&nbsp; Reinsurance News &nbsp;&bull;&nbsp;
        Insurance Journal &nbsp;&bull;&nbsp; Milliman
        &nbsp;&bull;&nbsp; Federal Register &nbsp;&bull;&nbsp;
        SEC EDGAR &nbsp;&bull;&nbsp; Google News
      </span>
    </td>
  </tr>

</table>
</td></tr>
</table>
</body>
</html>"""
