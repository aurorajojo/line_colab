# llm.py
# ===== 呼叫 Groq API（ llama-3.3-70b-versatile 模型）回應使用者輸入 =====


from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# 模型路徑
MODEL_PATH = "meta-llama/Llama-3.2-3B-Instruct"
SUMMARY_MODEL_PATH = "meta-llama/Llama-3.2-3B-Instruct"  # 可使用同一模型做摘要

# 載入 tokenizer 和模型
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, torch_dtype=torch.bfloat16, device_map="auto")

summary_tokenizer = AutoTokenizer.from_pretrained(SUMMARY_MODEL_PATH)
summary_model = AutoModelForCausalLM.from_pretrained(SUMMARY_MODEL_PATH, torch_dtype=torch.bfloat16, device_map="auto")


def call_groq_llm(messages, max_new_tokens=128, temperature=0.7):
    system_prompt = ""
    user_content = ""

    # 分開處理 system 與 user 的內容
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "system":
            system_prompt += content.strip() + "\n"
        elif role == "user":
            user_content += f"user: {content.strip()}\n"

    # 組成最終 prompt（系統規則 + 對話內容）
    prompt = f"{system_prompt}\n以下是使用者的輸入：\n{user_content}\nassistant:"

    inputs = summary_tokenizer(prompt, return_tensors="pt").to(summary_model.device)
    outputs = summary_model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=True,  # 開啟隨機取樣，避免重複
        top_p=0.9,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id
    )

    full_text = summary_tokenizer.decode(outputs[0], skip_special_tokens=True)

    # 只取出 assistant 的回答部分
    if "assistant:" in full_text:
        response = full_text.split("assistant:")[-1].strip()
    else:
        response = full_text.strip()

    print(response)
    return response


# 封裝摘要函式
def call_summary_llm(messages, max_new_tokens=512, temperature=0.7):
    prompt = ""
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        prompt += f"{role}: {content}\n"

    inputs = summary_tokenizer(prompt, return_tensors="pt").to(summary_model.device)
    outputs = summary_model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=True  ,
        top_p=0.9,
        eos_token_id=summary_tokenizer.eos_token_id
    )
    response = summary_tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response[len(prompt):].strip()
    
