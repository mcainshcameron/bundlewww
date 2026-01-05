"""
Agent C: Renderer
Deterministically renders static website from schema
"""
from pathlib import Path
from typing import AsyncGenerator
import shutil

from ..models import Blueprint, Project
from ..models.schema import (
    WebsiteSchema, ChapterSchema, SectionSchema, ContentBlock,
    ProseSection, Timeline, Table, Callout, KeyStat, CodeBlock
)
from ..models.events import PipelineEvent, EventType


class RendererAgent:
    """Agent responsible for assembling static website from schema"""

    def __init__(self):
        pass

    def _render_content_block(self, block: ContentBlock) -> str:
        """Render a single content block to HTML"""
        if isinstance(block, ProseSection):
            return self._render_prose(block)
        elif isinstance(block, Timeline):
            return self._render_timeline(block)
        elif isinstance(block, Table):
            return self._render_table(block)
        elif isinstance(block, Callout):
            return self._render_callout(block)
        elif isinstance(block, KeyStat):
            return self._render_key_stat(block)
        elif isinstance(block, CodeBlock):
            return self._render_code_block(block)
        else:
            return ""

    def _render_prose(self, prose: ProseSection) -> str:
        """Render prose section"""
        paragraphs = "".join(f"<p>{p}</p>" for p in prose.paragraphs)
        return f"""
<div class="prose-section">
  <h3>{prose.heading}</h3>
  {paragraphs}
</div>"""

    def _render_timeline(self, timeline: Timeline) -> str:
        """Render timeline"""
        events_html = ""
        for event in timeline.events:
            events_html += f"""
<div class="timeline-event">
  <div class="timeline-date">{event.date}</div>
  <div class="timeline-content">
    <h4>{event.title}</h4>
    <p>{event.description}</p>
  </div>
</div>"""

        return f"""
<div class="timeline-section">
  <h3>{timeline.heading}</h3>
  <div class="timeline">
    {events_html}
  </div>
</div>"""

    def _render_table(self, table: Table) -> str:
        """Render table"""
        header = "<tr>" + "".join(f"<th>{col}</th>" for col in table.columns) + "</tr>"
        rows = ""
        for row in table.rows:
            rows += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"

        return f"""
<div class="table-section">
  <h3>{table.heading}</h3>
  <table>
    <thead>{header}</thead>
    <tbody>{rows}</tbody>
  </table>
</div>"""

    def _render_callout(self, callout: Callout) -> str:
        """Render callout box"""
        return f"""
<div class="callout callout-{callout.style}">
  <h4>{callout.title}</h4>
  <p>{callout.content}</p>
</div>"""

    def _render_key_stat(self, stat: KeyStat) -> str:
        """Render key statistic"""
        context = f"<p class='stat-context'>{stat.context}</p>" if stat.context else ""
        return f"""
<div class="key-stat">
  <div class="stat-value">{stat.value}</div>
  <div class="stat-label">{stat.label}</div>
  {context}
</div>"""

    def _render_code_block(self, code: CodeBlock) -> str:
        """Render code block"""
        return f"""
<div class="code-section">
  <h3>{code.heading}</h3>
  <pre><code class="language-{code.language}">{self._escape_html(code.code)}</code></pre>
</div>"""

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _render_section(self, section: SectionSchema, section_title: str) -> str:
        """Render a section with all its blocks"""
        blocks_html = "".join(self._render_content_block(block) for block in section.blocks)
        return f"""
<section id="{section.section_id}" class="content-section">
  <h2 class="section-title">{section_title}</h2>
  {blocks_html}
</section>"""

    def _render_landing_page(
        self,
        project: Project,
        blueprint: Blueprint,
    ) -> str:
        """Render the landing/home page"""

        # Build chapter list for landing page
        chapters_html = ""
        for idx, chapter in enumerate(blueprint.chapters):
            href = f"chapter_{idx + 1}.html"
            chapters_html += f"""
<div class="landing-chapter">
  <div class="landing-chapter-number">{idx + 1}</div>
  <div class="landing-chapter-content">
    <h3><a href="{href}">{chapter.title}</a></h3>
    <p>{chapter.purpose}</p>
  </div>
</div>"""

        # Build navigation
        nav_html = self._build_navigation(blueprint, "home", project)

        # Complete landing page
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{project.topic}</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  {nav_html}
  <main class="landing-content">
    <div class="landing-hero">
      <h1>{project.topic}</h1>
      <p class="landing-subtitle">A comprehensive guide exploring this topic in depth</p>
    </div>

    <div class="landing-chapters">
      <h2>Chapters</h2>
      {chapters_html}
    </div>
  </main>
