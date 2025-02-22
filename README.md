markdown
# 微信猫娘助手机器人

🎮 专为微信设计的自动回复机器人，支持Ollama本地API与OpenAI云端API双模式，化身傲娇猫娘与好友互动！

---

## 🌟 快速部署指南（零基础版）

### 第一步：安装基础工具
1. 安装Python  
   - 访问[Python官网](https://www.python.org/)，下载最新版本（勾选`Add Python to PATH`）  
2. 安装微信客户端  
   - 从官网下载安装，**必须使用Windows版微信**  

### 第二步：获取代码文件
1. 下载本项目的两个文件：`Ollama.py`和`OpenAI.py`  
2. 将文件保存到单独的文件夹（例如：`D:\WechatBot`）

### 第三步：安装依赖库
打开命令提示符（按 Win+R 输入`cmd`），逐行执行：
```bash
pip install wxauto
pip install openai
```

### 第四步：选择模式配置
#### 🖥️ Ollama本地模式（推荐）
1. 下载安装Ollama：https://ollama.ai/  
2. 启动服务：在命令行输入`ollama run llama2`（示例模型）  
3. 修改`Ollama.py`中以下参数：  
   ```python
   modelName = 'llama2'  # 与本地运行的模型一致
   yourRobortName = '我的机器人'  # 微信中@你的名字
   ```

#### ☁️ OpenAI云端模式
1. 注册OpenAI账号：https://platform.openai.com/  
2. 获取API密钥  
3. 修改`OpenAI.py`中以下参数：  
   ```python
   APIKey = 'sk-xxxxxxxxxxxxxxxx'  # 你的API密钥
   modelName = 'gpt-3.5-turbo'     # 官方模型名
   url = 'https://api.openai.com/v1'  # 官方接口
   ```

### 第五步：启动机器人
1. 登录微信客户端（建议使用小号）  
2. 双击运行对应脚本：  
   - 本地模式：双击`Ollama.py`  
   - 云端模式：双击`OpenAI.py`  
3. 在任意聊天窗口@你的机器人名称即可触发回复！

---

## 🤖 功能特性

### 核心功能
- **智能回复**：基于大语言模型的上下文对话  
- **角色扮演**：可以自己设置角色
- **精准过滤**：自动忽略表情/图片/指定好友  
- **防刷屏设计**：随机延迟响应（1.5-3秒）  
- **异常恢复**：断网/闪退后自动重连  

### 进阶配置
```python
# 在脚本中可自定义：
ignoreFriends = ['老板', '工作群']  # 屏蔽名单
ignoreMessages = ['[红包]']        # 新增屏蔽内容
system_prompt = """..."""          # 修改角色设定
```

---

## ⚙️ 实现原理

### 架构设计
```mermaid
graph LR
    A[微信消息监听] --> B{消息过滤}
    B -->|触发@| C[AI处理模块]
    C --> D[Ollama/OpenAI API]
    D --> E[回复格式化]
    E --> F[微信消息发送]
```

### 关键技术
1. **wxauto库**：实现微信自动化控制  
2. **上下文管理**：`beforeContent`变量保存最近对话历史  
3. **正则清洗**：过滤AI返回的冗余思考过程  
4. **流量控制**：随机延迟防止账号风控  

---

## ❗ 注意事项
1. 微信需保持前台运行（不要最小化）  
2. 首次运行时可能需扫码登录确认  
3. 本地模型要求机器性能
4. 云端模式会产生API费用
5. 群聊中必须@机器人才能触发回复  

遇到问题可尝试：  
- 重启微信客户端  
- 检查API密钥有效性  
- 查看命令行提示的错误信息  

