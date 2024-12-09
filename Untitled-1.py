import discord  # Discord API 的主要套件
import json  # 用於讀取設定檔
from datetime import datetime, timedelta  # 用於追蹤冷卻時間

# 從 JSON 文件中載入設定
with open('py.json', 'r', encoding='utf-8') as jfile:
    config_data = json.load(jfile)

# 提及功能狀態（初始為關閉）
mention_feature_enabled = False

# 冷卻時間（秒）
COOLDOWN_TIME = 180  # 3 分鐘

# 紀錄用戶的最後提及時間
cooldown_tracker = {}

# 設定 Discord bot
intents = discord.Intents.default()
intents.message_content = True  # 確保可以讀取訊息內容
client = discord.Client(intents=intents)

# 檢查是否為管理員用戶的輔助函式
def has_permission(user_id):
    return user_id == config_data['admin_user_id']

@client.event
# 當機器人完成啟動
async def on_ready():
    print(f"目前登入身份 --> {client.user}")
    game = discord.Game('努力學習discord.py中')
    #discord.Status.<狀態>，可以是online,offline,idle,dnd,invisible
    await client.change_presence(status=discord.Status.idle, activity=game)

# 當收到訊息時觸發的事件
@client.event
async def on_message(message):
    global mention_feature_enabled

    # 排除機器人本身的訊息
    if message.author == client.user:
        return

    # 開啟功能指令（只能由特定管理員觸發）
    if message.content.lower() == "!enable":
        if has_permission(message.author.id):  # 檢查是否為指定管理員用戶
            mention_feature_enabled = True
            await message.channel.send("提及功能已啟用！")
        else:
            await message.channel.send(f"{message.author.mention}你沒有權限啟用此功能。")
        return

    # 關閉功能指令（只能由特定管理員觸發）
    if message.content.lower() == "!disable":
        if has_permission(message.author.id):  # 檢查是否為指定管理員用戶
            mention_feature_enabled = False
            await message.channel.send("提及功能已關閉！")
        else:
            await message.channel.send(f"{message.author.mention}你沒有權限關閉此功能。")
        return

    # 提及檢查
    if mention_feature_enabled and message.mentions:
        mentioned_user = message.mentions[0]  # 取得第一個被提及的用戶

        # 如果提及的是特定 ID 用戶（例如「貓貓」）
        if mentioned_user.id == config_data['target_user_id']:
            current_time = datetime.now()
            user_id = message.author.id  # 發送訊息的用戶 ID

            # 檢查是否在冷卻時間內
            if user_id in cooldown_tracker:
                last_trigger_time = cooldown_tracker[user_id]
                if current_time - last_trigger_time < timedelta(seconds=COOLDOWN_TIME):
                    # 冷卻時間未到，不觸發
                    return

            # 更新最後觸發時間
            cooldown_tracker[user_id] = current_time

            # 發送回應訊息
            reply_content = f"{message.author.mention} 他可能睡死了或者在忙 3分鐘後他無回應請再次tag他"
            await message.channel.send(reply_content)
    if message.content.lower()=="stop bot":
        print("收到指令，準備斷線...")
        await message.channel.send("Bot 斷線中...")
        await client.close()

# 啟動機器人（使用從 JSON 載入的 Token）
client.run(config_data['TOKEN'])
