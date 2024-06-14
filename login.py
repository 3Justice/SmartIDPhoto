import os
import sys
import threading
import time
from PIL import Image, ImageDraw, ImageOps
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QDialog, QMessageBox, \
    QFileDialog
from mainform import user_mainWindow

# 路径设置
script_directory = os.path.dirname(os.path.abspath(__file__))
user_info_file = os.path.join(script_directory, 'registered_users.txt')
if not os.path.exists(user_info_file):
    open(user_info_file, 'w').close()

# 读取用户信息
users = {}
with open(user_info_file, 'r') as file:
    for line in file:
        if line.strip():
            data = line.strip().split(', ')
            username, password, avatar_path = data[0], data[1], data[2] if len(data) > 2 else 'admin.png'
            avatar = Image.open(avatar_path) if os.path.exists(avatar_path) else None
            users[username] = (password, avatar, avatar_path)


class MainForm(QWidget):
    def __init__(self, name='MainForm'):
        super(MainForm, self).__init__()
        self.setWindowTitle(name)
        self.cwd = os.getcwd()  # Get the current directory
        self.setFixedSize(1170, 780)  # Set window size

        # Background label
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, 1170, 780)
        pixmap = QPixmap('blue.png')
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)

        # White background label
        self.white_background_label = QLabel(self)
        self.white_background_label.setGeometry(60, 100, 440, 590)
        self.white_background_label.setStyleSheet("background-color: white; border-radius: 10px;")
        self.default_admin_logo = QPixmap('admin.png').scaled(70, 70)
        self.init_ui()


    def init_ui(self):
        pix = QPixmap('login.PNG')
        password_logo = QPixmap('pswd.png').scaled(70, 70)

        # Offset for moving UI elements down
        offset_y = 110

        self.admin_logo = QLabel(self)
        self.admin_logo.setGeometry(70, 150 + offset_y, 70, 70)
        self.admin_logo.setPixmap(self.default_admin_logo)

        lb1 = QLabel(self)
        lb1.setGeometry(200, 10 + offset_y, 500, 110)
        lb1.setPixmap(pix)

        lb4 = QLabel(self)
        lb4.setGeometry(70, 250 + offset_y, 70, 70)
        lb4.setPixmap(password_logo)

        self.create_line(70, 225 + offset_y)
        self.create_line(70, 325 + offset_y)

        self.account_input = self.create_input(170, 150 + offset_y)
        self.account_input.textChanged.connect(self.update_avatar)
        self.passwd_input = self.create_input(170, 250 + offset_y, True)

        self.login = self.create_button(130, 380 + offset_y, "登录", "#419BF9", self.word_get)
        self.register_btn = self.create_button(235, 480 + offset_y, "注册", "gray", self.show_register_dialog)
        self.register_btn.setGeometry(QtCore.QRect(235, 480 + offset_y, 100, 60))

    def create_line(self, x, y):
        line = QLabel(self)
        line.setGeometry(x, y, 420, 1)
        line.setStyleSheet("background-color:gray")

    def create_input(self, x, y, is_password=False):
        input_field = QLineEdit(self)
        input_field.setGeometry(QtCore.QRect(x, y, 300, 60))
        font = QtGui.QFont()
        font.setFamily("AcadEref")
        font.setPointSize(20)
        input_field.setFont(font)
        input_field.setStyleSheet("border-width:0;border-style:outset")
        if is_password:
            input_field.setEchoMode(QLineEdit.Password)
        return input_field

    def create_button(self, x, y, text, color, func):
        button = QPushButton(self)
        button.setGeometry(QtCore.QRect(x, y, 300, 60))
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(15)
        button.setFont(font)
        button.setStyleSheet(f"background-color:{color};color:white")
        button.setText(text)
        button.clicked.connect(func)
        return button

    def show_register_dialog(self):
        self.close()
        register_dialog = RegisterDialog(self)
        register_dialog.exec_()

    def word_get(self):
        login_user = self.account_input.text()
        login_password = self.passwd_input.text()
        if login_user in users and users[login_user][0] == login_password:
            try:
                with open("permanent_log.txt", "a") as f:  # Open the file in append mode
                    f.write(f"{login_user}\n")  # Append the log entry with a newline
            except IOError as e:
                QMessageBox.warning(self, "错误", f"无法写入日志文件: {e}", QMessageBox.Yes)
                return
            self.close()
            user_ui.update_welcome_message()  # 更新欢迎信息
            user_ui.show()
        else:
            QMessageBox.warning(self, "警告", "用户名或密码错误！", QMessageBox.Yes)
            self.passwd_input.setText("")
            self.passwd_input.setFocus()

    def update_avatar(self):
        try:
            username = self.account_input.text()
            if username in users and users[username][2]:
                avatar_path = users[username][2]
                rounded_avatar = self.make_rounded_avatar(avatar_path)
                rounded_avatar.save("temp_avatar_login.png")
                pixmap = QPixmap("temp_avatar_login.png")
                self.admin_logo.setPixmap(pixmap.scaled(70, 70, QtCore.Qt.KeepAspectRatio))
            else:
                self.admin_logo.setPixmap(self.default_admin_logo)
        except Exception as e:
            print(f"Error updating avatar: {e}")

    def make_rounded_avatar(self, file_path):
        img = Image.open(file_path).convert("RGBA")
        size = (70, 70)
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        output = ImageOps.fit(img, size, centering=(0.5, 0.5))
        output.putalpha(mask)
        return output


