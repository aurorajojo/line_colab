# weekly_summary.py
#- 輸出本周(七天以來)每日的摘要
#- 輸出使用者要查詢的指定日期摘要

from datetime import datetime, timedelta
from daily_summary import check_and_summarize
from mongo import summary_collection,history_collection
import json
from linebot.v3.messaging import FlexMessage, FlexContainer
import re

# 定義七個柔和七彩背景
colors = [
    "#FFEAEA",  # 超淺粉
    "#FFF9E5",  # 超淺黃
    "#F0FFE5",  # 超淺綠
    "#E5F9FF",  # 超淺藍
    "#F4E5FF",  # 超淺紫
    "#FFE5F2",  # 超淺桃
    "#FFF3E5"   # 超淺橙
]
def get_weekday_chinese(date: datetime) -> str:
    weekdays = ["(一)", "(二)", "(三)", "(四)", "(五)", "(六)", "(日)"]
    return weekdays[date.weekday()]  # weekday() 0=Monday

def generate_weekly_summary(user_id: str) -> FlexMessage:
    """
    產生一個 FlexMessage，包含過去七天的摘要
    """
    check_and_summarize(user_id)          # 幫上次諮商那天做摘要
    
    today = datetime.now()   # 台灣時區
    yesterday = today - timedelta(days=1)
    bubbles = []

    # 額外增加一個 bubble：查詢摘要
    query_bubble ={
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
            {
                "type": "text",
                "text": "以下是您過去七天的個別每日摘要，希望您能藉此回顧自己的心情與思緒，了解自己的狀態，也別忘了給自己一些關心或尋求協助。",
                "wrap": True,
                "weight": "bold",
                "size": "lg",
                "color": "#333333"
            },
            {
                "type": "separator",
                "margin": "md"
            },
            {
                "type": "text",
                "text": "如果想看更多摘要，點擊下方'查詢摘要'選擇要查詢摘要的日期",
                "wrap": True,
                "size": "sm",
                "color": "#555555"
            }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
            {
                "type": "button",
                "style": "primary",
                "action": {
                "type": "message",
                "label": "查詢摘要",
                "text": "查詢摘要"
                },
                "color": "#8D8684FF"
            }
            ]
        }
    }
    
    bubbles.append(query_bubble)  

    for i in range(7):
        day = yesterday - timedelta(days=i)
        date_str = day.strftime("%Y-%m-%d") + " " + get_weekday_chinese(day)

        # 從 MongoDB 找該日期的摘要
        summary_doc = summary_collection.find_one(
            {
                "user_id": user_id,
                "date": {"$gte": day.replace(hour=0, minute=0, second=0, microsecond=0),
                         "$lt": (day + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)}
            }
        )
        if summary_doc and "summary" in summary_doc:
            summary_text = summary_doc["summary"]
            if not summary_text.strip():  # 判斷是空字串
                summary_text = "對話太短，無法做出摘要"
            date_color = "#000000"  # 黑色（有資料）
            bg_color = colors[i % len(colors)]  # 循環使用七彩顏色
        else:
            summary_text = "尚無摘要"
            date_color = "#888888"  # 灰色（沒資料）
            bg_color = "#FFFFFF"  

        # 每一天做成一個 bubble
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": bg_color ,
                "contents": [
                    {
                        "type": "text",
                        "text": f"{date_str}",
                        "weight": "bold",
                        "size": "lg",
                        "color": date_color
                    },
                    {
                        "type": "text",
                        "text": summary_text,
                        "wrap": True,
                        "size": "sm",
                        "margin": "md",
                        "color": "#555555"
                    }
              
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": bg_color ,
                "contents": [
                {
                    "type": "image",
                    "url": "https://img.icons8.com/?size=100&id=26138&format=png&color=000000",
                    "size": "xxs",
                    "align": "end",
                    "action": {
                    "type": "message",
                    "label": "看對話",
                    "text": f"我要看{date_str}對話"
                    }
                }
                ]
            }
        }
        bubbles.append(bubble)
  

    # Carousel 裝七個 bubble
    flex_content = {
        "type": "carousel",
        "contents": bubbles  # 往前七天，顯示時由舊到新
    }

    return FlexMessage(
        altText="過去七天摘要",
        contents=FlexContainer.from_json(json.dumps(flex_content))  #  dict 轉成 FlexContainer
    )

