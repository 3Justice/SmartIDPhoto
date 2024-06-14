import signal
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextOption
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtGui import QPainter, QBrush,QPainterPath, QColor
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QApplication
from PyQt5.QtWidgets import *
import sys
import threading
from PIL import Image, ImageTk, ImageDraw, ImageOps
import tkinter as tk
import pymysql
import re
import matplotlib.pyplot as plt
import csv
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
from main import deal
from PIL import Image
import cv2
import numpy as np
import tkinter as tk
import m_dlib.face_marks as fmarks
from face_beauty import beauty
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox,
    QLabel
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout
import os
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
global_user=None
global_balance = 0  # Initialize balance to 0

class RechargeDialog(QDialog):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle("充值")
        self.username = username

        layout = QVBoxLayout()

        amount_label = QLabel("请输入充值的金额:")
        layout.addWidget(amount_label)

        self.amount_edit = QLineEdit()
        self.amount_edit.setPlaceholderText("只能输入正数")
        layout.addWidget(self.amount_edit)

        recharge_button = QPushButton("确认充值")
        recharge_button.clicked.connect(self.recharge)
        layout.addWidget(recharge_button)

        self.setLayout(layout)

    def recharge(self):
        amount = self.amount_edit.text()
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
            with open("balance.txt", "r+") as f:
                lines = f.readlines()
                f.seek(0)
                found = False
                for line in lines:
                    data = line.strip().split(': ')
                    if data[0] == self.username:
                        balance = float(data[1]) + amount
                        f.write(f"{self.username}: {balance}\n")
                        found = True
                    else:
                        f.write(line)
                if not found:
                    f.write(f"{self.username}: {amount}\n")
                f.truncate()
            QMessageBox.information(self, "充值成功", f"成功充值 {amount} 元！")
            self.close()
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入一个大于零的数字！")

class ChangePasswordDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.setWindowTitle("修改密码")
        self.username = username
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        original_password_layout = QHBoxLayout()
        original_password_label = QLabel("原始密码:")
        original_password_layout.addWidget(original_password_label)
        self.original_password_edit = QLineEdit()
        self.original_password_edit.setPlaceholderText("请输入原始密码")
        self.original_password_edit.setEchoMode(QLineEdit.Password)
        original_password_layout.addWidget(self.original_password_edit)
        layout.addLayout(original_password_layout)

        new_password_layout = QHBoxLayout()
        new_password_label = QLabel("输入新密码:")
        new_password_layout.addWidget(new_password_label)
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setPlaceholderText("请输入新密码")
        self.new_password_edit.setEchoMode(QLineEdit.Password)
        new_password_layout.addWidget(self.new_password_edit)
        layout.addLayout(new_password_layout)

        confirm_password_layout = QHBoxLayout()
        confirm_password_label = QLabel("确定新密码:")
        confirm_password_layout.addWidget(confirm_password_label)
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setPlaceholderText("请确认新密码")
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        confirm_password_layout.addWidget(self.confirm_password_edit)
        layout.addLayout(confirm_password_layout)

        change_password_button = QPushButton("修改密码")
        change_password_button.clicked.connect(self.change_password)
        layout.addWidget(change_password_button)

        self.setLayout(layout)

        # 设置只能输入字母或数字的限制
        self.set_validator()

    def set_validator(self):
        # 创建一个只接受字母和数字的正则表达式
        regex = QRegExp("[A-Za-z0-9]+")
        validator = QRegExpValidator(regex)
        # 将该正则表达式应用到新密码和确认密码输入框中
        self.new_password_edit.setValidator(validator)
        self.confirm_password_edit.setValidator(validator)
        self.original_password_edit.setValidator(validator)

    def change_password(self):
        original_password = self.original_password_edit.text()
        new_password = self.new_password_edit.text()
        confirm_password = self.confirm_password_edit.text()

        # 检查新密码和确认密码是否一致
        if new_password != confirm_password:
            QMessageBox.warning(self, "警告", "新密码与确认密码不一致")
            return

        # 在这里检查原始密码是否正确，并更新密码
        if self.check_original_password(original_password):
            # 在 registered_users.txt 中更新密码
            self.update_password(new_password)
            QMessageBox.information(self, "成功", "密码已成功修改")
            self.close()
        else:
            QMessageBox.warning(self, "警告", "原始密码不正确")

    def check_original_password(self, password):
        # 在 registered_users.txt 文件中查找用户名和密码，然后比较原始密码是否正确
        try:
            with open("registered_users.txt", "r") as f:
                for line in f:
                    data = line.strip().split(', ')
                    if len(data) >= 2 and data[0] == self.username and data[1] == password:
                        return True
        except FileNotFoundError:
            print("registered_users.txt not found")
        except Exception as e:
            print(f"Error reading registered_users.txt: {e}")
        return False

    def update_password(self, new_password):
        # 在 registered_users.txt 中更新密码
        try:
            with open("registered_users.txt", "r") as f:
                lines = f.readlines()
            with open("registered_users.txt", "w") as f:
                for line in lines:
                    data = line.strip().split(', ')
                    if len(data) >= 2 and data[0] == self.username:
                        line = f"{data[0]}, {new_password}, {data[2] if len(data) > 2 else ''}"
                    f.write(line + '\n')
        except FileNotFoundError:
            print("找不到registered_users.txt文件")
        except Exception as e:
            print(f"在registered_users.txt中更新密码时出错：{e}")


