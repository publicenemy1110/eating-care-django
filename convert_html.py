#!/usr/bin/env python3
"""Convert html-css-site pages into Django templates."""

import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
HTML_DIR = Path('/Users/publicenemy/Desktop/html-css project')
TEMPLATES_DIR = BASE / 'pages' / 'templates' / 'pages'

# tests.html генерируется вручную (Django-опросники) — не перезаписывать
PAGES = {
    'index.html': ('index.html', ''),
    'rpp.html': ('rpp.html', 'rpp'),
    'parents.html': ('parents.html', 'parents'),
    'programs.html': ('programs.html', 'programs'),
    'aboutus.html': ('about.html', 'about'),
}

URL_MAP = {
    'index.html': "{% url 'pages:index' %}",
    'rpp.html': "{% url 'pages:rpp' %}",
    'tests.html': "{% url 'pages:tests' %}",
    'parents.html': "{% url 'pages:parents' %}",
    'programs.html': "{% url 'pages:programs' %}",
    'aboutus.html': "{% url 'pages:about' %}",
}


def convert_links(html: str) -> str:
    for old, new in URL_MAP.items():
        html = html.replace(f'href="{old}"', f'href="{new}"')
    def static_img(match: re.Match) -> str:
        return 'src="{% static \'images/' + match.group(1) + '\' %}"'

    def static_js(match: re.Match) -> str:
        return 'src="{% static \'js/' + match.group(1) + '\' %}"'

    html = re.sub(r'src="images/([^"]+)"', static_img, html)
    html = re.sub(r'src="js/([^"]+)"', static_js, html)
    return html


def extract_main(html: str) -> tuple[str, str, str, list[str]]:
    title_m = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
    title = title_m.group(1).strip() if title_m else 'Eating Care Platform'

    body_m = re.search(r'<body([^>]*)>(.*)</body>', html, re.DOTALL)
    body_attrs = body_m.group(1).strip() if body_m else ''
    body = body_m.group(2) if body_m else html

    body_class = ''
    class_m = re.search(r'class="([^"]*)"', body_attrs)
    if class_m:
        body_class = class_m.group(1)

    header_end = body.find('</header>')
    footer_start = body.find('<footer class="footer">')
    if header_end == -1 or footer_start == -1:
        raise ValueError('Could not find header/footer boundaries')

    content = body[header_end + len('</header>') : footer_start].strip()

    extra_js = re.findall(r'<script src="js/([^"]+)"></script>', html)
    return title, body_class, content, extra_js


def build_template(title: str, body_class: str, content: str, extra_js: list[str]) -> str:
    lines = [
        '{% extends "base.html" %}',
        '{% load static %}',
        '',
        '{% block title %}' + title + '{% endblock %}',
    ]
    if body_class:
        lines.append('{% block body_attrs %} class="' + body_class + '"{% endblock %}')
    lines.extend(['', '{% block content %}', content, '{% endblock %}'])
    if extra_js:
        lines.extend(['', '{% block extra_js %}'])
        for js in extra_js:
            if js != 'main.js':
                lines.append('<script src="{% static \'js/' + js + '\' %}"></script>')
        lines.append('{% endblock %}')
    return '\n'.join(lines) + '\n'


def main():
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    for src_name, (dst_name, _active) in PAGES.items():
        html = (HTML_DIR / src_name).read_text(encoding='utf-8')
        html = convert_links(html)
        title, body_class, content, extra_js = extract_main(html)
        content = convert_links(content)
        template = build_template(title, body_class, content, extra_js)
        (TEMPLATES_DIR / dst_name).write_text(template, encoding='utf-8')
        print(f'Created {dst_name}')


if __name__ == '__main__':
    main()