def get_summary_by_date(user_id: str, chosen_date: str) -> FlexMessage:
    """
    查詢指定日期的摘要並回傳 FlexMessage
    chosen_date 格式: "YYYY-MM-DD"
    """
    try:
        # 將字串轉 datetime
        date_obj = datetime.strptime(chosen_date, "%Y-%m-%d")

    except ValueError:
        # 格式錯誤
        return FlexMessage(
            altText="日期格式錯誤",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "日期格式錯誤，請選擇正確日期", "wrap": True, "color": "#FF0000"}
                    ]
                }
            }
        )

    # 查詢 MongoDB
    summary_doc = summary_collection.find_one(
        {
            "user_id": user_id,
            "date": {
                "$gte": date_obj.replace(hour=0, minute=0, second=0, microsecond=0),
                "$lt": (date_obj + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            }
        }
    )

    if summary_doc and "summary" in summary_doc:
        summary_text = summary_doc["summary"]
        if not summary_text.strip():  # 判斷是空字串
            summary_text = "對話太短，無法做出摘要"
        date_color = "#000000"
    else:
        summary_text = "尚無摘要"
        date_color = "#888888"

    date_str = date_obj.strftime("%Y-%m-%d") + " " + get_weekday_chinese(date_obj)
    
    # 建立 FlexMessage
    bubble = {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": date_str, "weight": "bold", "size": "lg", "color": date_color},
                {"type": "text", "text": summary_text, "wrap": True, "size": "sm", "margin": "md", "color": "#555555"}
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "image",
                "url": "https://img.icons8.com/?size=100&id=26138&format=png&color=000000",
                "size": "xxs",
                "align": "end",
                "action": {
                "type": "message",
                "label": "看對話",
                "text": f"我要看{date_str}對話"
                }
            }
            ]
        }
    }

    return FlexMessage(
        altText=f"{chosen_date} 摘要",
        contents=FlexContainer.from_json(json.dumps(bubble))
    )

def get_daily_conversation_bubbles(user_id: str, date_str: str):
    """
    取得指定日期的完整對話，每組 user_input + reply 做成一個 bubble
    """
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    start = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    history = list(history_collection.find({
        "user_id": user_id,
        "timestamp": {"$gte": start, "$lt": end}
    }).sort("timestamp", 1))

    if not history:
        bubbles = [{
                        "type": "bubble",
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": f"{date_str} 沒有對話紀錄喔！", "wrap": True}
                            ]
                        }
                    }]
        flex_content = {
            "type": "carousel",
            "contents": bubbles
        }
        return  FlexMessage(
                    altText=f"{date_str} 對話",
                    contents=FlexContainer.from_json(json.dumps(flex_content))
                )
    
    bubbles = []
    for h in history:
        user_msg = h.get("user_input", "")
        bot_msg = h.get("reply", "")
        bot_msg = re.sub(r"[\(\[\{]\d+[\)\]\}]", "", bot_msg).strip()

        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {"type": "filler"},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [],
                            "cornerRadius": "30px",
                            "height": "12px",
                            "width": "12px",
                            "borderColor": "#EF454D",
                            "borderWidth": "2px"
                        },
                        {"type": "filler"}
                        ],
                        "flex": 0
                    },
                    {
                        "type": "text",
                        "gravity": "center",
                        "flex": 4,
                        "size": "sm",
                        "text": "👤 你: " if user_msg else "👤 你："
                    }
                    ],
                    "spacing": "lg",
                    "cornerRadius": "30px",
                    "margin": "xl"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                            {"type": "filler"},
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [],
                                "width": "2px",
                                "backgroundColor": "#B7B7B7"
                            },
                            {"type": "filler"}
                            ],
                            "flex": 1
                        }
                        ],
                        "width": "12px"
                    },
                    {
                        "type": "text",
                        "text": f"{user_msg}",
                        "wrap": True,
                        "gravity": "center",
                        "flex": 4,
                        "size": "xs",
                        "color": "#8c8c8c"
                    }
                    ],
                    "spacing": "lg"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {"type": "filler"},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [],
                            "cornerRadius": "30px",
                            "width": "12px",
                            "height": "12px",
                            "borderWidth": "2px",
                            "borderColor": "#6486E3"
                        },
                        {"type": "filler"}
                        ],
                        "flex": 0
                    },
                    {
                        "type": "text",
                        "text": "🤖 諮商師: " if bot_msg else "🤖 諮商師：",
                        "gravity": "center",
                        "flex": 4,
                        "size": "sm"
                    }
                    ],
                    "spacing": "lg",
                    "cornerRadius": "30px"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                            {"type": "filler"},
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [],
                                "width": "2px",
                                "backgroundColor": "#6486E3"
                            },
                            {"type": "filler"}
                            ],
                            "flex": 1
                        }
                        ],
                        "width": "12px"
                    },
                    {
                        "type": "text",
                        "text": f"{bot_msg}",
                        "gravity": "center",
                        "wrap": True,
                        "flex": 4,
                        "size": "xs",
                        "color": "#8c8c8c"
                    }
                    ],
                    "spacing": "lg"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {"type": "filler"},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [],
                            "cornerRadius": "30px",
                            "width": "12px",
                            "height": "12px",
                            "borderColor": "#6486E3",
                            "borderWidth": "2px"
                        },
                        {"type": "filler"}
                        ],
                        "flex": 0
                    }
                    ],
                    "spacing": "lg",
                    "cornerRadius": "30px"
                }
                ]
            }
        }

        bubbles.append(bubble)

    bubbles = {
        "type": "carousel",
        "contents": bubbles
    }

    return FlexMessage(
        altText=f"{date_str} 對話",
        contents=FlexContainer.from_json(json.dumps(bubbles))
    )