import os
import time
import json
from pathlib import Path
import requests
from bs4 import BeautifulSoup

OUT_DIR = Path(r"路徑") #自己改
DATES = [
    "2013-10-01","2013-12-17","2014-03-25","2014-05-27","2014-09-23","2014-12-23",
    "2015-03-24","2015-05-26","2015-10-06","2015-12-22","2016-03-22","2016-05-24",
    "2016-10-04","2016-12-20","2017-03-28","2017-05-23","2017-09-26","2017-12-19",
    "2018-03-27","2018-05-29","2018-10-02","2018-12-18","2019-03-26","2019-05-28",
    "2019-09-24","2019-12-17","2020-05-26","2020-06-09","2020-10-20","2020-12-22",
    "2021-03-23","2021-10-19","2021-12-21","2022-03-22","2022-05-24","2022-10-18",
    "2022-12-13","2023-03-21","2023-05-23","2023-10-17","2023-12-12",
    "2024-04-23","2024-05-21","2024-10-15","2024-12-10","2025-03-25","2025-05-20","2025-09-30"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PythonFetcher/1.0"
}

def fetch_page(url, timeout=15, retries=2, backoff=1.2):
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            return r
        except Exception as e:
            if attempt < retries:
                time.sleep(backoff * (attempt + 1))
            else:
                raise

def parse_scoreboard(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"id": "scoreboard"}) or soup.find("table")
    if not table:
        return None
    rows = table.find_all("tr")
    items = []
    for tr in rows:
        tds = tr.find_all("td")
        if len(tds) < 4:
            continue
        rank = tds[0].get_text(strip=True) if len(tds) > 0 else ""
        school = tds[1].get_text(strip=True) if len(tds) > 1 else ""
        name = tds[2].get_text(strip=True) if len(tds) > 2 else ""
        solved = tds[3].get_text(strip=True) if len(tds) > 3 else ""
        minutes = tds[4].get_text(strip=True) if len(tds) > 4 else ""
        items.append({
            "排名": rank,
            "學校": school,
            "姓名": name,
            "題數": solved,
            "分鐘": minutes
        })
    return items

def save_json(date, data, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"{date}.json"
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    print("輸出資料夾:", OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for idx, date in enumerate(DATES, start=1):
        out_file = OUT_DIR / f"{date}.json"
        if out_file.exists():
            print(f"[{idx}/{len(DATES)}] {date} 已存在，跳過")
            continue

        url = f"https://cpe.mcu.edu.tw/cpe/scoreboard/{date}"
        print(f"[{idx}/{len(DATES)}] 抓取 {url} ...")
        try:
            resp = fetch_page(url)
        except Exception as e:
            print(f" 無法連線: {e}")
            continue

        if resp.status_code != 200:
            print(f"HTTP {resp.status_code}，跳過")
            continue

        parsed = parse_scoreboard(resp.text)
        if parsed is None or len(parsed) == 0:
            print("為空")
            parsed = []

        try:
            save_json(date, parsed, OUT_DIR)
            print(f"儲存:{out_file}")
        except Exception as e:
            print(f"儲存失敗:{e}")

        time.sleep(1.2) #怕太快會被告

    print("完成", OUT_DIR)

if __name__ == "__main__":
    main()
