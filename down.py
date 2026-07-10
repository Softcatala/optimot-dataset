import requests
import time
import os
from bs4 import BeautifulSoup

BASE_URL = "https://aplicacions.llengua.gencat.cat/llc/AppJava/index.html"
OUTPUT_DIR = "downloaded_pages"
MAX_ID = 65535
DELAY = 0.5  # seconds


def replace_breaks_preserving_children(soup):
    for br in soup.find_all("br"):
        if list(br.children):
            br.insert_before("\n")
            br.unwrap()
        else:
            br.replace_with("\n")


def extract_fitxa_text(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Find the header span with "Fitxa"
    fitxa_header = soup.find('span', string=lambda text: text and text.strip().startswith("Fitxa"))
    if not fitxa_header:
        return "Fitxa section not found."

    # Collect all relevant content starting from the containing element
    content = []
    current = fitxa_header.find_parent()

    while current and 'Classificació' not in current.get_text():
        content.append(current)
        current = current.find_next_sibling()

    # Join the HTML of the collected content
    full_html = ''.join(str(tag) for tag in content)

    # Pre-process line breaks and paragraph tags
    soup = BeautifulSoup(full_html, 'html.parser')

    # Replace <br> with newline without losing children from malformed HTML.
    replace_breaks_preserving_children(soup)

    # Add newlines after paragraphs and headings
    for tag in soup.find_all(['p', 'h3', 'h4', 'div']):
        tag.append('\n')

    # Now extract the text
    text = soup.get_text()

    # Normalize whitespace: remove extra newlines and spaces
    lines = [line.strip() for line in text.split('\n')]
    cleaned_text = '\n'.join(line for line in lines if line)

    return cleaned_text


def fetch_page(idFont):
    params = {
        "action": "Principal",
        "method": "detall",
        "input_cercar": "",
        "numPagina": "1",
        "database": "FITXES_PUB",
        "idFont": str(idFont),
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        text = response.text
        return text
    except requests.RequestException as e:
        print(f"Error fetching ID {idFont}: {e}")
        return None

def save_page(content, idFont):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = os.path.join(OUTPUT_DIR, f"page_{idFont}.html")
    filename_txt = os.path.join(OUTPUT_DIR, f"page_{idFont}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
        
    text = extract_fitxa_text(content)
    with open(filename_txt, "w", encoding="utf-8") as f:
        f.write(text)
        

def main():
    for i in range(1, MAX_ID + 1):
        print(f"Fetching page {i}...")
        content = fetch_page(i)
        if content:
            save_page(content, i)
#        time.sleep(DELAY)

if __name__ == "__main__":
    main()
