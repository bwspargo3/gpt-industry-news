from html import escape as html_escape
import config

def metric_tile(label, val, color="#1F3A60"):
    return f"""
    <td width="33.3%" style="padding:12px; border:1px solid #E2E8F0; text-align:center; background-color:#F8FAFC;">
        <div style="font-size:11px; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">{label}</div>
        <div style="font-size:20px; color:{color}; font-weight:700; margin-top:4px;">{val}</div>
    </td>
    """

def alm_indicator(label, val, color="#1F3A60"):
    return f"""
    <td width="25%" style="padding:10px; border-bottom:1px solid #E2E8F0; text-align:center;">
        <div style="font-size:11px; color:#64748B; font-weight:600;">{label}</div>
        <div style="font-size:14px; color:{color}; font-weight:700; margin-top:2px;">{val}</div>
    </td>
    """

def build_tag_badges(tags):
    badges = ""
    for tag in tags:
        badges += f"""
        <span style="display:inline-block; background-color:#E2E8F0; color:#1E3A8A; 
                     font-size:10px; font-weight:700; padding:2px 6px; margin-right:4px; 
                     border-radius:4px; text-transform:uppercase;">
            {html_escape(tag)}
        </span>
        """
    return badges

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
    spread_color = "#4CAF50"
    if spread is not None:
        if spread < -0.10:
            spread_color = "#E53935"
        elif spread < 0.15:
            spread_color = "#FFB300"

    # Dynamic styling for equity volatility/asset matching proxies (VIX)
    vix_item = additional.get("VIX")
    vix_color = "#1F3A60"
    if vix_item:
        v = vix_item["value"]
        if v > 25:
            vix_color = "#E53935"
        elif v > 18:
            vix_color = "#FFB300"
        else:
            vix_color = "#4CAF50"

    # Macro Assumption Evaluation
    def mval(key, fmt="{:.2f}%"):
        item = macro.get(key)
        return fmt.format(item["value"]) if item else "N/A"

    alm_bar = f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:8px; border-collapse:collapse; border-top:1px solid #1E3A5F;">
      <tr>
        {alm_indicator("IG OAS",         aval_bps("IG_OAS"))}
        {alm_indicator("HY OAS",         aval_bps("HY_OAS"))}
        {alm_indicator("10Y Breakeven",  aval_pct("BREAKEVEN_10Y"))}
        {alm_indicator("VIX",            aval_pct("VIX", "{:.1f}"), vix_color)}
      </tr>
    </table>
    """

    macro_bar = f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:8px; border-collapse:collapse; border-top:1px solid #1E3A5F;">
      <tr>
        {alm_indicator("Unemployment", mval("unemployment"))}
        {alm_indicator("30Y Mortgage", mval("mortgage_30y"))}
        <td width="25%" style="border-bottom:1px solid #E2E8F0;"></td>
        <td width="25%" style="border-bottom:1px solid #E2E8F0;"></td>
      </tr>
    </table>
    """

    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:15px; border-collapse:collapse;">
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
    {macro_bar}
    """

def build_impact_section(category_buckets, level, min_score=0, require_tags=None):
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
                or any(t in a.get("tags", []) for t in require_tags)
            )
        ]

        if not matching:
            continue

        rows += f"""
        <tr>
            <td style="padding:12px 0; font-size:16px; font-weight:bold; color:#13294B; border-bottom:1px solid #EEEEEE;">
                {html_escape(category)}
            </td>
        </tr>
        """

        # Uses cap definitions derived natively from your config limits
        for article in matching[:config.MAX_ARTICLES_PER_SECTION]:
            tags     = article.get("tags", ["GENERAL"])
            tag_html = build_tag_badges(tags)
            date_str = html_escape(article.get("date", ""))
            source   = html_escape(article.get("source", ""))
            snippet  = html_escape(article.get("snippet", ""))

            rows += f"""
            <tr>
                <td style="padding:12px 0; border-bottom:1px solid #F2F2F2;">
                    <div style="margin-bottom:5px;">{tag_html}</div>
                    <div style="font-weight:600; color:#1F3A60; font-size:14px;">
                        <a href="{article['url']}" style="color:#1F3A60; text-decoration:none;">
                            {html_escape(article['title'])}
                        </a>
                    </div>
                    <div style="color:#475569; font-size:12px; margin-top:6px; line-height:1.4;">
                        {snippet}
                    </div>
                    <div style="color:#94A3B8; font-size:11px; margin-top:6px;">
                        {source} &nbsp;·&nbsp; {date_str}
                    </div>
                </td>
            </tr>
            """

    if not rows:
        return ""

    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:25px;">
        <tr>
            <td style="background:{impact_color}; color:white; padding:12px 18px; font-weight:bold; font-size:15px; border-radius:6px; letter-spacing:0.5px;">
                {level} IMPACT DEVELOPMENTS
            </td>
        </tr>
        {rows}
    </table>
    """

def build_email_html(market_data, category_buckets, llm_summary):
    dashboard_html = build_market_dashboard(market_data)
    
    high_impact = build_impact_section(category_buckets, "HIGH")
    med_impact  = build_impact_section(category_buckets, "MEDIUM")
    low_impact  = build_impact_section(
        category_buckets, "LOW", 
        min_score=config.LOW_IMPACT_MIN_SCORE, 
        require_tags=config.LOW_IMPACT_ALLOWED_TAGS
    )

    formatted_summary = llm_summary.replace("\n", "<br>").replace("**", "<strong>")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Actuarial Intelligence Briefing</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin:0; padding:20px; background-color:#F1F5F9; color:#1E293B;">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width:700px; margin:0 auto; background-color:#FFFFFF; border-radius:8px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.1); border-collapse:collapse; overflow:hidden;">
            <tr>
                <td style="background-color:#13294B; padding:24px 30px; text-align:left;">
                    <h1 style="color:#FFFFFF; margin:0; font-size:22px; font-weight:700; letter-spacing:-0.5px;">Actuarial Intelligence Briefing</h1>
                    <p style="color:#94A3B8; margin:5px 0 0 0; font-size:13px; font-weight:500;">Strategic Market & Regulatory Analysis for Carrier Consultants</p>
                </td>
            </tr>
            <tr>
                <td style="padding:20px 30px 10px 30px;">
                    {dashboard_html}
                </td>
            </tr>
            <tr>
                <td style="padding:10px 30px 20px 30px; font-size:14px; line-height:1.6; color:#334155;">
                    <hr style="border:0; border-top:1px solid #E2E8F0; margin-bottom:20px;">
                    {formatted_summary}
                </td>
            </tr>
            <tr>
                <td style="padding:0 30px 30px 30px;">
                    {high_impact}
                    {med_impact}
                    {low_impact}
                </td>
            </tr>
            <tr>
                <td style="background-color:#F8FAFC; border-top:1px solid #E2E8F0; padding:15px 30px; text-align:center; font-size:11px; color:#94A3B8; font-weight:500;">
                    Actuarial Resources Corporation &nbsp;·&nbsp; Internal Consulting Briefing Pipeline
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
