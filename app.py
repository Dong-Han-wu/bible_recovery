from flask import Flask, render_template, request, send_file
import requests
from bs4 import BeautifulSoup
import ftfy
import csv
import codecs
from collections import OrderedDict
from urllib import parse
import os

app = Flask(__name__)

# 書名對應的縮寫
book_abbreviations = {
    "Matthew": "Mt",
    "Mark": "Mk",
    "Luke": "Lk",
    "John": "Jn",
    "Acts": "Ac",
    "Romans": "Rm",
    "1 Corinthians": "1C",
    "2 Corinthians": "2C",
    "Galatians": "Ga",
    "Ephesians": "Ep",
    "Philippians": "Pp",
    "Colossians": "Co",
    "1 Thessalonians": "1T",
    "2 Thessalonians": "2T",
    "1 Timothy": "1T",
    "2 Timothy": "2T",
    "Titus": "Tt",
    "Hebrews": "He",
    "James": "Ja",
    "1 Peter": "1P",
    "2 Peter": "2P",
    "1 John": "1J",
    "2 John": "2J",
    "3 John": "3J",
    "Jude": "Jd",
    "Revelation": "Rv"
}


# 根路由
@app.route('/', methods=['GET', 'POST'])
def index():
    log = []
    if request.method == 'POST':
        strong_number = request.form.get('strong_number')
        url = f'https://biblehub.com/greek/strongs_{strong_number}.htm'
        s = requests.session()
        response = s.get(url)
        log.append(
            f'Requesting URL: {url} - Status Code: {response.status_code}')

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            my_list = []
            for a in soup.find_all('a'):
                if "/greek" in a['href'] and f"_{strong_number}.htm" in a[
                        'href']:
                    my_list.append("https://biblehub.com" +
                                   parse.unquote(a['href']))

            my_list2 = []
            for greek in my_list:
                webPage3 = requests.get(greek)
                soup = BeautifulSoup(webPage3.text, 'html.parser')
                p_tag = soup.find_all("span", class_='encycheading')
                for item in p_tag:
                    greek_text = ftfy.fix_text(item.text)
                    my_list2.append(greek_text)

                for a in soup.find_all('a'):
                    verse_text = a.string
                    if "/text/" in a['href'] or "abbrev.htm" in a['href']:
                        my_list2.append(verse_text)

            # 替換書名為縮寫
            for i in range(len(my_list2)):
                for full_name, abbreviation in book_abbreviations.items():
                    my_list2[i] = my_list2[i].replace(full_name, abbreviation)

            # 移除重複項
            final_list = list(OrderedDict.fromkeys(my_list2))

            # Step 3: 開啟 CSV 文件以寫入
            csv_file_path = 'greek.csv'
            with codecs.open(csv_file_path, 'w',
                             encoding='utf-8-sig') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                for item in final_list:
                    wr.writerow([item])  # 將每個項目寫入同一欄位但不同列中

            log.append(f'Successfully created {csv_file_path}')

    return render_template('index.html', log=log)


@app.route('/download')
def download():
    csv_file_path = 'greek.csv'
    return send_file(csv_file_path,
                     as_attachment=True,
                     download_name='greek.csv',
                     mimetype='text/csv')


if __name__ == '__main__':
    app.run(debug=True)