class HelloPage(QDialog):
    def __init__(self):
        super().__init__()
        self.user_main_window = None
        self.setWindowTitle("用户中心")
        self.setGeometry(100, 100, 400, 300)

        self.setStyleSheet("background-color: white;")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 读取permanent_log.txt文件的最后一行
        try:
            with open("permanent_log.txt", "r") as f:
                lines = f.readlines()
                if lines:
                    last_user = lines[-1].strip()  # 获取最后一行用户名
                    self.show_user_info(last_user)
        except FileNotFoundError:
            print("permanent_log.txt not found")
        except Exception as e:
            print(f"Error reading permanent_log.txt: {e}")

    def open_change_password_dialog(self, username):
        dialog = ChangePasswordDialog(username)
        dialog.exec_()

    def show_user_info(self, username):
        try:
            with open("registered_users.txt", "r") as f:
                for line in f:
                    data = line.strip().split(', ')
                    if data[0] == username:
                        avatar_path = data[2] if len(data) > 2 else 'default_avatar.png'

                        # 检查头像文件是否存在
                        if not os.path.exists(avatar_path):
                            avatar_path = 'default_avatar.png'

                        # 创建 QLabel 来显示用户名
                        username_label = QLabel(f"你好, {username}!")

                        # 设置字体样式
                        font = username_label.font()
                        font.setPointSize(16)
                        username_label.setFont(font)

                        # 设置文本居中对齐
                        username_label.setAlignment(Qt.AlignCenter)

                        # 将 QLabel 添加到布局中
                        self.layout.addWidget(username_label)

                        # 创建 CircularLabel 来显示圆形头像
                        self.avatar_label = CircularLabel(size=150)  # 将圆形头像大小设置为200
                        self.layout.addWidget(self.avatar_label, alignment=Qt.AlignCenter)

                        # 加载头像并设置到 CircularLabel 中
                        pixmap = QPixmap(avatar_path)
                        self.avatar_label.setPixmap(pixmap)

                        # 将 CircularLabel 添加到布局中并居中显示
                        self.layout.addWidget(self.avatar_label, alignment=Qt.AlignCenter)
                        break
        except FileNotFoundError:
            print("registered_users.txt not found")
        except Exception as e:
            print(f"Error reading registered_users.txt: {e}")

        change_password_button = QPushButton("修改密码")
        change_password_button.clicked.connect(lambda: self.open_change_password_dialog(username))
        self.layout.addWidget(change_password_button, alignment=Qt.AlignCenter)

        recharge_button = QPushButton("充值")
        recharge_button.clicked.connect(lambda: self.open_recharge_dialog(username))
        self.layout.addWidget(recharge_button, alignment=Qt.AlignCenter)

        switch_window_button = QPushButton("进入主界面")
        switch_window_button.clicked.connect(self.switch_to_user_main_window)
        self.layout.addWidget(switch_window_button, alignment=Qt.AlignCenter)

        change_avatar_button = QPushButton("修改头像")
        change_avatar_button.clicked.connect(lambda: self.change_avatar(username))
        self.layout.addWidget(change_avatar_button, alignment=Qt.AlignCenter)

    def open_recharge_dialog(self, username):
        dialog = RechargeDialog(username)
        dialog.exec_()

    def change_avatar(self, username):
        # 打开文件对话框，让用户选择新的头像文件
        filepath, _ = QFileDialog.getOpenFileName(self, "选择新的头像", "", "Image Files (*.png *.jpg *.bmp)")

        # 如果用户选择了文件
        if filepath:
            try:
                # 更新用户头像路径到 registered_users.txt 文件中
                with open("registered_users.txt", "r+") as f:
                    lines = f.readlines()
                    f.seek(0)
                    for line in lines:
                        data = line.strip().split(', ')
                        if data[0] == username:
                            # 更新用户的头像路径
                            line = f"{data[0]}, {data[1]}, {filepath}\n"
                        f.write(line)
                    f.truncate()

                # 更新头像
                pixmap = QPixmap(filepath)
                self.avatar_label.setPixmap(pixmap)

            except FileNotFoundError:
                print("registered_users.txt not found")
            except Exception as e:
                print(f"Error updating avatar path: {e}")

    def switch_to_user_main_window(self):
        self.close()
        self.user_main_window = user_mainWindow()  # 将对 user_mainWindow 对象的引用存储在 self.user_main_window 中
        self.user_main_window.show()


