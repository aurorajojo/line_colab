# event_utils.py
# - 回傳最近10個藝文活動資訊(名稱、日期、時間、連結)

import json
from datetime import datetime, timedelta
import json
from linebot.v3.messaging import FlexMessage, FlexContainer
from resources import events

def load_upcoming_events():


    now = datetime.now()   # 台灣時間
    upcoming = []
    for e in events:
        try:
            dt = datetime.strptime(e["date"], "%Y-%m-%d")
            if dt > now:  # 還沒過期
                upcoming.append(e)
        except Exception as ex:
            print(f"日期格式錯誤 {e}: {ex}")
            continue

    # 依日期排序 & 取最近10個
    upcoming.sort(key=lambda x: x["date"])
    return upcoming[:10]


def events_to_flex(events):
    bubbles = []
    # === 第一個 bubble：介紹===
    intro_bubble = {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "即將到來的藝文活動", "weight": "bold", "size": "xl", "wrap": True},
                {"type": "separator", "margin": "md"},
                {"type": "text",
                 "text": "參加藝文活動可以：\n"
                         "1. 舒緩壓力與焦慮\n"
                         "2. 提升正向情緒與幸福感\n"
                         "3. 增進社交互動與人際連結\n"
                         "4. 培養專注力與創造力\n"
                         "趕快來參加一個活動看看吧～\n",
                 "size": "sm",
                 "wrap": True,
                 "color": "#555555",
                 "margin": "sm"}
            ]
        }
    }
    bubbles.append(intro_bubble)

    for e in events:
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": e.get("title", "未命名活動"), "weight": "bold", "size": "xl", "wrap": True},
                    {"type": "separator","margin": "md"},
                    {"type": "text", "text": f"📅 日期：{e.get('date', '')}", "size": "sm", "color": "#555555", "wrap": True, "margin": "sm"},
                    {"type": "text", "text": f"⏰ 時間：{e.get('time', '')}", "size": "sm", "color": "#555555", "wrap": True, "margin": "sm"},
                    {"type": "text", "text": f"🏫 地點：{e.get('location', '未提供')}", "size": "sm", "color": "#555555", "wrap": True,"margin": "sm"}
                ]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "詳細資訊",
                            "uri": e.get("url", "https://cycu.edu.tw")
                        },
                        "style": "primary",
                        "color": "#8D8684"
                    }
                ]
            }
        }
        bubbles.append(bubble)

    bubbles =  {
        "type": "carousel",
        "contents": bubbles
    }
    return FlexMessage(
        altText="活動列表",
        contents=FlexContainer.from_json(json.dumps(bubbles))
    )