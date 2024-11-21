from bs4 import BeautifulSoup
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from datetime import datetime, timedelta
from .utils._time import parse_date, is_within_range, fmt_date
from .utils.search import get_html

DOMAIN_NAME = "https://xueqiu.com"
URL = "https://xueqiu.com/S/{}"

keys = {
    '赞': "metric1",
    '评论': "metric2",
    '作者': "author",
    '最后更新': "time",
    'href': "link",
    '标题': "heading",
}

class PostsGetter:
    def __init__(self, id, driver):
        self.id = id
        self.url = URL.format(id)
        self.driver = driver
        self.soup = BeautifulSoup()

    def get_posts(self):
        self.driver.get(self.url)

        try:
            login_x_button = self.driver.find_element(By.XPATH, r'/html/body/div[1]/div[3]/div[1]/div[3]/a/i')
            login_x_button.click()
        except selenium.common.exceptions.NoSuchElementException:
            pass

        discuss_link = self.driver.find_element(By.LINK_TEXT, '讨论')
        discuss_link.click()

        wait = WebDriverWait(self.driver, 10)
        element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "status-list")))

        posts = []

        # loop until the first post outside date range
        page = 1
        while True:
            raw_html = self.driver.page_source
            self.soup = BeautifulSoup(raw_html, "html.parser")
            result, status = self._get_posts_table_from_stock_page()

            posts.extend(result)
            if status == -1:
                posts.sort(key=lambda a: a.get("最后更新", 0), reverse=True)
                return posts

            #try:
            #    next_page = self.driver.find_element(By.LINK_TEXT, '下一页')
            #    next_page.click()
            #except selenium.common.exceptions.NoSuchElementException:
            #    return posts
            return posts

            page += 1
#            print("Indexing Xueqiu page", page)
            wait = WebDriverWait(self.driver, 20)
            element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "status-list")))

    def _get_posts_table_from_stock_page(self):
        res = []
        table = self.soup.find("div", class_="status-list")

        articles = table.find_all("article", class_="timeline__item")
        for i in articles:
            curr = {}

            title = i.find("h3", class_="timeline__item__title")
            if title is None:
                content = i.find("div", class_="content--description").text
                content = re.sub(r"\$.*?\$", "", content)
                content = re.sub(r'<[^>]+>', "", content).strip() 
                curr['标题'] = "" if content is None else "\"" + content[:18] + "...\""
            else:
                title = re.sub(r"\$.*?\$", "", str(title))
                title = re.sub(r'<[^>]+>', "", title).strip()
                curr['标题'] = title
            
            date_source = i.find("a", class_="date-and-source")
            str_date = date_source.text.split("·")[0]
            date = fmt_date(str_date)
     
            if not is_within_range(parse_date(date)):
                return res, -1

            curr['最后更新'] = date

            href = date_source.attrs.get("href")
            curr['href'] = DOMAIN_NAME + href
            
            author = i.find("a", class_="user-name")
            curr['作者'] = author.text

            stats = i.find("div", class_="timeline__item__ft")
            for stat in stats.find_all("a"):
                matches = re.search(r"([\u4e00-\u9fff]+)\((\d+)\)", stat.text)
                if matches is not None:
                    curr[matches[1]] = int(matches[2])

            res.append(curr)

        return res, 0

# !-------

def fmt_image(img):
    alt = img.get("alt", "")
    src = img.get("src", "")

    return f"![{alt}]({src})"

def fmt_link(a):
    text = a.text
    href = a.get("href", "")

    return f"[{text}]({href})"

class ContentGetter:
    def __init__(self, url, include_imgs):
        self.url = url
        self.include_imgs = include_imgs

    def get_content(self):
        raw_html = get_html(self.url)
        soup = BeautifulSoup(raw_html, "html.parser")

        article_div = soup.find('div', {'class': 'article__bd__detail'})

        # initialize result content
        result_content = ""

        # define a function to recursively extract text and nested tags
        def extract_text(element):
            if element.name in ['p', 'strong', "h1", "h2", "h3", "h4", "h5", "h6"]:
                if element.get("style") and "display: none" in element["style"]:
                    return ""
                paragraph_text = ""
                for child in element.contents:
                    if child.name == 'img' and self.include_imgs:
                        paragraph_text += fmt_image(child)
                    elif child.name == 'a' and self.include_imgs:
                        paragraph_text += fmt_link(child)
                    elif child.name in ['strong', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        paragraph_text += extract_text(child)
                    elif child.name == "h-char":
                        paragraph_text += child.text
                    elif isinstance(child, str):
                        paragraph_text += child
                return paragraph_text + "\n\n"
            elif element.name == 'img' and self.include_imgs:
                return fmt_image(element) + "\n\n"
            elif element.name == 'a' and self.include_imgs:
                return fmt_link(element) + ""

        # iterate over all child elements of the article div
        for child in article_div.contents:
            if child.name == 'img' and self.include_imgs:
                result_content += fmt_image(child) + "\n\n"
            elif child.name == 'a' and self.include_imgs:
                result_content += fmt_link(child)
            elif child.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                result_content += extract_text(child)
            elif child.name == "h-char":
                result_content += child.text
            elif isinstance(child, str):
                result_content += child

        # print the result content
        return result_content
