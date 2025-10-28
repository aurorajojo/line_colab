# emotion_dashboard.py
# ===== 情緒儀表板的生成 ===== 

from datetime import datetime
from collections import Counter
from linebot.v3.messaging import FlexMessage, FlexContainer
import json
from mongo import history_collection
from datetime import datetime, timedelta

"""
根據使用者的歷史對話紀錄，產生情緒儀表板，分析使用者的情緒組成
為了讓情緒分析結果更有親和力，我們替每一種情緒設計了一個對應角色
"""

# === 情緒角色 ===
EMOTION_CHARACTERS = {
    "焦慮": "🐇 小兔子焦焦",
    "悲傷": "🐟 小魚淚淚",
    "憤怒": "🔥 火爆熊熊",
    "恐懼": "🦔 小刺蝟皮皮",
    "厭惡": "🐸 青蛙嘔嘔",
    "羞愧": "🦊 小狐狸羞羞",
    "滿足": "🐼 圓滾熊熊",
    "驚訝": "🐿️ 小松鼠驚驚",
    "興奮": "🐶 狗狗蹦蹦",
    "冷靜": "🐢 烏龜淡淡",
    "無法判斷": "🧊 空殼寶寶"
}

# === 不同情緒的顏色（背景色 / 長條顏色） ===
EMOTION_COLORS = {
    "焦慮": ("#b39ddb", "#7e57c2"),   # 紫色系
    "悲傷": ("#64b5f6", "#1e88e5"),   # 藍色系
    "憤怒": ("#ff3a3a", "#c62828"),   # 紅色系
    "恐懼": ("#90a4ae", "#546e7a"),   # 灰色系
    "厭惡": ("#aed581", "#689f38"),   # 綠色系
    "羞愧": ("#f28d52", "#ef6c00"),   # 橘色系
    "滿足": ("#413e3e", "#212121"),   # 黑灰系
    "驚訝": ("#fec269", "#f9a825"),   # 黃色系
    "興奮": ("#be6c0e", "#e65100"),   # 深橘系
    "冷靜": ("#0aa944", "#2e7d32"),   # 綠色系
    "無法判斷": ("#CFD8DC", "#90A4AE") # 淺灰系
}

def generate_text_dashboard(user_id):
    """
    依據使用者的歷史紀錄，生成情緒儀表板 FlexMessage
    """

    # 取得一週前的日期
    today = datetime.now() 
    one_week_ago = today - timedelta(days=7)

    # 查詢過去七天的紀錄
    user_data = list(history_collection.find({
        "user_id": user_id,
        "timestamp": {"$gte": one_week_ago, "$lte": today}  # 只取最近七天
    }))
    
    # === 如果沒有對話紀錄，回傳提示訊息 ===
    if not user_data:
        return FlexMessage(
            alt_text="情緒儀表板",
            contents=FlexContainer.from_json(json.dumps({
                "type": "bubble",
                "body": {"type": "box", "layout": "vertical", "contents":[
                    {"type": "text", "text": "查無對話紀錄，無法產生儀表板。", "wrap": True}
                ]}
            }))
        )

    # === 統計情緒出現次數 ===
    emotion_counter = Counter()
    for doc in user_data:
        emo = doc.get("emotion", "").strip()  # 取出紀錄中的情緒標籤
        if emo and emo != "無法判斷":  # 過濾掉「無法判斷」
            emotion_counter[emo] += 1   # 累計情緒次數

    # === 如果沒有情緒標記，回傳提示訊息 ===
    if not emotion_counter:
        return FlexMessage(
            alt_text="情緒儀表板",
            contents=FlexContainer.from_json(json.dumps({
                "type": "bubble",
                "body": {"type": "box", "layout": "vertical", "contents":[
                    {"type": "text", "text": "沒有明確的情緒標記，無法產生儀表板。", "wrap": True}
                ]}
            }))
        )

    # === 只取出現次數前12大的情緒 ===
    sorted_emotions = emotion_counter.most_common(11)
    total = sum(emotion_counter.values())  # 總情緒數量（計算比例用）

    bubbles = []  # 儲存每個情緒的 bubble
    for emo, count in sorted_emotions:
        percent = round(count / total * 100)  # 計算該情緒的百分比
        character = EMOTION_CHARACTERS.get(emo, "❓")  # 找對應角色
        bg_color, bar_color = EMOTION_COLORS.get(emo, ("#27ACB2", "#0D8186"))  # 找顏色

        # === 建立單一情緒的 bubble 卡片 ===
        bubble = {
            "type": "bubble",
            "size": "micro",  # 使用 micro 大小，適合多張卡片並列
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    # 顯示角色
                    {"type": "text", "text": character, "color": "#ffffff", "align": "start", "size": "md","wrap": True},
                    # 顯示比例 %
                    {"type": "text", "text": f"{percent}%", "color": "#ffffff", "align": "start", "size": "xs", "margin": "lg", "align": "center"},
                    # 進度條（長條圖）
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type":"filler"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [],
                                "backgroundColor": bar_color,  # 進度條顏色
                                "height": f"{percent}%"
                            }
                        ],
                        "backgroundColor": "#FFFFFF4D",  # 外框背景
                        "width": "20px",
                        "height": "100px",
                        "margin": "sm",
                        "paddingTop": "md",
                        "offsetStart": "60px",
                        "cornerRadius": "6px"
                    }
                ],
                "backgroundColor": bg_color,  # 卡片上方背景色
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    # 顯示情緒名稱
                    {"type": "text", "text": emo, "color": "#8C8C8C", "size": "sm", "wrap": True}
                ],
                "paddingAll": "24px"
            },
            "styles": {"footer": {"separator": False}}
        }
        bubbles.append(bubble)


    intro_bubble = {
        "type": "bubble",
        "size": "micro",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": (
                        "情緒儀表板\n"
                    ),
                    "wrap": True,
                    "size": "md",
                    "weight": "bold"
                },
                {
                    "type": "separator",
                    "margin": "sm"
                },
                {
                    "type": "text",
                    "text": (
                        "以下是您過去七天對話中出現的所有情緒。\n"
                        "進度條代表該情緒出現的比例。\n"
                        "看看誰陪你最久，順便回顧自己的心情，也別忘了給自己一些關心～"
                    ),
                    "wrap": True,
                    "size": "sm",
                    "color": "#555555"
                }
            ]
        }
    }

    bubbles = [intro_bubble] + bubbles  # 將介紹 bubble 放在最前面

    # === 建立 carousel（多張情緒卡片組成） ===
    flex_json = {"type": "carousel", "contents": bubbles}

    # === 回傳 FlexMessage ===
    return FlexMessage(
        alt_text="情緒儀表板",
        contents=FlexContainer.from_json(json.dumps(flex_json))
    )
