from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QDate, QSize

import sys
from time import sleep
from datetime import datetime
from jdatetime import GregorianToJalali
from os import mkdir, path
from pathlib import Path
import csv
import sqlite3


def resource_path(relative_path):
    # try:
    #     base_path = sys._MEIPASS
    # except Exception:
    #     base_path = path.abspath(".")

    # return path.join(base_path, relative_path)
    return path.join('media', relative_path)


light_blue_color = '#2ABFCD'

file_logo = resource_path('logo.ico')
file_signup_background = resource_path('signup_background.png')
file_signin_background = resource_path('signin_background.png')
file_new = resource_path('new.png')
file_history = resource_path('history.png')
file_about = resource_path('about.png')

file_new2 = resource_path('new2.png')
file_delete = resource_path('close.png')
file_clear = resource_path('clear.png')
file_save = resource_path('save.png')

file_filter = resource_path('filter.png')
file_text_about = R'C:\Users\AmirReza\Desktop\project_kharazmi\media\about.txt'

file_information = R'C:\ProgramData\financial_chores\informatiom.db'
file_costs = R'C:\ProgramData\financial_chores\costs.db'
file_accounts = R'C:\ProgramData\financial_chores\accounts.db'
file_kinds_items = R'C:\ProgramData\financial_chores\kinds_items.csv'


class InitProgram(QWidget):
    def __init__(self):
        super().__init__()

        self.load()
        self.sign()

    def load(self):
        screen = QSplashScreen(self, QPixmap(file_logo))
        screen.setStyleSheet('background-color : white;')
        screen.show()
        sleep(5)
        screen.finish(self)

    def sign(self):
        if not Path(file_information).exists():
            self.sign_up_win = Signup()
            self.sign_up_win.show()
        else:
            self.sign_in_win = Signin()
            self.sign_in_win.show()


