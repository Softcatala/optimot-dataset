import os
import re
import json
from bs4 import BeautifulSoup

SOURCE = "Optimot, Departament de Política Lingüística, Generalitat de Catalunya"
SOURCE_URL_TEMPLATE = (
    "https://aplicacions.llengua.gencat.cat/llc/AppJava/index.html"
    "?action=Principal&method=detall&input_cercar=&numPagina=1"
    "&database=FITXES_PUB&idFont={source_id}"
)
DOWNLOAD_DATE = "2026-07-08"


def normalize_category_text(parts):
    text = ""
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part == ".":
            text = text.rstrip() + ". "
        else:
            text += part + " "
    return " ".join(text.split())


def extract_category_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.find(
        lambda tag: tag.name == "h5" and tag.get_text(" ", strip=True) == "Categoria"
    )
    if not heading:
        return ""

    category_list = heading.find_next_sibling(
        lambda tag: tag.name == "div" and "SCL_llista" in tag.get("class", [])
    )
    if not category_list:
        return ""

    category_nodes = category_list.find_all("div", class_="FW_titBullet", recursive=False)
    if not category_nodes:
        category_nodes = [category_list]

    categories = []
    seen = set()
    for node in category_nodes:
        category = normalize_category_text(node.stripped_strings)
        if category and category not in seen:
            seen.add(category)
            categories.append(category)

    return "; ".join(categories)


def extract_category_from_file(filepath):
    html_path = re.sub(r"\.txt$", ".html", filepath)
    if not os.path.exists(html_path):
        return ""

    with open(html_path, "r", encoding="utf-8") as f:
        return extract_category_from_html(f.read())


def extract_info_from_text(text):
    fitxa_match = re.search(r"Fitxa\s+(\d+/\d+)", text)
    versio_match = re.search(r"Darrera versió:\s*([0-9.]+)", text)
    titol_match = re.search(r"Títol\s+(.*?)(?=\s+Resposta)", text, re.DOTALL)
    resposta_match = re.search(r"Resposta\s+(.*)", text, re.DOTALL)

    return {
        "Fitxa": fitxa_match.group(1) if fitxa_match else "",
        "Darrera versió": versio_match.group(1) if versio_match else "",
        "Títol": titol_match.group(1).strip() if titol_match else "",
        "Categoria": "",
        "Resposta": resposta_match.group(1).strip() if resposta_match else ""
    }

def source_id_from_filename(filename):
    match = re.fullmatch(r"page_(\d+)\.txt", filename)
    return match.group(1) if match else ""

def add_provenance(info, filename):
    source_id = source_id_from_filename(filename)
    return {
        **info,
        "source": SOURCE,
        "source_id": source_id,
        "source_url": SOURCE_URL_TEMPLATE.format(source_id=source_id) if source_id else "",
        "download_date": DOWNLOAD_DATE,
    }

def process_directory(directory):
    all_entries = []
    seen_entries = set()
    for filename in sorted(os.listdir(directory), key=lambda name: int(source_id_from_filename(name) or 0)):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
                info = extract_info_from_text(text)
                info["Categoria"] = extract_category_from_file(filepath)
                entry_key = tuple(info.items())
                if entry_key in seen_entries:
                    continue
                seen_entries.add(entry_key)
                all_entries.append(add_provenance(info, filename))
    return all_entries

def main():
    directory = "downloaded_pages"
    output_file = "optimot.jsonl"

    data = process_directory(directory)

    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"JSONL file written to {output_file} with {len(data)} entries.")


if __name__ == "__main__":
    main()
