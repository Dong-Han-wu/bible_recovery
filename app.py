from flask import Flask, render_template, send_file
import requests
from bs4 import BeautifulSoup
import openpyxl
from io import BytesIO

app = Flask(__name__)

# 你的書籍資料和爬取函數
def get_chapter_links(book_code):
    url = f"https://text.recoveryversion.bible/{book_code}_1.htm"
    response = requests.get(url)
    chapter_links = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        chapter_elements = soup.select('.chapter-links a')

        if not chapter_elements:
            chapter_links.append((book_code, "1"))
        else:
            for chapter in chapter_elements:
                chapter_num = chapter.text
                chapter_links.append((book_code, chapter_num))
    return chapter_links

def scrape_verses(book_code, chapter):
    url = f"https://text.recoveryversion.bible/{book_code}_{chapter}.htm"
    response = requests.get(url)

    verses = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        verse_elements = soup.select('p.verse')

        for verse in verse_elements:
            verse_text = verse.get_text(strip=True)
            verses.append(verse_text)
    return verses

# 書名和代碼
books = {
    "40_Matthew": "馬太福音",
    "41_Mark": "馬可福音",
    # ... 其他書籍
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download')
def download():
    # 建立 Excel 文件
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Bible Verses"
    
    # 寫入表頭
    ws.append(['Chapter', 'Verse'])
    
    # 爬取所有書的經文
    for book_code, book_name in books.items():
        chapter_links = get_chapter_links(book_code)
        for _, chapter in chapter_links:
            verses = scrape_verses(book_code, chapter)
            for verse in verses:
                ws.append([f"{book_name} {chapter}", verse])

    # 將 Excel 保存到 BytesIO 中
    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    # 下載 Excel 文件
    return send_file(file_stream, as_attachment=True, download_name='bible_recovery_version.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    app.run(debug=True)
