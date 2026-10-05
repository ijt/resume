#!/usr/bin/env python3
"""Render ijt-resume.md into index.html using template.html.

The Markdown file is the source of truth. This script understands only the
small, fixed structure that file uses, and fails loudly on anything else.
"""

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def inline(s):
    """Convert inline Markdown (links, bold, italic) to HTML."""
    s = html.escape(s.strip(), quote=False)
    s = re.sub(r"(?<=\w)'(?=\w)", "’", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    return s


def split_trailing_italic(s):
    """Split 'text *tail*' into ('text', 'tail')."""
    m = re.fullmatch(r"(.*?)\s*\*([^*]+)\*", s.strip())
    if not m:
        sys.exit(f"build.py: expected trailing *italic* in: {s!r}")
    return m.group(1), m.group(2)


def nonblank(lines):
    return [l for l in lines if l.strip() and l.strip() != "---"]


def render_header(lines):
    lines = nonblank(lines)
    name = re.fullmatch(r"# (.+)", lines[0]).group(1)
    role = re.fullmatch(r"\*\*(.+)\*\*", lines[1].strip()).group(1)
    contact = "<br>\n      ".join(
        inline(l).replace(" | ", " ·\n      ") for l in lines[2:]
    )
    return f"""  <header>
    <div>
      <h1>{inline(name)}</h1>
      <div class="role">{inline(role)}</div>
    </div>
    <div class="contact">
      {contact}
    </div>
  </header>
"""


def render_summary(lines):
    text = " ".join(l.strip() for l in nonblank(lines))
    return f'    <p class="summary">\n      {inline(text)}\n    </p>\n'


def render_skills(lines):
    lines = nonblank(lines)
    out = ['    <dl class="skills">']
    for label, value in zip(lines[0::2], lines[1::2]):
        label = re.fullmatch(r"\*\*(.+)\*\*", label.strip()).group(1)
        out.append(f"      <dt>{inline(label)}</dt>")
        out.append(f"      <dd>{inline(value)}</dd>")
    out.append("    </dl>")
    return "\n".join(out) + "\n"


def render_experience(lines):
    out = []
    in_job = in_list = False
    lines = nonblank(lines)
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        job = re.fullmatch(r"\*\*(.+?)\*\* — (.+)", line)
        sub = re.fullmatch(r"\*([^*]+)\*", line)
        if job:
            if in_list:
                out.append("      </ul>")
                in_list = False
            if in_job:
                out.append("    </div>\n")
            meta = re.fullmatch(r"\*([^*]+)\*", lines[i + 1].strip())
            if not meta:
                sys.exit(f"build.py: expected *dates* after {line!r}")
            out += [
                '    <div class="job">',
                '      <div class="job-head">',
                f'        <h3>{inline(job.group(1))} <span class="title">— {inline(job.group(2))}</span></h3>',
                f'        <span class="meta">{inline(meta.group(1))}</span>',
                "      </div>",
            ]
            in_job = True
            i += 2
            continue
        if sub:
            if in_list:
                out.append("      </ul>")
                in_list = False
            out.append(f'      <p class="sub">{inline(sub.group(1))}</p>')
        elif line.startswith("- "):
            if not in_list:
                out.append("      <ul>")
                in_list = True
            out.append(f"        <li>{inline(line[2:])}</li>")
        else:
            sys.exit(f"build.py: unexpected line in Experience: {line!r}")
        i += 1
    if in_list:
        out.append("      </ul>")
    if in_job:
        out.append("    </div>")
    return "\n".join(out) + "\n"


def render_open_source(lines):
    out = ['    <div class="projects">']
    for line in nonblank(lines):
        name, rest = line.strip()[2:].split(" — ", 1)
        desc, tags = split_trailing_italic(rest)
        out += [
            '      <div class="project">',
            f"        <h3>{inline(name.replace('**', ''))}</h3>",
            f"        <p>{inline(desc)}</p>",
            f'        <div class="tags">{inline(tags)}</div>',
            "      </div>",
        ]
    out.append("    </div>")
    return "\n".join(out) + "\n"


def render_earlier(lines):
    out = ['    <ul class="compact">']
    for line in nonblank(lines):
        text, dates = split_trailing_italic(line.strip()[2:])
        out.append(f'      <li>{inline(text)} <span class="meta">{inline(dates)}</span></li>')
    out.append("    </ul>")
    return "\n".join(out) + "\n"


def render_education(lines):
    out = ['    <div class="edu">']
    for line in nonblank(lines):
        m = re.fullmatch(r"\*\*(.+?)\*\* — (.+?)\s*", line)
        out.append(f"      <div><strong>{inline(m.group(1))}</strong>{inline(m.group(2))}</div>")
    out.append("    </div>")
    return "\n".join(out) + "\n"


SECTIONS = {
    "Summary": render_summary,
    "Skills": render_skills,
    "Experience": render_experience,
    "Open Source": render_open_source,
    "Earlier": render_earlier,
    "Education": render_education,
}


def main():
    md = (ROOT / "ijt-resume.md").read_text().splitlines()
    chunks = [("", [])]
    for line in md:
        if line.startswith("### "):
            chunks.append((line[4:].strip(), []))
        else:
            chunks[-1][1].append(line)

    body = [render_header(chunks[0][1])]
    for title, lines in chunks[1:]:
        if title not in SECTIONS:
            sys.exit(f"build.py: unknown section {title!r}")
        body.append(f"\n  <section>\n    <h2>{title}</h2>\n{SECTIONS[title](lines)}  </section>\n")

    template = (ROOT / "template.html").read_text()
    page = template.replace("{{body}}", "".join(body).rstrip("\n"))

    # index.html is the static resume; motion.html is the same page, animated,
    # with motion.css and motion.js inlined so it is a single file.
    motion_css = (ROOT / "motion.css").read_text()
    motion_js = (ROOT / "motion.js").read_text()
    outputs = {
        "index.html": ("", ""),
        "motion.html": (
            f"<style>\n{motion_css}</style>\n",
            f"<script>\n{motion_js}</script>\n",
        ),
    }
    for name, (head_extra, body_extra) in outputs.items():
        out = page.replace("{{head_extra}}", head_extra).replace("{{body_extra}}", body_extra)
        path = ROOT / name
        # Leave unchanged files alone so make doesn't needlessly reprint the PDF.
        if not path.exists() or path.read_text() != out:
            path.write_text(out)


if __name__ == "__main__":
    main()
