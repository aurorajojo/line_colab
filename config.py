# config.py
# ===== 儲存各種設定值與金鑰 =====

import os
from dotenv import load_dotenv

# 載入 .env
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))



# 資源檔案路徑
PROMPT_FILE = os.path.join(BASE_DIR, 'data', 'system_prompt.txt')
SUM_PROMPT = os.path.join(BASE_DIR, 'data', 'summary_prompt.txt')
RESOURCE_FILE = os.path.join(BASE_DIR, 'data', 'cycu_resources.json')
EVENTS_FILE = os.path.join(BASE_DIR, "data", "events.json")

