from flask import Flask, render_template_string, send_file, request
from parser import parse_page, parse_article_page
import os

app = Flask(__name__)

# HTML-шаблон для интерфейса
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Выпуски</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 50px;
        }
        select, h2, h3, ul {
            margin: 20px auto;
            width: 50%;
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        a {
            text-decoration: none;
            color: #007BFF;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>Выпуски</h1>
    <select id="h2-select" onchange="updateH3()">
        <option value="">Выберите том</option>
        {% for h2 in data %}
            <option value="{{ h2 }}">{{ h2 }}</option>
        {% endfor %}
    </select>

    <div id="h3-section" style="display: none;">
        <h2 id="h2-title"></h2>
        <select id="h3-select" onchange="updateContent()">
            <option value="">Выберите выпуск</option>
        </select>
    </div>

    <div id="content-section" style="display: none;">
        <h3 id="h3-title"></h3>
        <ul id="ul-list"></ul>
        <a id="h3-link" href="#" style="display: none;">Перейти к выпуску</a>
    </div>

    <script>
        const data = {{ data|tojson }};

        function updateH3() {
            const h2Select = document.getElementById('h2-select');
            const h3Section = document.getElementById('h3-section');
            const h3Select = document.getElementById('h3-select');
            const h2Title = document.getElementById('h2-title');

            if (h2Select.value) {
                h2Title.textContent = h2Select.value;
                h3Section.style.display = 'block';
                h3Select.innerHTML = '<option value="">Выберите выпуск</option>';
                Object.keys(data[h2Select.value]).forEach(h3 => {
                    const option = document.createElement('option');
                    option.value = h3;
                    option.textContent = h3;
                    h3Select.appendChild(option);
                });
            } else {
                h3Section.style.display = 'none';
                document.getElementById('content-section').style.display = 'none';
            }
        }

        function updateContent() {
            const h2Select = document.getElementById('h2-select');
            const h3Select = document.getElementById('h3-select');
            const contentSection = document.getElementById('content-section');
            const ulList = document.getElementById('ul-list');
            const h3Title = document.getElementById('h3-title');
            const h3Link = document.getElementById('h3-link');

            if (h3Select.value) {
                h3Title.textContent = h3Select.value;
                contentSection.style.display = 'block';
                ulList.innerHTML = '';
                h3Link.style.display = 'none';

                const h3Data = data[h2Select.value][h3Select.value];
                if (h3Data.items) {
                    // Если есть <ul>, отображаем список
                    h3Data.items.forEach(item => {
                        const li = document.createElement('li');
                        const a = document.createElement('a');
                        a.href = "#";
                        a.textContent = item.text;
                        a.onclick = () => downloadArticle(h2Select.value, h3Select.value, item.text, item.href);
                        li.appendChild(a);
                        ulList.appendChild(li);
                    });
                } else {
                    // Если нет <ul>, отображаем ссылку из <h3>
                    h3Link.href = "#";
                    h3Link.textContent = `Перейти к выпуску: ${h3Select.value}`;
                    h3Link.style.display = 'block';
                    h3Link.onclick = () => downloadArticle(h2Select.value, h3Select.value, h3Select.value, h3Data.link);
                }
            } else {
                contentSection.style.display = 'none';
            }
        }

        async function downloadArticle(h2, h3, liText, url) {
            const response = await fetch(`/download?h2=${encodeURIComponent(h2)}&h3=${encodeURIComponent(h3)}&li=${encodeURIComponent(liText)}&url=${encodeURIComponent(url)}`);
            if (response.ok) {
                const blob = await response.blob();
                const link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                link.download = `${h2}. ${h3}. ${liText}.txt`;
                link.click();
            } else {
                alert('Ошибка при загрузке статьи');
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    data = parse_page()
    return render_template_string(HTML_TEMPLATE, data=data)

@app.route('/download')
def download():
    h2 = request.args.get('h2')
    h3 = request.args.get('h3')
    li_text = request.args.get('li')
    url = request.args.get('url')

    articles = parse_article_page(url)
    if not articles:
        return "Не удалось получить данные", 404

    # Формируем текстовый файл
    text = ""
    for article in articles:
        text += f"Авторы:\n{article['author']}\n\n"
        text += f"Название:\n{article['title']}\n\n"
        text += f"Ссылка:\n{article['href']}\n\n"
        text += "=" * 50 + "\n\n"

    # Сохраняем в временный файл
    filename = f"{h2}. {h3}. {li_text}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)

    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)