class RegisterDialog(QDialog):
    def __init__(self, main_form):
        super(RegisterDialog, self).__init__()
        self.main_form = main_form
        self.setWindowTitle("注册用户")
        self.setGeometry(900, 270, 400, 430)
        self.avatar_path = None
        self.init_ui()

    def init_ui(self):
        self.username_label = QLabel(self)
        self.username_label.setText("用户名:")
        self.username_label.move(50, 200)
        self.username_entry = QLineEdit(self)
        self.username_entry.setGeometry(110, 190, 230, 30)

        self.password_label = QLabel(self)
        self.password_label.setText("密码:")
        self.password_label.move(50, 240)
        self.password_entry = QLineEdit(self)
        self.password_entry.setGeometry(110, 230, 230, 30)
        self.password_entry.setEchoMode(QLineEdit.Password)

        self.avatar_button = QPushButton(self)
        self.avatar_button.setText("选择头像")
        self.avatar_button.setGeometry(140, 300, 120, 30)
        self.avatar_button.clicked.connect(self.choose_avatar)

        self.register_button = QPushButton(self)
        self.register_button.setText("注册")
        self.register_button.setGeometry(140, 350, 120, 30)
        self.register_button.clicked.connect(self.confirm_registration)

        self.avatar_preview_label = QLabel(self)
        self.avatar_preview_label.setGeometry(140, 30, 130, 130)
        self.avatar_preview_label.setAlignment(QtCore.Qt.AlignCenter)
        initial_avatar = QPixmap('green.jpeg')
        self.avatar_preview_label.setPixmap(initial_avatar.scaled(130, 130, QtCore.Qt.KeepAspectRatio))

    def choose_avatar(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "选择头像", "", "Images (*.png *.xpm *.jpg)", options=options)
        if file_path:
            try:
                self.avatar_path = file_path
                rounded_avatar = self.make_rounded_avatar(file_path)
                rounded_avatar.save("temp_avatar.png")
                pixmap = QPixmap("temp_avatar.png")
                self.avatar_preview_label.setPixmap(pixmap.scaled(100, 100, QtCore.Qt.KeepAspectRatio))
            except Exception as e:
                QMessageBox.warning(self, "错误", f"处理头像时出错: {e}", QMessageBox.Yes)

    def make_rounded_avatar(self, file_path):
        img = Image.open(file_path).convert("RGBA")
        size = (100, 100)
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        output = ImageOps.fit(img, size, centering=(0.5, 0.5))
        output.putalpha(mask)
        return output

    def confirm_registration(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        if username in users:
            QMessageBox.warning(self, "注册失败", "该用户名已被注册！", QMessageBox.Yes)
        else:
            if not self.avatar_path:
                self.avatar_path = 'admin.png'
            users[username] = (password, None, self.avatar_path)
            try:
                with open(user_info_file, 'a') as file:
                    file.write(f"{username}, {password}, {self.avatar_path}\n")
                with open("balance.txt", 'a') as file:
                    file.write(f"{username}:0\n")
                QMessageBox.information(self, "注册成功", "用户注册成功！", QMessageBox.Yes)
                self.close()
                self.main_form.show()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"保存用户信息时出错: {e}", QMessageBox.Yes)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainForm = MainForm('智能证件照生成系统')
    user_ui = user_mainWindow()
    mainForm.show()
    sys.exit(app.exec_())








