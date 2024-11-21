from bs4 import BeautifulSoup
import re

from .utils._time import parse_date, is_within_range
from .utils.search import get_html

DOMAIN_NAME = "https://quote.eastmoney.com"
URL = "https://gbfek.eastmoney.com/deploy/article_list/work/article_list.html?code={}&ba_show=false&count=18&stock_type=true"

keys = {
    '阅读': "metric1",
    '评论': "metric2",
    '作者': "author",
    '最后更新': "time",
    'href': "link",
    '标题': "heading"
}

class PostsGetter:
    def __init__(self, id):
        if re.match(r"^[A-Za-z]{2}\d{5,6}$", id):
            id = id[2:]
        if not id.isnumeric():
            id = "us" + id.upper() # ex: usBABA
        else:
            if len(id) == 5:
                id = "hk" + id

        self.id = id
        self.soup = BeautifulSoup()
        self.url = URL.format(id)

    def get_posts(self):
        raw_html = get_html(self.url)
        self.soup = BeautifulSoup(raw_html, "html.parser")

        res = self._get_posts_table_from_stock_page()
        return self._sort_by_views(res)

    def _sort_by_views(self, post_data: list):
        return sorted(post_data, key=lambda a: a["最后更新"], reverse=True)

    def _get_posts_table_from_stock_page(self):
        res = []

        try:
            table = self.soup.find(id="articlelistnew")
            header = table.find("div", class_="dheader")
            schema = [col.text for col in header.find_all("span")]
            divs = table.find_all("div", class_="normal_post")
        except AttributeError:
            table = self.soup.find("table", class_="body_table")
            header = table.find("thead")
            schema = [col.text.strip() for col in header.find_all("td")]
            divs = table.find_all("tr", class_="articlerow")

        # loop through divs (1 for each article)
        for d in divs:
            stop = False
            curr = {}
            columns = d.find_all("td")
            # loop through cols (article attrs)
            for i, col in enumerate(columns):
                if col.find("a") is not None:
                    curr[schema[i]] = col.find("a").text.strip()
                else:
                    curr[schema[i]] = col.text.strip()
                if schema[i] == "标题":
                    href = col.find("a").get("href")
                    if "caifuhao" in href:
                        # curr["href"] = "http:" + href
                        stop = True
                        break
                    else:
                        curr["href"] = href
                if schema[i] == "最后更新":
                    date = curr[schema[i]]
                    if not is_within_range(parse_date(date)):
                        stop = True
                        break
            if not stop:
                res.append(curr)

        return res

# !-------

class ContentGetter:
    def __init__(self, url, include_imgs):
        self.url = url
        self.include_imgs = include_imgs

    def extract_text(self, element):
        result = ""
        
        if element.name is None:  # Text
            return str(element)

        elif element.name == "img" and self.include_imgs:  # Image
            src = element.get("src", "")
            alt = element.get("alt", "")
            result += f"![{alt}]({src})"

        elif element.name == "a" and self.include_imgs:  # Link
            href = element.get("href", "")
            text = element.get_text()
            result += f"[{text}]({href})"
        else:    
            for child in element.children:
                result += self.extract_text(child)

        return result

    def get_content(self):
        raw_html = get_html(self.url)
        soup = BeautifulSoup(raw_html, "html.parser")

        article_div = soup.find('div', id='zw_body')
        if article_div is None:
            article_div = soup.find("div", id="post_content")
        if article_div is None:
            article_div = soup.find("div", class_="newstext")

        result = self.extract_text(article_div)
        return result
