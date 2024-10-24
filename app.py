from flask import Flask, render_template, send_file
import requests
from bs4 import BeautifulSoup
import openpyxl
from io import BytesIO

app = Flask(__name__)


# 爬取函數
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
    "42_Luke": "路加福音",
    "43_John": "約翰福音",
    "44_Acts": "使徒行傳",
    "45_Romans": "羅馬書",
    "46_1Corinthians": "哥林多前書",
    "47_2Corinthians": "哥林多後書",
    "48_Galatians": "加拉太書",
    "49_Ephesians": "以弗所書",
    "50_Philippians": "腓立比書",
    "51_Colossians": "歌羅西書",
    "52_1Thessalonians": "帖撒羅尼迦前書",
    "53_2Thessalonians": "帖撒羅尼迦後書",
    "54_1Timothy": "提摩太前書",
    "55_2Timothy": "提摩太後書",
    "56_Titus": "提多書",
    "57_Philemon": "腓利門書",
    "58_Hebrews": "希伯來書",
    "59_James": "雅各書",
    "60_1Peter": "彼得前書",
    "61_2Peter": "彼得後書",
    "62_1John": "約翰壹書",
    "63_2John": "約翰貳書",
    "64_3John": "約翰參書",
    "65_Jude": "猶大書",
    "66_Revelation": "啟示錄"
}


@app.route('/')  # 根路由
def index():
    return render_template('index.html')  # 渲染模板


@app.route('/download')  # 下載路由
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
    return send_file(
        file_stream,
        as_attachment=True,
        download_name='bible_recovery_version.xlsx',
        mimetype=
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


if __name__ == '__main__':
    app.run(debug=True)  # 啟動應用程式