class CircularLabel(QLabel):
    def __init__(self, size=100, parent=None):
        super().__init__(parent)
        self.size = size
        self.setFixedSize(size, size)
        self.pixmap = None

    def setPixmap(self, pixmap):
        self.pixmap = pixmap
        self.update()

    def paintEvent(self, event):
        if self.pixmap is None:
            return super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Create a circular clip path
        path = QPainterPath()
        radius = self.size / 2
        path.addEllipse(0, 0, 2 * radius, 2 * radius)
        painter.setClipPath(path)

        # Draw the pixmap, scaled to cover the entire circular area
        scaled_pixmap = self.pixmap.scaled(self.size, self.size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        painter.drawPixmap(0, 0, scaled_pixmap)

        painter.end()


# Usage Example:
# app = QApplication(sys.argv)
# hello_page = HelloPage()
# hello_page.exec_()


class CollapsibleSection(QFrame):
    def __init__(self, title, parent=None):
        super(CollapsibleSection, self).__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)

        self.toggle_button = QPushButton(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.setFixedSize(250, 55)
        self.toggle_button.setStyleSheet("text-align: left; border-image: url(botton.png); border-radius: 15px; padding: 5px;")

        # 设置按钮标题的字体大小
        font = QFont()
        font.setFamily("宋体")
        font.setPointSize(20)  # 调整字体大小
        self.toggle_button.setFont(font)

        self.content_area = QWidget()
        self.content_area.setStyleSheet("border-image: url(picture3.png); border-radius: 12px; background-color: rgba(255, 255, 255, 0);")
        self.content_area.setMaximumHeight(0)
        self.content_area.setMinimumHeight(0)

        self.toggle_button.clicked.connect(self.toggle)

        layout = QVBoxLayout(self)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_area)
        #layout.addStretch()  # Ensures the button stays in place
        layout.setContentsMargins(0, 0, 0, 0)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setLayout(self.content_layout)
        self.content_layout.addSpacing(6)  # 在每一行之间添加 6像素的空白间距
        self.content_layout.setSpacing(10)  # 设置部件之间的间距为 10 像素


    def toggle(self):
        if not self.toggle_button.isChecked():
            self.content_area.setMaximumHeight(0)
            self.content_area.setMinimumHeight(0)
        else:
            self.content_area.setMaximumHeight(16777215)
            self.content_area.setMinimumHeight(70)

    def addWidget(self, widget):
        self.content_layout.addWidget(widget)

