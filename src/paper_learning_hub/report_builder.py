"""每日 HTML 报告生成器 — 精美双语论文日报。"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .blog_fetcher import BlogArticle

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{report_title}</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; background: #f8fafc; color: #1a1a2e; line-height: 1.6; }}
.container {{ max-width: 900px; margin: 0 auto; padding: 24px 20px 60px; }}

/* header */
.header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); color: white; padding: 40px 20px; text-align: center; border-radius: 16px; margin-bottom: 28px; }}
.header h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 8px; }}
.header p {{ font-size: 14px; opacity: 0.8; }}

/* stats */
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px,1fr)); gap: 16px; margin-bottom: 28px; }}
.stat-card {{ background: white; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }}
.stat-card .num {{ font-size: 32px; font-weight: 800; }}
.stat-card .label {{ font-size: 12px; color: #64748b; margin-top: 4px; }}

/* section */
.section {{ margin-bottom: 32px; }}
.section-title {{ display: flex; align-items: center; gap: 10px; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #e2e8f0; }}
.section-title .dot {{ width: 12px; height: 12px; border-radius: 50%; background: var(--org-color); flex-shrink: 0; }}
.section-title h2 {{ font-size: 20px; font-weight: 700; }}

/* article card */
.article {{ background: white; border-radius: 12px; padding: 20px 24px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border-left: 4px solid var(--org-color); transition: box-shadow 0.2s; }}
.article:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,0.1); }}
.article .meta {{ display: flex; align-items: center; gap: 10px; margin-bottom: 6px; flex-wrap: wrap; }}
.article .org-tag {{ display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; color: white; background: var(--org-color); }}
.article .date {{ font-size: 12px; color: #94a3b8; }}
.article h3 {{ font-size: 17px; font-weight: 700; margin-bottom: 10px; line-height: 1.4; }}
.article h3 a {{ color: #1a1a2e; text-decoration: none; }}
.article h3 a:hover {{ color: var(--org-color); text-decoration: underline; }}

/* bilingual */
.bilingual {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 12px; }}
.lang-block {{ background: #f8fafc; border-radius: 8px; padding: 14px 16px; }}
.lang-block .lang-label {{ font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.5px; }}
.lang-block p {{ font-size: 14px; color: #334155; line-height: 1.6; }}
.toggle-btn {{ display: inline-block; padding: 4px 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 12px; cursor: pointer; background: white; color: #64748b; margin-left: 8px; }}
.toggle-btn:hover {{ background: #f1f5f9; }}

/* footer */
.footer {{ text-align: center; padding: 32px 0 16px; font-size: 13px; color: #94a3b8; }}
.footer a {{ color: #0f3460; }}

@media (max-width: 640px) {{
    .bilingual {{ grid-template-columns: 1fr; }}
    .header h1 {{ font-size: 22px; }}
}}
</style>
</head>
<body>
<div class="container">

<div class="header">
    <h1>{report_title}</h1>
    <p>每日自动聚合 · {date_str} · 覆盖 Anthropic / OpenAI / DeepMind / Meta / DeepSeek</p>
</div>

<div class="stats">
    {stats_html}
</div>

{sections_html}

<div class="footer">
    <p>报告由 <strong>Paper Hub v2.0</strong> 自动生成 · 每日 {run_time} 更新</p>
    <p><a href="https://github.com/GroupeChou/paper-learning-hub" target="_blank">GitHub Pages</a> · <a href="#" onclick="toggleAllBilingual()">切换中英对照</a></p>
</div>

</div>

<script>
function toggleAllBilingual() {{
    const blocks = document.querySelectorAll('.bilingual');
    blocks.forEach(b => b.style.display = b.style.display === 'none' ? 'grid' : 'none');
}}
</script>
</body>
</html>"""


