import openai
import os
import httpx
import base64
import json
from datetime import datetime
from nonebot import on_message, get_driver
from nonebot.adapters.onebot.v11 import MessageEvent, Message, Bot
from nonebot.rule import Rule
from nonebot.exception import FinishedException

# --- 配置区 ---
config = get_driver().config
api_key = getattr(config, "moonshot_api_key", "")

client = openai.OpenAI(
    api_key=api_key, 
    base_url="https://api.moonshot.cn/v1",
)

chat_history = {}
MAX_HISTORY = 10 
LOG_DIR = "chat_logs"
HISTORY_PATH = "chat_history.json" 
FAVOR_PATH = "favorability.json"   
favor_data = {}

# --- 工具函数 ---
def save_history():
    try:
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(chat_history, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"记日记失败了呜: {e}")

def load_history():
    global chat_history
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                chat_history = json.load(f)
            print("对话记忆加载成功喵！")
        except: pass

def load_favor():
    global favor_data
    if os.path.exists(FAVOR_PATH):
        try:
            with open(FAVOR_PATH, "r", encoding="utf-8") as f:
                favor_data = json.load(f)
            print("心动档案加载成功喵！")
        except: pass

load_history()
load_favor()

# --- 触发规则定义 ---
def is_baka_mentioned(event: MessageEvent) -> bool:
    if event.is_tome():
        return True
    return "baka" in event.get_plaintext().lower()

# block=False 允许其他插件（比如 logger, img_saver）继续运行
handle_ai = on_message(rule=Rule(is_baka_mentioned), priority=10, block=False)

@handle_ai.handle()
async def _(bot: Bot, event: MessageEvent):
    session_id = event.get_session_id()
    user_id = str(event.user_id)
    user_name = event.sender.nickname or "主人"
    
    # 好感度校验
    raw_score = favor_data.get(user_id, 0)
    try:
        current_score = int(raw_score) if not isinstance(raw_score, dict) else 0
    except:
        current_score = 0

    limit_hint = " ⚠回复限制：极其简短，绝对不能超过20个字！"

    if current_score > 500:
        rel_level, behavior = "至死不渝", "你超级爱TA，极度依赖且爱撒娇。" + limit_hint
    elif current_score > 200:
        rel_level, behavior = "情投意合", "TA是你最好的知己，说话随性亲昵。" + limit_hint
    else:
        rel_level, behavior = "普通朋友", "语气礼貌温柔，是个笨笨的猫猫。" + limit_hint

    dynamic_system_content = (
        f"你名为baka。说话用“咱”“baka”称呼。回复常加上颜文字。不用表情。{behavior} "
        f"当前说话的是【{user_name}】，关系【{rel_level}】。"
    )

    # --- 核心修复：更鲁棒的消息获取 ---
    user_text = event.get_plaintext().strip()
    if not user_text:
        # 如果纯文本为空，尝试获取原始消息的字符串表示（包含表情等文字描述）
        user_text = str(event.get_message()).strip()
    
    if not user_text:
        user_text = "[动作]" # 最后的兜底，绝不让 API 拿到空字符串

    if session_id not in chat_history:
        chat_history[session_id] = []
    
    # 构建记忆：第一条始终是最新的 system
    new_history = [{"role": "system", "content": dynamic_system_content}]
    
    # 过滤旧消息并严格检查 content 不为空
    old_messages = [
        m for m in chat_history[session_id] 
        if m["role"] != "system" and m.get("content") and str(m["content"]).strip()
    ]
    new_history.extend(old_messages[-(MAX_HISTORY-1):])
    
    # 放入当前消息
    new_history.append({"role": "user", "content": user_text})
    chat_history[session_id] = new_history

    try:
        completion = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=chat_history[session_id],
            temperature=0.6, 
            max_tokens=70,   
        )
        
        reply = completion.choices[0].message.content.strip()
        if not reply:
            reply = "baka不知道该说什么喵..."

        chat_history[session_id].append({"role": "assistant", "content": reply})
        save_history() 
        
        await handle_ai.finish(reply)

    except FinishedException:
        pass
    except Exception as e:
        print(f"AI 出错啦: {e}")
        # 如果报错了，清理一下当前的历史记录，防止坏数据卡死
        chat_history[session_id] = []
        await handle_ai.finish("呜呜，baka的脑子刚才短路了，记忆已经重置了喵...")