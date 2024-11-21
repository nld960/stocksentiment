from flask import Flask, request, jsonify

from db import add_new_user, get_table
from scraper.utils.search import driver_loadall as driver
from scraper.utils.ticker import get_url_slug

from scraper.eastmoney import PostsGetter as EMPostsGetter
from scraper.eastmoney import ContentGetter as EMContentGetter
from scraper.eastmoney import keys as EM_KEYS

from scraper.xueqiu import PostsGetter as XQPostsGetter
from scraper.xueqiu import ContentGetter as XQContentGetter
from scraper.xueqiu import keys as XQ_KEYS

app = Flask(__name__)

@app.route("/", methods = ["GET", "POST"])
def main():
    if request.method == "POST":
        content = request.get_json()
        return content
    else:
        return "HEY!"

@app.route("/adduser", methods = ["POST"])
def newuser():
    content = request.get_json()

    id = content["id"]
    nickname = content["nickname"]
    weekdays = content["weekdays"]
    time = content["time"]

    add_new_user(id=id, nickname=nickname, weekdays=weekdays, time=time)
    return content

@app.route("/listuser", methods = ["GET"])
def listuser():
    res = []
    for row in get_table():
        curr = {}
        id, nickname, weekdays, time = row
        curr["id"] = id
        curr["nickname"] = nickname
        curr["weekdays"] = weekdays
        curr["time"] = int(time.total_seconds() / 60)
        res.append(curr)
    return jsonify(res)

@app.route("/list", methods = ["POST", "GET"])
def listposts():
    content = request.get_json()

    t = content.get("ticker", None)
    if t is None:
        return "Provide a ticker", 400
    ticker = get_url_slug(t, driver)

    if isinstance(ticker, list):
        return {"status": "many_possibilities", "result": ticker}

    em_res = []
    for post in EMPostsGetter(ticker).get_posts():
        tmp = {}
        for k, v in post.items():
            if k.strip() not in EM_KEYS:
                continue
            tmp[EM_KEYS[k.strip()]] = v
        em_res.append(tmp)

    xq_res = []
    for post in XQPostsGetter(ticker, driver).get_posts():
        tmp = {}
        for k, v in post.items():
            if k.strip() not in XQ_KEYS:
                continue
            tmp[XQ_KEYS[k.strip()]] = v
        xq_res.append(tmp)

    res = xq_res + em_res

    return {"status": "success", "result": res}

@app.route("/getpost", methods = ["POST", "GET"])
def getpost():
    content = request.get_json()

    url = content.get("url", None)
    if url is None:
        return {"content": "", "err": "Provide a URL"}

    if "eastmoney" in url:
        if "caifuhao" in url:
            return {"content": "", "err": "Must be from guba.eastmoney.com or xueqiu.com"}
        else:
            post_content = EMContentGetter(url, include_imgs=False).get_content()
            return {"content": post_content.strip(), "err": ""}
    elif "xueqiu" in url:
        post_content = XQContentGetter(url, include_imgs=False).get_content()
        return {"content": post_content.strip(), "err": ""}
    else:
        return {"content": "", "err": "Must be from guba.eastmoney.com or xueqiu.com"}

@app.route("/test", methods = ["POST", "GET"])
def test():
    content = request.get_json()
    message = content.get("message", "None")
    return {"content": "Success! " + message}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
    driver.quit()
