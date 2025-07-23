from bs4 import BeautifulSoup

def clean_html(text: str) -> str:
    return BeautifulSoup(text, "html.parser").get_text()