def generate_html_report(
    articles: list[BlogArticle],
    output_path: Path,
    report_title: str = "前沿 AI 技术日报",
) -> Path:
    """生成精美 HTML 日报。"""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y年%m月%d日")
    run_time = now.strftime("%H:%M UTC")

    # group articles by org
    from collections import defaultdict
    grouped: dict[str, list[BlogArticle]] = defaultdict(list)
    for a in articles:
        grouped[a.org].append(a)

    # stats cards
    total = len(articles)
    zh_count = sum(1 for a in articles if a.translated)
    org_count = len(grouped)
    stats_html = f"""<div class="stat-card"><div class="num" style="color:#0f3460">{total}</div><div class="label">今日文章</div></div>
    <div class="stat-card"><div class="num" style="color:#4285F4">{org_count}</div><div class="label">覆盖机构</div></div>
    <div class="stat-card"><div class="num" style="color:#D97757">{zh_count}</div><div class="label">中文摘要</div></div>"""

    # sections per org
    sections_parts = []
    for org, org_articles in grouped.items():
        org_color = org_articles[0].org_color
        articles_html = ""
        for a in org_articles:
            zh_display = f"<p>{a.summary_zh}</p>" if a.summary_zh else ""
            en_display = f"<p>{a.summary_en}</p>" if a.summary_en else f"<p>{a.title}</p>"
            if not a.summary_zh:
                zh_display = en_display

            date_str_short = ""
            if a.published:
                try:
                    dt = datetime.fromisoformat(a.published.replace("Z", "+00:00"))
                    date_str_short = dt.strftime("%m/%d")
                except Exception:
                    pass

            articles_html += f"""
            <div class="article" style="--org-color:{org_color}">
                <div class="meta">
                    <span class="org-tag" style="background:{org_color}">{a.org}</span>
                    <span class="date">{date_str_short}</span>
                </div>
                <h3><a href="{a.url}" target="_blank" rel="noopener">{a.title}</a></h3>
                <div class="bilingual">
                    <div class="lang-block">
                        <div class="lang-label">🇺🇸 English</div>
                        {en_display}
                    </div>
                    <div class="lang-block">
                        <div class="lang-label">🇨🇳 中文</div>
                        {zh_display}
                    </div>
                </div>
            </div>"""

        sections_parts.append(f"""
        <div class="section">
            <div class="section-title">
                <div class="dot" style="background:{org_color}"></div>
                <h2>{org}</h2>
                <span style="color:#94a3b8;font-size:13px">· {len(org_articles)} 篇</span>
            </div>
            {articles_html}
        </div>""")

    html = HTML_TEMPLATE.format(
        report_title=report_title,
        date_str=date_str,
        run_time=run_time,
        stats_html=stats_html,
        sections_html="\n".join(sections_parts),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path


def generate_simple_report(
    articles: list[BlogArticle],
    output_path: Path,
) -> Path:
    """生成纯 Markdown 版本的日报（作为 HTML 的降级方案）。"""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")

    lines = [
        f"# 前沿 AI 技术日报 · {date_str}",
        "",
        f"共 **{len(articles)}** 篇文章，覆盖 {len(set(a.org for a in articles))} 个机构。",
        "",
        "---",
        "",
    ]

    from collections import defaultdict
    grouped = defaultdict(list)
    for a in articles:
        grouped[a.org].append(a)

    for org, org_articles in grouped.items():
        lines.append(f"## {org} ({len(org_articles)} 篇)")
        lines.append("")
        for a in org_articles:
            url_text = a.url
            lines.append(f"### [{a.title}]({url_text})")
            if a.summary_en:
                lines.append(f"")
                lines.append(f"> {a.summary_en[:300]}")
            if a.summary_zh:
                lines.append(f"")
                lines.append(f"**中文摘要**: {a.summary_zh[:300]}")
            lines.append("")
        lines.append("---")
        lines.append("")

    lines.append(f"> 报告由 Paper Hub v2.0 自动生成 · {now.strftime('%H:%M UTC')}")
    lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path
