import os
import sys
from pathlib import Path
from bs4 import BeautifulSoup, Comment
import json
from typing import List, Dict

def extract_text_from_html(html_content: str) -> str:
    soup = BeautifulSoup(html_content, 'html.parser')
    
    for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
        comment.extract()
    
    for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
        element.decompose()
    
    main_content = soup.find("div", class_="document")
    if main_content:
        text = main_content.get_text()
    else:
        text = soup.body.get_text() if soup.body else soup.get_text()
    
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk and 
                    not chunk.startswith("Navigation") and
                    not chunk.startswith("Next") and
                    not chunk.startswith("Previous") and
                    not chunk.startswith("© Copyright") and
                    not chunk.startswith("Built with") and
                    not chunk.startswith("Note:") and
                    not chunk.startswith("Note ") and
                    not chunk.startswith("Warning:") and
                    not chunk.startswith("Warning ") and
                    not chunk.startswith("Important:") and
                    not chunk.startswith("Important "))
    
    return text

def process_docs(docs_dir: str) -> List[str]:
    documents = []
    docs_path = Path(docs_dir)
    
    for html_file in docs_path.rglob("*.html"):
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            text = extract_text_from_html(content)
            if text.strip():
                documents.append(text)
        except Exception as e:
            print(f"Error processing {html_file}: {str(e)}")
    
    return documents

if __name__ == "__main__":
    docs_dir = sys.argv[1] if len(sys.argv) > 1 else "/mnt/d/lfx/rtdocs"
    
    print(f"Processing documents from: {docs_dir}")
    documents = process_docs(docs_dir)
    
    output_file = "processed_docs.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"documents": documents}, f, indent=2)
    
    print(f"Processed {len(documents)} documents. Saved to {output_file}") 