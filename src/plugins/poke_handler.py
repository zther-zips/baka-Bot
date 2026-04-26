import random
import openai
from nonebot import on_notice, get_driver
from nonebot.adapters.onebot.v11 import Bot, PokeNotifyEvent
from .ai_chat import chat_history, client

# 优先级设为 10
poke_action = on_notice(priority=10)

@poke_action.handle()
async def _(bot: Bot, event: PokeNotifyEvent):
    if event.is_tome():
        session_id = f"group_{event.group_id}" if event.group_id else f"private_{event.user_id}"
        
        # 1. 检查有没有最近的聊天记忆
        if session_id in chat_history and len(chat_history[session_id]) > 1:
            try:
                # 拿最近的两条对话当背景，让 AI 决定怎么回戳
                recent_msgs = chat_history[session_id][-2:]
                prompt = f"用户刚才和你聊了这些内容。现在他戳了你一下，请作为baka给出一个非常简短（20字以内）、语气软萌的反应。刚才的对话：{recent_msgs}"
                
                response = client.chat.completions.create(
                    model="moonshot-v1-8k",
                    messages=[
                        {"role": "system", "content": "你现在是被戳中的状态。根据之前的聊天氛围，给出一个可爱、温柔的简短回应。"},
                        {"role": "user", "content": prompt}
                    ]
                )
                reply_text = response.choices[0].message.content
            except:
                # 如果 AI 宕机了，就用咱们的保底随机库喵
                reply_text = "呜哇！不要乱戳人家啦... 痒痒的喵~"
        else:
            #第一次默认喵
            responses = [
            "呜哇！不要乱戳人家啦... 痒痒的喵~",
            "唔... 刚才那一下，是在和咱打招呼吗？",
            "（缩进被窝）再戳的话，咱也要戳回去了哦！",
            "诶？是在找咱聊天吗喵？",
            "呜... 感觉脑袋晕乎乎的，一定是刚才戳baka太重了喵！",
            "别、别戳了，再戳就要变笨了喵...",
            "（歪头）笨笨是不是想咱了喵？",
            "戳一下 50 块，记得给baka扫码转账喵！",
            "咱正在梦里吃小鱼干呢，都被你戳醒了喵呜...",
            "笨蛋... 这种打招呼的方式好奇怪喵~"
            ]
            reply_text = random.choice(responses)
        
        
        await poke_action.finish(reply_text)