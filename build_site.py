#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DOCX_PATH = ROOT / "第四章.docx"
ASSETS_DIR = ROOT / "assets"
ARTICLE_SLUG = "chapter-04"


def run_textutil(docx_path: Path) -> str:
    result = subprocess.run(
        ["textutil", "-convert", "txt", "-stdout", str(docx_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def clean_line(line: str) -> str:
    line = line.replace("\u200f", "").replace("\ufeff", "")
    line = line.replace("\t", " ")
    line = re.sub(r"\s+", " ", line).strip()
    line = line.strip("•")
    return line.strip()


def parse_document(text: str) -> dict:
    raw_lines = [clean_line(line) for line in text.splitlines()]
    lines = [line for line in raw_lines if line]
    if not lines:
        raise ValueError("Document appears to be empty after conversion.")

    title = lines[0]
    abstract = lines[1] if len(lines) > 1 else ""
    content_lines = lines[2:]

    sections: list[dict] = []
    current_section: dict | None = None
    current_subsection: dict | None = None

    main_heading_re = re.compile(r"^[一二三四五六七八九十]+、")
    sub_heading_re = re.compile(r"^（[一二三四五六七八九十]+）")

    def ensure_section() -> dict:
        nonlocal current_section
        if current_section is None:
            current_section = {"title": "正文", "subsections": [], "paragraphs": []}
            sections.append(current_section)
        return current_section

    def ensure_subsection() -> dict:
        nonlocal current_subsection
        section = ensure_section()
        if current_subsection is None:
            current_subsection = {"title": "要点", "paragraphs": []}
            section["subsections"].append(current_subsection)
        return current_subsection

    for line in content_lines:
        if main_heading_re.match(line):
            current_section = {"title": line, "subsections": [], "paragraphs": []}
            sections.append(current_section)
            current_subsection = None
            continue
        if sub_heading_re.match(line):
            section = ensure_section()
            current_subsection = {"title": line, "paragraphs": []}
            section["subsections"].append(current_subsection)
            continue

        target = current_subsection if current_subsection else ensure_section()
        target["paragraphs"].append(line)

    keywords = ["新质生产力", "科技体制改革", "现代化产业体系", "教育与人才机制", "高水平对外开放"]
    return {
        "id": "CASE-CH04",
        "title": title,
        "theme": "新质生产力现实路径与制度落地",
        "abstract": abstract,
        "journal": "章节型文稿整理",
        "year": "2026",
        "source_file": DOCX_PATH.name,
        "slug": ARTICLE_SLUG,
        "keywords": keywords,
        "sections": sections,
    }


def slugify_heading(text: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "-", text).strip("-").lower()
    return slug or "section"


def render_article(doc: dict) -> str:
    toc_items = []
    content_parts = []

    for idx, section in enumerate(doc["sections"], start=1):
        section_id = f"s-{idx}-{slugify_heading(section['title'])}"
        toc_items.append(
            f'<li><a href="#{section_id}">{html.escape(section["title"])}</a></li>'
        )
        content_parts.append(
            f'<section class="article-section" id="{section_id}">'
            f'<h2>{html.escape(section["title"])}</h2>'
        )
        for paragraph in section["paragraphs"]:
            content_parts.append(f"<p>{html.escape(paragraph)}</p>")
        for sub_idx, subsection in enumerate(section["subsections"], start=1):
            sub_id = f"{section_id}-sub-{sub_idx}"
            toc_items.append(
                f'<li class="toc-sub"><a href="#{sub_id}">{html.escape(subsection["title"])}</a></li>'
            )
            content_parts.append(f'<section class="article-subsection" id="{sub_id}">')
            content_parts.append(f"<h3>{html.escape(subsection['title'])}</h3>")
            for paragraph in subsection["paragraphs"]:
                if re.match(r"^第[一二三四五六七八九十]+，", paragraph):
                    lead, rest = paragraph.split("，", 1)
                    content_parts.append(
                        "<p><strong>"
                        + html.escape(lead + "，")
                        + "</strong>"
                        + html.escape(rest)
                        + "</p>"
                    )
                else:
                    content_parts.append(f"<p>{html.escape(paragraph)}</p>")
            content_parts.append("</section>")
        content_parts.append("</section>")

    keyword_tags = "".join(
        f'<li>{html.escape(keyword)}</li>' for keyword in doc["keywords"]
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(doc["title"])} | XD Macau Basic Case</title>
  <meta name="description" content="{html.escape(doc["abstract"][:140])}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;700&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/styles.css">
</head>
<body class="article-page">
  <div class="site-shell">
    <header class="site-header">
      <a class="brand" href="index.html">XD Macau Basic Case</a>
      <nav class="top-nav">
        <a href="index.html">目录</a>
        <a href="#article-toc">章节导航</a>
      </nav>
    </header>

    <main>
      <section class="article-hero">
        <div class="eyebrow">Chapter Archive</div>
        <h1>{html.escape(doc["title"])}</h1>
        <p class="lead">{html.escape(doc["abstract"])}</p>
        <div class="meta-grid">
          <div><span>编号</span><strong>{html.escape(doc["id"])}</strong></div>
          <div><span>主题</span><strong>{html.escape(doc["theme"])}</strong></div>
          <div><span>来源文件</span><strong>{html.escape(doc["source_file"])}</strong></div>
          <div><span>整理类型</span><strong>{html.escape(doc["journal"])}</strong></div>
        </div>
        <ul class="keyword-list">{keyword_tags}</ul>
      </section>

      <section class="article-layout">
        <aside class="article-toc-card" id="article-toc">
          <div class="sticky-box">
            <h2>目录</h2>
            <ol class="toc-list">
              {''.join(toc_items)}
            </ol>
          </div>
        </aside>

        <article class="article-card prose">
          {''.join(content_parts)}
        </article>
      </section>
    </main>
  </div>
</body>
</html>
"""


def render_index(doc: dict) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>XD Macau Basic Case</title>
  <meta name="description" content="章节型静态网页目录，支持检索、摘要浏览与精读阅读。">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;700&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
  <div class="site-shell">
    <header class="site-header">
      <a class="brand" href="index.html">XD Macau Basic Case</a>
      <nav class="top-nav">
        <a href="#catalog">案件目录</a>
        <a href="#about">阅读说明</a>
      </nav>
    </header>

    <main>
      <section class="hero-panel">
        <div class="hero-copy">
          <div class="eyebrow">GitHub Pages Static Archive</div>
          <h1>章节文稿目录与精读页面</h1>
          <p>沿用参考站的“总目录 + 单篇阅读”信息架构，并升级为更适合长文阅读的静态网页。首页可检索条目、查看编号、主题与摘要，正文页则提供侧边目录、锚点跳转与更清晰的段落排版。</p>
        </div>
        <div class="hero-stats">
          <div class="stat-card"><span>条目数</span><strong>01</strong></div>
          <div class="stat-card"><span>内容类型</span><strong>章节文稿</strong></div>
          <div class="stat-card"><span>发布方式</span><strong>GitHub Pages</strong></div>
        </div>
      </section>

      <section class="controls-panel" id="catalog">
        <div>
          <p class="section-label">目录</p>
          <h2>案件 / 章节索引</h2>
          <p class="section-note">展示编号、主题、来源与摘要，可直接进入全文阅读。</p>
        </div>
        <label class="search-box">
          <span>检索</span>
          <input id="search-input" type="search" placeholder="输入标题、主题、关键词、摘要">
        </label>
      </section>

      <section>
        <div class="results-bar">
          <span id="result-count">共 1 条</span>
          <span>当前分类：全部</span>
        </div>
        <div class="card-grid" id="card-grid">
          <article class="record-card" data-search="{html.escape(' '.join([doc['id'], doc['title'], doc['theme'], doc['abstract'], ' '.join(doc['keywords'])]))}">
            <p class="record-type">章节文稿</p>
            <h3><a href="{html.escape(doc["slug"])}.html">{html.escape(doc["title"])}</a></h3>
            <dl class="meta-list">
              <div><dt>编号</dt><dd>{html.escape(doc["id"])}</dd></div>
              <div><dt>主题</dt><dd>{html.escape(doc["theme"])}</dd></div>
              <div><dt>来源</dt><dd>{html.escape(doc["source_file"])}</dd></div>
              <div><dt>年份</dt><dd>{html.escape(doc["year"])}</dd></div>
            </dl>
            <p class="record-abstract">{html.escape(doc["abstract"])}</p>
            <div class="card-footer">
              <div class="pill-row">
                {''.join(f'<span class="pill">{html.escape(keyword)}</span>' for keyword in doc["keywords"])}
              </div>
              <a class="read-link" href="{html.escape(doc["slug"])}.html">阅读全文</a>
            </div>
          </article>
        </div>
      </section>

      <section class="about-panel" id="about">
        <div>
          <p class="section-label">阅读说明</p>
          <h2>页面结构</h2>
        </div>
        <div class="about-grid">
          <article>
            <h3>目录视图</h3>
            <p>适合快速浏览文稿主题、摘要和关键词，保留参考站清晰的检索和卡片入口逻辑。</p>
          </article>
          <article>
            <h3>正文视图</h3>
            <p>使用侧边目录、段落留白、章节分隔和高对比阅读样式，让长文在手机和桌面端都更容易阅读。</p>
          </article>
          <article>
            <h3>可公开访问</h3>
            <p>站点文件是纯静态 HTML、CSS、JS，可直接发布到 GitHub Pages 并通过公网链接访问。</p>
          </article>
        </div>
      </section>
    </main>
  </div>

  <script src="assets/app.js"></script>
</body>
</html>
"""


def build() -> None:
    ASSETS_DIR.mkdir(exist_ok=True)
    text = run_textutil(DOCX_PATH)
    doc = parse_document(text)
    (ROOT / "index.html").write_text(render_index(doc), encoding="utf-8")
    (ROOT / f"{ARTICLE_SLUG}.html").write_text(render_article(doc), encoding="utf-8")
    (ROOT / "records.json").write_text(
        json.dumps([doc], ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    build()
