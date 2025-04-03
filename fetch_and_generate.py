import requests
from bs4 import BeautifulSoup
from datetime import datetime

# [게시판 주소 및 설정]
url = "https://aict.snu.ac.kr/?p=92"
base_url = "https://aict.snu.ac.kr"
post_base = "https://aict.snu.ac.kr/?p=92&page=1&viewMode=view&reqIdx="

# [게시판 요청]
res = requests.get(url)
soup = BeautifulSoup(res.text, "html.parser")

# [게시물 5개 추출]
items = soup.select(".gallery_list li")[:5]
now = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0900")

rss_items = ""

# [RSS 아이템 생성]
for item in items:
    title_tag = item.select_one("span.title a")
    title = title_tag.text.strip()

    # ✅ 링크 형식 오류 해결
    raw_href = title_tag["href"]
    if "reqIdx=" in raw_href:
        req_idx = raw_href.split("reqIdx=")[-1]
    elif "idx=" in raw_href:
        req_idx = raw_href.split("idx=")[-1]
    else:
        req_idx = raw_href[-18:]  # fallback

    fixed_link = post_base + req_idx

    img_tag = item.select_one("span.photo img")
    img_url = base_url + img_tag["src"] if img_tag else ""

    rss_items += f"""
  <item>
    <title>{title}</title>
    <link>{fixed_link}</link>
    <pubDate>{now}</pubDate>
    <description><![CDATA[
      <img src="{img_url}" width="500"><br>
      <a href="{fixed_link}">{title}</a>
    ]]></description>
  </item>
"""

rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>AICT 게시판 최신 5개</title>
  <link>{url}</link>
  <description>서울대 AICT 최근 게시물</description>
  <lastBuildDate>{now}</lastBuildDate>
{rss_items}
</channel>
</rss>"""

with open("feed.xml", "w", encoding="utf-8") as f:
    f.write(rss)

# [HTML 생성]
rss_soup = BeautifulSoup(rss, "xml")
items = rss_soup.find_all("item")

cards = ""
for item in items:
    title = item.title.text
    link = item.link.text.strip().replace("&", "&amp;")
    img_tag = BeautifulSoup(item.description.text, "html.parser").find("img")
    img = img_tag["src"] if img_tag else ""

    cards += f'''
    <a href="{link}" target="_blank" style="text-decoration: none; color: black; width: 100px; text-align: center;">
      <img src="{img}" width="100" height="80" style="object-fit: cover; border-radius: 4px;">
      <div style="font-size: 11px; margin-top: 4px;">{title}</div>
    </a>
    '''

html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body>
<div style="display: flex; gap: 10px; font-family: sans-serif;">
  {cards}
</div>
</body>
</html>
"""

with open("latest.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ feed.xml + latest.html 생성 완료")
