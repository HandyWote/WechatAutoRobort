import random
import re
import time
import requests
import json
from wxauto import WeChat

wx = WeChat()

# 从配置文件加载配置
try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
        ollama_config = config['ollama']
        url = ollama_config['url']
        modelName = ollama_config['modelName']
        yourRobortName = ollama_config['yourRobortName']
        ignoreFriends = ollama_config['ignoreFriends']
        ignoreMessages = ollama_config['ignoreMessages']
        system_prompt_template = ollama_config['system_prompt']
    print("成功加载配置文件")
except Exception as e:
    print(f"加载配置文件失败: {str(e)}")
    print("请确保config.json文件存在且格式正确")
    exit(1)

beforeContent = ''
def smart_reply(sender, content, beforeContent):
    system_prompt = system_prompt_template.format(sender=sender)



    data = {
        "model": modelName,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": '前情提要:' + beforeContent},
            {"role": "user", "content": f'{sender}说:' + content,
             }],
        "stream": False
    }
    r = requests.post(url, json=data)
    response = r.json()['message']['content']
    clean_text = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    return clean_text.strip()


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
                            beforeContent = beforeContent[len(query_content)::] +sender + '说:' + query_content
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