class user_mainWindow(QWidget):
    def __init__(self):
        super(user_mainWindow, self).__init__()
        self.avatar_label = QtWidgets.QLabel(self)
        self.setWindowTitle("C++程序设计实验课-智能证件照生成系统-第八组")
        self.resize(1920, 1080)  # 设置窗体大小
        self.setStyleSheet("background-color:#F6F6F6")
        self.sourcefile_path = ""
        self.cwd = os.getcwd()  # 获取当前程序文件位置
        self.color = "white"
        self.size_width = 295
        self.size_height = 413
        self.size3 = 20

        # 背景
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, 1920, 1080)
        pixmap = QPixmap('picture2.png')
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)

        # 图片
        pic4 = QLabel(self)
        pic4.setGeometry(150, 100, 700, 800)
        pic4.setStyleSheet("border-image: url(avatar.png); border-radius: 40px;background-color: rgba(255, 255, 255, 0.5);")

        pic2 = QLabel(self)
        pic2.setGeometry(1050, 100, 350, 800)
        pic2.setStyleSheet("border-image: url(picture3.png); border-radius: 40px;background-color: rgba(255, 255, 255, 0.5);")

        pic3 = QLabel(self)
        pic3.setGeometry(1450, 100, 350, 800)
        pic3.setStyleSheet(
            "border-image: url(picture3.png); border-radius: 40px;background-color: rgba(255, 255, 255, 0.5);")

        self.last_label = QLabel(self)


        # 创建折叠部分
        self.background_color_section = CollapsibleSection(" 背景颜色", self)
        self.size_section = CollapsibleSection(" 尺寸", self)
        self.whitening_section = CollapsibleSection(" 美肤", self)
        self.cloth_section = CollapsibleSection(" 换装", self)
        self.face_section = CollapsibleSection(" 面部调整", self)

        self.background_color_section.setGeometry(1100, 150, 250, 150)
        self.size_section.setGeometry(1100, 300, 250, 200)
        self.whitening_section.setGeometry(1100, 500, 250, 200)
        self.cloth_section.setGeometry(1500, 150, 250, 250)
        self.face_section.setGeometry(1500, 400, 250, 200)

        self.background_color_section.setStyleSheet("border-image: url(picture3.png); border-radius: 20px;background-color: rgba(255, 255, 255, 0);")
        self.size_section.setStyleSheet("border-image: url(picture3.png); border-radius: 20px; background-color: rgba(255, 255, 255, 0);")
        self.whitening_section.setStyleSheet("border-image: url(picture3.png); border-radius: 20px; background-color: rgba(255, 255, 255, 0);")
        self.cloth_section.setStyleSheet(
            "border-image: url(picture3.png); border-radius: 20px; background-color: rgba(255, 255, 255, 0);")
        self.face_section.setStyleSheet(
            "border-image: url(picture3.png); border-radius: 20px; background-color: rgba(255, 255, 255, 0);")

        # 背景颜色选项
        self.white_select = QPushButton(self)
        self.white_select.setStyleSheet("border:1px solid black;background-color:white")
        self.white_select.clicked.connect(self.click_white)

        self.red_select = QPushButton(self)
        self.red_select.setStyleSheet("background-color:red")
        self.red_select.clicked.connect(self.click_red)

        self.blue_select = QPushButton(self)
        self.blue_select.setStyleSheet("background-color:blue")
        self.blue_select.clicked.connect(self.click_blue)

        self.background_color_section.addWidget(self.white_select)
        self.background_color_section.addWidget(self.red_select)
        self.background_color_section.addWidget(self.blue_select)

        # 尺寸选项
        self.size_select1 = QRadioButton("一寸    25*35mm  295*413px")
        self.size_select1.setChecked(True)
        self.size_select1.clicked.connect(self.click1)

        self.size_select2 = QRadioButton("大一寸  33*48mm  390*566px")
        self.size_select2.clicked.connect(self.click2)

        self.size_select3 = QRadioButton("小二寸  35*45mm  413*531px")
        self.size_select3.clicked.connect(self.click3)

        self.size_select4 = QRadioButton("二寸    35*49mm  413*579px")
        self.size_select4.clicked.connect(self.click4)

        self.size_select5 = QRadioButton("大二寸  35*53mm  413*626px")
        self.size_select5.clicked.connect(self.click5)

        self.size_section.addWidget(self.size_select1)
        self.size_section.addWidget(self.size_select2)
        self.size_section.addWidget(self.size_select3)
        self.size_section.addWidget(self.size_select4)
        self.size_section.addWidget(self.size_select5)


        # 美白选项
        self.mopi_select1 = QRadioButton("磨皮")
        self.mopi_select1.clicked.connect(self.mopi1)

        self.whitening_select1 = QRadioButton("美白")
        self.whitening_select1.clicked.connect(self.whitening1)

        self.whitening_section.addWidget(self.mopi_select1)
        self.whitening_section.addWidget(self.whitening_select1)

        # 换装选项
        self.cloth_1 = QRadioButton(self)
        self.cloth_1.setStyleSheet("border-image: url(1.png); ")
        self.cloth_1.clicked.connect(self.clickcloth1)

        self.cloth_2 = QRadioButton(self)
        self.cloth_2.setStyleSheet("border-image: url(2.png); ")
        self.cloth_2.clicked.connect(self.clickcloth2)

        self.cloth_3 = QRadioButton(self)
        self.cloth_3.setStyleSheet("border-image: url(3.png); ")
        self.cloth_3.clicked.connect(self.clickcloth3)

        # 面部调整
        self.eyes = QRadioButton("放大双眼")
        self.eyes.clicked.connect(self.big_eye)

        self.face_section.addWidget(self.eyes)

        #布局
        self.cloth_1.setMinimumHeight(80)
        self.cloth_2.setMinimumHeight(80)
        self.cloth_3.setMinimumHeight(80)
        cloth_layout = QHBoxLayout()
        cloth_layout.addWidget(self.cloth_1)
        cloth_layout.addWidget(self.cloth_2)
        cloth_layout.addWidget(self.cloth_3)
        self.cloth_section.content_layout.addLayout(cloth_layout)

        layout1 = QVBoxLayout()
        layout1.addWidget(self.cloth_section)
        layout1.addWidget(self.face_section)
        layout1.addStretch()


        self.white_select.setMinimumHeight(50)
        self.red_select.setMinimumHeight(50)
        self.blue_select.setMinimumHeight(50)
        color_layout = QHBoxLayout()
        color_layout.addWidget(self.white_select)
        color_layout.addWidget(self.red_select)
        color_layout.addWidget(self.blue_select)
        self.background_color_section.content_layout.addLayout(color_layout)

        layout = QVBoxLayout()
        layout.addWidget(self.background_color_section)
        layout.addWidget(self.size_section)
        layout.addWidget(self.whitening_section)
        layout.addStretch()
        layout.addWidget(self.avatar_label)  # 添加 avatar_label 到布局中

        self.transfer = QPushButton(self)
        self.transfer.setGeometry(QtCore.QRect(1500, 630, 250, 90))
        self.transfer.setStyleSheet("border-image:url(user.png); border-radius: 40px")
        self.transfer.clicked.connect(self.transfer_pic)

        self.upload_pic = QPushButton(self)
        self.upload_pic.setGeometry(QtCore.QRect(1100, 750, 250, 90))
        self.upload_pic.setStyleSheet("border-image:url(upload.png); border-radius: 40px")
        self.upload_pic.clicked.connect(self.deal_pic)

        self.download_pic = QPushButton(self)
        self.download_pic.setGeometry(QtCore.QRect(1500, 750, 250, 90))
        self.download_pic.setStyleSheet("border-image:url(down.png); border-radius: 40px")
        self.download_pic.clicked.connect(self.saveImage)

        self.welcome_label = QLabel(self)
        self.welcome_label.setGeometry(50, 920, 1400, 120)
        self.welcome_label.setStyleSheet(
        "background-color: rgba(255, 255, 255, 0.8); border: 1px solid #000; font-size: 24px;")
        self.welcome_label.setAlignment(Qt.AlignCenter)

        self.load_welcome_message()


    mutex = threading.Lock()


    def make_rounded_avatar(self, file_path):
            img = Image.open(file_path).convert("RGBA")
            size = (100, 100)
            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + size, fill=255)
            output = ImageOps.fit(img, size, centering=(0.5, 0.5))
            output.putalpha(mask)

            output_cv2 = np.array(output)
            output_cv2 = cv2.cvtColor(output_cv2, cv2.COLOR_RGB2BGR)

            return output_cv2


    def update_welcome_message(self):
        self.load_welcome_message()

    def load_welcome_message(self):
        global global_balance
        global global_user
        try:
            # Deleting the old avatar file
            if os.path.exists("temp_avatar_welcome.png"):
                os.remove("temp_avatar_welcome.png")

            # Reading the last user from permanent_log.txt
            with open("permanent_log.txt", "r") as f:
                lines = f.readlines()
                if lines:
                    last_user = lines[-1].strip()
                    global_user=lines[-1].strip()
                else:
                    last_user = None

            # Finding the avatar path for the last user
            avatar_path = None
            if last_user:
                with open("registered_users.txt", "r") as f:
                    for line in f:
                        data = line.strip().split(', ')
                        if data[0] == last_user:
                            if len(data) > 2:
                                avatar_path = data[2]
                            else:
                                avatar_path = 'admin.png'

            # Reading the balance for the last user from balance.txt
            if last_user:
                with open("balance.txt", "r") as f:
                    for line in f:
                        data = line.strip().split(':')
                        if data[0] == last_user:
                            global_balance = float(data[1])

            # Setting the welcome message and avatar
            if last_user:
                welcome_message = f"欢迎回来, {last_user}！余额：{global_balance}"
                if avatar_path:
                    rounded_avatar = self.make_rounded_avatar(avatar_path)
                    cv2.imwrite("temp_avatar_welcome.png", rounded_avatar)
                    self.last_label.setGeometry(1500, 925, 100, 100)
                    self.last_label.setStyleSheet("border-image:url(temp_avatar_welcome.png)")
            else:
                welcome_message = "日志文件为空。"

        except IOError as e:
            welcome_message = f"无法读取日志文件: {e}"

        self.welcome_label.setText(welcome_message)

    def whitening1(self):
        if (self.sourcefile_path == ""):
            QMessageBox.warning(self,
                                "警告",
                                "请先上传图片",
                                QMessageBox.Yes)
        else:
            thread = threading.Thread(target=self.whitening_face)
            thread.start()
            thread.join()

            # self.current_img = cv2.imdecode(np.fromfile("last.jpg", dtype=np.uint8), -1)
            self.last_label.setGeometry(300, 220, 410, 575)
            self.last_label.setStyleSheet("border-image:url(last.jpg)")



    def click_white(self):
        if (self.sourcefile_path == ""):
            QMessageBox.warning(self,
                                "警告",
                                "请先上传图片",
                                QMessageBox.Yes)
        else:
          with self.mutex:
            self.color = "white"

            thread = threading.Thread(target=deal, args=(self.sourcefile_path, self.color, self.size_width, self.size_height, self.size3))
            thread.start()
            thread.join()
            # os.kill(os.getpid(),signal.SIGTERM)
            # deal(self.sourcefile_path, self.color, self.size_width, self.size_height, self.size3)
            self.current_img=cv2.imdecode(np.fromfile("last.jpg",dtype=np.uint8),-1)
            self.last_label.setGeometry(280, 200, 413, 579)
            self.last_label.setStyleSheet("border-image:url(last.jpg)")

    def click_red(self):
        if (self.sourcefile_path == ""):
            QMessageBox.warning(self,
                                "警告",
                                "请先上传图片",
                                QMessageBox.Yes)
        else:
          with self.mutex:
            self.color = "red"


            thread=threading.Thread(target=deal,args=(self.sourcefile_path, self.color, self.size_width, self.size_height, self.size3))
            thread.start()
            thread.join()
            # thread.join()
            # os.kill(os.getpid(), signal.SIGTERM)
            # deal(self.sourcefile_path, self.color, self.size_width, self.size_height, self.size3)

            # if thread.is_alive() == 0:
            self.current_img = cv2.imdecode(np.fromfile("last.jpg", dtype=np.uint8), -1)
            self.last_label.setGeometry(300, 220, 413, 579)
            self.last_label.setStyleSheet("border-image:url(last.jpg)")


    def click_blue(self):
        if (self.sourcefile_path == ""):
            QMessageBox.warning(self,
                                "警告",
                                "请先上传图片",
                                QMessageBox.Yes)
        else:
          with self.mutex:
            self.color = "blue"

            thread = threading.Thread(target=deal, args=(self.sourcefile_path, self.color, self.size_width, self.size_height, self.size3))
            thread.start()
            thread.join()
            # os.kill(os.getpid(), signal.SIGTERM)
            # deal(self.sourcefile_path, self.color, self.size_width, self.size_height, self.size3)
            self.current_img = cv2.imdecode(np.fromfile("last.jpg", dtype=np.uint8), -1)
            self.last_label.setGeometry(300, 220, 413, 579)
            self.last_label.setStyleSheet("border-image:url(last.jpg)")

    def click1(self):
        if (self.sourcefile_path == ""):
            QMessageBox.warning(self,
                                "警告",
                                "请先上传图片",
                                QMessageBox.Yes)
        else:
          with self.mutex:
            self.size_width = 295
            self.size_height = 413
            self.size3 = 10

            thread = threading.Thread(target=deal, args=(self.sourcefile_path, self.color, self.size_width, self.size_height, self.size3))
            thread.start()
            thread.join()
            # os.kill(os.getpid(), signal.SIGTERM)
            # deal(self.sourcefile_path, self.color, self.size_width, self.size_height, self.size3)
            self.current_img = cv2.imdecode(np.fromfile("last.jpg", dtype=np.uint8), -1)
            self.last_label.setGeometry(300, 220, 410, 575)
            self.last_label.setStyleSheet("border-image:url(last.jpg)")

    def click2(self):
        if (self.sourcefile_path == ""):
            QMessageBox.warning(self,
                                "警告",
                                "请先上传图片",
                                QMessageBox.Yes)
        else:
          with self.mutex:
            self.size_width = 390
            self.size_height = 566
            self.size3 = 100

            thread = threading.Thread(target=deal, args=(
            self.sourcefile_path, self.color, self.size_width, self.size_height, self.size3))
            thread.start()
            thread.join()
            # os.kill(os.getpid(), signal.SIGTERM)
            # deal(self.sourcefile_path, self.color, self.size_width, self.size_height, self.size3)
            self.current_img = cv2.imdecode(np.fromfile("last.jpg", dtype=np.uint8), -1)
            self.last_label.setGeometry(300, 220, int(self.size_width), int(self.size_height))
            self.last_label.setStyleSheet("border-image:url(last.jpg)")

    def click3(self):
        if (self.sourcefile_path == ""):
            QMessageBox.warning(self,
                                "警告",
                                "请先上传图片",
                                QMessageBox.Yes)
        else:
          with self.mutex:
            self.size_width = 413
            self.size_height = 531
            self.size3 = 80

            thread = threading.Thread(target=deal, args=(
            self.sourcefile_path, self.color, self.size_width, self.size_height, self.size3))
            thread.start()
            thread.join()
            # os.kill(os.getpid(), signal.SIGTERM)
            # deal(self.sourcefile_path, self.color, self.size_width, self.size_height, self.size3)
            self.current_img = cv2.imdecode(np.fromfile("last.jpg", dtype=np.uint8), -1)
            self.last_label.setGeometry(300, 220, int(self.size_width), int(self.size_height))
            self.last_label.setStyleSheet("border-image:url(last.jpg)")

    def click4(self):
        if (self.sourcefile_path == ""):
            QMessageBox.warning(self,
                                "警告",
                                "请先上传图片",
                                QMessageBox.Yes)
        else:
          with self.mutex:
            self.size_width = 413
            self.size_height = 579
            self.size3 = 110

            thread = threading.Thread(target=deal, args=(
            self.sourcefile_path, self.color, self.size_width, self.size_height, self.size3))
            thread.start()
            thread.join()
            # os.kill(os.getpid(), signal.SIGTERM)
            # deal(self.sourcefile_path, self.color, self.size_width, self.size_height, self.size3)
            self.current_img = cv2.imdecode(np.fromfile("last.jpg", dtype=np.uint8), -1)
            self.last_label.setGeometry(300, 220, int(self.size_width), int(self.size_height))
            self.last_label.setStyleSheet("border-image:url(last.jpg)")

    def click5(self):
        if (self.sourcefile_path == ""):
            QMessageBox.warning(self,
                                "警告",
                                "请先上传图片",
                                QMessageBox.Yes)
        else:
          with self.mutex:
            self.size_width = 413
            self.size_height = 626
            self.size3 = 140

            thread = threading.Thread(target=deal, args=(
            self.sourcefile_path, self.color, self.size_width, self.size_height, self.size3))
            thread.start()
            thread.join()
            # os.kill(os.getpid(), signal.SIGTERM)
            # deal(self.sourcefile_path, self.color, self.size_width, self.size_height, self.size3)
            self.current_img = cv2.imdecode(np.fromfile("last.jpg", dtype=np.uint8), -1)
            self.last_label.setGeometry(300, 220, int(self.size_width), int(self.size_height))
            self.last_label.setStyleSheet("border-image:url(last.jpg)")

    def slot_btn_chooseFile(self):
        fileName_choose, filetype = QFileDialog.getOpenFileName(self,
                                                                "选取文件",
                                                                self.cwd,  # 起始路径
                                                                "All Files (*)")  # 设置文件扩展名过滤,用双分号间隔  All Files (*);;
        if fileName_choose == "":
            return

        print("\n你选择的文件为:")
        print(fileName_choose)
        img=cv2.imdecode(np.fromfile(fileName_choose,dtype=np.uint8),-1)
        self.sourcefile_path = fileName_choose
        self.raw_image = img
        self.current_img = img
        self.imgskin = np.zeros(self.raw_image.shape)
        self.gray_img=img
        # self.calculated = False
        # self.calculate()
        return fileName_choose

    # 换装
    def clickcloth1(self):
        if (self.sourcefile_path == ""):
            QMessageBox.warning(self,
                                "警告",
                                "请先上传图片",
                                QMessageBox.Yes)
        else:
            with self.mutex:
              self.cloth_path="1.png"
              thread = threading.Thread(target=self.overlay_clothes, args=(self.cloth_path,))
              thread.start()
              thread.join()
              self.current_img = cv2.imdecode(np.fromfile("last.jpg", dtype=np.uint8), -1)
              self.last_label.setGeometry(300, 220, 410, 575)
              self.last_label.setStyleSheet("border-image:url(last.jpg)")

    def clickcloth2(self):
        if (self.sourcefile_path == ""):
            QMessageBox.warning(self,
                                "警告",
                                "请先上传图片",
                                QMessageBox.Yes)
        else:
            with self.mutex:
              self.cloth_path="2.png"
              thread = threading.Thread(target=self.overlay_clothes, args=(self.cloth_path,))
              thread.start()
              thread.join()
              self.current_img = cv2.imdecode(np.fromfile("last.jpg", dtype=np.uint8), -1)
              self.last_label.setGeometry(300, 220, 410, 575)
              self.last_label.setStyleSheet("border-image:url(last.jpg)")

    def clickcloth3(self):
        if (self.sourcefile_path == ""):
            QMessageBox.warning(self,
                                "警告",
                                "请先上传图片",
                                QMessageBox.Yes)
        else:
            with self.mutex:
              self.cloth_path="3.png"
              thread = threading.Thread(target=self.overlay_clothes, args=(self.cloth_path,))
              thread.start()
              thread.join()
              self.current_img = cv2.imdecode(np.fromfile("last.jpg", dtype=np.uint8), -1)
              self.last_label.setGeometry(300, 220, 410, 575)
              self.last_label.setStyleSheet("border-image:url(last.jpg)")

    def overlay_clothes(self, cloth_path):
        temp_image_path = "temp_image.jpg"
        cv2.imwrite(temp_image_path, self.current_img)
        # 使用临时文件路径进行面部检测
        shape, d = fmarks.predictor_face(temp_image_path)
        # 加载面部图像和服装图像
        face_image = Image.open(temp_image_path).convert("RGBA")
        clothes_image = Image.open(cloth_path).convert("RGBA")
        # 删除临时文件
        os.remove(temp_image_path)
        # 计算面部位置和尺寸
        face_width = d.right() - d.left()
        face_height = d.bottom() - d.top()
        face_center_x = d.left() + face_width // 2
        face_center_y = d.top() + face_height // 2

        # 调整服装图像的大小和位置
        clothes_width, clothes_height = clothes_image.size
        scale_factor_width = face_width * 2.5 / clothes_width
        scale_factor_height = face_height * 2.2 / clothes_height
        scale_factor = max(scale_factor_width, scale_factor_height)  # 取宽高比例中较大的一个
        new_clothes_width = int(clothes_width * scale_factor)
        new_clothes_height = int(clothes_height * scale_factor)
        resized_clothes = clothes_image.resize((new_clothes_width, new_clothes_height), Image.LANCZOS)

        # 初始化衣服位置为面部下方中心
        offset_x = face_center_x - new_clothes_width // 2
        offset_y = d.bottom() - new_clothes_height // 2

        # 创建一个透明背景的图像，用于叠加
        final_image = Image.new("RGBA", face_image.size)

        # 叠加面部图像和服装图像
        final_image.paste(face_image, (0, 0), face_image)
        final_image.paste(resized_clothes, (offset_x, offset_y), resized_clothes)
        # 保存最终图像
        self.current_img = final_image
        final_image = final_image.convert("RGB")
        final_image.save("last.jpg", format='JPEG')



    # 人脸识别
    def test_detect_face(self):
        img = self.current_img
        face_cascade = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        self.gray_img= faces

    def detect_face(self):
        # img = self.gray_img
        img = self.current_img
        face_cascade = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        return faces

    # def detect_face(self):
    #     gray = cv2.cvtColor(self.current_img, cv2.COLOR_BGR2GRAY)
    #     face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    #     faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    #     return faces

    # 皮肤识别
    # def detect_skin(self):
    #     img = self.current_img
    #     rows, cols, channals = img.shape
    #     for r in range(rows):
    #         for c in range(cols):
    #             B = img.item(r, c, 0)
    #             G = img.item(r, c, 1)
    #             R = img.item(r, c, 2)
    #             if (abs(R - G) > 15) and (R > G) and (R > B):
    #                 if (R > 95) and (G > 40) and (B > 20) and (max(R, G, B) - min(R, G, B) > 15):
    #                     self.imgskin[r, c] = (1, 1, 1)
    #                 elif (R > 220) and (G > 210) and (B > 170):
    #                     self.imgskin[r, c] = (1, 1, 1)

    def detect_skin(self):
        img = self.current_img
        img_ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        (y, cr, cb) = cv2.split(img_ycrcb)
        cr1 = cv2.GaussianBlur(cr, (5, 5), 0)
        _, skin = cv2.threshold(cr1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        self.imgskin = cv2.merge((skin, skin, skin))

    def YCrCb_ellipse_model(self):
        skinCrCbHist = np.zeros((256, 256), dtype=np.uint8)
        cv2.ellipse(skinCrCbHist, (113, 155), (23, 25), 43, 0, 360, (255, 255, 255), -1)
        YCrCb = cv2.cvtColor(self.current_img, cv2.COLOR_BGR2YCR_CB)
        (Y, Cr, Cb) = cv2.split(YCrCb)
        skin = np.zeros(Cr.shape, dtype=np.uint8)
        (x, y) = Cr.shape
        for i in range(0, x):
            for j in range(0, y):
                if skinCrCbHist[Cr[i][j], Cb[i][j]] > 0:
                    skin[i][j] = 255
        res = cv2.bitwise_and(self.current_img,self.current_img, mask=skin)
        return skin, res

    def mopi1(self):
        if (self.sourcefile_path == ""):
            QMessageBox.warning(self,
                                "警告",
                                "请先上传图片",
                                QMessageBox.Yes)
        else:
            with self.mutex:

                img1 = beauty.mopi(self.current_img)
                thread = threading.Thread(target=cv2.imwrite, args=("last.jpg",img1))
                thread.start()
                thread.join()

                # img1.save("last.jpg")

                self.current_img = cv2.imdecode(np.fromfile("last.jpg", dtype=np.uint8), -1)
                self.last_label.setGeometry(300, 220, 410, 575)
                self.last_label.setStyleSheet("border-image:url(last.jpg)")

    def big_eye(self):
        if (self.sourcefile_path == ""):
            QMessageBox.warning(self,
                                "警告",
                                "请先上传图片",
                                QMessageBox.Yes)
        else:
            with self.mutex:


                img1 = beauty.big_eye(self.current_img,30,0.1)
                # img2 = Image.fromarray(img1)
                thread=threading.Thread(target=cv2.imwrite, args=("last.jpg",img1))
                thread.start()
                thread.join()


                # img2.save("last.jpg")
                self.current_img = cv2.imdecode(np.fromfile("last.jpg", dtype=np.uint8), -1)
                self.last_label.setGeometry(300, 220, 410, 575)
                self.last_label.setStyleSheet("border-image:url(last.jpg)")



        # 美白算法(皮肤识别)
    def whitening_skin(self):
        with self.mutex:
            value = 25
            self.detect_skin()
            img = self.current_img
            # imgw = np.zeros(img.shape, dtype='uint8')
            imgw = img.copy()
            midtones_add = np.zeros(256)

            for i in range(256):
                midtones_add[i] = 0.667 * (1 - ((i - 127.0) / 127) * ((i - 127.0) / 127))

            lookup = np.zeros(256, dtype="uint8")

            for i in range(256):
                red = i
                red += np.uint8(value * midtones_add[red])
                red = max(0, min(255, red))
                lookup[i] = np.uint8(red)

            rows, cols, channals = img.shape
            for r in range(rows):
                for c in range(cols):

                    if self.imgskin[r, c, 0] == 255:
                        imgw[r, c, 0] = lookup[imgw[r, c, 0]]
                        imgw[r, c, 1] = lookup[imgw[r, c, 1]]
                        imgw[r, c, 2] = lookup[imgw[r, c, 2]]
            self.current_img = imgw
            img1 = Image.fromarray(self.current_img)
            img1.save("last.jpg", format='JPEG')

            # 美白算法(人脸识别)

    def whitening_face(self):
        with self.mutex:
            value = 10
            img = self.current_img
            imgw = img.copy()
            midtones_add = np.zeros(256)
            for i in range(256):
                midtones_add[i] = 0.667 * (1 - ((i - 127.0) / 127) * ((i - 127.0) / 127))

            lookup = np.zeros(256, dtype="uint8")

            for i in range(256):
                red = i
                red += np.uint8(value * midtones_add[red])
                red = max(0, min(0xff, red))
                lookup[i] = np.uint8(red)

            # faces可全局变量
            faces = self.detect_face()

            # 此处当没检测到人脸时不应该对图片进行操作，否则会对整个图片改变颜色
            # 应改为if faces.size!=0  开始操作，前面的直接不要

            if faces.size == 0:
                return imgw

            if faces.size != 0:

                for (x, y, w, h) in faces:
                    x = int(max(x - (w * np.sqrt(2) - w) / 2, 0))
                    y = int(max(y - (h * np.sqrt(2) - h) / 2, 0))
                    w = int(w * np.sqrt(2))
                    h = int(h * np.sqrt(2))

                    rows, cols, _ = img.shape
                    rows = min(rows, y + h)
                    cols = min(cols, x + w)

                    for r in range(y, rows):
                        for c in range(x, cols):
                            imgw[r, c, 0] = lookup[imgw[r, c, 0]]
                            imgw[r, c, 1] = lookup[imgw[r, c, 1]]
                            imgw[r, c, 2] = lookup[imgw[r, c, 2]]

                    process_width = max(min(rows - y, cols - x) // 8, 2)
                    for i in range(1, process_width):
                        alpha = (i - 1) / process_width
                        for r in range(y, rows):
                            imgw[r, x + i - 1] = np.uint8(
                                imgw[r, x + i - 1] * alpha + img[r, x + i - 1] * (1 - alpha))
                            imgw[r, cols - i] = np.uint8(
                                imgw[r, cols - i] * alpha + img[r, cols - i] * (1 - alpha))
                        for c in range(x + process_width, cols - process_width):
                            imgw[y + i - 1, c] = np.uint8(
                                imgw[y + i - 1, c] * alpha + img[y + i - 1, c] * (1 - alpha))
                            imgw[rows - i, c] = np.uint8(
                                imgw[rows - i, c] * alpha + img[rows - i, c] * (1 - alpha))

            def save_image(img_to_save):
                cv2.imwrite("last.jpg", img_to_save)

            thread = threading.Thread(target=save_image, args=(imgw,))
            thread.start()
            thread.join()

            self.current_img = cv2.imdecode(np.fromfile("last.jpg", dtype=np.uint8), -1)

    def deal_pic(self):
      with self.mutex:
        path = self.slot_btn_chooseFile()
        # img1=Image.open(path)
        #deal(path, self.color, self.size_width, self.size_height, self.size3)
        # self.calculated=False
        # thread=threading.Thread(target=self.calculate())
        # thread.start()
        # thread.join()
        self.last_label.setGeometry(300, 220, 400, 500)
        self.last_label.setStyleSheet("border-image:url({});".format(path))


    #图片相关操作
    #保存图片
    def saveImage(self):
        global global_balance
        if (global_balance < 10):
            QMessageBox.warning(self,
                                "警告",
                                "余额不足",
                                QMessageBox.Yes)
        else:
            img = Image.open("last.jpg")
        # 该方法同上
            fdir, ftype = QFileDialog.getSaveFileName(self, "Save Image",
                                                  "./", "Image Files (*.jpg)")
            img.save(fdir)
            try:
            # 减少余额
             reduction_amount = 10.0  # 设定减少的金额
             global_balance -= reduction_amount

            # 更新显示的余额
             welcome_message = f"欢迎回来, {global_user}！余额：{global_balance}"
             self.welcome_label.setText(welcome_message)

            # 更新 balance.txt 文件
             with open("balance.txt", "r") as f:
                lines = f.readlines()

             with open("balance.txt", "w") as f:
                for line in lines:
                    data = line.strip().split(':')
                    if data[0] == global_user:
                        f.write(f"{data[0]}:{global_balance}\n")
                    else:
                        f.write(line)
            except Exception as e:
                self.welcome_label.setText(f"无法更新余额: {e}")

    def transfer_pic(self):
        self.close()
        self.hello_page = HelloPage()
        self.hello_page.exec_()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    mainForm = user_mainWindow()
    mainForm.show()
    sys.exit(app.exec_())