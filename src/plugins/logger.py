from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent
import os
import aiofiles
from datetime import datetime

# 这个插件优先级最高(1)，且不阻断(block=False)，确保能抓到每一句话
logger = on_message(priority=1, block=False)

@logger.handle()
async def _(event: MessageEvent):
    group_id = str(getattr(event, 'group_id', 'private'))
    user_id = str(event.user_id)
    msg = event.get_plaintext()
    
    log_dir = "chat_logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiofiles.open(f"{log_dir}/group_{group_id}.txt", mode="a", encoding="utf-8") as f:
        await f.write(f"[{time_str}] {user_id}: {msg}\n")
    
    # 偷偷在后台打印一下，让我们知道它在工作
    print(f"日志已记录: {group_id} - {user_id}")

    