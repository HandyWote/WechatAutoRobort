import random
import time
import json
from wxauto import WeChat
from openai import OpenAI

wx = WeChat()


# 从配置文件加载配置
try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
        openai_config = config['openai']
        APIKey = openai_config['APIKey']
        url = openai_config['url']
        modelName = openai_config['modelName']
        yourRobortName = openai_config['yourRobortName']
        ignoreFriends = openai_config['ignoreFriends']
        ignoreMessages = openai_config['ignoreMessages']
        system_prompt_template = openai_config['system_prompt']
    print("成功加载配置文件")
except Exception as e:
    print(f"加载配置文件失败: {str(e)}")
    print("请确保config.json文件存在且格式正确")
    exit(1)

def smart_reply(sender, content, beforeContent):
    system_prompt = system_prompt_template.format(sender=sender)



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