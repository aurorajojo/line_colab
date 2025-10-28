# config.py
# ===== 儲存各種設定值與金鑰 =====

import os
from dotenv import load_dotenv

# 嘗試載入 google.colab.userdata（若在 Colab 以外環境不會出錯）
try:
    from google.colab import userdata
except ImportError:
    userdata = None

# 載入 .env（適用本地開發）
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_env(name: str, default: str = "") -> str:
    """優先順序：Colab userdata > .env > 系統環境變數"""
    if userdata is not None:
        value = userdata.get(name)
        if value:
            return value
    return os.getenv(name, default)

# ===== 設定值 =====
# LINE Bot 設定
CHANNEL_SECRET = get_env("LINE_CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = get_env("LINE_CHANNEL_ACCESS_TOKEN")

# MongoDB 連線字串
MONGODB_URI = get_env("MONGODB_URI")

# 資源檔案路徑
PROMPT_FILE = os.path.join(BASE_DIR, 'data', 'system_prompt.txt')
SUM_PROMPT = os.path.join(BASE_DIR, 'data', 'summary_prompt.txt')
RESOURCE_FILE = os.path.join(BASE_DIR, 'data', 'cycu_resources.json')
EVENTS_FILE = os.path.join(BASE_DIR, 'data', 'events.json')