</body>
</html>"""

    def _render_chapter(
        self,
        chapter_schema: ChapterSchema,
        blueprint: Blueprint,
        project: Project,
    ) -> str:
        """Render a complete chapter page"""

        # Find chapter in blueprint for titles
        chapter = next((c for c in blueprint.chapters if c.id == chapter_schema.chapter_id), None)
        if not chapter:
            return ""

        # Render introduction
        intro_paragraphs = "".join(f"<p>{p}</p>" for p in chapter_schema.introduction)
        intro_html = f"""
<div class="chapter-introduction">
  {intro_paragraphs}
</div>"""

        # Render sections
        sections_html = ""
        for section_schema in chapter_schema.sections:
            # Find section title from blueprint
            section = next((s for s in chapter.sections if s.id == section_schema.section_id), None)
            section_title = section.title if section else "Section"
            sections_html += self._render_section(section_schema, section_title)

        # Build navigation
        nav_html = self._build_navigation(blueprint, chapter.id, project)

        # Add hero image if available
        hero_image_html = ""
        if chapter_schema.image_path:
            hero_image_html = f"""
<div class="chapter-hero-image">
  <img src="{chapter_schema.image_path}" alt="{chapter.title}" />
</div>"""

        # Complete page
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{chapter.title} - {project.topic}</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  {nav_html}
  <main class="chapter-content">
    <h1>{chapter.title}</h1>
    {hero_image_html}
    {intro_html}
    {sections_html}
  </main>
</body>
</html>"""

    def _build_navigation(self, blueprint: Blueprint, current_chapter_id: str, project: Project) -> str:
        """Build site sidebar navigation"""
        # Home link
        home_active = "active" if current_chapter_id == "home" else ""
        nav_items = f'<li class="{home_active}"><a href="index.html">🏠 Home</a></li>'

        # Chapter links
        for idx, chapter in enumerate(blueprint.chapters):
            active = "active" if chapter.id == current_chapter_id else ""
            href = f"chapter_{idx + 1}.html"
            nav_items += f'<li class="{active}"><a href="{href}">{idx + 1}. {chapter.title}</a></li>'

        return f"""
<nav class="site-nav">
  <div class="nav-header">
    <h1>{project.topic}</h1>
  </div>
  <ul class="nav-menu">
    {nav_items}
  </ul>
</nav>"""

    def _generate_stylesheet(self) -> str:
        """Generate CSS stylesheet"""
        return """/* BundleWWW Generated Website Styles */

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  line-height: 1.6;
  color: #333;
  background: #f5f5f5;
  min-height: 100vh;
  margin: 0;
  padding: 0;
  display: flex;
}

/* Left Sidebar Navigation */
.site-nav {
  width: 220px;
  min-width: 220px;
  background: #2c3e50;
  padding: 1.5rem 0;
  height: 100vh;
  overflow-y: auto;
  position: sticky;
  top: 0;
  flex-shrink: 0;
}

.nav-header {
  padding: 0 1rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 1rem;
}

.nav-header h1 {
  font-size: 1rem;
  color: #ecf0f1;
  font-weight: 600;
  border: none;
  padding: 0;
  margin: 0;
}

.nav-menu {
  list-style: none;
  padding: 0;
}

.nav-menu li {
  margin: 0;
}

.nav-menu a {
  display: block;
  color: #ecf0f1;
  text-decoration: none;
  padding: 0.625rem 1rem;
  transition: background 0.2s;
  border-left: 3px solid transparent;
  font-size: 0.875rem;
}

.nav-menu a:hover {
  background: rgba(255, 255, 255, 0.05);
  border-left-color: #3498db;
}

.nav-menu .active a {
  background: rgba(52, 152, 219, 0.2);
  border-left-color: #3498db;
  font-weight: 500;
}

/* Main Content Area */
main {
  flex: 1;
  padding: 2.5rem 3rem;
  background: white;
  min-height: 100vh;
  box-sizing: border-box;
  overflow-x: hidden;
}

.chapter-content,
.landing-content {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

/* Landing Page Styles */
.landing-hero {
  text-align: center;
  padding: 4rem 0;
  border-bottom: 1px solid #e0e0e0;
  margin-bottom: 3rem;
}

.landing-hero h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.landing-subtitle {
  font-size: 1.25rem;
  color: #666;
  margin: 0;
}

.landing-chapters h2 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 2rem;
}

.landing-chapter {
  display: flex;
  gap: 1.5rem;
  padding: 1.5rem;
  margin-bottom: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.landing-chapter:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.landing-chapter-number {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #3498db;
  color: white;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1.25rem;
}

.landing-chapter-content {
  flex: 1;
}

.landing-chapter-content h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.125rem;
}

.landing-chapter-content h3 a {
  color: #2c3e50;
  text-decoration: none;
}

.landing-chapter-content h3 a:hover {
  color: #3498db;
}

.landing-chapter-content p {
  margin: 0;
  color: #666;
  font-size: 0.9375rem;
  text-align: left;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 1.5rem;
  color: #2c3e50;
  border-bottom: 3px solid #3498db;
  padding-bottom: 0.5rem;
}

.chapter-hero-image {
  margin: 2rem 0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  max-width: 100%;
}

.chapter-hero-image img {
  width: 100%;
  max-width: 100%;
  height: auto;
  display: block;
  object-fit: cover;
}

h2 {
  font-size: 2rem;
  margin: 2rem 0 1rem;
  color: #34495e;
}

.section-title {
  font-size: 1.75rem;
  margin: 2.5rem 0 1.5rem;
  color: #2c3e50;
  font-weight: 600;
}

h3 {
  font-size: 1.5rem;
  margin: 1.5rem 0 0.75rem;
  color: #34495e;
}

h4 {
  font-size: 1.25rem;
  margin: 1rem 0 0.5rem;
  color: #555;
}

p {
  margin: 1rem 0;
  text-align: justify;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.chapter-introduction {
  font-size: 1.1rem;
  line-height: 1.8;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #ecf0f1;
  border-left: 4px solid #3498db;
}

.content-section {
  margin: 3rem 0;
  padding: 1.5rem 0;
  border-top: 1px solid #ddd;
}

.prose-section {
  margin: 1.5rem 0;
}

.timeline {
  position: relative;
  padding-left: 2rem;
  margin: 1.5rem 0;
}

.timeline-event {
  position: relative;
  padding: 1rem 0 1rem 1.5rem;
  border-left: 2px solid #3498db;
}

.timeline-event::before {
  content: "";
  position: absolute;
  left: -6px;
  top: 1.5rem;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #3498db;
}

.timeline-date {
  font-weight: bold;
  color: #3498db;
  margin-bottom: 0.5rem;
}

.table-section {
  margin: 1.5rem 0;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}

th, td {
  padding: 0.75rem;
  text-align: left;
  border: 1px solid #ddd;
}

th {
  background: #3498db;
  color: white;
  font-weight: 600;
}

tr:nth-child(even) {
  background: #f9f9f9;
}

.callout {
  padding: 1rem 1.5rem;
  margin: 1.5rem 0;
  border-radius: 4px;
  border-left: 4px solid;
}

.callout-info {
  background: #e8f4f8;
  border-color: #3498db;
}

.callout-warning {
  background: #fff3cd;
  border-color: #ffc107;
}

.callout-tip {
  background: #d4edda;
  border-color: #28a745;
}

.key-stat {
  text-align: center;
  padding: 1.5rem;
  margin: 1.5rem 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
}

.stat-value {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 1.25rem;
  opacity: 0.9;
}

.stat-context {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  opacity: 0.8;
}

.code-section {
  margin: 1.5rem 0;
}

pre {
  background: #2c3e50;
  color: #ecf0f1;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
}

code {
  font-family: "Courier New", Courier, monospace;
  font-size: 0.9rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  body {
    flex-direction: column;
  }

  .site-nav {
    width: 100%;
    min-width: 100%;
    height: auto;
    position: relative;
    padding: 1rem 0;
  }

  .nav-header {
    padding: 0 1rem 1rem;
  }

  .nav-menu a {
    padding: 0.5rem 1rem;
  }

  main {
    padding: 1.5rem;
  }

  .chapter-content,
  .landing-content {
    max-width: 100%;
  }

  .landing-hero h1 {
    font-size: 2rem;
  }

  .landing-subtitle {
    font-size: 1rem;
  }

  .landing-chapter {
    flex-direction: column;
    gap: 1rem;
  }

  .landing-chapter-number {
    width: 40px;
    height: 40px;
    font-size: 1rem;
  }

  h1 {
    font-size: 2rem;
  }

  h2 {
    font-size: 1.5rem;
  }

  .section-title {
    font-size: 1.375rem;
  }
}
"""

    async def render_website(
        self,
        project: Project,
        blueprint: Blueprint,
        schema: WebsiteSchema,
        output_dir: Path,
    ) -> AsyncGenerator[PipelineEvent, None]:
        """Render complete static website"""

        yield PipelineEvent(
            event_type=EventType.RENDER_START,
            message="Starting website rendering",
            progress=0.0,
        )

        try:
            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)

            # Clean up old HTML/CSS files but preserve images
            if output_dir.exists():
                for file in output_dir.iterdir():
                    if file.is_file() and file.suffix in ['.html', '.css']:
                        file.unlink()

            # Generate stylesheet
            css_path = output_dir / "styles.css"
            with open(css_path, "w", encoding="utf-8") as f:
                f.write(self._generate_stylesheet())

            # Render landing page as index.html
            landing_html = self._render_landing_page(project, blueprint)
            landing_path = output_dir / "index.html"
            with open(landing_path, "w", encoding="utf-8") as f:
                f.write(landing_html)

            yield PipelineEvent(
                event_type=EventType.PROGRESS,
                message="Rendered landing page",
                progress=0.0,
            )

            # Render each chapter as chapter_1.html, chapter_2.html, etc.
            total_chapters = len(schema.chapters)
            for idx, chapter_schema in enumerate(schema.chapters):
                # All chapters are numbered (no index.html for first chapter)
                filename = f"chapter_{idx + 1}.html"
                chapter_path = output_dir / filename

                # Render chapter HTML
                html_content = self._render_chapter(chapter_schema, blueprint, project)

                # Write file
                with open(chapter_path, "w", encoding="utf-8") as f:
                    f.write(html_content)

                # Emit progress
                progress = ((idx + 1) / total_chapters) * 100
                yield PipelineEvent(
                    event_type=EventType.PROGRESS,
                    message=f"Rendered chapter {idx + 1}/{total_chapters}",
                    progress=progress,
                )

            yield PipelineEvent(
                event_type=EventType.RENDER_COMPLETE,
                message="Website rendering complete",
                progress=100.0,
            )

            yield PipelineEvent(
                event_type=EventType.EXPORT_READY,
                message="Website is ready for preview and download",
                data={"output_path": str(output_dir)},
            )

        except Exception as e:
            yield PipelineEvent(
                event_type=EventType.ERROR,
                message=f"Rendering failed: {str(e)}",
                data={"error": str(e)},
            )
            raise
