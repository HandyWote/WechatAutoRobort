import sys
import json
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QTabWidget, 
                             QPushButton, QGroupBox, QFormLayout, QTextEdit,
                             QMessageBox, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, QProcess

# 设置全局样式
def set_style():
    return """
    QMainWindow, QWidget {
        background-color: rgba(240, 240, 240, 220);
        border-radius: 10px;
    }
    
    QTabWidget::pane {
        border: none;
        background-color: rgba(255, 255, 255, 180);
        border-radius: 8px;
    }
    
    QTabBar::tab {
        background-color: rgba(220, 220, 220, 200);
        color: #333333;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        padding: 8px 16px;
        margin-right: 2px;
    }
    
    QTabBar::tab:selected {
        background-color: rgba(255, 255, 255, 220);
        color: #000000;
    }
    
    QGroupBox {
        background-color: rgba(255, 255, 255, 180);
        border-radius: 8px;
        margin-top: 16px;
        font-weight: bold;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 5px;
    }
    
    QLineEdit, QTextEdit {
        background-color: rgba(255, 255, 255, 200);
        border: 1px solid rgba(200, 200, 200, 200);
        border-radius: 4px;
        padding: 4px;
    }
    
    QPushButton {
        background-color: rgba(0, 122, 255, 220);
        color: white;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: rgba(0, 102, 235, 220);
    }
    
    QPushButton:pressed {
        background-color: rgba(0, 82, 215, 220);
    }
    
    QLabel {
        color: #333333;
    }
    """