class Information:
    def sign_up(username, password, income):
        if not Path(R'C:\ProgramData\financial_chores').exists():
            mkdir(R'C:\ProgramData\financial_chores')

        connector = sqlite3.connect(file_information)
        cursor = connector.cursor()
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS information (username TEXT, password TEXT, income INTEGER)')
        cursor.execute('INSERT INTO information VALUES (?, ?, ?)',
                       (username, password, income))
        connector.commit()
        connector.close()

        lst_kind_items = [['مخارج منزل', 'خرید لوازم خانگی', 'خرید مواد غذایی', 'خرید لوازم و مواد بهداشتی', 'خرید وسایل عمومی', 'فبض آب و برق و گاز'],
                          ['بدهی و اقساط', 'اجاره ی خانه',
                          'خرید لوازم منزل', 'وام بانکی'],
                          ['تعمیرات', 'تعمیر لوازم منزل', 'تعمیر ماشین']]
        with open(file_kinds_items, 'w', encoding='UTF8', newline='\n') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerows(lst_kind_items)

        connector = sqlite3.connect(file_accounts)
        cursor = connector.cursor()

        cursor.execute('CREATE TABLE IF NOT EXISTS accounts (name TEXT, bank_name TEXT, account_number TEXT, owner_name TEXT, account_type TEXT, telephone TEXT, address TEXT, descriptions TEXT)')

        connector.commit()
        connector.close()

    def load_information():
        connector = sqlite3.connect(file_information)
        cursor = connector.cursor()
        cursor.execute('SELECT * FROM information')
        data = cursor.fetchmany()
        connector.commit()
        connector.close()
        return data[0]

    def search_kinds():
        with open(file_kinds_items, 'r', encoding='UTF8') as file:
            csv_reader = list(csv.reader(file))
            kinds = []
            for row in csv_reader:
                kinds.append(row[0])
        return kinds

    def search_items(kind):
        items = []

        with open(file_kinds_items, 'r', encoding='UTF8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if row[0] == kind:
                    items.extend(row[1:])
                    break
        return items

    def save_new_costs(lst_cost):
        connector = sqlite3.connect(file_costs)
        cursor = connector.cursor()
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS costs (name TEXT , kind TEXT, item TEXT, cost INTEGER , date TEXT, payment_type TEXT, account_name TEXT , bank_document_number INTEGER , place_of_payment TEXT, description TEXT, id INTEGER)')

        cursor.execute('SELECT * FROM costs')
        try:
            id = cursor.fetchall()[-1][-1] + 1
        except:
            id = 0
        lst_cost.append(id)

        cursor.execute(
            'INSERT INTO costs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', lst_cost)
        connector.commit()
        connector.close()

    def load_history(from_date, to_date, from_kind, from_item, from_cost, to_cost, from_payment_type, from_account, from_place_of_payment):
        connector = sqlite3.connect(file_costs)
        cursor = connector.cursor()
        cursor.execute('SELECT * FROM costs')
        rows = cursor.fetchall()

        rows_filter = []
        for row in rows:
            date = row[4].split('/')
            date = QDate(int(date[0]), int(date[1]), int(date[2]))

            if date >= from_date and date <= to_date:
                if (from_cost == '' or row[3] >= int(from_cost)) and (to_cost == '' or row[3] <= int(to_cost)):
                    if row[1] == from_kind or from_kind == 'همه ی دسته ها':
                        if row[2] == from_item or from_item == 'همه ی نوع ها':
                            if row[5] == from_payment_type or from_payment_type == 'همه ی انواع پرداخت':
                                if row[6] == from_account or from_account == 'همه ی حساب ها':
                                    if row[8] == from_place_of_payment or from_place_of_payment == 'همه ی مکان های پرداخت':
                                        rows_filter.append(row)

        connector.commit()
        connector.close()
        return rows_filter

    def add_account(name, bank_name, account_number, owner_name, account_type, telephone, address, descriptions):
        connector = sqlite3.connect(file_accounts)
        cursor = connector.cursor()

        cursor.execute('CREATE TABLE IF NOT EXISTS accounts (name TEXT, bank_name TEXT, account_number TEXT, owner_name TEXT, account_type TEXT, telephone TEXT, address TEXT, descriptions TEXT)')
        cursor.execute('INSERT INTO accounts VALUES (?, ?, ?, ?, ?, ?, ?, ?)', [
                       name, bank_name, account_number, owner_name, account_type, telephone, address, descriptions])

        connector.commit()
        connector.close()

    def load_accounts():
        connector = sqlite3.connect(file_accounts)
        cursor = connector.cursor()

        cursor.execute('SELECT * FROM accounts')
        rows = cursor.fetchall()

        connector.commit()
        connector.close()

        return rows


class Signup (QWidget):
    def __init__(self):
        super().__init__()

        self.window()
        self.username_password()
        self.income_register()

    def window(self):
        self.setGeometry(600, 200, 370, 420)
        self.setFixedSize(360, 420)
        self.setStyleSheet('QWidget {background-color : white;}')
        self.setWindowIcon(QIcon(file_logo))
        self.setWindowTitle('ثبت نام')

        self.grid_layout = QGridLayout(self)
        self.grid_layout.setHorizontalSpacing(20)

        self.lb_style = '''font-family: B Koodak; font-size: 16pt; font-weight: Bold;
                            color : darkblue; background-color : rgba(0, 0, 0, 0)'''
        self.le_style = '''QLineEdit {font-family: Calibri; font-size: 12pt; font-weight: Bold;
                        background-color : white; border : 2px solid #2ABFCD; border-radius : 10px}
                        QLineEdit::ToolTip {border : 1px solid black; font-family : B Koodak;}'''

        lb_background = QLabel(self)
        lb_background.setPixmap(QPixmap(file_signup_background))
        lb_background.setGeometry(0, 0, 360, 420)

        self.grid_layout.addItem(QSpacerItem(100, 30), 0, 0, 1, 2)

    def username_password(self):
        self.lb_username = QLabel(self)
        self.grid_layout.addWidget(self.lb_username, 1, 2)
        self.lb_username.setText('نام کاربری:')
        self.lb_username.setAlignment(Qt.AlignRight)
        self.lb_username.setStyleSheet(self.lb_style)
        self.lb_username.setMinimumSize(150, 40)

        self.username = QLineEdit(self)
        self.grid_layout.addWidget(self.username, 1, 0)
        self.username.setPlaceholderText(' نام کاربری خود را وارد نمایید')
        self.username.setStyleSheet(self.le_style)
        self.username.setMinimumSize(200, 40)
        self.username.setMaximumSize(200, 40)
        self.username.returnPressed.connect(lambda: self.password.setFocus())
        self.username.setToolTip('<b> نام کاربری <\b>')

        #########################################################################

        self.lb_password = QLabel(self)
        self.grid_layout.addWidget(self.lb_password, 2, 2)
        self.lb_password.setText('رمز عبور:')
        self.lb_password.setAlignment(Qt.AlignRight)
        self.lb_password.setStyleSheet(self.lb_style)
        self.lb_password.setMinimumSize(150, 40)

        self.password = QLineEdit(self)
        self.grid_layout.addWidget(self.password, 2, 0)
        self.password.setPlaceholderText(' رمز عبور خود را وارد نمایید')
        self.password.setStyleSheet(self.le_style)
        self.password.setMinimumSize(200, 40)
        self.password.setMaximumSize(200, 40)
        self.password.returnPressed.connect(
            lambda: self.confirm_password.setFocus())
        self.password.setToolTip('<b> رمز عبور <\b>')

        ############################################################################

        self.lb_confirm_password = QLabel(self)
        self.grid_layout.addWidget(self.lb_confirm_password, 3, 2)
        self.lb_confirm_password.setText('تایید رمز عبور:')
        self.lb_confirm_password.setAlignment(Qt.AlignRight)
        self.lb_confirm_password.setStyleSheet(self.lb_style)
        self.lb_confirm_password.setMinimumSize(150, 40)

        self.confirm_password = QLineEdit(self)
        self.grid_layout.addWidget(self.confirm_password, 3, 0)
        self.confirm_password.setPlaceholderText(
            ' رمز عبور خود را مجددا وارد نمایید')
        self.confirm_password.setStyleSheet(self.le_style)
        self.confirm_password.setMinimumSize(200, 40)
        self.confirm_password.setMaximumSize(200, 40)
        self.confirm_password.returnPressed.connect(
            lambda: self.month_income.setFocus())
        self.confirm_password.setToolTip('<b> تایید رمز عبور <\b>')

    def income_register(self):
        self.lb_income = QLabel(self)
        self.grid_layout.addWidget(self.lb_income, 4, 2)
        self.lb_income.setText('درآمد ماهانه:')
        self.lb_income.setAlignment(Qt.AlignRight)
        self.lb_income.setStyleSheet(self.lb_style)
        self.lb_income.setMinimumSize(150, 40)

        self.month_income = QLineEdit(self)
        self.grid_layout.addWidget(self.month_income, 4, 0)
        self.month_income.setPlaceholderText(
            ' درآمد ماهانه خود را وارد نمایید')
        self.month_income.setStyleSheet(self.le_style)
        self.month_income.setMinimumSize(200, 40)
        self.month_income.setMaximumSize(200, 40)
        self.month_income.returnPressed.connect(
            lambda: self.btn_register.click())
        self.month_income.setToolTip('<b> درآمد ماهانه <\b>')

        ##########################################################################

        self.btn_register = QPushButton(self)
        self.grid_layout.addWidget(self.btn_register, 5, 1)
        self.btn_register.setText('"ثبت اطلاعات در "حساب کتاب')
        self.btn_register.setStyleSheet(
            'font-family: B Koodak; font-size: 13pt; font-weight: Bold;' +
            'background-color : darkblue; color : white; border: 2px solid #2ABFCD; border-radius : 10px;')
        self.btn_register.setMinimumSize(200, 40)
        self.btn_register.setMaximumSize(200, 40)
        self.btn_register.setCursor(Qt.PointingHandCursor)

        def click_register():
            if self.correct_info() == True:
                Information.sign_up(self.username.text(),
                                    self.password.text(), int(self.month_income.text()))
                self.close()
                self.main_win = MainProgram()
                self.main_win.show()
            else:
                title = self.correct_info()[0]
                text = self.correct_info()[1]
                msg = QMessageBox(QMessageBox.Warning, title,
                                  text, QMessageBox.Ok)
                msg.setWindowIcon(QIcon(file_logo))
                msg.setGeometry(650, 400, 100, 100)
                msg.exec()

        self.btn_register.clicked.connect(click_register)

    def correct_info(self):
        title_error = ''
        text_error = ''
        if self.username.text() == '':
            title_error = 'نام کاربری نادرست'
            text_error = 'لطفا یک نام کاربری وارد نمایید'

        elif self.password.text() == '':
            title_error = 'رمز عبور نادرست'
            text_error = 'لطفا یک رمز عبور وارد نمایید'

        elif self.confirm_password.text() == '':
            title_error = 'تایید رمز عبور نادرست'
            text_error = 'لطفا رمز عبور خود را مجددا\n در تایید پسورد وارد نمایید'

        elif self.month_income.text() == '':
            title_error = 'درآمد نادرست'
            text_error = 'لطفا درآمد ماهیانه ی خود\n را وارد نمایید'

        elif self.confirm_password.text() != self.password.text():
            title_error = 'تایید رمز عبور نادرست'
            text_error = 'کلمه ی تایید رمز عبور نادرست است.\n لطفا مجددا امتحان کنید'

        elif not self.month_income.text().isdigit():
            title_error = 'درآمد نادرست'
            text_error = 'این درآمد ماهانه نامعتبر می باشد.\n لطفا مجددا امتحان کنید'

        if title_error != '' and text_error != '':
            return (title_error, text_error)
        else:
            return True


class Signin (QWidget):
    def __init__(self):
        super().__init__()

        self.window()
        self.username_password()

    def window(self):
        self.setGeometry(600, 200, 350, 270)
        self.setFixedSize(330, 250)
        self.setStyleSheet('QWidget {background-color : white;}')
        self.setWindowIcon(QIcon(file_logo))
        self.setWindowTitle('ورود به برنامه')

        self.grid_layout = QGridLayout(self)
        self.grid_layout.setHorizontalSpacing(30)

        self.lb_style = '''font-family: B koodak; font-size: 16pt; font-weight: Bold;
                            color : darkblue; background-color : rgb(0, 0, 0, 0)'''
        self.le_style = '''QLineEdit {font-family: B Koodak; font-size: 12pt; font-weight: Bold;
                        background-color : white; border : 2px solid #2ABFCD; border-radius : 10px}
                        QLineEdit::ToolTip {border : 1px solid black}'''

        lb_background = QLabel(self)
        lb_background.setGeometry(0, 0, 330, 250)
        lb_background.setPixmap(QPixmap(file_signin_background))

        self.grid_layout.addItem(QSpacerItem(100, 30), 0, 0)

    def username_password(self):
        self.lb_username = QLabel(self)
        self.grid_layout.addWidget(self.lb_username, 1, 2)
        self.lb_username.setText('نام کاربری:')
        self.lb_username.setAlignment(Qt.AlignRight)
        self.lb_username.setStyleSheet(self.lb_style)
        self.lb_username.setMinimumSize(150, 40)

        self.username = QLineEdit(self)
        self.grid_layout.addWidget(self.username, 1, 0)
        self.username.setPlaceholderText(' نام کاربری خود را وارد نمایید')
        self.username.setStyleSheet(self.le_style)
        self.username.setMinimumSize(200, 40)
        self.username.setMaximumSize(200, 40)
        self.username.returnPressed.connect(lambda: self.password.setFocus())
        self.username.setToolTip('<b> نام کاربری <\b>')

        #########################################################################

        self.lb_password = QLabel(self)
        self.grid_layout.addWidget(self.lb_password, 2, 2)
        self.lb_password.setText('رمز عبور:')
        self.lb_password.setAlignment(Qt.AlignRight)
        self.lb_password.setStyleSheet(self.lb_style)
        self.lb_password.setMinimumSize(150, 40)

        self.password = QLineEdit(self)
        self.grid_layout.addWidget(self.password, 2, 0)
        self.password.setPlaceholderText(' رمز عبور خود را وارد نمایید')
        self.password.setStyleSheet(self.le_style)
        self.password.setMinimumSize(200, 40)
        self.password.setMaximumSize(200, 40)
        self.password.returnPressed.connect(lambda: self.btn_register.click())
        self.password.setToolTip('<b> رمز عبور <\b>')

        #########################################################################

        self.btn_register = QPushButton(self)
        self.grid_layout.addWidget(self.btn_register, 3, 1)
        self.btn_register.setText('ورود به نرم افزار')
        self.btn_register.setStyleSheet(
            'QPushButton {font-family: B titr; font-size: 10pt; font-weight: Bold;' +
            'background-color : darkblue; color : white; border: 2px solid #2ABFCD; border-radius : 10px;}' +
            'QPushButton::ToolTip {border : 1px solid black}')
        self.btn_register.setMinimumSize(150, 40)
        self.btn_register.setMaximumSize(150, 40)
        self.btn_register.setToolTip('<b> ورود نرم افزار <\b>')
        self.btn_register.setCursor(Qt.PointingHandCursor)

        def click_register():
            if self.correct_info() == True:
                self.close()
                self.main_win = MainProgram()
                self.main_win.show()
            else:
                title = self.correct_info()[0]
                text = self.correct_info()[1]
                msg = QMessageBox(QMessageBox.Warning, title,
                                  text, QMessageBox.Ok)
                msg.setWindowIcon(QIcon(file_logo))
                msg.setGeometry(650, 400, 100, 100)
                msg.exec()

        self.btn_register.clicked.connect(click_register)

    def correct_info(self):
        title_error = ''
        text_error = ''
        username, password, income = Information.load_information()

        if self.username.text() != username:
            title_error = 'نام کاربری نادرست'
            text_error = 'نام کاربری مورد نظر یافت نشد'
        elif self.password.text() != password:
            title_error = 'رمز عبور نادرست'
            text_error = 'رمز عبور وارد شده صحیح نمی باشد'

        if title_error != '' and text_error != '':
            return (title_error, text_error)
        else:
            return True


class MainProgram (QWidget):
    def __init__(self):
        super().__init__()

        self.window()
        self.make_tabs()

    def window(self):
        self.setFixedSize(920, 600)
        self.setWindowIcon(QIcon(file_logo))
        self.setWindowTitle('حساب کتاب')

        self.main_layout = QGridLayout(self)

    def make_tabs(self):
        buttons_style = 'QToolButton {color : white; font-family : B Traffic; font-size : 13pt; font-weight : Bold}' + \
            'QToolButton::Hover {background-color : #8DDEE7; color : black}'

        self.toolbar = QToolBar(self)
        self.toolbar.setStyleSheet(
            'QToolBar {background-color : #333333; border : 2px solid %s; border-radius : 8px;}' % light_blue_color)
        self.toolbar.setOrientation(Qt.Vertical)
        self.toolbar.setMinimumHeight(580)
        self.toolbar.setMinimumWidth(235)
        self.main_layout.addWidget(self.toolbar, 0, 1)

        self.start_win = QFrame(self)
        self.main_layout.addWidget(self.start_win, 0, 0)
        self.lb_start = QLabel('یک منو را انتخاب نمایید', self.start_win)
        self.lb_start.setGeometry(130, 250, 350, 70)
        self.lb_start.setFont(QFont('B Koodak', 25))
        self.selected_frame = self.start_win

        #############################################################

        self.new_btn = QToolButton(self.toolbar)
        self.new_btn.setStyleSheet(buttons_style)
        self.new_btn.setText('                ثبت هزینه ی جدید')
        self.new_btn.setMinimumSize(220, 40)
        self.new_btn.clicked.connect(lambda: self.open_menus(self.New))
        self.new_btn.setCursor(Qt.PointingHandCursor)
        self.new_btn.setIcon(QIcon(file_new))
        self.new_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.new_btn.setLayoutDirection(Qt.RightToLeft)
        self.toolbar.addWidget(self.new_btn)

        self.recent_btn = QToolButton(self.toolbar)
        self.recent_btn.setStyleSheet(buttons_style)
        self.recent_btn.setText('               تاریخچه ی هزینه ها')
        self.recent_btn.setMinimumSize(220, 40)
        self.recent_btn.clicked.connect(lambda: self.open_menus(self.History))
        self.recent_btn.setCursor(Qt.PointingHandCursor)
        self.recent_btn.setIcon(QIcon(file_history))
        self.recent_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.recent_btn.setLayoutDirection(Qt.RightToLeft)
        self.toolbar.addWidget(self.recent_btn)

        self.bank_accounts_btn = QToolButton(self.toolbar)
        self.bank_accounts_btn.setStyleSheet(buttons_style)
        self.bank_accounts_btn.setText('    مدیریت حساب های بانکی')
        self.bank_accounts_btn.setMinimumSize(220, 40)
        self.bank_accounts_btn.clicked.connect(
            lambda: self.open_menus(self.bank_accounts))
        self.bank_accounts_btn.setCursor(Qt.PointingHandCursor)
        self.bank_accounts_btn.setIcon(QIcon(file_history))
        self.bank_accounts_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.bank_accounts_btn.setLayoutDirection(Qt.RightToLeft)
        self.toolbar.addWidget(self.bank_accounts_btn)

        self.about_btn = QToolButton(self.toolbar)
        self.about_btn.setStyleSheet(buttons_style)
        self.about_btn.setText('                            درباره ی ما')
        self.about_btn.setMinimumSize(220, 40)
        self.about_btn.clicked.connect(lambda: self.open_menus(self.About))
        self.about_btn.setCursor(Qt.PointingHandCursor)
        self.about_btn.setIcon(QIcon(file_about))
        self.about_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.about_btn.setLayoutDirection(Qt.RightToLeft)
        self.toolbar.addWidget(self.about_btn)

    def open_menus(self, widget):
        self.selected_frame.hide()
        self.main_layout.removeWidget(self.selected_frame)
        widget()

    def New(self):
        le_style = 'QLineEdit {border : 2px solid %s; border-radius: 5px;}' % light_blue_color + \
            'QLineEdit::Hover {border : 2px solid darkblue; background-color : #EAEAEA}'

        cb_style = 'QComboBox {border : 2px solid %s; border-radius: 5px;}' % light_blue_color + \
            'QComboBox::Hover {border : 2px solid darkblue; background-color : #EAEAEA;}'

        def make_frames():
            self.new_frame = QFrame(self)
            self.new_frame.setStyleSheet(
                'QFrame {background-color : white; border: 2px solid %s;}' % light_blue_color)
            self.new_frame.setMinimumSize(600, 500)
            self.new_frame.show()

            self.new_layout = QGridLayout(self.new_frame)
            self.new_layout.setHorizontalSpacing(20)
            self.new_layout.setVerticalSpacing(25)
            self.new_frame.setLayout(self.new_layout)

            #############################################################

            self.list_new_frame = QFrame(self)
            self.list_new_frame.setStyleSheet(
                'QFrame {background-color : white; border: 2px solid %s;}' % light_blue_color)
            self.list_new_frame.setMinimumSize(600, 500)

            self.list_new_layout = QGridLayout(self.list_new_frame)
            self.list_new_layout.setHorizontalSpacing(30)
            self.list_new_frame.setLayout(self.list_new_layout)

            #############################################################

            self.new_tabs = QTabWidget(self)
            self.new_tabs.setFont(QFont('B yekan', 12))
            self.new_tabs.setStyleSheet('')
            self.new_tabs.setLayoutDirection(Qt.RightToLeft)
            self.new_tabs.addTab(self.new_frame, 'ثبت اطلاعات هزینه')
            self.new_tabs.addTab(self.list_new_frame, 'لیست هزینه های جدید')

            self.main_layout.addWidget(self.new_tabs, 0, 0)
            self.selected_frame = self.new_tabs

        def make_combobox():
            lb_kind = QLabel(self)
            lb_kind.setText('دسته ی هزینه')
            self.new_layout.addWidget(lb_kind, 1, 0)
            lb_kind.setFont(QFont('B titr', 12))
            lb_kind.setAlignment(Qt.AlignRight)
            lb_kind.setStyleSheet('border : 0px')

            self.cb_kind = QComboBox(self)
            self.new_layout.addWidget(self.cb_kind, 1, 1)
            self.cb_kind.setFont(QFont('B koodak', 12))
            self.cb_kind.setMinimumWidth(180)
            self.cb_kind.addItems(Information.search_kinds())
            self.cb_kind.setCurrentIndex(0)
            self.cb_kind.setEditable(True)
            self.cb_kind.lineEdit().setFont(QFont('B Koodak', 11))
            self.cb_kind.setLayoutDirection(Qt.RightToLeft)
            self.cb_kind.setStyleSheet(cb_style)

            #####################################################

            lb_item = QLabel(self)
            lb_item.setText('نوع هزینه')
            self.new_layout.addWidget(lb_item, 1, 2)
            lb_item.setFont(QFont('B titr', 12))
            lb_item.setAlignment(Qt.AlignRight)
            lb_item.setStyleSheet('border : 0px')
            lb_item.setMinimumWidth(110)

            self.cb_item = QComboBox(self)
            self.new_layout.addWidget(self.cb_item, 1, 3)
            self.cb_item.setFont(QFont('B koodak', 12))
            self.cb_item.setMinimumWidth(180)
            self.cb_item.addItems(
                Information.search_items(self.cb_kind.currentText()))
            self.cb_item.setEditable(True)
            self.cb_item.lineEdit().setFont(QFont('B Koodak', 11))
            self.cb_item.setLayoutDirection(Qt.RightToLeft)
            self.cb_item.setStyleSheet(cb_style)

            def edit_items():
                kind = self.cb_kind.currentText()
                self.cb_item.clear()
                self.cb_item.addItems(Information.search_items(kind))

            self.cb_kind.currentTextChanged.connect(edit_items)

        def make_entry():
            lb_name = QLabel(self)
            lb_name.setText('عنوان هزینه')
            lb_name.setAlignment(Qt.AlignRight)
            self.new_layout.addWidget(lb_name, 2, 0)
            lb_name.setFont(QFont('B titr', 12))
            lb_name.setStyleSheet('border : 0px')
            lb_name.setMinimumWidth(100)

            self.le_name = QLineEdit(self)
            self.new_layout.addWidget(self.le_name, 2, 1)
            self.le_name.setFont(QFont('B Koodak', 11))
            self.le_name.setMaximumWidth(200)
            self.le_name.setAlignment(Qt.AlignCenter)
            self.le_name.setStyleSheet(le_style)

            ##################################################

            lb_cost = QLabel(self)
            lb_cost.setText('مقدار هزینه')
            lb_cost.setAlignment(Qt.AlignRight)
            self.new_layout.addWidget(lb_cost, 3, 2)
            lb_cost.setFont(QFont('B titr', 12))
            lb_cost.setStyleSheet('border : 0px')
            lb_cost.setMinimumWidth(70)

            self.le_cost = QLineEdit(self)
            self.new_layout.addWidget(self.le_cost, 3, 3)
            self.le_cost.setFont(QFont('B Koodak', 11))
            self.le_cost.setAlignment(Qt.AlignCenter)
            self.le_cost.setStyleSheet(le_style)
            self.le_cost.setMaximumWidth(200)

            ##################################################

            lb_desc = QLabel(self)
            lb_desc.setText('توضیحات')
            lb_desc.setAlignment(Qt.AlignRight)
            self.new_layout.addWidget(lb_desc, 6, 0)
            lb_desc.setFont(QFont('B titr', 12))
            lb_desc.setStyleSheet('border : 0px')
            lb_desc.setMinimumWidth(100)

            self.le_desc = QLineEdit(self)
            self.le_desc.setLayoutDirection(Qt.RightToLeft)
            self.new_layout.addWidget(self.le_desc, 6, 1, 1, 3)
            self.le_desc.setFont(QFont('B Koodak', 11))
            self.le_desc.setMaximumSize(400, 40)
            self.le_desc.setStyleSheet(le_style)

        def make_date_register():
            lb_date = QLabel(self)
            lb_date.setText('تاریخ هزینه')
            self.new_layout.addWidget(lb_date, 0, 0)
            lb_date.setFont(QFont('B titr', 12))
            lb_date.setAlignment(Qt.AlignRight)
            lb_date.setStyleSheet('border : 0px')
            lb_date.setMinimumWidth(70)

            now_date = str(datetime.now().date())
            now_date = GregorianToJalali(int(now_date.split(
                '-')[0]), int(now_date.split('-')[1]), int(now_date.split('-')[2])).getJalaliList()
            year = now_date[0]
            month = now_date[1]
            day = now_date[2]

            self.date = QDateEdit(self)
            self.date.setDateRange(QDate(1400, 1, 1), QDate(2050, 12, 30))
            self.date.setDisplayFormat('yyyy/MM/dd')
            self.date.setMaximumSize(200, 30)
            self.date.setDate(QDate(year, month, day))
            self.date.setFont(QFont('B Koodak', 11))
            self.date.setAlignment(Qt.AlignCenter)
            self.date.setStyleSheet('QDateEdit {border : 2px solid %s; border-radius: 5px;}' % light_blue_color +
                                    'QDateEdit::Hover {border : 2px solid darkblue; background-color : #EAEAEA}')
            self.new_layout.addWidget(self.date, 0, 1)

            #################################################################

            def add_cost():
                if correct_info() == True:
                    self.tb_new_costs.insertRow(0)
                    item1 = QTableWidgetItem(self.le_name.text())
                    item2 = QTableWidgetItem(self.cb_kind.currentText())
                    item3 = QTableWidgetItem(self.cb_item.currentText())
                    item4 = QTableWidgetItem(self.le_cost.text())
                    item5 = QTableWidgetItem(
                        str(self.date.date().toString('yyyy/MM/dd')))
                    item6 = QTableWidgetItem(
                        self.cb_payment_type.currentText())

                    if self.cb_payment_type.currentText() == 'صندوق':
                        item7 = QTableWidgetItem('')
                        item8 = QTableWidgetItem('')
                        item9 = QTableWidgetItem('')
                    else:
                        item7 = QTableWidgetItem(
                            self.cb_account_name.currentText())
                        item8 = QTableWidgetItem(
                            self.le_bank_document_number.text())
                        item9 = QTableWidgetItem(
                            self.cb_place_of_payment.currentText())
                    item10 = QTableWidgetItem(self.le_desc.text())

                    item1.setTextAlignment(Qt.AlignCenter)
                    item2.setTextAlignment(Qt.AlignCenter)
                    item3.setTextAlignment(Qt.AlignCenter)
                    item4.setTextAlignment(Qt.AlignCenter)
                    item5.setTextAlignment(Qt.AlignCenter)
                    item6.setTextAlignment(Qt.AlignCenter)
                    item7.setTextAlignment(Qt.AlignCenter)
                    item8.setTextAlignment(Qt.AlignCenter)
                    item9.setTextAlignment(Qt.AlignCenter)
                    item10.setTextAlignment(Qt.AlignCenter)

                    self.tb_new_costs.setItem(0, 0, item1)
                    self.tb_new_costs.setItem(0, 1, item2)
                    self.tb_new_costs.setItem(0, 2, item3)
                    self.tb_new_costs.setItem(0, 3, item4)
                    self.tb_new_costs.setItem(0, 4, item5)
                    self.tb_new_costs.setItem(0, 5, item6)
                    self.tb_new_costs.setItem(0, 6, item7)
                    self.tb_new_costs.setItem(0, 7, item8)
                    self.tb_new_costs.setItem(0, 8, item9)
                    self.tb_new_costs.setItem(0, 9, item10)

                    self.le_name.setText('')
                    self.le_desc.setText('')
                    self.le_cost.setText('')
                    self.le_bank_document_number.setText('')
                    self.cb_kind.setCurrentIndex(0)
                    self.cb_payment_type.setCurrentIndex(1)
                    self.cb_account_name.setCurrentIndex(0)
                    self.cb_place_of_payment.setCurrentIndex(0)
                else:
                    title = correct_info()[0]
                    text = correct_info()[1]
                    msg = QMessageBox(QMessageBox.Warning, title,
                                      text, QMessageBox.Ok)
                    msg.setWindowIcon(QIcon(file_logo))
                    msg.setGeometry(650, 400, 100, 100)
                    msg.exec()

            self.new_layout.addItem(QSpacerItem(100, 50), 7, 0, 1, 3)

            self.save_btn = QPushButton(self.new_frame)
            self.save_btn.setText('افزودن هزینه به لیست هزینه های جدید  ')
            self.save_btn.setFont(QFont('B Koodak', 12))
            self.save_btn.setIcon(QIcon(file_new2))
            self.save_btn.setIconSize(QSize(30, 30))
            self.save_btn.setStyleSheet(
                'background-color: %s; border: 2px solid #16646C; border-radius : 5px' % (light_blue_color))
            self.save_btn.setLayoutDirection(Qt.RightToLeft)
            self.save_btn.setCursor(Qt.PointingHandCursor)
            self.save_btn.clicked.connect(add_cost)
            self.new_layout.addChildWidget(self.save_btn)
            self.save_btn.setGeometry(210, 480, 290, 40)

        def make_bank_account():
            lb_payment_type = QLabel(self)
            lb_payment_type.setText('نوع پرداخت')
            self.new_layout.addWidget(lb_payment_type, 3, 0)
            lb_payment_type.setFont(QFont('B titr', 12))
            lb_payment_type.setAlignment(Qt.AlignRight)
            lb_payment_type.setStyleSheet('border : 0px')

            def change_item(text):
                if text == 'صندوق':
                    self.cb_account_name.setEnabled(False)
                    self.le_bank_document_number.setEnabled(False)
                    self.cb_place_of_payment.setEnabled(False)

                else:
                    self.cb_account_name.setEnabled(True)
                    self.le_bank_document_number.setEnabled(True)
                    self.cb_place_of_payment.setEnabled(True)

            self.cb_payment_type = QComboBox(self)
            self.new_layout.addWidget(self.cb_payment_type, 3, 1)
            self.cb_payment_type.setFont(QFont('B koodak', 11))
            self.cb_payment_type.setMaximumWidth(200)
            self.cb_payment_type.addItems(['صندوق', 'حساب بانکی'])
            self.cb_payment_type.setCurrentIndex(1)
            self.cb_payment_type.currentTextChanged.connect(change_item)
            self.cb_payment_type.setLayoutDirection(Qt.RightToLeft)
            self.cb_payment_type.setStyleSheet(cb_style)

            #############################################################

            lb_account_name = QLabel(self)
            lb_account_name.setText('نام حساب')
            self.new_layout.addWidget(lb_account_name, 4, 0)
            lb_account_name.setFont(QFont('B titr', 12))
            lb_account_name.setAlignment(Qt.AlignRight)
            lb_account_name.setStyleSheet('border : 0px')

            self.cb_account_name = QComboBox(self)
            self.new_layout.addWidget(self.cb_account_name, 4, 1)
            self.cb_account_name.setFont(QFont('B koodak', 11))
            self.cb_account_name.setMaximumWidth(200)

            accounts = Information.load_accounts()
            accounts_name = []
            for account in accounts:
                accounts_name.append(account[0])
            self.cb_account_name.addItems(accounts_name)

            self.cb_account_name.setLayoutDirection(Qt.RightToLeft)
            self.cb_account_name.setStyleSheet(cb_style)

            #############################################################

            lb_bank_document_number = QLabel(self)
            lb_bank_document_number.setText('شماره ی سند بانکی')
            self.new_layout.addWidget(lb_bank_document_number, 4, 2)
            lb_bank_document_number.setFont(QFont('B titr', 12))
            lb_bank_document_number.setAlignment(Qt.AlignRight)
            lb_bank_document_number.setStyleSheet('border : 0px')

            self.le_bank_document_number = QLineEdit(self)
            self.new_layout.addWidget(self.le_bank_document_number, 4, 3)
            self.le_bank_document_number.setFont(QFont('B Koodak', 11))
            self.le_bank_document_number.setMaximumWidth(200)
            self.le_bank_document_number.setAlignment(Qt.AlignCenter)
            self.le_bank_document_number.setStyleSheet(le_style)

            #############################################################

            lb_place_of_payment = QLabel(self)
            lb_place_of_payment.setText('محل پرداخت')
            self.new_layout.addWidget(lb_place_of_payment, 5, 0)
            lb_place_of_payment.setFont(QFont('B titr', 12))
            lb_place_of_payment.setAlignment(Qt.AlignRight)
            lb_place_of_payment.setStyleSheet('border : 0px')

            self.cb_place_of_payment = QComboBox(self)
            self.new_layout.addWidget(self.cb_place_of_payment, 5, 1)
            self.cb_place_of_payment.setFont(QFont('B koodak', 12))
            self.cb_place_of_payment.setMaximumWidth(200)
            self.cb_place_of_payment.addItems(
                ['دستگاه کارت خوان', 'عابر بانک', 'اینترنت', 'همراه بانک'])
            self.cb_place_of_payment.setLayoutDirection(Qt.RightToLeft)
            self.cb_place_of_payment.setStyleSheet(cb_style)

        def make_toolbar():
            toolbar = QToolBar(self)
            toolbar.setStyleSheet(
                'QToolBar {border : 1.5px solid %s; border-radius : 5px}' % light_blue_color)
            self.list_new_layout.addWidget(toolbar, 0, 1)
            toolbar.setFixedSize(445, 40)

            def delete_cost():
                button = self.sender()
                if button:
                    row = self.tb_new_costs.currentRow()
                    self.tb_new_costs.removeRow(row)

            def clear_costs():
                for i in range(0, int(self.tb_new_costs.rowCount())):
                    self.tb_new_costs.removeRow(0)

            self.delete_btn = QToolButton(self)
            self.delete_btn.setText('حذف هزینه')
            self.delete_btn.setFont(QFont('B Koodak', 12))
            toolbar.addWidget(self.delete_btn)
            self.delete_btn.clicked.connect(delete_cost)
            self.delete_btn.setIcon(QIcon(file_delete))
            self.delete_btn.setLayoutDirection(Qt.RightToLeft)
            self.delete_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            self.delete_btn.setCursor(Qt.PointingHandCursor)

            toolbar.addSeparator()

            self.clear_btn = QToolButton(self)
            self.clear_btn.setText('پاک کردن هزینه ها')
            self.clear_btn.setFont(QFont('B Koodak', 12))
            toolbar.addWidget(self.clear_btn)
            self.clear_btn.clicked.connect(clear_costs)
            self.clear_btn.setIcon(QIcon(file_clear))
            self.clear_btn.setLayoutDirection(Qt.RightToLeft)
            self.clear_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            self.clear_btn.setCursor(Qt.PointingHandCursor)

            toolbar.addSeparator()

            self.add_btn = QToolButton(self)
            self.add_btn.setText('ذخیره ی هزینه های جدید')
            self.add_btn.setFont(QFont('B Koodak', 12))
            toolbar.addWidget(self.add_btn)
            self.add_btn.clicked.connect(save_costs)
            self.add_btn.setIcon(QIcon(file_save))
            self.add_btn.setLayoutDirection(Qt.RightToLeft)
            self.add_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            self.add_btn.setCursor(Qt.PointingHandCursor)

        def make_list_costs():
            self.tb_new_costs = QTableWidget(0, 10, self)
            self.list_new_layout.addWidget(self.tb_new_costs, 1, 0, 1, 3)
            self.tb_new_costs.setStyleSheet(
                'border : 1.5px solid %s' % light_blue_color)
            self.tb_new_costs.horizontalHeader().setStyleSheet(
                'border : 0px solid white; border-right : 1px solid %s; border-bottom : 1px solid %s;' % (light_blue_color, light_blue_color))
            self.tb_new_costs.verticalHeader().setStyleSheet(
                'border : 0px solid white; border-left : 1px solid %s; border-top : 1px solid %s;' % (light_blue_color, light_blue_color))

            self.tb_new_costs.setFont(QFont('B koodak', 12))
            self.tb_new_costs.setFixedSize(620, 400)
            self.tb_new_costs.horizontalHeader().setMinimumHeight(30)
            self.tb_new_costs.horizontalHeader().setFont(QFont('B koodak', 12))
            self.tb_new_costs.verticalHeader().setMinimumWidth(20)

            self.tb_new_costs.setColumnWidth(0, 100)
            self.tb_new_costs.setColumnWidth(1, 100)
            self.tb_new_costs.setColumnWidth(2, 100)
            self.tb_new_costs.setColumnWidth(3, 100)
            self.tb_new_costs.setColumnWidth(4, 100)
            self.tb_new_costs.setColumnWidth(5, 100)
            self.tb_new_costs.setColumnWidth(6, 120)
            self.tb_new_costs.setColumnWidth(7, 120)
            self.tb_new_costs.setColumnWidth(8, 100)
            self.tb_new_costs.setColumnWidth(9, 100)
            self.tb_new_costs.setHorizontalHeaderLabels(
                list(reversed(['توضیحات', 'محل پرداخت', 'شماره ی سند بانکی', 'نام حساب', 'نوع پرداخت', 'تاریخ هزینه', 'میزان هزینه', 'نوع هزینه', 'دسته هزینه', 'عنوان هزینه'])))

        def correct_info():
            self.title = ''
            self.message = ''

            if self.le_name.text() == '':
                self.title = 'عنوان نادرست'
                self.message = 'لطفا یک عنوان برای هزینه ی خود انتخاب نمایید'

            elif self.le_cost.text() == '':
                self.title = 'هزینه نادرست'
                self.message = 'لطفا یک مقدار برای هزینه ی خود انتخاب نمایید'

            elif not self.le_cost.text().isdigit():
                self.title = 'هزینه نادرست'
                self.message = 'این مقدار برای هزینه ی جدید معتبر نمی باشد'

            elif self.cb_payment_type.currentText() != 'صندوق':
                if self.le_bank_document_number.text() == '':
                    self.title = 'شماره ی سند بانکی نادرست'
                    self.message = 'لطفا یک مقدار برای شماره ی سند بانکی خود وارد نمایید'

            elif self.cb_kind.lineEdit().text() == '':
                self.title = 'دسته ی هزینه ی نادرست'
                self.message = 'لطفا یک مقدار برای دسته ی هزینه ی خود وارد نمایید'

            elif self.cb_item.lineEdit().text() == '':
                self.title = 'نوع هزینه ی نادرست'
                self.message = 'لطفا یک مقدار برای نوع هزینه ی خود وارد نمایید'

            if self.title != '':
                return (self.title, self.message)
            else:
                return True

        def save_costs():
            for i in range(self.tb_new_costs.rowCount()):
                button = self.sender()
                if button:
                    row = self.tb_new_costs.indexAt(button.pos()).row()

                    row_texts = [str(self.tb_new_costs.item(row, 0).text()),
                                 str(self.tb_new_costs.item(row, 1).text()),
                                 str(self.tb_new_costs.item(row, 2).text()),
                                 int(self.tb_new_costs.item(row, 3).text()),
                                 str(self.tb_new_costs.item(row, 4).text()),
                                 str(self.tb_new_costs.item(row, 5).text()),
                                 str(self.tb_new_costs.item(row, 6).text()),
                                 str(self.tb_new_costs.item(row, 7).text()),
                                 str(self.tb_new_costs.item(row, 8).text()),
                                 str(self.tb_new_costs.item(row, 9).text())]

                    self.tb_new_costs.removeRow(row)

                    Information.save_new_costs(row_texts)

        make_frames()
        make_combobox()
        make_entry()
        make_date_register()
        make_bank_account()
        make_list_costs()
        make_toolbar()

    def History(self):
        le_style = 'QLineEdit {border : 2px solid %s; border-radius: 5px;}' % light_blue_color + \
            'QLineEdit::Hover {border : 2px solid darkblue; background-color : #EAEAEA}'

        date_style = 'QDateEdit {border : 1.5px solid %s; border-radius: 5px;}' % light_blue_color + \
            'QDateEdit::Hover {border : 1.5px solid darkblue; background-color : #EAEAEA}'

        cb_style = 'QComboBox {border : 2px solid %s; border-radius: 5px;}' % light_blue_color + \
            'QComboBox::Hover {border : 2px solid darkblue; background-color : #EAEAEA;}'

        def make_frame():
            self.filter_frame = QFrame(self)
            self.filter_frame.setStyleSheet(
                'QFrame {background-color : white; border: 2px solid %s;}' % light_blue_color)
            self.filter_frame.setMinimumSize(600, 500)
            self.filter_frame.setLayoutDirection(Qt.RightToLeft)
            self.filter_frame.show()

            self.filter_layout = QGridLayout(self.filter_frame)
            self.filter_layout.setHorizontalSpacing(20)
            self.filter_layout.setVerticalSpacing(25)
            self.filter_frame.setLayout(self.filter_layout)

            #############################################################

            self.history_frame = QFrame(self)
            self.history_frame.setStyleSheet(
                'QFrame {background-color : white; border: 2px solid %s;}' % light_blue_color)
            self.history_frame.setMinimumSize(600, 500)
            self.history_frame.setLayoutDirection(Qt.RightToLeft)
            self.history_frame.show()

            self.history_layout = QGridLayout(self.history_frame)
            self.history_layout.setHorizontalSpacing(20)
            self.history_layout.setVerticalSpacing(25)
            self.history_frame.setLayout(self.history_layout)

            #############################################################

            self.history_tabs = QTabWidget(self)
            self.history_tabs.setFont(QFont('B yekan', 12))
            self.history_tabs.setStyleSheet('')
            self.history_tabs.setLayoutDirection(Qt.RightToLeft)
            self.history_tabs.addTab(self.filter_frame, 'فیلتر ها')
            self.history_tabs.addTab(self.history_frame, 'تاریخچه')

            self.main_layout.addWidget(self.history_tabs, 0, 0)
            self.selected_frame = self.history_tabs

        def make_history():
            self.tb_history = QTableWidget(0, 11, self)
            self.history_layout.addWidget(self.tb_history, 1, 0, 1, 3)
            self.tb_history.setStyleSheet(
                'border : 1.5px solid %s' % light_blue_color)
            self.tb_history.horizontalHeader().setStyleSheet(
                'border : 0px solid white; border-right : 1px solid %s; border-bottom : 1px solid %s;' % (light_blue_color, light_blue_color))
            self.tb_history.verticalHeader().setStyleSheet(
                'border : 0px solid white; border-left : 1px solid %s; border-top : 1px solid %s;' % (light_blue_color, light_blue_color))

            self.tb_history.setFont(QFont('B koodak', 12))
            self.tb_history.setFixedSize(620, 430)
            self.tb_history.horizontalHeader().setMinimumHeight(30)
            self.tb_history.horizontalHeader().setFont(QFont('B koodak', 12))
            self.tb_history.verticalHeader().setMinimumWidth(20)
            self.tb_history.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.tb_history.setSelectionMode(
                QAbstractItemView.ExtendedSelection)

            self.tb_history.setColumnWidth(0, 100)
            self.tb_history.setColumnWidth(1, 100)
            self.tb_history.setColumnWidth(2, 100)
            self.tb_history.setColumnWidth(3, 100)
            self.tb_history.setColumnWidth(4, 100)
            self.tb_history.setColumnWidth(5, 100)
            self.tb_history.setColumnWidth(6, 120)
            self.tb_history.setColumnWidth(7, 120)
            self.tb_history.setColumnWidth(8, 100)
            self.tb_history.setColumnWidth(9, 100)
            self.tb_history.setColumnWidth(10, 100)
            self.tb_history.setHorizontalHeaderLabels(
                list(reversed(['توضیحات', 'محل پرداخت', 'شماره ی سند بانکی', 'نام حساب', 'نوع پرداخت', 'تاریخ هزینه', 'میزان هزینه', 'نوع هزینه', 'دسته هزینه', 'عنوان هزینه', 'شماره ی سند'])))

        def load_history():
            if correct_filters() == True:
                if Path(file_costs).exists():
                    self.history_tabs.setCurrentIndex(1)
                    for i in range(0, int(self.tb_history.rowCount())):
                        self.tb_history.removeRow(0)

                    self.costs = Information.load_history(
                        self.from_date.date(), self.to_date.date(), self.from_kind.currentText(),
                        self.from_item.currentText(), self.from_cost.text(),
                        self.to_cost.text(), self.from_payment_type.currentText(), self.from_account.currentText(), self.from_place_of_payment.currentText())

                    document_number = len(self.costs)

                    for cost in self.costs[-1::-1]:
                        number_of_row = self.tb_history.rowCount()
                        self.tb_history.insertRow(number_of_row)

                        item1 = QTableWidgetItem(cost[0])
                        item2 = QTableWidgetItem(cost[1])
                        item3 = QTableWidgetItem(cost[2])
                        item4 = QTableWidgetItem(str(cost[3]))
                        item5 = QTableWidgetItem(cost[4])
                        item6 = QTableWidgetItem(cost[5])
                        item7 = QTableWidgetItem(cost[6])
                        item8 = QTableWidgetItem(str(cost[7]))
                        item9 = QTableWidgetItem(cost[8])
                        item10 = QTableWidgetItem(cost[9])
                        item11 = QTableWidgetItem(str(document_number))

                        item1.setTextAlignment(Qt.AlignCenter)
                        item2.setTextAlignment(Qt.AlignCenter)
                        item3.setTextAlignment(Qt.AlignCenter)
                        item4.setTextAlignment(Qt.AlignCenter)
                        item5.setTextAlignment(Qt.AlignCenter)
                        item6.setTextAlignment(Qt.AlignCenter)
                        item7.setTextAlignment(Qt.AlignCenter)
                        item8.setTextAlignment(Qt.AlignCenter)
                        item9.setTextAlignment(Qt.AlignCenter)
                        item10.setTextAlignment(Qt.AlignCenter)
                        item11.setTextAlignment(Qt.AlignCenter)

                        self.tb_history.setItem(number_of_row, 0, item11)
                        self.tb_history.setItem(number_of_row, 1, item1)
                        self.tb_history.setItem(number_of_row, 2, item2)
                        self.tb_history.setItem(number_of_row, 3, item3)
                        self.tb_history.setItem(number_of_row, 4, item4)
                        self.tb_history.setItem(number_of_row, 5, item5)
                        self.tb_history.setItem(number_of_row, 6, item6)
                        self.tb_history.setItem(number_of_row, 7, item7)
                        self.tb_history.setItem(number_of_row, 8, item8)
                        self.tb_history.setItem(number_of_row, 9, item9)
                        self.tb_history.setItem(number_of_row, 10, item10)

                        document_number -= 1
            else:
                title = correct_filters()[0]
                text = correct_filters()[1]
                msg = QMessageBox(QMessageBox.Warning, title,
                                  text, QMessageBox.Ok)
                msg.setWindowIcon(QIcon(file_logo))
                msg.setGeometry(650, 400, 100, 100)
                msg.exec()

        def date_filters():
            now_date = str(datetime.now().date())
            now_date = GregorianToJalali(int(now_date.split(
                '-')[0]), int(now_date.split('-')[1]), int(now_date.split('-')[2])).getJalaliList()
            year = now_date[0]
            month = now_date[1]
            day = now_date[2]

            ###############################################

            lb_from_date = QLabel('از تاریخ', self)
            lb_from_date.setStyleSheet('border : 0px')
            lb_from_date.setFont(QFont('B titr', 12))
            lb_from_date.setAlignment(Qt.AlignRight)
            self.filter_layout.addWidget(lb_from_date, 1, 0)

            self.from_date = QDateEdit(self)
            self.from_date.setDateRange(QDate(1400, 1, 1), QDate(2050, 12, 30))
            self.from_date.setDisplayFormat('yyyy/MM/dd')
            self.from_date.setMinimumSize(150, 30)
            self.from_date.setDate(QDate(year, month, day))
            self.from_date.setFont(QFont('B Koodak', 12))
            self.from_date.setAlignment(Qt.AlignCenter)
            self.from_date.setStyleSheet(date_style)
            self.filter_layout.addWidget(self.from_date, 1, 1)

            ###############################################

            lb_to_date = QLabel('تا تاریخ', self)
            lb_to_date.setStyleSheet('border : 0px')
            lb_to_date.setFont(QFont('B titr', 12))
            lb_to_date.setAlignment(Qt.AlignRight)
            self.filter_layout.addWidget(lb_to_date, 1, 2)

            self.to_date = QDateEdit(self)
            self.to_date.setDisplayFormat('yyyy/MM/dd')
            self.to_date.setDateRange(QDate(1400, 1, 1), QDate(2050, 12, 30))
            self.to_date.setMinimumSize(150, 30)
            self.to_date.setDate(QDate(year, month, day))
            self.to_date.setFont(QFont('B Koodak', 12))
            self.to_date.setAlignment(Qt.AlignCenter)
            self.to_date.setStyleSheet(date_style)
            self.filter_layout.addWidget(self.to_date, 1, 3)

        def kind_item_filters():
            lb_kind = QLabel(self)
            lb_kind.setText('دسته ی هزینه')
            lb_kind.setFont(QFont('B titr', 12))
            lb_kind.setAlignment(Qt.AlignRight)
            lb_kind.setStyleSheet('border : 0px')
            self.filter_layout.addWidget(lb_kind, 2, 0)

            self.from_kind = QComboBox(self)
            self.from_kind.setFont(QFont('B koodak', 12))
            self.from_kind.setMinimumWidth(200)
            self.from_kind.addItems(Information.search_kinds())
            self.from_kind.addItem('همه ی دسته ها')
            self.from_kind.setCurrentIndex(0)
            self.from_kind.setEditable(True)
            self.from_kind.lineEdit().setFont(QFont('B Koodak', 12))
            self.from_kind.setLayoutDirection(Qt.RightToLeft)
            self.from_kind.setStyleSheet(cb_style)
            self.filter_layout.addWidget(self.from_kind, 2, 1)

            #####################################################

            lb_item = QLabel(self)
            lb_item.setText('نوع هزینه')
            lb_item.setFont(QFont('B titr', 12))
            lb_item.setAlignment(Qt.AlignRight)
            lb_item.setStyleSheet('border : 0px')
            lb_item.setMinimumWidth(110)
            self.filter_layout.addWidget(lb_item, 2, 2)

            self.from_item = QComboBox(self)
            self.from_item.setFont(QFont('B koodak', 12))
            self.from_item.setMinimumWidth(200)
            self.from_item.addItems(
                Information.search_items(self.from_kind.currentText()))
            self.from_item.addItem('همه ی نوع ها')
            self.from_item.setEditable(True)
            self.from_item.lineEdit().setFont(QFont('B Koodak', 12))
            self.from_item.setLayoutDirection(Qt.RightToLeft)
            self.from_item.setStyleSheet(cb_style)
            self.filter_layout.addWidget(self.from_item, 2, 3)

            def edit_items():
                kind = self.from_kind.currentText()
                self.from_item.clear()
                self.from_item.addItems(Information.search_items(kind))
                self.from_item.addItem('همه ی نوع ها')

            self.from_kind.currentTextChanged.connect(edit_items)

        def cost_filters():
            lb_from_cost = QLabel(self)
            lb_from_cost.setText('از مقدار هزینه')
            lb_from_cost.setAlignment(Qt.AlignRight)
            lb_from_cost.setFont(QFont('B titr', 12))
            lb_from_cost.setStyleSheet('border : 0px')
            lb_from_cost.setMinimumWidth(70)
            self.filter_layout.addWidget(lb_from_cost, 3, 0)

            self.from_cost = QLineEdit(self)
            self.from_cost.setFont(QFont('B Koodak', 12))
            self.from_cost.setAlignment(Qt.AlignCenter)
            self.from_cost.setStyleSheet(le_style)
            self.from_cost.setMaximumWidth(200)
            self.filter_layout.addWidget(self.from_cost, 3, 1)

            #################################################

            lb_to_cost = QLabel(self)
            lb_to_cost.setText('تا مقدار هزینه')
            lb_to_cost.setAlignment(Qt.AlignRight)
            lb_to_cost.setFont(QFont('B titr', 12))
            lb_to_cost.setStyleSheet('border : 0px')
            lb_to_cost.setMinimumWidth(70)
            self.filter_layout.addWidget(lb_to_cost, 3, 2)

            self.to_cost = QLineEdit(self)
            self.to_cost.setFont(QFont('B Koodak', 12))
            self.to_cost.setAlignment(Qt.AlignCenter)
            self.to_cost.setStyleSheet(le_style)
            self.to_cost.setMaximumWidth(200)
            self.filter_layout.addWidget(self.to_cost, 3, 3)

        def payment_type_account_place_filters():
            lb_payment_type = QLabel(self)
            lb_payment_type.setText('نوع پرداخت')
            lb_payment_type.setFont(QFont('B titr', 12))
            lb_payment_type.setAlignment(Qt.AlignRight)
            lb_payment_type.setStyleSheet('border : 0px')
            self.filter_layout.addWidget(lb_payment_type, 4, 0)

            def change_item(text):
                if text == 'صندوق':
                    self.from_account.setEnabled(False)
                    self.from_place_of_payment.setEnabled(False)
                else:
                    self.from_account.setEnabled(True)
                    self.from_place_of_payment.setEnabled(True)

            self.from_payment_type = QComboBox(self)
            self.from_payment_type.setFont(QFont('B koodak', 12))
            self.from_payment_type.setMaximumWidth(200)
            self.from_payment_type.addItems(
                ['صندوق', 'حساب بانکی', 'همه ی انواع پرداخت'])
            self.from_payment_type.setCurrentIndex(1)
            self.from_payment_type.currentTextChanged.connect(change_item)
            self.from_payment_type.setLayoutDirection(Qt.RightToLeft)
            self.from_payment_type.setStyleSheet(cb_style)
            self.filter_layout.addWidget(self.from_payment_type, 4, 1)

            ##########################################################

            lb_from_account = QLabel(self)
            lb_from_account.setText('نام حساب')
            lb_from_account.setFont(QFont('B titr', 12))
            lb_from_account.setAlignment(Qt.AlignRight)
            lb_from_account.setStyleSheet('border : 0px')
            self.filter_layout.addWidget(lb_from_account, 4, 2)

            self.from_account = QComboBox(self)
            self.from_account.setFont(QFont('B koodak', 12))
            self.from_account.setMaximumWidth(200)

            accounts = Information.load_accounts()
            accounts_name = []
            for account in accounts:
                accounts_name.append(account[0])
            self.from_account.addItems(accounts_name)
            self.from_account.addItem('همه ی حساب ها')

            self.from_account.setLayoutDirection(Qt.RightToLeft)
            self.from_account.setStyleSheet(cb_style)
            self.filter_layout.addWidget(self.from_account, 4, 3)

            ##########################################################

            lb_from_place_of_payment = QLabel(self)
            lb_from_place_of_payment.setText('محل پرداخت')
            lb_from_place_of_payment.setFont(QFont('B titr', 12))
            lb_from_place_of_payment.setAlignment(Qt.AlignRight)
            lb_from_place_of_payment.setStyleSheet('border : 0px')
            self.filter_layout.addWidget(lb_from_place_of_payment, 5, 0)

            self.from_place_of_payment = QComboBox(self)
            self.from_place_of_payment.setFont(QFont('B koodak', 12))
            self.from_place_of_payment.setMaximumWidth(200)
            self.from_place_of_payment.addItems(
                ['دستگاه کارت خوان', 'عابر بانک', 'اینترنت', 'همراه بانک', 'همه ی مکان های پرداخت'])
            self.from_place_of_payment.setLayoutDirection(Qt.RightToLeft)
            self.from_place_of_payment.setStyleSheet(cb_style)
            self.filter_layout.addWidget(self.from_place_of_payment, 5, 1)

        def filter_btn():
            self.filter_layout.addItem(QSpacerItem(100, 60), 0, 0, 1, 3)

            lb_filter = QLabel(self)
            lb_filter.setText('فیلتر های جست و جو در تاریخچه ی هزینه ها')
            lb_filter.setStyleSheet('border: 0px; color : darkblue')
            lb_filter.setFont(QFont('B Titr', 15))
            lb_filter.setMaximumHeight(40)
            self.filter_layout.addChildWidget(lb_filter)
            lb_filter.setGeometry(200, 20, 320, 40)

            #############################################################

            self.filter_layout.addItem(QSpacerItem(100, 60), 6, 0, 1, 3)

            self.filter_btn = QPushButton(self)
            self.filter_btn.setText('اعمال فیلتر تاریخ  ')
            self.filter_btn.setFont(QFont('B Koodak', 13))
            self.filter_btn.setStyleSheet(
                'background-color: %s; border: 2px solid #16646C; border-radius : 5px' % (light_blue_color))
            self.filter_btn.setIcon(QIcon(file_filter))
            self.filter_btn.setIconSize(QSize(25, 25))
            self.filter_btn.setLayoutDirection(Qt.RightToLeft)
            self.filter_btn.setCursor(Qt.PointingHandCursor)
            self.filter_btn.setMaximumSize(200, 40)
            self.filter_btn.clicked.connect(load_history)
            self.filter_layout.addChildWidget(self.filter_btn)
            self.filter_btn.setGeometry(240, 480, 200, 40)

        def make_toolbar():
            toolbar = QToolBar(self)
            toolbar.setStyleSheet(
                'QToolBar {border : 1.5px solid %s; border-radius : 5px}' % light_blue_color)
            self.history_layout.addWidget(toolbar, 0, 1)
            toolbar.setFixedSize(340, 40)

            def delete_cost():
                button = self.sender()
                if button:
                    row = self.tb_history.currentRow()
                    connector = sqlite3.connect(file_costs)
                    cursor = connector.cursor()

                    id = self.costs[len(self.costs)-row-1][-1]
                    cursor.execute(
                        'DELETE FROM costs WHERE id = ?', str(id))
                    connector.commit()
                    connector.close()
                    self.tb_history.removeRow(row)

            def clear_costs():
                for i in range(0, int(self.tb_history.rowCount())):
                    self.tb_history.removeRow(0)

                connector = sqlite3.connect(file_costs)
                cursor = connector.cursor()
                cursor.execute('DELETE FROM costs')
                connector.commit()
                connector.close()

            self.delete2_btn = QToolButton(self)
            self.delete2_btn.setText('حذف هزینه')
            self.delete2_btn.setFont(QFont('B Koodak', 12))
            toolbar.addWidget(self.delete2_btn)
            self.delete2_btn.setIcon(QIcon(file_delete))
            self.delete2_btn.setLayoutDirection(Qt.RightToLeft)
            self.delete2_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            self.delete2_btn.setCursor(Qt.PointingHandCursor)
            self.delete2_btn.clicked.connect(delete_cost)

            toolbar.addSeparator()

            self.clear2_btn = QToolButton(self)
            self.clear2_btn.setText('پاک کردن کل تارخچه ی هزینه ها')
            self.clear2_btn.setFont(QFont('B Koodak', 12))
            toolbar.addWidget(self.clear2_btn)
            self.clear2_btn.setIcon(QIcon(file_clear))
            self.clear2_btn.setLayoutDirection(Qt.RightToLeft)
            self.clear2_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            self.clear2_btn.setCursor(Qt.PointingHandCursor)
            self.clear2_btn.clicked.connect(clear_costs)

        def correct_filters():
            self.title = ''
            self.message = ''

            if self.from_kind.lineEdit().text() == '':
                self.title = 'دسته ی هزینه ی نادرست'
                self.message = 'لطفا یک مقدار برای دسته ی هزینه ی خود انتخاب نمایید'

            elif self.from_item.lineEdit().text() == '':
                self.title = 'نوع هزینه نادرست'
                self.message = 'لطفا یک مقدار برای نوع هزینه ی خود انتخاب نمایید'

            if self.title != '':
                return (self.title, self.message)
            else:
                return True

        make_frame()
        filter_btn()
        date_filters()
        kind_item_filters()
        cost_filters()
        payment_type_account_place_filters()

        make_history()
        make_toolbar()

    def bank_accounts(self):
        le_style = 'QLineEdit {border : 2px solid %s; border-radius: 5px;}' % light_blue_color + \
            'QLineEdit::Hover {border : 2px solid darkblue; background-color : #EAEAEA}'

        cb_style = 'QComboBox {border : 2px solid %s; border-radius: 5px;}' % light_blue_color + \
            'QComboBox::Hover {border : 2px solid darkblue; background-color : #EAEAEA;}'

        def make_frame():
            self.accounts_frame = QFrame(self)
            self.accounts_frame.setStyleSheet(
                'QFrame {background-color : white; border: 2px solid %s;}' % light_blue_color)
            self.accounts_frame.setMinimumSize(600, 500)
            self.accounts_frame.setLayoutDirection(Qt.RightToLeft)
            self.accounts_frame.show()

            self.accounts_layout = QGridLayout(self.accounts_frame)
            self.accounts_layout.setHorizontalSpacing(25)
            self.accounts_layout.setVerticalSpacing(10)
            self.accounts_frame.setLayout(self.accounts_layout)

            self.main_layout.addWidget(self.accounts_frame, 0, 0)
            self.selected_frame = self.accounts_frame

            self.accounts_layout.addItem(QSpacerItem(250, 40), 0, 0)

            lb_accounts = QLabel(self)
            lb_accounts.setText('ایجاد حساب بانکی جدید')
            lb_accounts.setAlignment(Qt.AlignRight)
            lb_accounts.setFont(QFont('B titr', 13))
            lb_accounts.setStyleSheet('border : 0px; color: darkblue')
            lb_accounts.setMinimumWidth(250)
            lb_accounts.setMaximumHeight(30)
            self.accounts_layout.addChildWidget(lb_accounts)
            lb_accounts.setGeometry(270, 20, 100, 30)

        def make_name_bank_accountnumber():
            lb_name = QLabel(self)
            lb_name.setText('نام نمایشی حساب بانکی')
            lb_name.setAlignment(Qt.AlignRight)
            lb_name.setFont(QFont('B titr', 12))
            lb_name.setStyleSheet('border : 0px')
            self.accounts_layout.addWidget(lb_name, 1, 0)

            self.name = QLineEdit(self)
            self.name.setFont(QFont('B Koodak', 11))
            self.name.setAlignment(Qt.AlignCenter)
            self.name.setMaximumWidth(170)
            self.name.setStyleSheet(le_style)
            self.accounts_layout.addWidget(self.name, 1, 1, 1, 2)

            ######################################################

            lb_bank_name = QLabel(self)
            lb_bank_name.setText('نام بانک')
            lb_bank_name.setAlignment(Qt.AlignRight)
            lb_bank_name.setFont(QFont('B titr', 12))
            lb_bank_name.setStyleSheet('border : 0px')
            self.accounts_layout.addWidget(lb_bank_name, 2, 0)

            self.cb_banks = QComboBox(self)
            self.cb_banks.setFont(QFont('B koodak', 12))
            self.cb_banks.addItems(['پارسیان', 'ملت', 'شهر', 'تجارت',
                                   'ملی', 'سینا', 'صادرات', 'کشاورزی', 'مسکن', 'رفاه کارگران'])
            self.cb_banks.setCurrentIndex(0)
            self.cb_banks.setEditable(True)
            self.cb_banks.setMaximumWidth(140)
            self.cb_banks.lineEdit().setFont(QFont('B Koodak', 11))
            self.cb_banks.setLayoutDirection(Qt.RightToLeft)
            self.cb_banks.setStyleSheet(cb_style)
            self.accounts_layout.addWidget(self.cb_banks, 2, 1)

            ######################################################

            lb_account_number = QLabel(self)
            lb_account_number.setText('شماره ی حساب')
            lb_account_number.setAlignment(Qt.AlignRight)
            lb_account_number.setFont(QFont('B titr', 12))
            lb_account_number.setStyleSheet('border : 0px')
            lb_account_number.setMinimumWidth(170)
            self.accounts_layout.addWidget(lb_account_number, 2, 2)

            self.account_number = QLineEdit(self)
            self.account_number.setFont(QFont('B Koodak', 11))
            self.account_number.setAlignment(Qt.AlignCenter)
            self.account_number.setStyleSheet(le_style)
            self.account_number.setMinimumWidth(170)
            self.accounts_layout.addWidget(self.account_number, 2, 3)

        def make_owner_name_account_type():
            lb_owner_name = QLabel(self)
            lb_owner_name.setText('نام صاحب حساب')
            lb_owner_name.setAlignment(Qt.AlignRight)
            lb_owner_name.setFont(QFont('B titr', 12))
            lb_owner_name.setStyleSheet('border : 0px')
            self.accounts_layout.addWidget(lb_owner_name, 3, 0)

            self.owner_name = QLineEdit(self)
            self.owner_name.setFont(QFont('B Koodak', 11))
            self.owner_name.setAlignment(Qt.AlignCenter)
            self.owner_name.setMaximumWidth(140)
            self.owner_name.setStyleSheet(le_style)
            self.accounts_layout.addWidget(self.owner_name, 3, 1)

            #########################################################

            lb_account_type = QLabel(self)
            lb_account_type.setText('نوع حساب')
            lb_account_type.setAlignment(Qt.AlignRight)
            lb_account_type.setFont(QFont('B titr', 12))
            lb_account_type.setStyleSheet('border : 0px')
            lb_account_type.setMinimumWidth(170)
            self.accounts_layout.addWidget(lb_account_type, 3, 2)

            self.account_type = QComboBox(self)
            self.account_type.setFont(QFont('B koodak', 12))
            self.account_type.addItems(
                ['جاری', 'قرض الحسنه', 'سپرده ی کوتاه مدت', 'سپرده ی بلند مدت'])
            self.account_type.setCurrentIndex(0)
            self.account_type.setEditable(True)
            self.account_type.lineEdit().setFont(QFont('B Koodak', 11))
            self.account_type.setLayoutDirection(Qt.RightToLeft)
            self.account_type.setMinimumWidth(170)
            self.account_type.setStyleSheet(cb_style)
            self.accounts_layout.addWidget(self.account_type, 3, 3)

        def make_telephone_address():
            lb_telephone = QLabel(self)
            lb_telephone.setText('تلفن بانک')
            lb_telephone.setAlignment(Qt.AlignRight)
            lb_telephone.setFont(QFont('B titr', 12))
            lb_telephone.setStyleSheet('border : 0px')
            self.accounts_layout.addWidget(lb_telephone, 4, 0)

            self.telephone = QLineEdit(self)
            self.telephone.setFont(QFont('B Koodak', 11))
            self.telephone.setAlignment(Qt.AlignCenter)
            self.telephone.setMaximumWidth(140)
            self.telephone.setStyleSheet(le_style)
            self.accounts_layout.addWidget(self.telephone, 4, 1)

            ##########################################################

            lb_address = QLabel(self)
            lb_address.setText('آدرس بانک')
            lb_address.setAlignment(Qt.AlignRight)
            lb_address.setFont(QFont('B titr', 12))
            lb_address.setStyleSheet('border : 0px')
            lb_address.setMinimumWidth(170)
            self.accounts_layout.addWidget(lb_address, 4, 2)

            self.address = QLineEdit(self)
            self.address.setFont(QFont('B Koodak', 11))
            self.address.setAlignment(Qt.AlignCenter)
            self.address.setMinimumWidth(170)
            self.address.setStyleSheet(le_style)
            self.accounts_layout.addWidget(self.address, 4, 3)

            ##########################################################

            lb_desc = QLabel(self)
            lb_desc.setText('توضیحات')
            lb_desc.setAlignment(Qt.AlignRight)
            lb_desc.setFont(QFont('B titr', 12))
            lb_desc.setStyleSheet('border : 0px')
            self.accounts_layout.addWidget(lb_desc, 5, 0)

            self.desc = QLineEdit(self)
            self.desc.setFont(QFont('B Koodak', 11))
            self.desc.setAlignment(Qt.AlignCenter)
            self.desc.setMaximumWidth(270)
            self.desc.setStyleSheet(le_style)
            self.accounts_layout.addWidget(self.desc, 5, 1, 1, 3)

        def make_toolbar():
            toolbar = QToolBar(self)
            toolbar.setStyleSheet(
                'QToolBar {border : 1.5px solid %s; border-radius : 5px}' % light_blue_color)
            self.accounts_layout.addWidget(toolbar, 6, 1, 1, 2)
            toolbar.setFixedSize(250, 40)

            def delete_account():
                button = self.sender()
                if button:
                    row = self.tb_accounts.currentRow()
                    self.tb_accounts.removeRow(row)

                account_number = self.accounts[len(self.accounts)-row-1][2]
                connector = sqlite3.connect(file_accounts)
                cursor = connector.cursor()
                cursor.execute('DELETE FROM accounts WHERE account_number = ?', [
                               account_number])
                connector.commit()
                connector.close()

            def add_account():
                if correct_info() == True:

                    Information.add_account(self.name.text(), self.cb_banks.currentText(),
                                            self.account_number.text(), self.owner_name.text(),
                                            self.account_type.currentText(), self.telephone.text(),
                                            self.address.text(), self.desc.text())

                    self.tb_accounts.insertRow(0)
                    item1 = QTableWidgetItem(self.name.text())
                    item2 = QTableWidgetItem(self.cb_banks.currentText())
                    item3 = QTableWidgetItem(self.account_number.text())
                    item4 = QTableWidgetItem(self.owner_name.text())
                    item5 = QTableWidgetItem(self.account_type.currentText())
                    item6 = QTableWidgetItem(self.telephone.text())
                    item7 = QTableWidgetItem(self.address.text())
                    item8 = QTableWidgetItem(self.desc.text())

                    item1.setTextAlignment(Qt.AlignCenter)
                    item2.setTextAlignment(Qt.AlignCenter)
                    item3.setTextAlignment(Qt.AlignCenter)
                    item4.setTextAlignment(Qt.AlignCenter)
                    item5.setTextAlignment(Qt.AlignCenter)
                    item6.setTextAlignment(Qt.AlignCenter)
                    item7.setTextAlignment(Qt.AlignCenter)
                    item8.setTextAlignment(Qt.AlignCenter)

                    self.tb_accounts.setItem(0, 0, item1)
                    self.tb_accounts.setItem(0, 1, item2)
                    self.tb_accounts.setItem(0, 2, item3)
                    self.tb_accounts.setItem(0, 3, item4)
                    self.tb_accounts.setItem(0, 4, item5)
                    self.tb_accounts.setItem(0, 5, item6)
                    self.tb_accounts.setItem(0, 6, item7)
                    self.tb_accounts.setItem(0, 7, item8)

                    self.name.setText('')
                    self.account_number.setText('')
                    self.owner_name.setText('')
                    self.telephone.setText('')
                    self.address.setText('')
                    self.desc.setText('')
                    self.cb_banks.setCurrentIndex(0)
                    self.account_type.setCurrentIndex(0)

                else:
                    title = correct_info()[0]
                    text = correct_info()[1]
                    msg = QMessageBox(QMessageBox.Warning, title,
                                      text, QMessageBox.Ok)
                    msg.setWindowIcon(QIcon(file_logo))
                    msg.setGeometry(650, 400, 100, 100)
                    msg.exec()

            self.delete_btn = QToolButton(self)
            self.delete_btn.setText('حذف حساب')
            self.delete_btn.setFont(QFont('B Koodak', 12))
            self.delete_btn.clicked.connect(delete_account)
            self.delete_btn.setIcon(QIcon(file_delete))
            self.delete_btn.setLayoutDirection(Qt.RightToLeft)
            self.delete_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            self.delete_btn.setCursor(Qt.PointingHandCursor)
            toolbar.addWidget(self.delete_btn)

            toolbar.addSeparator()

            self.add_btn = QToolButton(self)
            self.add_btn.setText('افزودن حساب')
            self.add_btn.setFont(QFont('B Koodak', 12))
            self.add_btn.clicked.connect(add_account)
            self.add_btn.setIcon(QIcon(file_new2))
            self.add_btn.setLayoutDirection(Qt.RightToLeft)
            self.add_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            self.add_btn.setCursor(Qt.PointingHandCursor)
            toolbar.addWidget(self.add_btn)

        def make_tb_accounts():
            self.tb_accounts = QTableWidget(0, 8, self)
            self.accounts_layout.addWidget(self.tb_accounts, 7, 0, 1, 4)
            self.tb_accounts.setStyleSheet(
                'border : 1.5px solid %s' % light_blue_color)
            self.tb_accounts.horizontalHeader().setStyleSheet(
                'border : 0px solid white; border-right : 1px solid %s; border-bottom : 1px solid %s;' % (light_blue_color, light_blue_color))
            self.tb_accounts.verticalHeader().setStyleSheet(
                'border : 0px solid white; border-left : 1px solid %s; border-top : 1px solid %s;' % (light_blue_color, light_blue_color))

            self.tb_accounts.setFont(QFont('B koodak', 12))
            self.tb_accounts.setFixedSize(620, 200)
            self.tb_accounts.horizontalHeader().setMinimumHeight(30)
            self.tb_accounts.horizontalHeader().setFont(QFont('B koodak', 12))
            self.tb_accounts.verticalHeader().setMinimumWidth(20)

            self.tb_accounts.setColumnWidth(0, 100)
            self.tb_accounts.setColumnWidth(1, 100)
            self.tb_accounts.setColumnWidth(2, 100)
            self.tb_accounts.setColumnWidth(3, 100)
            self.tb_accounts.setColumnWidth(4, 100)
            self.tb_accounts.setColumnWidth(5, 100)
            self.tb_accounts.setColumnWidth(6, 100)
            self.tb_accounts.setColumnWidth(7, 100)
            self.tb_accounts.setHorizontalHeaderLabels(
                ['نام نمایشی', 'نام بانک', 'شماره ی حساب', 'نام صاحب', 'نوع حساب', 'تلفن بانک', 'آدرس بانک', 'توضیحات'])

            if Path(file_accounts).exists():
                self.accounts = Information.load_accounts()

                for account in self.accounts:
                    self.tb_accounts.insertRow(0)
                    item1 = QTableWidgetItem(account[0])
                    item2 = QTableWidgetItem(account[1])
                    item3 = QTableWidgetItem(str(account[2]))
                    item4 = QTableWidgetItem(account[3])
                    item5 = QTableWidgetItem(account[4])
                    item6 = QTableWidgetItem(str(account[5]))
                    item7 = QTableWidgetItem(account[6])
                    item8 = QTableWidgetItem(account[7])

                    item1.setTextAlignment(Qt.AlignCenter)
                    item2.setTextAlignment(Qt.AlignCenter)
                    item3.setTextAlignment(Qt.AlignCenter)
                    item4.setTextAlignment(Qt.AlignCenter)
                    item5.setTextAlignment(Qt.AlignCenter)
                    item6.setTextAlignment(Qt.AlignCenter)
                    item7.setTextAlignment(Qt.AlignCenter)
                    item8.setTextAlignment(Qt.AlignCenter)

                    self.tb_accounts.setItem(0, 0, item1)
                    self.tb_accounts.setItem(0, 1, item2)
                    self.tb_accounts.setItem(0, 2, item3)
                    self.tb_accounts.setItem(0, 3, item4)
                    self.tb_accounts.setItem(0, 4, item5)
                    self.tb_accounts.setItem(0, 5, item6)
                    self.tb_accounts.setItem(0, 6, item7)
                    self.tb_accounts.setItem(0, 7, item8)

        def correct_info():
            self.title = ''
            self.message = ''

            if self.name.text() == '':
                self.title = 'نام نمایشی نادرست'
                self.message = 'لطفا یک نام نمایشی برای حساب خود انتخاب نمایید'

            elif not self.account_number.text().isdigit():
                self.title = 'شماره ی حساب نادرست'
                self.message = 'این شماره ی حساب معتبر نمی باشد'

            elif self.owner_name.text() == '':
                self.title = 'نام صاحب نادرست'
                self.message = 'لطفا نام صاحب حساب را وارد نمایید'

            elif self.telephone.text() != '':
                if not self.telephone.text().isdigit():
                    self.title = 'تلفن نادرست'
                    self.message = 'این شماره ی تلفن معتبر نمی باشد'

            if self.title != '':
                return (self.title, self.message)
            else:
                return True

        make_frame()
        make_name_bank_accountnumber()
        make_owner_name_account_type()
        make_telephone_address()
        make_toolbar()
        make_tb_accounts()

    def About(self):

        def make_frame():
            self.about_frame = QFrame(self)
            self.about_frame.setStyleSheet(
                'background-color : white; border: 2px solid %s;' % light_blue_color)
            self.about_frame.setMinimumSize(600, 500)
            self.about_frame.show()

            self.main_layout.addWidget(self.about_frame, 0, 0)
            self.selected_frame = self.about_frame

            self.frame3_layout = QGridLayout(self.about_frame)

        def make_about():
            lb_about = QLabel(self.about_frame)
            lb_about.setGeometry(20, 20, 600, 600)
            self.frame3_layout.addWidget(lb_about, 0, 0)

            with open(file_text_about, 'r', encoding='UTF8') as file:
                text_about = file.read()
            lb_about.setText(text_about)
            lb_about.setWordWrap(True)
            lb_about.setStyleSheet('border: 0px')
            lb_about.setAlignment(Qt.AlignCenter)
            lb_about.setLayoutDirection(Qt.RightToLeft)
            lb_about.setFont(QFont('B Koodak', 15))

            lb_logo = QPushButton(self.about_frame)
            lb_logo.setStyleSheet('border: 0px')
            self.frame3_layout.addWidget(lb_logo, 1, 0)
            lb_logo.setIcon(QIcon(file_logo))
            lb_logo.setFixedSize(100, 100)
            lb_logo.setIconSize(QSize(95, 95))

        make_frame()
        make_about()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InitProgram()
    sys.exit(app.exec())
