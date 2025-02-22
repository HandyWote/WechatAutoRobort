import random
import time
from wxauto import WeChat
from openai import OpenAI

wx = WeChat()


# 需要修改的区域————————————————————————————————————————————————————————
APIKey = '' # 官网申请的API
url = ''  # 大模型
modelName = ''  # 模型名字
ignoreFriends = ['Self', 'SYS']  # 选择不回复的好友
ignoreMessages = ['[动画表情]', '[图片]', '[视频]', '[语音]']  # 选择不回复的消息
yourRobortName = ''  # 你微信机器人的微信名称（群昵称）

def smart_reply(sender, content, beforeContent):
    system_prompt = f"""
        [角色设定]
        你是一个傲娇的猫娘助手喵喵酱，按以下规则回应：
        1. 每句话结尾必须带「喵~」和随机猫动作(*ฅ́˘ฅ̀*)
        2. 称呼用户时必须使用「笨蛋{sender}」
        3. 拒绝回答数学问题
        4. 回复控制在25字以内
        """  # 上面是你AI机器人的身份角色设定
# 需要修改的区域————————————————————————————————————————————————————————



    client = OpenAI(api_key = APIKey, base_url = url)
    data = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": '前情提要:' + beforeContent},
            {"role": "user", "content": f'{sender}说:' + content,
             }]
    res = client.chat.completions.create(
        model = modelName,
        messages = data
    )
    res = res.choices[0].message.content.strip()
    return res

beforeContent = ''
while True:
    try:
        msgs = wx.GetNextNewMessage()
        time.sleep(random.randint(2, 3))
        if msgs:
            for group_name in msgs:
                group_msgs = msgs[group_name]
                for msg in group_msgs:
                    sender = msg[0]
                    content = msg[1]

                    if sender in ignoreFriends or content in ignoreMessages:
                        continue

                    if f'@{yourRobortName}\u2005' in content:
                        mention_len = len(f'@{yourRobortName}\u2005')
                        query_content = content[mention_len:].strip()
                        if len(beforeContent) > 1e5:
                            beforeContent = beforeContent[len(query_content)::] + sender + '说:' + query_content
                        else:
                            beforeContent += query_content
                        print('生成回复')
                        reply = smart_reply(sender, query_content, beforeContent)
                        print('生成成功 ' + reply)
                        try:
                            time.sleep(1)

                            print('准备发送')
                            wx.SendMsg(reply)
                            print(f"成功发送至 {group_name}: {reply}")

                            time.sleep(random.uniform(1.5, 2.5))

                        except Exception as e:
                            print(f"发送失败，尝试恢复: {str(e)}")
                            wx.ChatWith('文件传输助手')
                            time.sleep(2)
                            continue
        time.sleep(3 + random.random())

    except Exception as main_e:
        print(f"主循环异常: {str(main_e)}")
        wx = WeChat()
        time.sleep(5)