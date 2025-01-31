import datetime
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv()

discord_url = os.getenv("DISCORD_URL")
url = "https://software.cbnu.ac.kr/sub0401"
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"}
CACHE_FILE = "sent_notices.txt"
res = requests.get(url, headers=headers)

soup = BeautifulSoup(res.text, "lxml")
notices = soup.find_all("td",attrs={"class":"title"})
times = soup.find_all("td",attrs={"class":"time"})
today = datetime.datetime.now().strftime("%Y.%m.%d")

# test_time = datetime.datetime.now()
# test_message = {"content":f"{test_time.strftime('%Y-%m-%d %H:%M:%S')}"} # github action 테스트코드
# requests.post(discord_url,data=test_message)

# 파일이 없을경우
if not os.path.exists(CACHE_FILE):
    with open(CACHE_FILE,"w",encoding="utf-8") as f:
        f.write(today + "\n")

# 기존에 보낸 공지 확인
with open(CACHE_FILE,"r",encoding="utf-8") as f:
    sent_notices = f.read().splitlines()

if sent_notices:
    last_update_date = sent_notices[0]
else:
    last_update_date = ""

# 하루마다 파일 내용 초기화
if last_update_date != today:
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        f.write(today + "\n")
    sent_notice = []
else:
    sent_notice = sent_notices[1:]

# 오늘 올라온 공지글이고 이전에 보낸적이 없다면 메세지 전송
for notice, time in zip(notices,times):
    link = notice.a["href"]
    time = time.get_text().strip()

    if notice.a.find("span"):
        notice_title = notice.span.get_text()
    else:
        notice_title = notice.a.get_text(strip=True)

    if time == today and notice_title not in sent_notice:
        message = f"📢 **{notice_title}**\n📅 {time}\n🔗 [공지 확인]({link})"
        data = {"content":message}

        requests.post(discord_url,data=data)

        with open(CACHE_FILE,"a",encoding="utf-8") as f:
            f.write(notice_title + "\n")


#테스트 코드
# first_link = notices[0].a["href"]
# first_time = times[0].get_text()
# first_title = notices[0].a.get_text()
# message = f"📢 **{first_title}**\n📅 {first_time}\n🔗 [공지 확인]({first_link})"
# print(message)
# data = {"content" : message}
# today = datetime.datetime.now().strftime("%Y.%m.%d")
# if first_time == today:
#     requests.post(discord_url,data=data)
# else:
#     print("not today")