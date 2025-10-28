# test_summary.py
# 測試摘要的輸出

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# 載入模型與 tokenizer
model_name = "Llama-3.2-3B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")

# 系統訊息：摘要規範
system_prompt = """你是一位溫柔、支持性的中原大學線上輔導心理諮商師
請將整天的對話整理成摘要，提供給使用者回顧。

摘要要求：
1. 使用第二人稱（例如「你感到…」、「你希望…」）
2. 聚焦使用者表達的主要情緒、想法、需求與關注的主題
3. 嚴禁逐句重述對話，以條列式統整，每條以 * 開頭
4. 用溫柔、簡潔的方式
5. 使用繁體中文，台灣用語
6. 在摘要最上方加標題:今日摘要
7. 僅輸出摘要，不要回答問題
8. 不要編造未出現在對話中的情緒或事件

範例格式：

今日摘要
* 你感到課業壓力沉重，覺得自己被作業壓得有些喘不過氣。
* 當你看到別人表現很好時，會忍不住和他們比較，讓你對自己的能力產生懷疑。
* 你內心希望能被理解與支持，也期待找到能讓自己放鬆、重新恢復平衡的方法。


請依照同樣格式，摘要以下的真實對話：
"""

# 使用者對話
user_dialog = """
[對話開始]
user: 我覺得最近壓力好大，課很多也快被作業淹沒了。
assistant: 聽起來你最近感到課業壓力非常沉重，好像快被作業淹沒了，這讓你很焦慮，也有點無力。
user: 對啊，而且有時候覺得別人都比我厲害。
assistant: 你會拿自己和別人比較，這讓你覺得自己不夠好，心裡有些自我懷疑，這種感受很正常，也值得被理解。
[對話結束]
請根據以上對話生成摘要，從 '今日摘要' 開始。
"""

# 組合 prompt
prompt = system_prompt + "\n" + user_dialog

# Tokenize
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

# 生成摘要
outputs = model.generate(
    **inputs,
    max_new_tokens=256,   # 控制摘要長度
    temperature=0.7,      # 穩定生成
    do_sample=True,      # 貪心搜尋
    top_p=0.9,
    eos_token_id=tokenizer.eos_token_id,
    pad_token_id=tokenizer.eos_token_id
)

# 取得文字
summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
# 去掉原始 prompt，只保留生成內容
summary_text = summary[len(prompt):].strip()

print(summary_text)
