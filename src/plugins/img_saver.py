import os
import httpx
from datetime import datetime
from nonebot import on_message
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent

# 设置图片保存的根目录，就在 baka 文件夹下
IMAGE_ROOT = "chat_images"

# 优先级设为 1，确保它能第一时间看到图片，不阻断(block=False)让 AI 也能看到
img_monitor = on_message(priority=1, block=False)

@img_monitor.handle()
async def handle_img_save(event: MessageEvent):
    # 1. 获取群号或私聊 ID 用来分文件夹
    if isinstance(event, GroupMessageEvent):
        folder_name = f"group_{event.group_id}"
    else:
        folder_name = f"private_{event.user_id}"
    
    # 2. 这里的路径就是：baka/chat_images/群号/
    save_path = os.path.join(IMAGE_ROOT, folder_name)
    
    # 3. 遍历消息里的所有段落，寻找图片
    for seg in event.message:
        if seg.type == "image":
            # 如果文件夹不存在就建一个
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            
            img_url = seg.data["url"]
            # 文件名：时间_随机后缀.jpg
            time_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            file_name = f"{time_str}.jpg"
            full_file_path = os.path.join(save_path, file_name)
            
            # 开始下载
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(img_url, timeout=10)
                    if resp.status_code == 200:
                        with open(full_file_path, "wb") as f:
                            f.write(resp.content)
                        print(f"成功保存图片到: {full_file_path} 喵！")
            except Exception as e:
                print(f"保存图片失败了喵: {e}")