import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11_Adapter

nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11_Adapter)

# --- 必须加上这一行，机器人才能识别到 src/plugins ---
nonebot.load_plugins("src/plugins") 

if __name__ == "__main__":
    nonebot.run()