# 毛玻璃效果框架
class GlassFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("glassFrame")
        
        # 检测系统是否支持毛玻璃效果
        try:
            import platform
            self.supports_blur = platform.system() == 'Windows' and int(platform.release()) >= 10
        except:
            self.supports_blur = False
        
        # 设置半透明背景样式
        self.setStyleSheet("""#glassFrame {
                background-color: rgba(255, 255, 255, 180);
                border-radius: 10px;
            }
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

# 主窗口类
class WechatRobotGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.process = None
        self.init_ui()
        self.load_config()
        self.oldPos = None
        
    def init_ui(self):
        # 设置窗口基本属性
        self.setWindowTitle("微信AI助手")
        self.setMinimumSize(800, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框窗口
        self.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景
        
        # 应用全局样式
        self.setStyleSheet(set_style())
        
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建毛玻璃效果容器
        glass_container = GlassFrame(self)
        glass_container.setLayout(main_layout)
        
        # 创建标题栏
        title_layout = QHBoxLayout()
        title_label = QLabel("微信AI助手")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_layout.addWidget(title_label)
        
        # 添加最小化和关闭按钮
        button_layout = QHBoxLayout()
        minimize_button = QPushButton("-")
        minimize_button.setFixedSize(40, 40)
        minimize_button.setStyleSheet("QPushButton { background-color: #2ecc71; color: white; font-size: 20px; font-weight: bold; } QPushButton:hover { background-color: #27ae60; }")
        minimize_button.clicked.connect(self.showMinimized)
        
        close_button = QPushButton("X")
        close_button.setFixedSize(40, 40)
        close_button.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; font-size: 20px; font-weight: bold; } QPushButton:hover { background-color: #c0392b; }")
        close_button.clicked.connect(self.close)
        
        button_layout.addWidget(minimize_button)
        button_layout.addWidget(close_button)
        button_layout.setSpacing(0)
        title_layout.addLayout(button_layout)
        
        main_layout.addLayout(title_layout)
        
        # 创建标签页切换不同模式
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("QTabWidget { background-color: transparent; }")
        
        # 创建Ollama本地模式标签页
        self.ollama_tab = QWidget()
        self.setup_ollama_tab()
        self.tab_widget.addTab(self.ollama_tab, "本地AI模式 (Ollama)")
        
        # 创建OpenAI云端模式标签页
        self.openai_tab = QWidget()
        self.setup_openai_tab()
        self.tab_widget.addTab(self.openai_tab, "云端AI模式 (OpenAI)")
        
        main_layout.addWidget(self.tab_widget)
        
        # 创建底部控制区域
        control_layout = QHBoxLayout()
        
        # 状态标签
        self.status_label = QLabel("状态: 已停止")
        self.status_label.setStyleSheet("color: #e74c3c;")
        control_layout.addWidget(self.status_label)
        
        # 保存配置按钮
        save_button = QPushButton("保存配置")
        save_button.clicked.connect(self.save_config)
        control_layout.addWidget(save_button)
        
        # 启动/停止按钮
        self.start_button = QPushButton("启动机器人")
        self.start_button.clicked.connect(self.start_robot)
        control_layout.addWidget(self.start_button)
        
        main_layout.addLayout(control_layout)
        
        # 设置中央窗口部件
        central_widget = QWidget()
        central_widget.setLayout(QVBoxLayout())
        central_widget.layout().addWidget(glass_container)
        central_widget.layout().setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(central_widget)
    
    def setup_ollama_tab(self):
        layout = QVBoxLayout(self.ollama_tab)
        layout.setContentsMargins(10, 20, 10, 10)
        
        # 基本配置组
        basic_group = QGroupBox("基本配置")
        basic_form = QFormLayout(basic_group)
        
        self.ollama_url = QLineEdit()
        self.ollama_url.setPlaceholderText("Ollama API地址 (例如: http://127.0.0.1:11434/api/chat)")
        basic_form.addRow("API地址:", self.ollama_url)
        
        self.ollama_model = QLineEdit()
        self.ollama_model.setPlaceholderText("模型名称 (例如: llama2)")
        basic_form.addRow("模型名称:", self.ollama_model)
        
        self.ollama_name = QLineEdit()
        self.ollama_name.setPlaceholderText("机器人名称 (例如: 小助手)")
        basic_form.addRow("机器人名称:", self.ollama_name)
        
        layout.addWidget(basic_group)
        
        # 高级配置组
        advanced_group = QGroupBox("高级配置")
        advanced_form = QFormLayout(advanced_group)
        
        self.ollama_ignore_friends = QTextEdit()
        self.ollama_ignore_friends.setPlaceholderText("每行一个好友名称")
        self.ollama_ignore_friends.setMaximumHeight(80)
        advanced_form.addRow("忽略好友:", self.ollama_ignore_friends)
        
        self.ollama_ignore_messages = QTextEdit()
        self.ollama_ignore_messages.setPlaceholderText("每行一个消息类型")
        self.ollama_ignore_messages.setMaximumHeight(80)
        advanced_form.addRow("忽略消息:", self.ollama_ignore_messages)
        
        layout.addWidget(advanced_group)
        
        # 系统提示词配置
        prompt_group = QGroupBox("系统提示词")
        prompt_layout = QVBoxLayout(prompt_group)
        
        self.ollama_system_prompt = QTextEdit()
        self.ollama_system_prompt.setPlaceholderText("设置AI助手的角色和行为")
        self.ollama_system_prompt.setMinimumHeight(120)
        prompt_layout.addWidget(self.ollama_system_prompt)
        
        layout.addWidget(prompt_group)
        layout.addStretch()
    
    def setup_openai_tab(self):
        layout = QVBoxLayout(self.openai_tab)
        layout.setContentsMargins(10, 20, 10, 10)
        
        # 基本配置组
        basic_group = QGroupBox("基本配置")
        basic_form = QFormLayout(basic_group)
        
        self.openai_api_key = QLineEdit()
        self.openai_api_key.setPlaceholderText("输入您的OpenAI API密钥")
        self.openai_api_key.setEchoMode(QLineEdit.Password)  # 密码模式显示
        basic_form.addRow("API密钥:", self.openai_api_key)
        
        self.openai_url = QLineEdit()
        self.openai_url.setPlaceholderText("API地址 (例如: https://api.openai.com/v1)")
        basic_form.addRow("API地址:", self.openai_url)
        
        self.openai_model = QLineEdit()
        self.openai_model.setPlaceholderText("模型名称 (例如: gpt-3.5-turbo)")
        basic_form.addRow("模型名称:", self.openai_model)
        
        self.openai_name = QLineEdit()
        self.openai_name.setPlaceholderText("机器人名称 (例如: 小助手)")
        basic_form.addRow("机器人名称:", self.openai_name)
        
        layout.addWidget(basic_group)
        
        # 高级配置组
        advanced_group = QGroupBox("高级配置")
        advanced_form = QFormLayout(advanced_group)
        
        self.openai_ignore_friends = QTextEdit()
        self.openai_ignore_friends.setPlaceholderText("每行一个好友名称")
        self.openai_ignore_friends.setMaximumHeight(80)
        advanced_form.addRow("忽略好友:", self.openai_ignore_friends)
        
        self.openai_ignore_messages = QTextEdit()
        self.openai_ignore_messages.setPlaceholderText("每行一个消息类型")
        self.openai_ignore_messages.setMaximumHeight(80)
        advanced_form.addRow("忽略消息:", self.openai_ignore_messages)
        
        layout.addWidget(advanced_group)
        
        # 系统提示词配置
        prompt_group = QGroupBox("系统提示词")
        prompt_layout = QVBoxLayout(prompt_group)
        
        self.openai_system_prompt = QTextEdit()
        self.openai_system_prompt.setPlaceholderText("设置AI助手的角色和行为")
        self.openai_system_prompt.setMinimumHeight(120)
        prompt_layout.addWidget(self.openai_system_prompt)
        
        layout.addWidget(prompt_group)
        layout.addStretch()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()
    
    def mouseMoveEvent(self, event):
        if self.oldPos:
            delta = event.globalPos() - self.oldPos
            self.move(self.pos() + delta)
            self.oldPos = event.globalPos()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = None
            
    def start_robot(self):
        # 保存当前配置
        self.save_config()
        
        # 获取当前选中的模式
        current_tab = self.tab_widget.currentWidget()
        mode = "本地" if current_tab == self.ollama_tab else "云AI"
        
        # 如果已有进程在运行，先停止
        if self.process and self.process.state() == QProcess.Running:
            self.process.kill()
            self.process.waitForFinished()
        
        # 创建新进程
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.readyReadStandardError.connect(self.handle_error)
        self.process.finished.connect(self.handle_finished)
        
        # 设置工作目录
        self.process.setWorkingDirectory(os.path.dirname(os.path.abspath(__file__)))
        
        # 启动对应模式的脚本
        script = "Ollama.py" if mode == "ollama" else "OpenAI.py"
        self.process.start(sys.executable, [script])
        
        # 更新UI状态
        self.start_button.setText("停止机器人")
        self.start_button.clicked.disconnect()
        self.start_button.clicked.connect(self.stop_robot)
        self.status_label.setText(f"状态: 正在运行 ({mode}模式)")
        self.status_label.setStyleSheet("color: #2ecc71;")
        
    def stop_robot(self):
        if self.process and self.process.state() == QProcess.Running:
            # 先尝试正常终止进程
            self.process.terminate()
            self.process.kill()
            self.process.waitForFinished()
        
        # 恢复UI状态
        self.start_button.setText("启动机器人")
        self.start_button.clicked.disconnect()
        self.start_button.clicked.connect(self.start_robot)
        self.status_label.setText("状态: 已停止")
        self.status_label.setStyleSheet("color: #e74c3c;")
    
    def handle_output(self):
        data = self.process.readAllStandardOutput().data().decode()
        print(data, end='')
    
    def handle_error(self):
        data = self.process.readAllStandardError().data().decode()
        print(data, end='')
    
    def handle_finished(self, exit_code, exit_status):
        # 仅当进程崩溃时显示错误
        if exit_code != 0:
            QMessageBox.information(self, "提示", "机器人已正常停止")
        elif exit_status == QProcess.CrashExit:
            QMessageBox.warning(self, "错误", f"进程异常终止 (代码: {exit_code})")
        self.stop_robot()
        
    def load_config(self):
        # 设置默认值
        default_config = {
            'ollama': {
                'url': 'http://127.0.0.1:11434/api/chat',
                'modelName': '',
                'yourRobortName': '小助手',
                'ignoreFriends': ['Self', 'SYS'],
                'ignoreMessages': ['[动画表情]', '[图片]', '[视频]', '[语音]'],
                'system_prompt': '你是一个友好的AI助手，能够帮助用户解答问题。'
            },
            'openai': {
                'APIKey': '',
                'url': 'https://api.openai.com/v1',
                'modelName': 'gpt-3.5-turbo',
                'yourRobortName': '小助手',
                'ignoreFriends': ['Self', 'SYS'],
                'ignoreMessages': ['[动画表情]', '[图片]', '[视频]', '[语音]'],
                'system_prompt': '你是一个友好的AI助手，能够帮助用户解答问题。'
            }
        }
        
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    # 合并保存的配置和默认配置
                    if 'ollama' in saved_config:
                        default_config['ollama'].update(saved_config['ollama'])
                    if 'openai' in saved_config:
                        default_config['openai'].update(saved_config['openai'])
            
            # 加载Ollama配置
            ollama_config = default_config['ollama']
            self.ollama_url.setText(ollama_config['url'])
            self.ollama_model.setText(ollama_config['modelName'])
            self.ollama_name.setText(ollama_config['yourRobortName'])
            # 过滤掉默认的ignoreFriends值
            custom_ignore_friends = [f for f in ollama_config['ignoreFriends'] if f not in ['Self', 'SYS']]
            self.ollama_ignore_friends.setPlainText('\n'.join(custom_ignore_friends))
            self.ollama_ignore_messages.setPlainText('\n'.join(ollama_config['ignoreMessages']))
            self.ollama_system_prompt.setPlainText(ollama_config['system_prompt'])
            
            # 加载OpenAI配置
            openai_config = default_config['openai']
            self.openai_api_key.setText(openai_config['APIKey'])
            self.openai_url.setText(openai_config['url'])
            self.openai_model.setText(openai_config['modelName'])
            self.openai_name.setText(openai_config['yourRobortName'])
            # 过滤掉默认的ignoreFriends值
            custom_ignore_friends = [f for f in openai_config['ignoreFriends'] if f not in ['Self', 'SYS']]
            self.openai_ignore_friends.setPlainText('\n'.join(custom_ignore_friends))
            self.openai_ignore_messages.setPlainText('\n'.join(openai_config['ignoreMessages']))
            self.openai_system_prompt.setPlainText(openai_config['system_prompt'])
            
        except Exception as e:
            QMessageBox.warning(self, "警告", f"加载配置失败: {str(e)}\n已加载默认配置")
            # 使用默认配置
            self.load_default_config(default_config)
    
    def load_default_config(self, default_config):
        # 加载默认Ollama配置
        ollama_config = default_config['ollama']
        self.ollama_url.setText(ollama_config['url'])
        self.ollama_model.setText(ollama_config['modelName'])
        self.ollama_name.setText(ollama_config['yourRobortName'])
        self.ollama_ignore_friends.setPlainText('')
        self.ollama_ignore_messages.setPlainText('\n'.join(ollama_config['ignoreMessages']))
        self.ollama_system_prompt.setPlainText(ollama_config['system_prompt'])
        
        # 加载默认OpenAI配置
        openai_config = default_config['openai']
        self.openai_api_key.setText(openai_config['APIKey'])
        self.openai_url.setText(openai_config['url'])
        self.openai_model.setText(openai_config['modelName'])
        self.openai_name.setText(openai_config['yourRobortName'])
        self.openai_ignore_friends.setPlainText('')
        self.openai_ignore_messages.setPlainText('\n'.join(openai_config['ignoreMessages']))
        self.openai_system_prompt.setPlainText(openai_config['system_prompt'])

    def save_config(self):
        try:
            config = {}
            
            # 保存Ollama配置
            custom_ignore_friends = [f.strip() for f in self.ollama_ignore_friends.toPlainText().split('\n') if f.strip()]
            config['ollama'] = {
                'url': self.ollama_url.text(),
                'modelName': self.ollama_model.text(),
                'yourRobortName': self.ollama_name.text(),
                'ignoreFriends': ['Self', 'SYS'] + custom_ignore_friends,
                'ignoreMessages': [m.strip() for m in self.ollama_ignore_messages.toPlainText().split('\n') if m.strip()],
                'system_prompt': self.ollama_system_prompt.toPlainText()
            }
            
            # 保存OpenAI配置
            custom_ignore_friends = [f.strip() for f in self.openai_ignore_friends.toPlainText().split('\n') if f.strip()]
            config['openai'] = {
                'APIKey': self.openai_api_key.text(),
                'url': self.openai_url.text(),
                'modelName': self.openai_model.text(),
                'yourRobortName': self.openai_name.text(),
                'ignoreFriends': ['Self', 'SYS'] + custom_ignore_friends,
                'ignoreMessages': [m.strip() for m in self.openai_ignore_messages.toPlainText().split('\n') if m.strip()],
                'system_prompt': self.openai_system_prompt.toPlainText()
            }
            
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "成功", "配置已保存")
            return True
        except Exception as e:
            QMessageBox.warning(self, "警告", f"保存配置失败: {str(e)}")
            return False
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WechatRobotGUI()
    window.show()
    sys.exit(app.exec_())