import requests
from bs4 import BeautifulSoup
import json

def parse_article_page(url):
    """Парсит страницу статьи и извлекает данные из <div class="entry-con">."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    entry_con = soup.find('div', class_='entry-con')
    if not entry_con:
        return None

    articles = []
    for p in entry_con.find_all('p'):
        strong = p.find('strong')
        link = p.find('a')
        if strong and link:
            author = strong.text.strip()
            title = link.text.replace(strong.text, '').strip()  # Убираем текст из <strong>
            href = f"https://esj.today/{link['href']}"  # Форматируем ссылку
            articles.append({
                'author': author,
                'title': title,
                'href': href
            })

    return articles

def parse_page():
    """Парсит основную страницу и извлекает данные."""
    url = "https://esj.today/issues.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    container = soup.find('div', id='container')
    if not container:
        return {}

    data = {}
    current_h2 = None
    current_h3 = None

    for element in container.find_all(['h2', 'h3', 'ul']):
        if element.name == 'h2':
            current_h2 = element.text.strip()
            data[current_h2] = {}
            current_h3 = None  # Сбрасываем текущий h3 при смене h2

        elif element.name == 'h3' and current_h2:
            h3_text = element.text.strip()
            if h3_text:  # Проверяем, что h3 содержит текст
                h3_link = element.find('a')['href'] if element.find('a') else None
                data[current_h2][h3_text] = {'link': h3_link, 'items': None}
                current_h3 = h3_text

        elif element.name == 'ul' and current_h2:
            if current_h3 in data[current_h2]:  # Проверяем, что h3 существует
                if data[current_h2][current_h3]['items'] is None:
                    data[current_h2][current_h3]['items'] = []
                for li in element.find_all('li'):
                    link = li.find('a')
                    if link:
                        data[current_h2][current_h3]['items'].append({
                            'text': link.text.strip(),
                            'href': link['href']
                        })

    # Вывод отладочной информации
    print(json.dumps(data, ensure_ascii=False, indent=4))
    return data

if __name__ == "__main__":
    print(parse_page())
