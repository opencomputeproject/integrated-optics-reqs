"""Render the GitHub and browser views from the editable sources in data/."""

import argparse
from datetime import date
from html import escape
import json
from pathlib import Path
import re
from string import Template


ROOT = Path(__file__).resolve().parents[1]
URL_PATTERN = re.compile(r"(https?://|www\.)[^\s<]+?(?=[.,]?(?:\s|$))")


def load(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def html_value(value):
    lines = value.splitlines()
    if all(line.startswith("• ") for line in lines):
        return '<ul class="cell-list">' + "".join(f"<li>{escape(line[2:])}</li>" for line in lines) + "</ul>"
    return "<br>".join(map(escape, lines))


def paragraphs_html(paragraphs):
    def link(match):
        url = match[0]
        href = url if url.startswith("http") else f"https://{url}"
        return f'<a href="{href}">{url}</a>'

    return "\n".join(
        f"<p>{URL_PATTERN.sub(link, escape(text))}</p>"
        for text in paragraphs
    )


def note_link(option):
    number = option.get("note")
    return f'<sup><a href="#note-{number}" aria-label="Terminology note {number}">{number}</a></sup>' if number else ""


def matrix_html(contribution, data):
    locations, families, options = data["locations"], data["families"], data["options"]
    family_location = {family["id"]: family["location"] for family in families}
    family_size = {family["id"]: sum(o["family"] == family["id"] for o in options) for family in families}
    cols = ['<col class="criterion-column">']
    location_headers = ['<th rowspan="2" id="location" class="criterion">Location</th>']
    family_headers = []
    option_headers = ['<th id="name" scope="col" class="criterion">Name</th>']

    for location in locations:
        key = location["id"]
        size = sum(family_size[f] for f, loc in family_location.items() if loc == key)
        location_headers.append(
            f'<th colspan="{size}" id="loc-{key}" data-location="{key}">{escape(location["name"])}</th>'
        )
    for family in families:
        key = family["id"]
        family_headers.append(
            f'<th colspan="{family_size[key]}" id="family-{key}" data-family="{key}" class="family">'
            f'{escape(family["name"])}<small>{escape(family["placement"])}</small></th>'
        )
    for option in options:
        key, family = option["id"], option["family"]
        cols.append(f'<col class="option-column" data-family="{family}">')
        option_headers.append(
            f'<th id="col-{key}" data-family="{family}" scope="col" class="option">'
            f'<span>{escape(option["name"])}</span>{note_link(option)}'
            f'<small>{escape(option["description"])}</small></th>'
        )

    rows = []
    for criterion in data["criteria"]:
        key = criterion["id"]
        cells = [f'<th scope="row" id="row-{key}" class="criterion">{escape(criterion["name"])}</th>']
        if key == "standards":
            for family in families:
                group = family["id"]
                members = " ".join(f'col-{o["id"]}' for o in options if o["family"] == group)
                cells.append(
                    f'<td colspan="{family_size[group]}" data-family="{group}" '
                    f'headers="row-{key} loc-{family_location[group]} family-{group} {members}">'
                    f'{html_value(family["standards"])}</td>'
                )
        else:
            for option in options:
                group = option["family"]
                cells.append(
                    f'<td data-family="{group}" headers="row-{key} loc-{family_location[group]} '
                    f'family-{group} col-{option["id"]}">{html_value(option["values"][key])}</td>'
                )
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return "\n".join([
        f'<table class="matrix"><caption class="visually-hidden">{escape(contribution["tableCaption"])}</caption>',
        "<colgroup>" + "".join(cols) + "</colgroup>",
        '<thead><tr class="locations">' + "".join(location_headers) + "</tr>",
        "<tr>" + "".join(family_headers) + "</tr>",
        "<tr>" + "".join(option_headers) + "</tr></thead>",
        "<tbody>", *rows, "</tbody></table>",
    ])


def option_cards_html(data):
    families = {family["id"]: family for family in data["families"]}
    cards = []
    for option in data["options"]:
        key, group = option["id"], option["family"]
        family = families[group]
        values = dict(option["values"], standards=family["standards"])
        properties = [
            f'<div><dt>{escape(criterion["name"])}</dt><dd>{html_value(values[criterion["id"]])}</dd></div>'
            for criterion in data["criteria"]
        ]
        cards.append(
            f'<details class="option-card" data-family="{group}" data-option="{key}" id="option-{key}">'
            f'<summary><span><strong>{escape(option["name"])}</strong>'
            f'<span class="option-description">{escape(option["description"])}</span></span></summary>'
            f'<div class="option-details"><p>{escape(family["name"])}{note_link(option)}</p>'
            f'<dl>{"".join(properties)}</dl>'
            f'<a class="source-link" href="#illustrations" data-figure="{key}">See placement <span aria-hidden="true">↗</span></a>'
            "</div></details>"
        )
    return "\n".join(cards)


def markdown_table(data):
    options = data["options"]
    families = {family["id"]: family for family in data["families"]}
    locations = {location["id"]: location["name"] for location in data["locations"]}

    def row(values):
        escaped = [escape(str(value), quote=False).replace("|", r"\|").replace("\n", "<br>") for value in values]
        return "| " + " | ".join(escaped) + " |"

    names = [o["name"] + (f' [{o["note"]}]' if "note" in o else "") for o in options]
    rows = [
        row(["Criterion", *names]),
        row(["---"] * (len(options) + 1)),
        row(["Location", *(locations[families[o["family"]]["location"]] for o in options)]),
        row(["Family", *(families[o["family"]]["name"] for o in options)]),
        row(["Name", *(o["description"] for o in options)]),
    ]
    for criterion in data["criteria"]:
        key = criterion["id"]
        rows.append(row([criterion["name"], *(
            families[o["family"]]["standards"] if key == "standards" else o["values"][key] for o in options
        )]))
    return "\n".join(rows)


def write_views(check):
    contribution, data = load("contribution.json"), load("optical-options.json")
    drafted = date.fromisoformat(contribution["date"])
    date_display = f"{drafted:%B} {drafted.day}, {drafted.year}"
    filters = "".join(
        f'<button type="button" data-filter="{escape(f["id"])}" '
        f'aria-label="{escape(f["name"])}" aria-pressed="false">{escape(f["id"].upper())}</button>'
        for f in data["families"]
    )
    notes_html = "<ol>" + "".join(
        f'<li id="note-{n["number"]}">{escape(n["text"])}</li>' for n in data["notes"]
    ) + "</ol>"
    template = Template((ROOT / "src" / "index.html").read_text(encoding="utf-8"))
    site = template.substitute(
        title=escape(contribution["title"]),
        version=escape(contribution["version"]), date=contribution["date"], date_display=date_display,
        author=escape(contribution["author"]), affiliation=escape(contribution["affiliation"]),
        filters=filters, matrix=matrix_html(contribution, data),
        option_cards=option_cards_html(data), option_count=len(data["options"]), notes=notes_html,
        introduction=escape(contribution["introduction"]), license_title=escape(contribution["licenseTitle"]),
        license_text=paragraphs_html(contribution["licenseText"]), about_title=escape(contribution["aboutTitle"]),
        about_text=paragraphs_html(contribution["aboutText"]),
    )
    notes_md = "\n".join(f'{n["number"]}. {n["text"]}' for n in data["notes"])
    draft = "\n\n".join([
        "<!-- Generated from data/contribution.json and data/optical-options.json by scripts/build.py. -->",
        f'# {contribution["title"]}',
        f'Workstream draft {contribution["version"]} · {date_display}\n\n'
        f'{contribution["author"]}, {contribution["affiliation"]}',
        "## Introduction", contribution["introduction"],
        "## Optical Connectivity Options",
        f'*{contribution["tableCaption"]}*',
        markdown_table(data), "### Terminology notes", notes_md,
        "## Illustrations",
        "![Side and top views of six optics placements with a component legend](docs/assets/placement-options.png)",
        f'*{contribution["figureCaption"]}*',
        "[Editable side-view SVG](docs/assets/naming-drawings.svg)",
        "## License", f'### {contribution["licenseTitle"]}', *contribution["licenseText"],
        f'## {contribution["aboutTitle"]}', *contribution["aboutText"],
    ]) + "\n"

    stale = []
    for file, content in [("docs/index.html", site), ("contribution.md", draft)]:
        path = ROOT / file
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(file)
        else:
            path.write_text(content, encoding="utf-8")
    if stale:
        raise SystemExit(f"Regenerate {', '.join(stale)} with python3 scripts/build.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if a generated file is out of date")
    write_views(parser.parse_args().check)
