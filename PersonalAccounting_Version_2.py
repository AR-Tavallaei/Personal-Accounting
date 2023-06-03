from PyQt5.QtWidgets import QApplication, QWidget, QToolBar, QFrame, QToolButton, QTableWidget, QTableWidgetItem, QPushButton
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, QDateEdit, QLineEdit, QSpacerItem
from PyQt5.QtWidgets import QLabel, QAbstractItemView, QTabWidget, QSplashScreen, QGroupBox, QRadioButton
from PyQt5.QtGui import QIcon, QPixmap, QFont, QFontDatabase
from PyQt5.QtCore import Qt, QDate, QSize

import sys
from time import sleep
from datetime import datetime
from jdatetime import GregorianToJalali, date
from os import mkdir, path, remove, listdir
from pathlib import Path
import csv
import sqlite3
from webbrowser import WindowsDefault
from hashlib import sha512
from matplotlib import pyplot as plt
from numpy import array
import arabic_reshaper
from bidi.algorithm import get_display


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")

    if relative_path == 'fonts':
        return path.join(base_path, relative_path)
    else:
        return path.join(base_path, 'media\\' + relative_path)


light_blue_color = '#2ABFCD'

file_logo = resource_path('logo.ico')
file_new = resource_path('new.png')
file_history = resource_path('history.png')
file_bank_account = resource_path('bank.png')
file_analyze = resource_path('analyze.png')
file_new_user = resource_path('add_user.png')
file_signin_again = resource_path('login.png')
file_remove_user = resource_path('remove_user.png')
file_about = resource_path('about.png')

file_new2 = resource_path('new2.png')
file_new3 = resource_path('new3.png')
file_delete = resource_path('close.png')
file_clear = resource_path('clear.png')
file_save = resource_path('save.png')

file_filter = resource_path('filter.png')
file_text_about = resource_path('about.txt')
file_fonts = resource_path('fonts')

file_information = 'C:/ProgramData/financial_chores/informatiom.db'
file_costs = 'C:/ProgramData/financial_chores/costs%s.db'
file_temporary_costs = 'C:/ProgramData/financial_chores/temporary_costs%s.db'
file_accounts = 'C:/ProgramData/financial_chores/accounts%s.db'
file_kinds_items = 'C:/ProgramData/financial_chores/kinds_items.csv'


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
            self.sign_up_win = Signup(1000)
            self.sign_up_win.show()
        else:
            self.sign_in_win = Signin(1000)
            self.sign_in_win.show()


class Information:
    def sign_up(username, password, income, user_id):
        if not Path(R'C:\ProgramData\financial_chores').exists():
            mkdir(R'C:\ProgramData\financial_chores')

        ##########################################################
        connector = sqlite3.connect(file_information)
        cursor = connector.cursor()
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS information (username TEXT, password TEXT, income INTEGER, user_id INTEGER)')
        cursor.execute('INSERT INTO information VALUES (?, ?, ?, ?)',
                       (Information.make_secret_username(username), str(sha512(password.encode()).hexdigest()), income, user_id))
        connector.commit()
        connector.close()

        ##########################################################
        lst_kind_items = [['مخارج منزل', 'خرید لوازم خانگی', 'خرید مواد غذایی', 'خرید لوازم و مواد بهداشتی',
                           'خرید پوشاک', 'شارژ ساختمان', 'خرید وسایل عمومی', 'قبض آب و برق و گاز', 'دیگر'],
                          ['بدهی و اقساط', 'اجاره ی خانه', 'پرداخت شهریه',
                           'خرید لوازم منزل', 'وام بانکی', 'دیکر'],
                          ['تعمیرات', 'تعمیر لوازم منزل', 'تعمیر ماشین',
                              'تعمیر وسایل الکترونیکی', 'دیگر'],
                          ['مخارج عمومی', 'بازدید از مکان های تفریحی', 'تاکسی اینترنتی',
                          'پرداخت شهریه', 'بلیط هواپیما و قطار و اتوبوس', 'دیگر']]
        with open(file_kinds_items, 'w', encoding='UTF8', newline='\n') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerows(lst_kind_items)

        ##########################################################
        connector = sqlite3.connect(file_accounts % user_id)
        cursor = connector.cursor()
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS accounts (name TEXT, bank_name TEXT, account_number TEXT, owner_name TEXT, account_type TEXT, telephone TEXT, address TEXT, descriptions TEXT)')
        connector.commit()
        connector.close()

        ##########################################################
        connector = sqlite3.connect(file_costs % user_id)
        cursor = connector.cursor()
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS costs (name TEXT , kind TEXT, item TEXT, cost INTEGER , date TEXT, payment_type TEXT, account_name TEXT , bank_document_number INTEGER , place_of_payment TEXT, description TEXT, id INTEGER)')
        connector.commit()
        connector.close()

        ##########################################################
        connector = sqlite3.connect(file_temporary_costs % user_id)
        cursor = connector.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS temporary_costs (name TEXT , kind TEXT, item TEXT, cost INTEGER , date TEXT, payment_type TEXT, account_name TEXT , bank_document_number INTEGER , place_of_payment TEXT, description TEXT)')
        connector.commit()
        connector.close()

    def sign_in(input_username, input_password):
        connector = sqlite3.connect(file_information)
        cursor = connector.cursor()
        cursor.execute('SELECT * FROM information')
        data = cursor.fetchall()

        for user in data:
            if user[0] == input_username:
                if user[1] == input_password:
                    connector.commit()
                    connector.close()
                    return [True, True, user[3]]
                else:
                    return [True, None, None]

        return [None, None, None]

    def load_information(user_id):
        connector = sqlite3.connect(file_information)
        cursor = connector.cursor()
        cursor.execute(
            'SELECT * FROM information WHERE user_id = ?', [str(user_id)])
        data = cursor.fetchone()
        connector.commit()
        connector.close()

        return data

    def search_kinds():
        if not Path(file_kinds_items).exists():
            lst_kind_items = [['مخارج منزل', 'خرید لوازم خانگی', 'خرید مواد غذایی', 'خرید لوازم و مواد بهداشتی',
                               'خرید پوشاک', 'شارژ ساختمان', 'خرید وسایل عمومی', 'قبض آب و برق و گاز', 'دیگر'],
                              ['بدهی و اقساط', 'اجاره ی خانه', 'پرداخت شهریه',
                               'خرید لوازم منزل', 'وام بانکی', 'دیکر'],
                              ['تعمیرات', 'تعمیر لوازم منزل', 'تعمیر ماشین',
                              'تعمیر وسایل الکترونیکی', 'دیگر'],
                              ['مخارج عمومی', 'بازدید از مکان های تفریحی', 'تاکسی اینترنتی',
                               'پرداخت شهریه', 'بلیط هواپیما و قطار و اتوبوس', 'دیگر']]
            with open(file_kinds_items, 'w', encoding='UTF8', newline='\n') as file:
                csv_writer = csv.writer(file)
                csv_writer.writerows(lst_kind_items)

        with open(file_kinds_items, 'r', encoding='UTF8') as file:
            csv_reader = list(csv.reader(file))
            kinds = []
            for row in csv_reader:
                kinds.append(row[0])
        return kinds

    def search_items(kind):
        if not Path(file_kinds_items).exists():
            lst_kind_items = [['مخارج منزل', 'خرید لوازم خانگی', 'خرید مواد غذایی', 'خرید لوازم و مواد بهداشتی',
                               'خرید پوشاک', 'شارژ ساختمان', 'خرید وسایل عمومی', 'قبض آب و برق و گاز', 'دیگر'],
                              ['بدهی و اقساط', 'اجاره ی خانه', 'پرداخت شهریه',
                               'خرید لوازم منزل', 'وام بانکی', 'دیکر'],
                              ['تعمیرات', 'تعمیر لوازم منزل', 'تعمیر ماشین',
                              'تعمیر وسایل الکترونیکی', 'دیگر'],
                              ['مخارج عمومی', 'بازدید از مکان های تفریحی', 'تاکسی اینترنتی',
                               'پرداخت شهریه', 'بلیط هواپیما و قطار و اتوبوس', 'دیگر']]
            with open(file_kinds_items, 'w', encoding='UTF8', newline='\n') as file:
                csv_writer = csv.writer(file)
                csv_writer.writerows(lst_kind_items)

        items = []
        with open(file_kinds_items, 'r', encoding='UTF8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if row[0] == kind:
                    items.extend(row[1:])
                    break
        return items

    def save_new_costs(lst_cost, user_id):
        connector = sqlite3.connect(file_costs % user_id)
        cursor = connector.cursor()
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS costs (name TEXT , kind TEXT, item TEXT, cost INTEGER , date TEXT, payment_type TEXT, account_name TEXT , bank_document_number INTEGER , place_of_payment TEXT, description TEXT, id INTEGER)')

        for cost in lst_cost:
            cost = list(cost)
            cursor.execute('SELECT * FROM costs')
            try:
                id = cursor.fetchall()[-1][-1] + 1
            except:
                id = 1
            cost.append(id)

            cursor.execute(
                'INSERT INTO costs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', cost)

        connector.commit()
        connector.close()

    def save_temporary_new_cost(lst_cost, user_id):
        connector = sqlite3.connect(file_temporary_costs % user_id)
        cursor = connector.cursor()

        cursor.execute('CREATE TABLE IF NOT EXISTS temporary_costs (name TEXT , kind TEXT, item TEXT, cost INTEGER , date TEXT, payment_type TEXT, account_name TEXT , bank_document_number INTEGER , place_of_payment TEXT, description TEXT)')

        cursor.execute(
            'INSERT INTO temporary_costs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', lst_cost)
        connector.commit()
        connector.close()

    def load_history(user_id, from_date, to_date, from_kind, from_item, from_cost, to_cost, from_payment_type, from_account, from_place_of_payment, name, desc):
        connector = sqlite3.connect(file_costs % user_id)
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
                                        if (name == '' or name in row[0]) and (desc == '' or desc in row[9]):
                                            rows_filter.append(row)

        connector.commit()
        connector.close()
        return rows_filter

    def load_temporary_costs(user_id):
        connctor = sqlite3.connect(file_temporary_costs % user_id)
        cursor = connctor.cursor()

        cursor.execute('SELECT * FROM temporary_costs')
        temporary_costs = cursor.fetchall()

        connctor.commit()
        connctor.close()

        return temporary_costs

    def add_account(user_id, name, bank_name, account_number, owner_name, account_type, telephone, address, descriptions):
        connector = sqlite3.connect(file_accounts % user_id)
        cursor = connector.cursor()

        cursor.execute(
            'CREATE TABLE IF NOT EXISTS accounts (name TEXT, bank_name TEXT, account_number TEXT, owner_name TEXT, account_type TEXT, telephone TEXT, address TEXT, descriptions TEXT)')
        cursor.execute('INSERT INTO accounts VALUES (?, ?, ?, ?, ?, ?, ?, ?)', [
            name, bank_name, account_number, owner_name, account_type, telephone, address, descriptions])

        connector.commit()
        connector.close()

    def load_accounts(user_id):
        connector = sqlite3.connect(file_accounts % user_id)
        cursor = connector.cursor()

        cursor.execute('SELECT * FROM accounts')
        rows = cursor.fetchall()

        connector.commit()
        connector.close()

        return rows

    def remove_temporary_cost(lst_cost, user_id):
        connector = sqlite3.connect(file_temporary_costs % user_id)
        cursor = connector.cursor()

        cursor.execute('DELETE FROM temporary_costs WHERE name = ? AND kind = ? AND item = ? AND cost = ? AND date = ? AND payment_type = ? AND account_name = ? AND bank_document_number = ? AND place_of_payment = ? AND description = ?', lst_cost)

        connector.commit()
        connector.close()

    def remove_cost(id, user_id):
        connector = sqlite3.connect(file_costs % user_id)
        cursor = connector.cursor()

        cursor.execute('DELETE FROM costs WHERE id = ?', [id])
        cursor.execute('UPDATE costs SET id = id - 1 WHERE id > ?', [id])

        connector.commit()
        connector.close()

    def remove_account(account_number, user_id):
        connector = sqlite3.connect(file_accounts % user_id)
        cursor = connector.cursor()
        cursor.execute('DELETE FROM accounts WHERE account_number = ?', [
            account_number])
        connector.commit()
        connector.close()

    def get_new_user_id():
        if Path(file_information).exists():
            connector = sqlite3.connect(file_information)
            cursor = connector.cursor()
            cursor.execute('SELECT * FROM information')
            data = cursor.fetchall()
            connector.commit()
            connector.close()
            return data[-1][-1] + 1
        else:
            return 1001

    def make_secret_username(username):
        secret_username = ''
        for i in range(1, len(username), 2):
            secret_username += username[i] + username[i-1]
        if len(username) % 2 == 1:
            secret_username += username[-1]

        for j in range(0, int(len(secret_username)/2)):
            section1 = secret_username[:j]
            section2 = secret_username[-j-1]
            section3 = secret_username[j+1:-j-1]
            section4 = secret_username[j]
            section5 = secret_username[len(
                section1 + section2 + section3 + section4):]

            secret_username = section1 + section2 + section3 + section4 + section5

        return secret_username

    def convert_secret_to_username(secret_username):
        for j in range(0, int(len(secret_username)/2)):
            section1 = secret_username[:j]
            section2 = secret_username[-j-1]
            section3 = secret_username[j+1:-j-1]
            section4 = secret_username[j]
            section5 = secret_username[len(
                section1 + section2 + section3 + section4):]

            secret_username = section1 + section2 + section3 + section4 + section5

        username = ''
        for i in range(1, len(secret_username), 2):
            username += secret_username[i] + secret_username[i-1]
        if len(secret_username) % 2 == 1:
            username += secret_username[-1]

        return username

    def remove_user(user_id):
        connector = sqlite3.connect(file_information)
        cursor = connector.cursor()
        cursor.execute(
            'DELETE FROM information WHERE user_id = ?', [user_id])
        cursor.execute('SELECT * FROM information')
        data = cursor.fetchall()
        connector.commit()
        connector.close()
        if data == []:
            remove(file_information)

        remove(file_costs % user_id)
        remove(file_accounts % user_id)
        remove(file_temporary_costs % user_id)

    def get_min_max_date_costs(user_id):
        connector = sqlite3.connect(file_costs % user_id)
        cursor = connector.cursor()
        cursor.execute('SELECT date FROM costs')
        data = cursor.fetchall()
        dates = set()
        for date in data:
            date = date[0].split('/')
            dates.add(QDate(int(date[0]), int(date[1]), int(date[2])))

        dates = sorted(dates)
        return [dates[0], dates[-1]]

    def get_costs_of_month(user_id, year, month):
        connector = sqlite3.connect(file_costs % user_id)
        cursor = connector.cursor()
        cursor.execute('SELECT cost, date, item FROM costs')
        data = cursor.fetchall()
        connector.commit()
        connector.close()

        dict_cost = {str(i): [] for i in range(1, 32)}

        for cost, date, item in data:
            date = list(map(int, date.split('/')))
            if date[0] == int(year) and date[1] == int(month):
                dict_cost.get(str(date[2])).append((cost, item))

        return dict_cost

    def get_costs_of_year(user_id, year):
        dict_cost = {str(i): {} for i in range(1, 13)}
        for month in dict_cost:
            dict_cost[month] = Information.get_costs_of_month(
                user_id, year, month)

        return dict_cost

    def get_percentages_month(user_id, year, month):
        connector = sqlite3.connect(file_costs % user_id)
        cursor = connector.cursor()
        cursor.execute('SELECT date, item, cost FROM costs')
        data = cursor.fetchall()
        connector.commit()
        connector.close()

        dict_percentages = {}

        for cost in data:
            date = list(map(int, cost[0].split('/')))
            if (date[0] == int(year) and month == 'all') or (date[0] == int(year) and date[1] == int(month)):
                dict_percentages[cost[1]] = dict_percentages.get(
                    cost[1], 0) + cost[2]

        sum_of_costs = sum(dict_percentages.values())

        for item in dict_percentages:
            dict_percentages[item] = round(
                (dict_percentages[item] / sum_of_costs) * 100, 2)

        return dict_percentages


class Signup (QWidget):
    def __init__(self, user_id):
        super().__init__()

        self.user_id = user_id
        self.window()
        self.username_password()
        self.income_register()

    def window(self):
        self.setGeometry(600, 200, 420, 490)
        self.setFixedSize(420, 490)
        self.setStyleSheet('QWidget {background-color : #2b2b2b;}')
        self.setWindowIcon(QIcon(file_logo))
        self.setWindowTitle('ثبت نام')
        self.setLayoutDirection(Qt.RightToLeft)

        self.grid_layout = QGridLayout(self)
        self.grid_layout.setVerticalSpacing(30)

        self.btn_style = '''QPushButton {font-family : B Titr; font-size: 11pt; font-weight: bold;
                            background-color : #2b2b2b; color : white; border: 2px solid #2ABFCD; border-radius : 10px; padding: 5px}
                            QPushButton::Hover {background-color: darkgray; color: black;}'''

        self.lb_style = '''font-family: B Koodak; font-size: 16pt; font-weight: Bold;
                            color : white; background-color : rgba(0, 0, 0, 0)'''

        self.le_style = '''QLineEdit {font-family: B Koodak; font-size: 12pt; font-weight: Bold;
                        background-color : white; border : 2px solid #2ABFCD; border-radius : 10px; min-height: 35px}
                        QLineEdit::ToolTip {border : 1px solid black; font-family : B Koodak;}
                        QLineEdit::Hover {border: 2px solid darkblue; background-color: #EAEAEA;}
                        QLineEdit:Focus {border : 2px solid darkblue; background-color : #EAEAEA;}'''

        self.lb_welcome = QLabel(self)
        self.grid_layout.addWidget(self.lb_welcome, 0, 0, 1, 2, Qt.AlignLeft)
        self.lb_welcome.setText('به اپلیکیشن "حساب کتاب" خوش آمدید!')
        self.lb_welcome.setAlignment(Qt.AlignRight)
        self.lb_welcome.setStyleSheet(
            'background-color: rgba(0, 0, 0, 0); color: #00c4c2; font-family: B Zar; font-size: 15pt; font-weight : bold')

    def username_password(self):
        self.hbox1 = QHBoxLayout(self)
        self.grid_layout.addLayout(self.hbox1, 1, 0, 1, 2)

        self.lb_username = QLabel(self)
        self.hbox1.addWidget(self.lb_username, 1)
        self.lb_username.setText('نام کاربری:')
        self.lb_username.setAlignment(Qt.AlignRight)
        self.lb_username.setStyleSheet(self.lb_style)

        self.hbox1.addSpacing(30)

        self.username = QLineEdit(self)
        self.hbox1.addWidget(self.username, 2)
        self.username.setPlaceholderText(' نام کاربری خود را وارد نمایید')
        self.username.setStyleSheet(self.le_style)
        self.username.returnPressed.connect(lambda: self.password.setFocus())
        self.username.setToolTip('<b> نام کاربری <\b>')

        #########################################################################
        self.hbox2 = QHBoxLayout(self)
        self.grid_layout.addLayout(self.hbox2, 2, 0, 1, 2)

        self.lb_password = QLabel(self)
        self.hbox2.addWidget(self.lb_password, 1)
        self.lb_password.setText('رمز عبور:')
        self.lb_password.setAlignment(Qt.AlignRight)
        self.lb_password.setStyleSheet(self.lb_style)

        self.hbox2.addSpacing(30)

        self.password = QLineEdit(self)
        self.hbox2.addWidget(self.password, 2)
        self.password.setPlaceholderText(' رمز عبور خود را وارد نمایید')
        self.password.setStyleSheet(self.le_style)
        self.password.returnPressed.connect(
            lambda: self.confirm_password.setFocus())
        self.password.setToolTip('<b> رمز عبور <\b>')
        self.password.setEchoMode(QLineEdit.Password)

        ############################################################################
        self.hbox3 = QHBoxLayout(self)
        self.grid_layout.addLayout(self.hbox3, 3, 0, 1, 2)

        self.lb_confirm_password = QLabel(self)
        self.hbox3.addWidget(self.lb_confirm_password, 1)
        self.lb_confirm_password.setText('تایید رمز عبور:')
        self.lb_confirm_password.setAlignment(Qt.AlignRight)
        self.lb_confirm_password.setStyleSheet(self.lb_style)

        self.hbox3.addSpacing(15)

        self.confirm_password = QLineEdit(self)
        self.hbox3.addWidget(self.confirm_password, 2)
        self.confirm_password.setPlaceholderText(
            ' رمز عبور خود را مجددا وارد نمایید')
        self.confirm_password.setStyleSheet(self.le_style)
        self.confirm_password.returnPressed.connect(
            lambda: self.month_income.setFocus())
        self.confirm_password.setToolTip('<b> تایید رمز عبور <\b>')
        self.confirm_password.setEchoMode(QLineEdit.Password)

    def income_register(self):
        self.hbox4 = QHBoxLayout(self)
        self.grid_layout.addLayout(self.hbox4, 4, 0, 1, 2)

        self.lb_income = QLabel(self)
        self.hbox4.addWidget(self.lb_income, 1)
        self.lb_income.setText('درآمد ماهانه:')
        self.lb_income.setAlignment(Qt.AlignRight)
        self.lb_income.setStyleSheet(self.lb_style)

        self.hbox4.addSpacing(30)

        self.month_income = QLineEdit(self)
        self.hbox4.addWidget(self.month_income, 2)
        self.month_income.setPlaceholderText(
            ' درآمد ماهانه خود را وارد نمایید')
        self.month_income.setStyleSheet(self.le_style)
        self.month_income.returnPressed.connect(
            lambda: self.btn_register.click())
        self.month_income.setToolTip('<b> درآمد ماهانه <\b>')

        ##########################################################################

        self.btn_register = QPushButton(self)
        self.grid_layout.addWidget(
            self.btn_register, 5, 0, Qt.AlignCenter)
        self.btn_register.setText('"ثبت اطلاعات در "حساب کتاب')
        self.btn_register.setStyleSheet(self.btn_style)
        self.btn_register.setCursor(Qt.PointingHandCursor)
        self.btn_register.setFixedSize(250, 40)

        self.btn_cancel = QPushButton(self)
        self.grid_layout.addWidget(self.btn_cancel, 6, 0, Qt.AlignCenter)
        self.btn_cancel.setFixedSize(250, 40)
        self.btn_cancel.setText('لغو و بستن پنجره')
        self.btn_cancel.setStyleSheet(
            self.btn_style + 'QPushButton {font-size: 12pt}')
        self.btn_cancel.setToolTip('<b> ورود نرم افزار <\b>')
        self.btn_cancel.setCursor(Qt.PointingHandCursor)

        def click_register():
            try:
                if self.correct_info() == True:
                    new_user_id = Information.get_new_user_id()
                    Information.sign_up(self.username.text(), self.password.text(),
                                        int(self.month_income.text()), new_user_id)
                    self.close()
                    self.main_win = User(new_user_id)
                else:
                    title = self.correct_info()[0]
                    text = self.correct_info()[1]
                    msg = QMessageBox(QMessageBox.Warning, title,
                                      text, QMessageBox.Ok)
                    msg.setWindowIcon(QIcon(file_logo))
                    msg.setGeometry(650, 400, 100, 100)
                    msg.exec()
            except:
                title = 'ثبت نام کاربر جدید در برنامه'
                text = 'ناموفق در ثبت نام کاربر جدید در برنامه'
                msg = QMessageBox(QMessageBox.Information,
                                  title, text, QMessageBox.Ok)
                msg.setWindowIcon(QIcon(file_logo))
                msg.exec()

        def click_cancel():
            if self.user_id == 1000:
                exit()
            else:
                self.close()
                main = User(self.user_id)

        self.btn_register.clicked.connect(click_register)
        self.btn_cancel.clicked.connect(click_cancel)

        self.btn_logo = QPushButton(self)
        self.btn_logo.setIcon(QIcon(file_logo))
        self.grid_layout.addWidget(self.btn_logo, 5, 1, 2, 1, Qt.AlignCenter)
        self.btn_logo.setIconSize(QSize(100, 100))
        self.btn_logo.setStyleSheet(
            'background-color: rgba(0, 0, 0, 0); border: 0px')

    def correct_info(self):
        title_error = ''
        text_error = ''

        username = self.username.text()
        password = self.password.text()
        confrim_password = self.confirm_password.text()
        month_income = self.month_income.text()

        if username == '':
            title_error = 'نام کاربری نادرست'
            text_error = 'لطفا یک نام کاربری وارد نمایید'

        elif password == '':
            title_error = 'رمز عبور نادرست'
            text_error = 'لطفا یک رمز عبور وارد نمایید'

        elif confrim_password == '':
            title_error = 'تایید رمز عبور نادرست'
            text_error = 'لطفا رمز عبور خود را مجددا\n در تایید پسورد وارد نمایید'

        elif month_income == '':
            title_error = 'درآمد نادرست'
            text_error = 'لطفا درآمد ماهیانه ی خود\n را وارد نمایید'

        elif confrim_password != password:
            title_error = 'تایید رمز عبور نادرست'
            text_error = 'کلمه ی تایید رمز عبور نادرست است.\n لطفا مجددا امتحان کنید'

        elif not month_income.isdigit():
            title_error = 'درآمد نادرست'
            text_error = 'این درآمد ماهانه نامعتبر می باشد.\n لطفا مجددا امتحان کنید'

        elif Path(file_information).exists():
            if Information.sign_in(Information.make_secret_username(username), str(sha512(self.password.text().encode())))[0] == True:
                title_error = 'نام کاربری نادرست'
                text_error = 'این نام کاربری قبلا انتخاب شده است.\n لطفا عبارت دیگری انتخاب نمایید'

        if title_error != '' and text_error != '':
            return (title_error, text_error)
        else:
            return True


class Signin (QWidget):
    def __init__(self, user_id):
        super().__init__()

        self.user_id = user_id
        self.window()
        self.username_password()

    def window(self):
        self.setGeometry(600, 200, 400, 400)
        self.setFixedSize(400, 400)
        self.setStyleSheet('QWidget {background-color : #2b2b2b;}')
        self.setWindowIcon(QIcon(file_logo))
        self.setWindowTitle('ورود به برنامه')
        self.setLayoutDirection(Qt.RightToLeft)

        self.grid_layout = QGridLayout(self)

        self.btn_style = '''QPushButton {font-family: B Titr; font-size: 10pt; font-weight: Bold;
                        background-color : #2b2b2b; color : white; border: 2px solid #2ABFCD; border-radius : 10px;}
                        QPushButton::ToolTip {border : 1px solid black;}
                        QPushButton::Hover {background-color: darkgray; color: black}'''

        self.lb_style = '''font-family: B koodak; font-size: 16pt; font-weight: Bold;
                        color : white; background-color : rgba(0, 0, 0, 0);'''

        self.le_style = '''QLineEdit {font-family: B Koodak; font-size: 12pt; font-weight: Bold;
                        background-color : white; border : 2px solid #2ABFCD; border-radius : 10px}
                        QLineEdit::ToolTip {border : 1px solid black}
                        QLineEdit::Hover {border : 2px solid darkblue; background-color : #EAEAEA;}
                        QLineEdit:Focus {border : 2px solid darkblue; background-color : #EAEAEA;}'''

        self.lb_welcome = QLabel(self)
        self.grid_layout.addWidget(self.lb_welcome, 0, 0, 1, 2, Qt.AlignLeft)
        self.lb_welcome.setText('به اپلیکیشن "حساب کتاب" خوش آمدید!')
        self.lb_welcome.setAlignment(Qt.AlignRight)
        self.lb_welcome.setStyleSheet(
            'background-color: rgba(0, 0, 0, 0); color: #00c4c2; font-family: B Zar; font-size: 15pt; font-weight : bold')

    def username_password(self):
        self.hbox1 = QHBoxLayout(self)
        self.grid_layout.addLayout(self.hbox1, 1, 0, 1, 2, Qt.AlignCenter)

        self.lb_username = QLabel(self)
        self.hbox1.addWidget(self.lb_username, 1)
        self.lb_username.setText('نام کاربری:')
        self.lb_username.setAlignment(Qt.AlignRight)
        self.lb_username.setStyleSheet(self.lb_style)

        self.hbox1.addSpacing(30)

        self.username = QLineEdit(self)
        self.hbox1.addWidget(self.username, 2)
        self.username.setPlaceholderText(' نام کاربری خود را وارد نمایید')
        self.username.setStyleSheet(self.le_style)
        self.username.returnPressed.connect(lambda: self.password.setFocus())
        self.username.setToolTip('<b> نام کاربری <\b>')

        #########################################################################
        self.hbox2 = QHBoxLayout(self)
        self.grid_layout.addLayout(self.hbox2, 2, 0, 1, 2, Qt.AlignCenter)

        self.lb_password = QLabel(self)
        self.hbox2.addWidget(self.lb_password, 1)
        self.lb_password.setText('رمز عبور:')
        self.lb_password.setAlignment(Qt.AlignRight)
        self.lb_password.setStyleSheet(self.lb_style)

        self.hbox2.addSpacing(30)

        self.password = QLineEdit(self)
        self.hbox2.addWidget(self.password, 2)
        self.password.setPlaceholderText(' رمز عبور خود را وارد نمایید')
        self.password.setStyleSheet(self.le_style + 'QLineEdit {show: *}')
        self.password.returnPressed.connect(lambda: self.btn_register.click())
        self.password.setToolTip('<b> رمز عبور <\b>')
        self.password.setEchoMode(QLineEdit.Password)

        #########################################################################

        self.btn_register = QPushButton(self)
        self.grid_layout.addWidget(self.btn_register, 3, 0, Qt.AlignCenter)
        self.btn_register.setMinimumWidth(160)
        self.btn_register.setMinimumHeight(40)
        self.btn_register.setText('ورود به نرم افزار')
        self.btn_register.setStyleSheet(self.btn_style)
        self.btn_register.setToolTip('<b> ورود نرم افزار <\b>')
        self.btn_register.setCursor(Qt.PointingHandCursor)

        self.btn_cancel = QPushButton(self)
        self.grid_layout.addWidget(self.btn_cancel, 4, 0, Qt.AlignCenter)
        self.btn_cancel.setMinimumWidth(160)
        self.btn_cancel.setMinimumHeight(40)
        self.btn_cancel.setText('لغو و بستن پنجره')
        self.btn_cancel.setStyleSheet(self.btn_style)
        self.btn_cancel.setToolTip('<b> لغو و بستن پنجره <\b>')
        self.btn_cancel.setCursor(Qt.PointingHandCursor)

        self.btn_signup = QPushButton(self)
        self.grid_layout.addWidget(self.btn_signup, 5, 0, Qt.AlignCenter)
        self.btn_signup.setMinimumWidth(160)
        self.btn_signup.setMinimumHeight(40)
        self.btn_signup.setText('ثبت نام مجدد در برنامه')
        self.btn_signup.setStyleSheet(self.btn_style)
        self.btn_signup.setToolTip('<b> ثبت نام مجدد در برنامه <\b>')
        self.btn_signup.setCursor(Qt.PointingHandCursor)

        def click_register():
            try:
                correct_info = self.correct_info()
                if correct_info[0] == True:
                    self.close()
                    self.main_win = User(correct_info[1])
                else:
                    title = self.correct_info()[0]
                    text = self.correct_info()[1]
                    msg = QMessageBox(QMessageBox.Warning, title,
                                      text, QMessageBox.Ok)
                    msg.setWindowIcon(QIcon(file_logo))
                    msg.setGeometry(650, 400, 100, 100)
                    msg.exec()
            except:
                title = 'ثبت نام کاربر جدید در برنامه'
                text = 'ناموفق در ثبت نام کاربر جدید در برنامه'
                msg = QMessageBox(QMessageBox.Information,
                                  title, text, QMessageBox.Ok)
                msg.setWindowIcon(QIcon(file_logo))
                msg.exec()

        def click_cancel():
            if self.user_id == 1000:
                exit()
            else:
                self.close()
                main = User(self.user_id)

        self.btn_register.clicked.connect(click_register)
        self.btn_cancel.clicked.connect(click_cancel)
        self.btn_signup.clicked.connect(lambda: exec(
            f'signup_win = Signup({self.user_id})\nsignup_win.show()\nself.close()'))

        #########################################################################

        self.btn_logo = QPushButton(self)
        self.btn_logo.setIcon(QIcon(file_logo))
        self.grid_layout.addWidget(self.btn_logo, 3, 1, 3, 1, Qt.AlignCenter)
        self.btn_logo.setIconSize(QSize(120, 120))
        self.btn_logo.setStyleSheet(
            'background-color: rgba(0, 0, 0, 0); border: 0px')

    def correct_info(self):
        title_error = ''
        text_error = ''

        input_password = str(sha512(self.password.text().encode()).hexdigest())
        input_username = Information.make_secret_username(self.username.text())
        username, password, user_id = Information.sign_in(
            input_username, input_password)

        if username == None:
            title_error = 'نام کاربری نادرست'
            text_error = 'نام کاربری مورد نظر یافت نشد'
        elif password == None:
            title_error = 'رمز عبور نادرست'
            text_error = 'رمز عبور وارد شده صحیح نمی باشد'

        if title_error != '' and text_error != '':
            return (title_error, text_error)
        else:
            return (True, user_id)


class User:
    def __init__(self, user_id):

        global main_program_win
        main_program_win = QWidget()

        global main_program_layout
        main_program_layout = QGridLayout(main_program_win)

        self.user_id = user_id
        self.username = Information.load_information(self.user_id)[0]
        self.username = Information.convert_secret_to_username(self.username)

        self.window()
        self.make_tabs()
        main_program_win.show()

    def window(self):
        main_program_win.setFixedSize(1100, 840)
        main_program_win.setWindowIcon(QIcon(file_logo))
        main_program_win.setWindowTitle('حساب کتاب')
        main_program_win.setLayoutDirection(Qt.RightToLeft)

        self.lb_username = QLabel('کاربر فعلی: ' + self.username)
        self.lb_username.setFont(QFont('B Yekan', 14))
        self.lb_username.setAlignment(Qt.AlignLeft)
        self.lb_username.setStyleSheet(
            'background-color: white; border: 2px dashed %s; color: darkblue' % light_blue_color)
        self.lb_username.setMaximumSize(400, 40)
        main_program_layout.addWidget(self.lb_username, 0, 1, Qt.AlignLeft)

    def make_tabs(self):
        buttons_style = 'QToolButton {color : white; font-family : B Traffic; font-size : 13pt; font-weight : Bold}' + \
            'QToolButton::Hover {background-color : #8DDEE7; color : black}'

        self.toolbar = QToolBar(main_program_win)
        self.toolbar.setStyleSheet(
            'QToolBar {background-color : #333333; border : 2px solid %s; border-radius : 8px;}' % light_blue_color)
        self.toolbar.setOrientation(Qt.Vertical)
        self.toolbar.setMinimumHeight(580)
        self.toolbar.setMinimumWidth(235)
        main_program_layout.addWidget(self.toolbar, 0, 0, 2, 1, Qt.AlignLeft)

        self.start_win = QFrame(main_program_win)
        main_program_layout.addWidget(self.start_win, 1, 1, Qt.AlignLeft)
        self.grid_start_win = QGridLayout(self.start_win)
        self.start_win.setLayout(self.grid_start_win)

        self.lb_start = QLabel('یک منو را انتخاب نمایید')
        self.lb_start.setFont(QFont('B Koodak', 25))
        self.grid_start_win.addWidget(self.lb_start, 0, 0, Qt.AlignCenter)

        global selected_frame
        selected_frame = self.start_win

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

        ###########################################################################

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

        ###########################################################################

        self.bank_accounts_btn = QToolButton(self.toolbar)
        self.bank_accounts_btn.setStyleSheet(buttons_style)
        self.bank_accounts_btn.setText('    مدیریت حساب های بانکی')
        self.bank_accounts_btn.setMinimumSize(220, 40)
        self.bank_accounts_btn.clicked.connect(
            lambda: self.open_menus(self.Bank_Accounts))
        self.bank_accounts_btn.setCursor(Qt.PointingHandCursor)
        self.bank_accounts_btn.setIcon(QIcon(file_bank_account))
        self.bank_accounts_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.bank_accounts_btn.setLayoutDirection(Qt.RightToLeft)
        self.toolbar.addWidget(self.bank_accounts_btn)

        ###########################################################################

        self.analyze_btn = QToolButton(self.toolbar)
        self.analyze_btn.setStyleSheet(buttons_style)
        self.analyze_btn.setText('   آنالیز هزینه های ثبت شده')
        self.analyze_btn.setMinimumSize(220, 40)
        self.analyze_btn.clicked.connect(
            lambda: self.open_menus(self.Analyze))
        self.analyze_btn.setCursor(Qt.PointingHandCursor)
        self.analyze_btn.setIcon(QIcon(file_analyze))
        self.analyze_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.analyze_btn.setLayoutDirection(Qt.RightToLeft)
        self.toolbar.addWidget(self.analyze_btn)

        self.toolbar.addSeparator()
        ###########################################################################

        self.signup_again_btn = QToolButton(self.toolbar)
        self.signup_again_btn.setStyleSheet(buttons_style)
        self.signup_again_btn.setText(
            '               ثبت نام کاربر جدید')
        self.signup_again_btn.setMinimumSize(220, 40)
        self.signup_again_btn.clicked.connect(
            lambda: self.open_menus(self.UsersManager))
        self.signup_again_btn.setCursor(Qt.PointingHandCursor)
        self.signup_again_btn.setIcon(QIcon(file_new_user))
        self.signup_again_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.signup_again_btn.setLayoutDirection(Qt.RightToLeft)
        self.toolbar.addWidget(self.signup_again_btn)

        ###########################################################################

        self.signin_again_btn = QToolButton(self.toolbar)
        self.signin_again_btn.setStyleSheet(buttons_style)
        self.signin_again_btn.setText(
            '             ورود مجدد به برنامه')
        self.signin_again_btn.setMinimumSize(220, 40)
        self.signin_again_btn.clicked.connect(
            lambda: self.open_menus(self.UsersManager))
        self.signin_again_btn.setCursor(Qt.PointingHandCursor)
        self.signin_again_btn.setIcon(QIcon(file_signin_again))
        self.signin_again_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.signin_again_btn.setLayoutDirection(Qt.RightToLeft)
        self.toolbar.addWidget(self.signin_again_btn)

        ###########################################################################

        self.remove_user_btn = QToolButton(self.toolbar)
        self.remove_user_btn.setStyleSheet(buttons_style)
        self.remove_user_btn.setText(
            '     حذف کاربر فعلی از برنامه')
        self.remove_user_btn.setMinimumSize(220, 40)
        self.remove_user_btn.clicked.connect(
            lambda: self.open_menus(self.UsersManager))
        self.remove_user_btn.setCursor(Qt.PointingHandCursor)
        self.remove_user_btn.setIcon(QIcon(file_remove_user))
        self.remove_user_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.remove_user_btn.setLayoutDirection(Qt.RightToLeft)
        self.toolbar.addWidget(self.remove_user_btn)

        self.toolbar.addSeparator()
        ###########################################################################

        self.about_btn = QToolButton(self.toolbar)
        self.about_btn.setStyleSheet(buttons_style)
        self.about_btn.setText('                              درباره ی ما')
        self.about_btn.setMinimumSize(220, 40)
        self.about_btn.clicked.connect(lambda: self.open_menus(self.About))
        self.about_btn.setCursor(Qt.PointingHandCursor)
        self.about_btn.setIcon(QIcon(file_about))
        self.about_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.about_btn.setLayoutDirection(Qt.RightToLeft)
        self.toolbar.addWidget(self.about_btn)

    def open_menus(self, widget):
        selected_frame.hide()
        main_program_layout.removeWidget(selected_frame)

        if widget in [self.New, self.History, self.Bank_Accounts]:
            widget(self.user_id)
        elif widget == self.About:
            widget()
        elif widget == self.UsersManager:
            if main_program_win.sender() == self.signup_again_btn:
                widget('signup', self.user_id, self.username)
            elif main_program_win.sender() == self.signin_again_btn:
                widget('signin', self.user_id, self.username)
            else:
                widget('remove', self.user_id, self.username)
        else:
            widget(self.user_id)

    class New:
        def __init__(self, user_id):
            self.le_style = 'QLineEdit {border : 2px solid %s; border-radius: 5px;}' % light_blue_color + \
                'QLineEdit:Hover {border : 2px solid darkblue; background-color : #EAEAEA}' + \
                'QLineEdit:Focus {border : 2px solid darkblue; background-color : #EAEAEA;}'

            self.cb_style = 'QComboBox {border : 2px solid %s; border-radius: 5px;}' % light_blue_color + \
                'QComboBox:Hover {border : 2px solid darkblue; background-color : #EAEAEA;}' + \
                'QComboBox:Focus {border : 2px solid darkblue; background-color : #EAEAEA;}'

            self.user_id = user_id
            self.make_frames()
            self.make_date()
            self.make_combobox()
            self.make_entry()
            self.make_bank_account()
            self.make_desc()
            self.make_list_costs()
            self.make_toolbar()
            self.make_register()

        def make_frames(self):
            self.new_frame = QFrame(main_program_win)
            self.new_frame.setStyleSheet(
                'QFrame {background-color : white; border: 2px solid %s;}' % light_blue_color)
            self.new_frame.show()

            self.new_layout = QGridLayout(self.new_frame)
            self.new_frame.setLayout(self.new_layout)
            self.new_layout.setSpacing(30)
            self.new_layout.addItem(QSpacerItem(100, 600), 0, 0)

            self.new_vbox1 = QVBoxLayout(self.new_frame)
            self.new_layout.addLayout(self.new_vbox1, 0, 1, Qt.AlignRight)
            self.new_vbox1.setSpacing(10)

            self.new_vbox2 = QVBoxLayout(self.new_frame)
            self.new_layout.addLayout(self.new_vbox2, 0, 2, Qt.AlignRight)
            self.new_vbox2.setSpacing(25)

            #############################################################

            self.list_new_frame = QFrame(main_program_win)
            self.list_new_frame.setStyleSheet(
                'QFrame {background-color : white; border: 2px solid %s;}' % light_blue_color)
            self.list_new_frame.setMinimumSize(600, 500)

            self.list_new_layout = QGridLayout(self.list_new_frame)
            self.list_new_layout.setHorizontalSpacing(30)
            self.list_new_frame.setLayout(self.list_new_layout)

            #############################################################

            self.new_tabs = QTabWidget(main_program_win)
            self.new_tabs.setFont(QFont('B Yekan', 12))
            self.new_tabs.setStyleSheet('')
            self.new_tabs.setLayoutDirection(Qt.RightToLeft)
            self.new_tabs.addTab(self.new_frame, 'ثبت اطلاعات هزینه ی جدید')
            self.new_tabs.addTab(self.list_new_frame,
                                 'لیست هزینه های جدید و ثبت نهایی')

            main_program_layout.addWidget(self.new_tabs, 1, 1)
            global selected_frame
            selected_frame = self.new_tabs

        def make_date(self):
            lb_date = QLabel(main_program_win)
            self.new_vbox1.addWidget(lb_date)
            lb_date.setText('تاریخ هزینه')
            lb_date.setFont(QFont('B Titr', 12))
            lb_date.setAlignment(Qt.AlignRight)
            lb_date.setStyleSheet('border : 0px')

            now_date = str(datetime.now().date())
            now_date = GregorianToJalali(int(now_date.split(
                '-')[0]), int(now_date.split('-')[1]), int(now_date.split('-')[2])).getJalaliList()
            year = now_date[0]
            month = now_date[1]
            day = now_date[2]

            self.date = QDateEdit(main_program_win)
            self.date.setDateRange(QDate(1400, 1, 1), QDate(2050, 12, 30))
            self.date.setDisplayFormat('dd/MM/yyyy')
            self.date.setDate(QDate(year, month, day))
            self.date.setFont(QFont('B Koodak', 12))
            self.date.setAlignment(Qt.AlignCenter)
            self.date.setStyleSheet('QDateEdit {border : 2px solid %s; border-radius: 5px;}' % light_blue_color +
                                    'QDateEdit::Hover {border : 2px solid darkblue; background-color : #EAEAEA}' +
                                    'QDateEdit:Focus {border : 2px solid darkblue; background-color : #EAEAEA;}')
            self.new_vbox2.addWidget(self.date)

        def make_combobox(self):
            lb_kind = QLabel(main_program_win)
            self.new_vbox1.addWidget(lb_kind)
            lb_kind.setText('دسته ی هزینه')
            lb_kind.setFont(QFont('B Titr', 12))
            lb_kind.setAlignment(Qt.AlignRight)
            lb_kind.setStyleSheet('border : 0px')

            self.cb_kind = QComboBox(main_program_win)
            self.new_vbox2.addWidget(self.cb_kind)
            self.cb_kind.setFont(QFont('B Koodak', 12))
            self.cb_kind.addItems(Information.search_kinds())
            self.cb_kind.setCurrentIndex(0)
            self.cb_kind.setLayoutDirection(Qt.RightToLeft)
            self.cb_kind.setStyleSheet(self.cb_style)

            #####################################################
            lb_item = QLabel(main_program_win)
            self.new_vbox1.addWidget(lb_item)
            lb_item.setText('نوع هزینه')
            lb_item.setFont(QFont('B Titr', 12))
            lb_item.setAlignment(Qt.AlignRight)
            lb_item.setStyleSheet('border : 0px')

            self.cb_item = QComboBox(main_program_win)
            self.new_vbox2.addWidget(self.cb_item)
            self.cb_item.setFont(QFont('B Koodak', 12))
            self.cb_item.addItems(
                Information.search_items(self.cb_kind.currentText()))
            self.cb_item.setLayoutDirection(Qt.RightToLeft)
            self.cb_item.setStyleSheet(self.cb_style)

            def edit_items():
                kind = self.cb_kind.currentText()
                self.cb_item.clear()
                self.cb_item.addItems(Information.search_items(kind))
                self.cb_item.showPopup()

            self.cb_item.activated.connect(
                lambda: self.le_name.setFocus())
            self.cb_kind.activated.connect(edit_items)

        def make_entry(self):
            lb_name = QLabel(main_program_win)
            self.new_vbox1.addWidget(lb_name)
            lb_name.setText('عنوان هزینه')
            lb_name.setAlignment(Qt.AlignRight)
            lb_name.setFont(QFont('B Titr', 12))
            lb_name.setStyleSheet('border : 0px')

            self.le_name = QLineEdit(main_program_win)
            self.new_vbox2.addWidget(self.le_name)
            self.le_name.setFont(QFont('B Koodak', 12))
            self.le_name.setAlignment(Qt.AlignCenter)
            self.le_name.setStyleSheet(self.le_style)

            ##################################################
            lb_cost = QLabel(main_program_win)
            self.new_vbox1.addWidget(lb_cost)
            lb_cost.setText('مقدار هزینه')
            lb_cost.setAlignment(Qt.AlignRight)
            lb_cost.setFont(QFont('B Titr', 12))
            lb_cost.setStyleSheet('border : 0px')

            self.le_cost = QLineEdit(main_program_win)
            self.new_vbox2.addWidget(self.le_cost)
            self.le_cost.setFont(QFont('B Koodak', 12))
            self.le_cost.setAlignment(Qt.AlignCenter)
            self.le_cost.setStyleSheet(self.le_style)

            self.le_name.returnPressed.connect(
                lambda: self.le_cost.setFocus())
            self.le_cost.returnPressed.connect(
                lambda: self.cb_payment_type.showPopup())

        def make_bank_account(self):
            lb_payment_type = QLabel(main_program_win)
            self.new_vbox1.addWidget(lb_payment_type)
            lb_payment_type.setText('نوع پرداخت')
            lb_payment_type.setFont(QFont('B Titr', 12))
            lb_payment_type.setAlignment(Qt.AlignRight)
            lb_payment_type.setStyleSheet('border : 0px')

            def change_item(text):
                if text == 'صندوق':
                    self.cb_account_name.setEnabled(False)
                    self.le_bank_document_number.setEnabled(False)
                    self.cb_place_of_payment.setEnabled(False)
                    self.le_desc.setFocus()

                else:
                    self.cb_account_name.setEnabled(True)
                    self.le_bank_document_number.setEnabled(True)
                    self.cb_place_of_payment.setEnabled(True)
                    self.cb_account_name.showPopup()

            self.cb_payment_type = QComboBox(main_program_win)
            self.new_vbox2.addWidget(self.cb_payment_type)
            self.cb_payment_type.setFont(QFont('B Koodak', 12))
            self.cb_payment_type.addItems(['صندوق', 'حساب بانکی'])
            self.cb_payment_type.setCurrentIndex(1)
            self.cb_payment_type.activated[str].connect(change_item)
            self.cb_payment_type.setLayoutDirection(Qt.RightToLeft)
            self.cb_payment_type.setStyleSheet(self.cb_style)

            #############################################################
            lb_account_name = QLabel(main_program_win)
            self.new_vbox1.addWidget(lb_account_name)
            lb_account_name.setText('نام حساب')
            lb_account_name.setFont(QFont('B Titr', 12))
            lb_account_name.setAlignment(Qt.AlignRight)
            lb_account_name.setStyleSheet('border : 0px')

            self.cb_account_name = QComboBox(main_program_win)
            self.new_vbox2.addWidget(self.cb_account_name)
            self.cb_account_name.setFont(QFont('B Koodak', 12))

            accounts = Information.load_accounts(self.user_id)
            accounts_name = []
            for account in accounts:
                accounts_name.append(account[0])
            self.cb_account_name.addItems(accounts_name)

            self.cb_account_name.setLayoutDirection(Qt.RightToLeft)
            self.cb_account_name.setStyleSheet(self.cb_style)

            #############################################################
            lb_bank_document_number = QLabel(main_program_win)
            self.new_vbox1.addWidget(lb_bank_document_number)
            lb_bank_document_number.setText('شماره ی سند بانکی')
            lb_bank_document_number.setFont(QFont('B Titr', 12))
            lb_bank_document_number.setAlignment(Qt.AlignRight)
            lb_bank_document_number.setStyleSheet('border : 0px')

            self.le_bank_document_number = QLineEdit(main_program_win)
            self.new_vbox2.addWidget(self.le_bank_document_number)
            self.le_bank_document_number.setFont(QFont('B Koodak', 12))
            self.le_bank_document_number.setAlignment(Qt.AlignCenter)
            self.le_bank_document_number.setStyleSheet(self.le_style)
            self.le_bank_document_number.setPlaceholderText('اختیاری')

            #############################################################
            lb_place_of_payment = QLabel(main_program_win)
            self.new_vbox1.addWidget(lb_place_of_payment)
            lb_place_of_payment.setText('محل پرداخت')
            lb_place_of_payment.setFont(QFont('B Titr', 12))
            lb_place_of_payment.setAlignment(Qt.AlignRight)
            lb_place_of_payment.setStyleSheet('border : 0px')

            self.cb_place_of_payment = QComboBox(main_program_win)
            self.new_vbox2.addWidget(self.cb_place_of_payment)
            self.cb_place_of_payment.setFont(QFont('B Koodak', 12))
            self.cb_place_of_payment.addItems(
                ['دستگاه کارت خوان', 'عابر بانک', 'اینترنت', 'همراه بانک'])
            self.cb_place_of_payment.setLayoutDirection(Qt.RightToLeft)
            self.cb_place_of_payment.setStyleSheet(self.cb_style)

            ##########################################################
            self.cb_account_name.activated.connect(
                lambda: self.le_bank_document_number.setFocus())
            self.le_bank_document_number.returnPressed.connect(
                lambda: self.cb_place_of_payment.showPopup())

        def make_desc(self):
            lb_desc = QLabel(main_program_win)
            self.new_vbox1.addWidget(lb_desc)
            lb_desc.setText('توضیحات')
            lb_desc.setAlignment(Qt.AlignRight)
            lb_desc.setFont(QFont('B Titr', 12))
            lb_desc.setStyleSheet('border : 0px')

            self.le_desc = QLineEdit(main_program_win)
            self.new_vbox2.addWidget(self.le_desc)
            self.le_desc.setLayoutDirection(Qt.RightToLeft)
            self.le_desc.setFont(QFont('B Koodak', 12))
            self.le_desc.setStyleSheet(self.le_style)
            self.le_desc.setPlaceholderText('اختیاری')

            self.cb_place_of_payment.activated.connect(
                lambda: self.le_desc.setFocus())

        def make_register(self):
            def add_cost():
                if self.correct_info() == True:
                    lst_info_cost = [self.le_name.text(), self.cb_kind.currentText(),
                                     self.cb_item.currentText(), self.le_cost.text(),
                                     str(self.date.date().toString('yyyy/MM/dd')),
                                     self.cb_payment_type.currentText()]

                    if self.cb_payment_type.currentText() == 'صندوق':
                        lst_info_cost.extend(['', '', ''])
                    else:
                        lst_info_cost.append(
                            self.cb_account_name.currentText())
                        lst_info_cost.append(
                            self.le_bank_document_number.text())
                        lst_info_cost.append(
                            self.cb_place_of_payment.currentText())
                    lst_info_cost.append(self.le_desc.text())

                    Information.save_temporary_new_cost(
                        lst_info_cost, self.user_id)

                    #################################################
                    self.tb_new_costs.insertRow(0)
                    item1 = QTableWidgetItem(lst_info_cost[0])
                    item2 = QTableWidgetItem(lst_info_cost[1])
                    item3 = QTableWidgetItem(lst_info_cost[2])
                    item4 = QTableWidgetItem(lst_info_cost[3])
                    item5 = QTableWidgetItem(lst_info_cost[4])
                    item6 = QTableWidgetItem(lst_info_cost[5])
                    item7 = QTableWidgetItem(lst_info_cost[6])
                    item8 = QTableWidgetItem(lst_info_cost[7])
                    item9 = QTableWidgetItem(lst_info_cost[8])
                    item10 = QTableWidgetItem(lst_info_cost[9])

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
                    self.cb_item.clear()
                    self.cb_item.addItems(
                        Information.search_items(self.cb_kind.currentText()))

                    self.cb_payment_type.setCurrentIndex(1)
                    self.cb_account_name.setCurrentIndex(0)
                    self.cb_place_of_payment.setCurrentIndex(0)

                else:
                    title = self.correct_info()[0]
                    text = self.correct_info()[1]
                    msg = QMessageBox(QMessageBox.Warning, title,
                                      text, QMessageBox.Ok)
                    msg.setWindowIcon(QIcon(file_logo))
                    msg.setGeometry(650, 400, 100, 100)
                    msg.exec()

            self.save_btn = QPushButton(self.new_frame)
            self.save_btn.setText('افزودن هزینه به لیست هزینه های جدید  ')
            self.save_btn.setFont(QFont('B Koodak', 12))
            self.save_btn.setFixedSize(410, 50)
            self.save_btn.setIcon(QIcon(file_new2))
            self.save_btn.setIconSize(QSize(30, 30))
            self.save_btn.setStyleSheet(
                '''QPushButton {background-color: %s; border: 2px solid #16646C; border-radius : 5px}
                QPushButton:Hover {background-color: #599cff; color: white}''' % (light_blue_color))
            self.save_btn.setLayoutDirection(Qt.RightToLeft)
            self.save_btn.setCursor(Qt.PointingHandCursor)
            self.save_btn.clicked.connect(add_cost)
            self.new_layout.addWidget(
                self.save_btn, 1, 1, 1, 2, Qt.AlignCenter)

            self.new_layout.addItem(QSpacerItem(150, 600), 0, 3)

            self.le_desc.returnPressed.connect(
                lambda: self.save_btn.click())

        def make_toolbar(self):
            toolbar = QToolBar(main_program_win)
            toolbar.setStyleSheet(
                'QToolBar {border : 1.5px solid %s; border-radius : 5px}' % light_blue_color)
            self.list_new_layout.addWidget(toolbar, 0, 0, 1, 1, Qt.AlignCenter)
            toolbar.setMaximumSize(620, 70)

            tool_style = 'QToolButton:Hover {background-color : #abf8ff}'

            def delete_cost():
                button = main_program_win.sender()
                if button:
                    title = 'حذف هزینه از لیست هزینه های جدید'
                    text = 'آیا مایل به حذف هزینه ی انتخاب شده\nاز لیست هزینه های جدید ثبت نشده هستید؟'
                    msg = QMessageBox(QMessageBox.Warning, title,
                                      text, QMessageBox.Yes | QMessageBox.No)
                    msg.setWindowIcon(QIcon(file_logo))
                    msg.setGeometry(650, 400, 100, 100)
                    if msg.exec() == 16384:
                        try:
                            row = self.tb_new_costs.currentRow()
                            lst_cost = []

                            for column in range(10):
                                lst_cost.append(
                                    self.tb_new_costs.item(row, column).text())

                            self.tb_new_costs.removeRow(row)

                            Information.remove_temporary_cost(
                                lst_cost, self.user_id)
                        except:
                            title = 'حذف هزینه از لیست هزینه های جدید'
                            text = 'ناموفق در حذف هزینه از لیست هزینه های جدیدها'
                            msg = QMessageBox(QMessageBox.Information, title,
                                              text, QMessageBox.Ok)
                            msg.setWindowIcon(QIcon(file_logo))
                            msg.setGeometry(650, 400, 100, 100)

            def clear_costs():
                title = 'حذف همه ی هزینه ها از لیست هزینه های جدید'
                text = 'آیا مایل به حذف همه ی هزینه های موجود\nدر لیست هزینه های جدید ثبت نشده هستید؟'
                msg = QMessageBox(QMessageBox.Warning, title,
                                  text, QMessageBox.Yes | QMessageBox.No)
                msg.setWindowIcon(QIcon(file_logo))
                msg.setGeometry(650, 400, 100, 100)
                if msg.exec() == 16384:
                    try:
                        for i in range(self.tb_new_costs.rowCount()):
                            lst_cost = []

                            for column in range(10):
                                lst_cost.append(
                                    self.tb_new_costs.item(0, column).text())

                            Information.remove_temporary_cost(
                                lst_cost, self.user_id)
                            self.tb_new_costs.removeRow(0)
                    except:
                        title = 'حذف همه ی هزینه ها از لیست هزینه های جدید'
                        text = 'ناموفق در حذف همه ی هزینه ها از لیست هزینه های جدید'
                        msg = QMessageBox(QMessageBox.Information, title,
                                          text, QMessageBox.Ok)
                        msg.setWindowIcon(QIcon(file_logo))
                        msg.setGeometry(650, 400, 100, 100)

            def save_costs():
                title = 'ذخیره ی همه ی هزینه های لیست هزینه های جدید'
                text = 'آیا مایل به ذخیره ی همه ی هزینه های موجود\nدر لیست هزینه های جدید ثبت نشده هستید؟'
                msg = QMessageBox(QMessageBox.Warning, title,
                                  text, QMessageBox.Yes | QMessageBox.No)
                msg.setWindowIcon(QIcon(file_logo))
                msg.setGeometry(650, 400, 100, 100)
                if msg.exec() == 16384:
                    try:
                        new_costs = []
                        for i in range(self.tb_new_costs.rowCount()):
                            lst_cost = []
                            for column in range(10):
                                lst_cost.append(
                                    self.tb_new_costs.item(0, column).text())
                            self.tb_new_costs.removeRow(0)
                            new_costs.append(lst_cost)

                        Information.save_new_costs(new_costs, self.user_id)

                        connector = sqlite3.connect(
                            file_temporary_costs % self.user_id)
                        cursor = connector.cursor()
                        cursor.execute('DELETE FROM temporary_costs')
                        connector.commit()
                        connector.close()
                    except:
                        title = 'ذخیره ی همه ی هزینه های لیست هزینه های جدید'
                        text = 'ناموفق در ذخیره ی همه ی هزینه های لیست هزینه های جدید'
                        msg = QMessageBox(QMessageBox.Information, title,
                                          text, QMessageBox.Ok)
                        msg.setWindowIcon(QIcon(file_logo))
                        msg.setGeometry(650, 400, 100, 100)

            self.delete_btn = QToolButton(main_program_win)
            self.delete_btn.setText('حذف هزینه از لیست')
            self.delete_btn.setFont(QFont('B Koodak', 12))
            toolbar.addWidget(self.delete_btn)
            self.delete_btn.clicked.connect(delete_cost)
            self.delete_btn.setIcon(QIcon(file_delete))
            self.delete_btn.setIconSize(QSize(45, 45))
            self.delete_btn.setLayoutDirection(Qt.RightToLeft)
            self.delete_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            self.delete_btn.setCursor(Qt.PointingHandCursor)
            self.delete_btn.setEnabled(False)
            self.delete_btn.setStyleSheet(tool_style)

            toolbar.addSeparator()

            self.clear_btn = QToolButton(main_program_win)
            self.clear_btn.setText('پاک کردن همه ی هزینه های لیست')
            self.clear_btn.setFont(QFont('B Koodak', 12))
            toolbar.addWidget(self.clear_btn)
            self.clear_btn.clicked.connect(clear_costs)
            self.clear_btn.setIcon(QIcon(file_clear))
            self.clear_btn.setIconSize(QSize(45, 45))
            self.clear_btn.setLayoutDirection(Qt.RightToLeft)
            self.clear_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            self.clear_btn.setCursor(Qt.PointingHandCursor)
            self.clear_btn.setStyleSheet(tool_style)

            toolbar.addSeparator()

            self.add_btn = QToolButton(main_program_win)
            self.add_btn.setText('ذخیره ی هزینه های جدید')
            self.add_btn.setFont(QFont('B Koodak', 12))
            toolbar.addWidget(self.add_btn)
            self.add_btn.clicked.connect(save_costs)
            self.add_btn.setIcon(QIcon(file_save))
            self.add_btn.setIconSize(QSize(45, 45))
            self.add_btn.setLayoutDirection(Qt.RightToLeft)
            self.add_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            self.add_btn.setCursor(Qt.PointingHandCursor)
            self.add_btn.setStyleSheet(tool_style)

        def load_temporary_costs(self):
            temporary_costs = Information.load_temporary_costs(self.user_id)
            if temporary_costs != []:
                for cost in temporary_costs:
                    self.tb_new_costs.insertRow(self.tb_new_costs.rowCount())
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

                    self.tb_new_costs.setItem(
                        temporary_costs.index(cost), 0, item1)
                    self.tb_new_costs.setItem(
                        temporary_costs.index(cost), 1, item2)
                    self.tb_new_costs.setItem(
                        temporary_costs.index(cost), 2, item3)
                    self.tb_new_costs.setItem(
                        temporary_costs.index(cost), 3, item4)
                    self.tb_new_costs.setItem(
                        temporary_costs.index(cost), 4, item5)
                    self.tb_new_costs.setItem(
                        temporary_costs.index(cost), 5, item6)
                    self.tb_new_costs.setItem(
                        temporary_costs.index(cost), 6, item7)
                    self.tb_new_costs.setItem(
                        temporary_costs.index(cost), 7, item8)
                    self.tb_new_costs.setItem(
                        temporary_costs.index(cost), 8, item9)
                    self.tb_new_costs.setItem(
                        temporary_costs.index(cost), 9, item10)

        def make_list_costs(self):
            self.tb_new_costs = QTableWidget(0, 10, main_program_win)
            self.list_new_layout.addWidget(self.tb_new_costs, 1, 0)
            self.tb_new_costs.setStyleSheet(
                'border : 1.5px solid %s' % light_blue_color)
            self.tb_new_costs.horizontalHeader().setStyleSheet(
                'border : 0px solid white; border-right : 1px solid %s; border-bottom : 1px solid %s;' % (light_blue_color, light_blue_color))
            self.tb_new_costs.verticalHeader().setStyleSheet(
                'border : 0px solid white; border-left : 1px solid %s; border-top : 1px solid %s;' % (light_blue_color, light_blue_color))

            self.tb_new_costs.setFont(QFont('B Koodak', 12))
            self.tb_new_costs.setFixedSize(700, 570)
            self.tb_new_costs.horizontalHeader().setMinimumHeight(30)
            self.tb_new_costs.horizontalHeader().setFont(QFont('B Koodak', 12))
            self.tb_new_costs.verticalHeader().setMinimumWidth(20)
            self.tb_new_costs.setSelectionMode(QTableWidget.SingleSelection)
            self.tb_new_costs.itemClicked.connect(
                lambda: self.delete_btn.setEnabled(True))

            self.tb_new_costs.setColumnWidth(0, 100)
            self.tb_new_costs.setColumnWidth(1, 100)
            self.tb_new_costs.setColumnWidth(2, 100)
            self.tb_new_costs.setColumnWidth(3, 100)
            self.tb_new_costs.setColumnWidth(4, 100)
            self.tb_new_costs.setColumnWidth(5, 100)
            self.tb_new_costs.setColumnWidth(6, 120)
            self.tb_new_costs.setColumnWidth(7, 140)
            self.tb_new_costs.setColumnWidth(8, 100)
            self.tb_new_costs.setColumnWidth(9, 100)
            self.tb_new_costs.setHorizontalHeaderLabels(
                list(reversed(['توضیحات', 'محل پرداخت', 'شماره ی سند بانکی', 'نام حساب', 'نوع پرداخت', 'تاریخ هزینه', 'میزان هزینه', 'نوع هزینه', 'دسته هزینه', 'عنوان هزینه'])))

            self.load_temporary_costs()

        def correct_info(self):
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
                self.message = 'مقدار هزینه ی وارد شده معتبر نمی باشد. لطفا عددی معتبر وارد نمایید'

            elif self.cb_account_name.currentText() == '' and self.cb_account_name.count() == 0:
                self.title = 'نام حساب بانکی نادرست'
                self.message = 'برای ثبت هزینه ی جدید ابتدا به منوی "مدیریت حساب های بانکی"\n وارد شده و اطلاعات حساب های خود را وارد نمایید '

            if self.title != '':
                return (self.title, self.message)
            else:
                return True

    class History:
        def __init__(self, user_id):
            self.le_style = 'QLineEdit {border : 2px solid %s; border-radius: 5px;}' % light_blue_color + \
                'QLineEdit:Hover {border : 2px solid darkblue; background-color : #EAEAEA}' +\
                'QLineEdit:Focus {border : 2px solid darkblue; background-color : #EAEAEA;}'

            self.date_style = 'QDateEdit {border : 1.5px solid %s; border-radius: 5px;}' % light_blue_color + \
                'QDateEdit:Hover {border : 1.5px solid darkblue; background-color : #EAEAEA}' + \
                'QDateEdit:Focus {border : 2px solid darkblue; background-color : #EAEAEA;}'

            self.cb_style = 'QComboBox {border : 2px solid %s; border-radius: 5px;}' % light_blue_color + \
                'QComboBox:Hover {border : 2px solid darkblue; background-color : #EAEAEA;}' + \
                'QComboBox:Focus {border : 2px solid darkblue; background-color : #EAEAEA;}'

            self.user_id = user_id
            self.make_frame()
            self.date_filters()
            self.cost_filters()
            self.kind_item_filters()
            self.payment_type_account_place_filters()
            self.make_name_desc_filters()
            self.btn_filter()

            self.make_history()
            self.make_toolbar()

        def make_frame(self):
            self.filter_frame = QFrame(main_program_win)
            self.filter_frame.setStyleSheet(
                'QFrame {background-color : white; border: 2px solid %s;}' % light_blue_color)
            self.filter_frame.setLayoutDirection(Qt.RightToLeft)
            self.filter_frame.show()

            self.filter_layout = QGridLayout(self.filter_frame)
            self.filter_layout.setHorizontalSpacing(20)
            self.filter_layout.setVerticalSpacing(25)
            self.filter_frame.setLayout(self.filter_layout)

            self.filter_vbox1 = QVBoxLayout(self.filter_frame)
            self.filter_vbox1.setSpacing(20)
            self.filter_layout.addLayout(
                self.filter_vbox1, 1, 1, Qt.AlignRight)

            self.filter_vbox2 = QVBoxLayout(self.filter_frame)
            self.filter_vbox2.setSpacing(20)
            self.filter_layout.addLayout(self.filter_vbox2, 1, 2, Qt.AlignLeft)

            #############################################################

            self.history_frame = QFrame(main_program_win)
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

            self.history_tabs = QTabWidget(main_program_win)
            self.history_tabs.setFont(QFont('B Yekan', 12))
            self.history_tabs.setStyleSheet('')
            self.history_tabs.setLayoutDirection(Qt.RightToLeft)
            self.history_tabs.addTab(self.filter_frame, 'فیلتر ها')
            self.history_tabs.addTab(self.history_frame, 'تاریخچه ی هزینه ها')

            main_program_layout.addWidget(self.history_tabs, 1, 1)
            global selected_frame
            selected_frame = self.history_tabs

        def date_filters(self):
            now_date = str(datetime.now().date())
            now_date = GregorianToJalali(int(now_date.split(
                '-')[0]), int(now_date.split('-')[1]), int(now_date.split('-')[2])).getJalaliList()
            year = now_date[0]
            month = now_date[1]
            day = now_date[2]

            ###############################################

            lb_from_date = QLabel('از تاریخ', main_program_win)
            lb_from_date.setStyleSheet('border : 0px')
            lb_from_date.setFont(QFont('B Titr', 12))
            lb_from_date.setAlignment(Qt.AlignRight)
            self.filter_vbox1.addWidget(lb_from_date)

            self.from_date = QDateEdit(main_program_win)
            self.from_date.setDateRange(QDate(1400, 1, 1), QDate(2050, 12, 30))
            self.from_date.setDisplayFormat('dd/MM/yyyy')
            self.from_date.setDate(QDate(year, month, day))
            self.from_date.setFont(QFont('B Koodak', 12))
            self.from_date.setAlignment(Qt.AlignCenter)
            self.from_date.setStyleSheet(self.date_style)
            self.filter_vbox2.addWidget(self.from_date)

            ###############################################

            lb_to_date = QLabel('تا تاریخ', main_program_win)
            lb_to_date.setStyleSheet('border : 0px')
            lb_to_date.setFont(QFont('B Titr', 12))
            lb_to_date.setAlignment(Qt.AlignRight)
            self.filter_vbox1.addWidget(lb_to_date)

            self.to_date = QDateEdit(main_program_win)
            self.to_date.setDisplayFormat('dd/MM/yyyy')
            self.to_date.setDateRange(QDate(1400, 1, 1), QDate(2050, 12, 30))
            self.to_date.setDate(QDate(year, month, day))
            self.to_date.setFont(QFont('B Koodak', 12))
            self.to_date.setAlignment(Qt.AlignCenter)
            self.to_date.setStyleSheet(self.date_style)
            self.filter_vbox2.addWidget(self.to_date)

        def cost_filters(self):
            lb_from_cost = QLabel(main_program_win)
            lb_from_cost.setText('از مقدار هزینه')
            lb_from_cost.setAlignment(Qt.AlignRight)
            lb_from_cost.setFont(QFont('B Titr', 12))
            lb_from_cost.setStyleSheet('border : 0px')
            self.filter_vbox1.addWidget(lb_from_cost)

            self.from_cost = QLineEdit(main_program_win)
            self.from_cost.setFont(QFont('B Koodak', 12))
            self.from_cost.setAlignment(Qt.AlignCenter)
            self.from_cost.setStyleSheet(self.le_style)
            self.from_cost.setPlaceholderText('اختیاری')
            self.filter_vbox2.addWidget(self.from_cost)

            #################################################

            lb_to_cost = QLabel(main_program_win)
            lb_to_cost.setText('تا مقدار هزینه')
            lb_to_cost.setAlignment(Qt.AlignRight)
            lb_to_cost.setFont(QFont('B Titr', 12))
            lb_to_cost.setStyleSheet('border : 0px')
            self.filter_vbox1.addWidget(lb_to_cost)

            self.to_cost = QLineEdit(main_program_win)
            self.to_cost.setFont(QFont('B Koodak', 12))
            self.to_cost.setAlignment(Qt.AlignCenter)
            self.to_cost.setStyleSheet(self.le_style)
            self.to_cost.setPlaceholderText('اختیاری')
            self.filter_vbox2.addWidget(self.to_cost)

            self.from_cost.returnPressed.connect(
                lambda: self.to_cost.setFocus())

        def kind_item_filters(self):
            lb_kind = QLabel(main_program_win)
            lb_kind.setText('دسته ی هزینه')
            lb_kind.setFont(QFont('B Titr', 12))
            lb_kind.setAlignment(Qt.AlignRight)
            lb_kind.setStyleSheet('border : 0px')
            self.filter_vbox1.addWidget(lb_kind)

            self.from_kind = QComboBox(main_program_win)
            self.from_kind.setFont(QFont('B Koodak', 12))
            self.from_kind.addItems(Information.search_kinds())
            self.from_kind.addItem('همه ی دسته ها')
            self.from_kind.setCurrentIndex(self.from_kind.count()-1)
            self.from_kind.setLayoutDirection(Qt.RightToLeft)
            self.from_kind.setStyleSheet(self.cb_style)
            self.filter_vbox2.addWidget(self.from_kind)

            #####################################################

            lb_item = QLabel(main_program_win)
            lb_item.setText('نوع هزینه')
            lb_item.setFont(QFont('B Titr', 12))
            lb_item.setAlignment(Qt.AlignRight)
            lb_item.setStyleSheet('border : 0px')
            self.filter_vbox1.addWidget(lb_item)

            self.from_item = QComboBox(main_program_win)
            self.from_item.setFont(QFont('B Koodak', 12))
            self.from_item.addItems(
                Information.search_items(self.from_kind.currentText()))
            self.from_item.addItem('همه ی نوع ها')
            self.from_item.setLayoutDirection(Qt.RightToLeft)
            self.from_item.setStyleSheet(self.cb_style)
            self.filter_vbox2.addWidget(self.from_item)

            def edit_items():
                kind = self.from_kind.currentText()
                self.from_item.clear()
                self.from_item.addItems(Information.search_items(kind))
                self.from_item.addItem('همه ی نوع ها')
                self.from_item.showPopup()

            self.to_cost.returnPressed.connect(
                lambda: self.from_kind.showPopup())
            self.from_kind.activated.connect(edit_items)

        def payment_type_account_place_filters(self):
            lb_payment_type = QLabel(main_program_win)
            lb_payment_type.setText('نوع پرداخت')
            lb_payment_type.setFont(QFont('B Titr', 12))
            lb_payment_type.setAlignment(Qt.AlignRight)
            lb_payment_type.setStyleSheet('border : 0px')
            self.filter_vbox1.addWidget(lb_payment_type)

            def change_item(text):
                if text == 'صندوق':
                    self.from_account.setCurrentIndex(
                        self.from_account.count()-1)
                    self.from_place_of_payment.setCurrentIndex(
                        self.from_place_of_payment.count()-1)
                    self.from_account.setEnabled(False)
                    self.from_place_of_payment.setEnabled(False)
                    self.from_name_cost.setFocus()
                else:
                    self.from_account.setEnabled(True)
                    self.from_place_of_payment.setEnabled(True)
                    self.from_account.showPopup()

            self.from_payment_type = QComboBox(main_program_win)
            self.from_payment_type.setFont(QFont('B Koodak', 12))
            self.from_payment_type.addItems(
                ['صندوق', 'حساب بانکی', 'همه ی انواع پرداخت'])
            self.from_payment_type.setCurrentIndex(
                self.from_payment_type.count()-1)
            self.from_payment_type.activated[str].connect(change_item)
            self.from_payment_type.setLayoutDirection(Qt.RightToLeft)
            self.from_payment_type.setStyleSheet(self.cb_style)
            self.filter_vbox2.addWidget(self.from_payment_type)

            ##########################################################

            lb_from_account = QLabel(main_program_win)
            lb_from_account.setText('نام حساب')
            lb_from_account.setFont(QFont('B Titr', 12))
            lb_from_account.setAlignment(Qt.AlignRight)
            lb_from_account.setStyleSheet('border : 0px')
            self.filter_vbox1.addWidget(lb_from_account)

            self.from_account = QComboBox(main_program_win)
            self.from_account.setFont(QFont('B Koodak', 12))

            accounts = Information.load_accounts(self.user_id)
            accounts_name = []
            for account in accounts:
                accounts_name.append(account[0])

            self.from_account.addItems(accounts_name)
            self.from_account.addItem('همه ی حساب ها')
            self.from_account.setLayoutDirection(Qt.RightToLeft)
            self.from_account.setStyleSheet(self.cb_style)
            self.from_account.setCurrentIndex(self.from_account.count()-1)
            self.filter_vbox2.addWidget(self.from_account)

            ##########################################################

            lb_from_place_of_payment = QLabel(main_program_win)
            lb_from_place_of_payment.setText('محل پرداخت')
            lb_from_place_of_payment.setFont(QFont('B Titr', 12))
            lb_from_place_of_payment.setAlignment(Qt.AlignRight)
            lb_from_place_of_payment.setStyleSheet('border : 0px')
            self.filter_vbox1.addWidget(lb_from_place_of_payment)

            self.from_place_of_payment = QComboBox(main_program_win)
            self.from_place_of_payment.setFont(QFont('B Koodak', 12))
            self.from_place_of_payment.addItems(
                ['دستگاه کارت خوان', 'عابر بانک', 'اینترنت', 'همراه بانک', 'همه ی مکان های پرداخت'])
            self.from_place_of_payment.setLayoutDirection(Qt.RightToLeft)
            self.from_place_of_payment.setStyleSheet(self.cb_style)
            self.from_place_of_payment.setCurrentIndex(
                self.from_place_of_payment.count() - 1)
            self.filter_vbox2.addWidget(self.from_place_of_payment)

            ###########################################
            self.from_item.activated.connect(
                lambda: self.from_payment_type.showPopup())
            self.from_account.activated.connect(
                lambda: self.from_place_of_payment.showPopup())

        def make_name_desc_filters(self):
            lb_from_name_cost = QLabel(main_program_win)
            lb_from_name_cost.setText('عنوان هزینه')
            lb_from_name_cost.setAlignment(Qt.AlignRight)
            lb_from_name_cost.setFont(QFont('B Titr', 12))
            lb_from_name_cost.setStyleSheet('border : 0px')
            self.filter_vbox1.addWidget(lb_from_name_cost)

            self.from_name_cost = QLineEdit(main_program_win)
            self.from_name_cost.setFont(QFont('B Koodak', 12))
            self.from_name_cost.setAlignment(Qt.AlignCenter)
            self.from_name_cost.setStyleSheet(self.le_style)
            self.from_name_cost.setPlaceholderText('اختیاری')
            self.filter_vbox2.addWidget(self.from_name_cost)

            ##################################################

            lb_from_desc_cost = QLabel(main_program_win)
            lb_from_desc_cost.setText('توضیحات هزینه')
            lb_from_desc_cost.setAlignment(Qt.AlignRight)
            lb_from_desc_cost.setFont(QFont('B Titr', 12))
            lb_from_desc_cost.setStyleSheet('border : 0px')
            self.filter_vbox1.addWidget(lb_from_desc_cost)

            self.from_desc_cost = QLineEdit(main_program_win)
            self.from_desc_cost.setFont(QFont('B Koodak', 12))
            self.from_desc_cost.setAlignment(Qt.AlignCenter)
            self.from_desc_cost.setStyleSheet(self.le_style)
            self.from_desc_cost.setPlaceholderText('اختیاری')
            self.filter_vbox2.addWidget(self.from_desc_cost)

            self.from_place_of_payment.activated.connect(
                lambda: self.from_name_cost.setFocus())
            self.from_name_cost.returnPressed.connect(
                lambda: self.from_desc_cost.setFocus())

        def btn_filter(self):
            lb_filter = QLabel(main_program_win)
            self.filter_layout.addWidget(lb_filter, 0, 1, 1, 2)
            lb_filter.setText('فیلتر های جست و جو در تاریخچه ی هزینه ها')
            lb_filter.setStyleSheet('border: 0px; color : darkblue')
            lb_filter.setFont(QFont('B Titr', 15))

            self.filter_layout.addItem(QSpacerItem(150, 600), 1, 0)

            #############################################################

            self.filter_btn = QPushButton(main_program_win)
            self.filter_btn.setText('اعمال فیلتر های جست و جو  ')
            self.filter_btn.setFont(QFont('B Koodak', 13))
            self.filter_btn.setStyleSheet(
                '''QPushButton {background-color: %s; border: 2px solid #16646C; border-radius : 5px}
                QPushButton:Hover {background-color: #599cff; color: white}''' % (light_blue_color))
            self.filter_btn.setIcon(QIcon(file_filter))
            self.filter_btn.setIconSize(QSize(25, 25))
            self.filter_btn.setLayoutDirection(Qt.RightToLeft)
            self.filter_btn.setCursor(Qt.PointingHandCursor)
            self.filter_btn.clicked.connect(lambda: self.load_history([self.from_date.date(), self.to_date.date(),
                                                                       self.from_kind.currentText(), self.from_item.currentText(),
                                                                       self.from_cost.text(), self.to_cost.text(),
                                                                       self.from_payment_type.currentText(), self.from_account.currentText(),
                                                                       self.from_place_of_payment.currentText(), self.from_name_cost.text(),
                                                                       self.from_desc_cost.text()]))

            self.filter_btn.setMinimumSize(300, 40)
            self.filter_layout.addWidget(
                self.filter_btn, 2, 1, 1, 2, Qt.AlignCenter)

            self.filter_layout.addItem(QSpacerItem(150, 600), 1, 3)

            self.from_desc_cost.returnPressed.connect(
                lambda: self.filter_btn.click())

        def make_history(self):
            self.tb_history = QTableWidget(0, 11, main_program_win)
            self.history_layout.addWidget(self.tb_history, 1, 0)
            self.tb_history.setStyleSheet(
                'border : 1.5px solid %s' % light_blue_color)
            self.tb_history.horizontalHeader().setStyleSheet(
                'border : 0px solid white; border-right : 1px solid %s; border-bottom : 1px solid %s;' % (light_blue_color, light_blue_color))
            self.tb_history.verticalHeader().setStyleSheet(
                'border : 0px solid white; border-left : 1px solid %s; border-top : 1px solid %s;' % (light_blue_color, light_blue_color))

            self.tb_history.setFont(QFont('B Koodak', 12))
            self.tb_history.setFixedSize(700, 570)
            self.tb_history.horizontalHeader().setMinimumHeight(30)
            self.tb_history.horizontalHeader().setFont(QFont('B Koodak', 12))
            self.tb_history.verticalHeader().setMinimumWidth(20)
            self.tb_history.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.tb_history.setSelectionMode(
                QAbstractItemView.SingleSelection)
            self.tb_history.itemClicked.connect(
                lambda: self.delete2_btn.setEnabled(True))

            self.tb_history.setColumnWidth(0, 100)
            self.tb_history.setColumnWidth(1, 100)
            self.tb_history.setColumnWidth(2, 100)
            self.tb_history.setColumnWidth(3, 100)
            self.tb_history.setColumnWidth(4, 100)
            self.tb_history.setColumnWidth(5, 100)
            self.tb_history.setColumnWidth(6, 120)
            self.tb_history.setColumnWidth(7, 120)
            self.tb_history.setColumnWidth(8, 140)
            self.tb_history.setColumnWidth(9, 100)
            self.tb_history.setColumnWidth(10, 100)
            self.tb_history.setHorizontalHeaderLabels(
                list(reversed(['توضیحات', 'محل پرداخت', 'شماره ی سند بانکی', 'نام حساب', 'نوع پرداخت', 'تاریخ هزینه', 'میزان هزینه', 'نوع هزینه', 'دسته هزینه', 'عنوان هزینه', 'شماره ی سند'])))

            try:
                self.load_history(self.previous_filter_history)
            except:
                pass

        def load_history(self, lst_filter_history):
            if self.correct_filters() == True:
                if Path(file_costs % self.user_id).exists():
                    self.history_tabs.setCurrentIndex(1)

                    for i in range(0, int(self.tb_history.rowCount())):
                        self.tb_history.removeRow(0)

                    self.previous_filter_history = lst_filter_history

                    self.costs = Information.load_history(
                        self.user_id, *lst_filter_history)

                    self.tb_history.setSortingEnabled(False)

                    for cost in self.costs:
                        self.tb_history.insertRow(0)

                        item1 = QTableWidgetItem()
                        item1.setData(Qt.DisplayRole, cost[10])
                        item2 = QTableWidgetItem(cost[0])
                        item3 = QTableWidgetItem(cost[1])
                        item4 = QTableWidgetItem(cost[2])
                        item5 = QTableWidgetItem()
                        item5.setData(Qt.DisplayRole, cost[3])
                        item6 = QTableWidgetItem(cost[4])
                        item6.setData(Qt.DisplayRole, cost[4])
                        item7 = QTableWidgetItem(cost[5])
                        item8 = QTableWidgetItem(cost[6])
                        item9 = QTableWidgetItem()
                        item9.setData(Qt.DisplayRole, cost[7])
                        item10 = QTableWidgetItem(cost[8])
                        item11 = QTableWidgetItem(cost[9],)

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

                        self.tb_history.setItem(0, 0, item1)
                        self.tb_history.setItem(0, 1, item2)
                        self.tb_history.setItem(0, 2, item3)
                        self.tb_history.setItem(0, 3, item4)
                        self.tb_history.setItem(0, 4, item5)
                        self.tb_history.setItem(0, 5, item6)
                        self.tb_history.setItem(0, 6, item7)
                        self.tb_history.setItem(0, 7, item8)
                        self.tb_history.setItem(0, 8, item9)
                        self.tb_history.setItem(0, 9, item10)
                        self.tb_history.setItem(0, 10, item11)

                    ##########################################################################
                    # Sorting

                    self.tb_history.setSortingEnabled(True)

            else:
                title = self.correct_filters()[0]
                text = self.correct_filters()[1]
                msg = QMessageBox(QMessageBox.Warning, title,
                                  text, QMessageBox.Ok)
                msg.setWindowIcon(QIcon(file_logo))
                msg.setGeometry(650, 400, 100, 100)
                msg.exec()

        def make_toolbar(self):
            toolbar = QToolBar(main_program_win)
            toolbar.setStyleSheet(
                'QToolBar {border : 1.5px solid %s; border-radius : 5px}' % light_blue_color)
            self.history_layout.addWidget(toolbar, 0, 0, Qt.AlignCenter)
            toolbar.setFixedSize(595, 70)

            tool_style = 'QToolButton:Hover {background-color : #abf8ff}'

            def delete_cost():
                button = main_program_win.sender()
                if button:
                    title = 'حذف هزینه از تاریخچه ی هزینه ها'
                    text = 'آیا مایل به حذف هزینه ی انتخاب شده\nاز تاریخچه ی هزینه های ثبت شده هستید؟'
                    msg = QMessageBox(QMessageBox.Warning, title,
                                      text, QMessageBox.Yes | QMessageBox.No)
                    msg.setWindowIcon(QIcon(file_logo))
                    msg.setGeometry(650, 400, 100, 100)
                    if msg.exec() == 16384:
                        try:
                            row = self.tb_history.currentRow()
                            id = self.tb_history.item(row, 0)
                            Information.remove_cost(id.text(), self.user_id)
                            self.tb_history.removeRow(row)
                            self.load_history(self.previous_filter_history)
                        except:
                            title = 'حذف هزینه از تاریخچه ی هزینه ها'
                            text = 'ناموفق در حذف هزینه از تاریخچه ی هزینه ها'
                            msg = QMessageBox(QMessageBox.Information, title,
                                              text, QMessageBox.Ok)
                            msg.setWindowIcon(QIcon(file_logo))
                            msg.setGeometry(650, 400, 100, 100)
                            msg.exec()

            def clear_costs():
                title = 'حذف همه ی هزینه های جدول تاریخچه ی فعلی'
                text = 'آیا مایل به حذف همه ی هزینه های موجود\nدر جدول فعلی زیر از تاریخچه هستید؟'
                msg = QMessageBox(QMessageBox.Warning, title,
                                  text, QMessageBox.Yes | QMessageBox.No)
                msg.setWindowIcon(QIcon(file_logo))
                msg.setGeometry(650, 400, 100, 100)
                if msg.exec() == 16384:
                    try:
                        for i in range(self.tb_history.rowCount()):
                            id = self.tb_history.item(0, 0)
                            Information.remove_cost(id.text(), self.user_id)
                            self.tb_history.removeRow(0)
                    except:
                        title = 'حذف همه ی هزینه های جدول تاریخچه ی فعلی'
                        text = 'ناموفق در حذف همه ی هزینه های جدول تاریخچه ی فعلی'
                        msg = QMessageBox(QMessageBox.Information, title,
                                          text, QMessageBox.Ok)
                        msg.setWindowIcon(QIcon(file_logo))
                        msg.setGeometry(650, 400, 100, 100)

            self.delete2_btn = QToolButton(main_program_win)
            self.delete2_btn.setText('حذف هزینه انتخاب شده از تاریخچه')
            self.delete2_btn.setFont(QFont('B Koodak', 12))
            toolbar.addWidget(self.delete2_btn)
            self.delete2_btn.setIcon(QIcon(file_delete))
            self.delete2_btn.setLayoutDirection(Qt.RightToLeft)
            self.delete2_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            self.delete2_btn.setCursor(Qt.PointingHandCursor)
            self.delete2_btn.setEnabled(False)
            self.delete2_btn.clicked.connect(delete_cost)
            self.delete2_btn.setStyleSheet(tool_style)

            toolbar.addSeparator()

            self.clear2_btn = QToolButton(main_program_win)
            self.clear2_btn.setText('پاک کردن همه ی هزینه های جدول از تاریخچه')
            self.clear2_btn.setFont(QFont('B Koodak', 12))
            toolbar.addWidget(self.clear2_btn)
            self.clear2_btn.setIcon(QIcon(file_clear))
            self.clear2_btn.setLayoutDirection(Qt.RightToLeft)
            self.clear2_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            self.clear2_btn.setCursor(Qt.PointingHandCursor)
            self.clear2_btn.clicked.connect(clear_costs)
            self.clear2_btn.setStyleSheet(tool_style)

        def correct_filters(self):
            self.title = ''
            self.message = ''

            if self.from_cost.text() != '' and not self.from_cost.text().isdigit():
                self.title = 'حداقل هزینه ی نادرست'
                self.message = 'حداقل مقدار هزینه ی وارد شده معتبر نمی باشد. لطفا عددی معتبر وارد نمایید'

            elif self.to_cost.text() != '' and not self.to_cost.text().isdigit():
                self.title = 'حداکثر هزینه ی نادرست'
                self.message = 'حداکثر مقدار هزینه ی وارد شده معتبر نمی باشد. لطفا عددی معتبر وارد نمایید'

            if self.title != '':
                return (self.title, self.message)
            else:
                return True

    class Bank_Accounts:
        def __init__(self, user_id):
            self.le_style = 'QLineEdit {border : 2px solid %s; border-radius: 5px;}' % light_blue_color + \
                'QLineEdit::Hover {border : 2px solid darkblue; background-color : #EAEAEA}' + \
                'QLineEdit:Focus {border : 2px solid darkblue; background-color : #EAEAEA;}'

            self.cb_style = 'QComboBox {border : 2px solid %s; border-radius: 5px;}' % light_blue_color + \
                'QComboBox::Hover {border : 2px solid darkblue; background-color : #EAEAEA;}' + \
                'QComboBox:Focus {border : 2px solid darkblue; background-color : #EAEAEA;}'

            self.user_id = user_id
            self.make_frame()
            self.make_name_bank_accountnumber()
            self.make_owner_name_account_type()
            self.make_telephone_address_desc()
            self.make_toolbar()
            self.make_tb_accounts()

        def make_frame(self):
            self.accounts_frame = QFrame(main_program_win)
            self.accounts_frame.setStyleSheet(
                'QFrame {background-color : white; border: 2px solid %s;}' % light_blue_color)
            self.accounts_frame.setLayoutDirection(Qt.RightToLeft)
            self.accounts_frame.show()

            self.accounts_layout = QGridLayout(self.accounts_frame)
            self.accounts_layout.setSpacing(25)
            self.accounts_frame.setLayout(self.accounts_layout)

            main_program_layout.addWidget(self.accounts_frame, 1, 1)
            global selected_frame
            selected_frame = self.accounts_frame

            lb_accounts = QLabel(main_program_win)
            lb_accounts.setText('ایجاد حساب بانکی جدید')
            lb_accounts.setAlignment(Qt.AlignRight)
            lb_accounts.setFont(QFont('B Titr', 13))
            lb_accounts.setStyleSheet('border : 0px; color: darkblue')
            self.accounts_layout.addWidget(
                lb_accounts, 0, 1, 1, 2, Qt.AlignCenter)

        def make_name_bank_accountnumber(self):
            lb_name = QLabel(main_program_win)
            lb_name.setText('نام نمایشی حساب بانکی')
            lb_name.setAlignment(Qt.AlignRight)
            lb_name.setFont(QFont('B Titr', 12))
            lb_name.setStyleSheet('border : 0px')
            self.accounts_layout.addWidget(lb_name, 1, 0, Qt.AlignRight)

            self.name = QLineEdit(main_program_win)
            self.name.setFont(QFont('B Koodak', 11))
            self.name.setAlignment(Qt.AlignCenter)
            self.name.setStyleSheet(self.le_style)
            self.accounts_layout.addWidget(self.name, 1, 1, Qt.AlignLeft)

            ######################################################

            lb_bank_name = QLabel(main_program_win)
            lb_bank_name.setText('نام بانک')
            lb_bank_name.setAlignment(Qt.AlignRight)
            lb_bank_name.setFont(QFont('B Titr', 12))
            lb_bank_name.setStyleSheet('border : 0px')
            self.accounts_layout.addWidget(lb_bank_name, 2, 0, Qt.AlignRight)

            self.cb_banks = QComboBox(main_program_win)
            self.cb_banks.setFont(QFont('B Koodak', 12))
            self.cb_banks.addItems(['پارسیان', 'ملت', 'شهر', 'تجارت',
                                   'ملی', 'سینا', 'صادرات', 'کشاورزی', 'مسکن', 'رفاه کارگران'])
            self.cb_banks.setCurrentIndex(0)
            self.cb_banks.setEditable(False)
            self.cb_banks.setLayoutDirection(Qt.RightToLeft)
            self.cb_banks.setStyleSheet(self.cb_style)
            self.accounts_layout.addWidget(self.cb_banks, 2, 1, Qt.AlignLeft)

            ######################################################

            lb_account_number = QLabel(main_program_win)
            lb_account_number.setText('شماره ی حساب')
            lb_account_number.setAlignment(Qt.AlignRight)
            lb_account_number.setFont(QFont('B Titr', 12))
            lb_account_number.setStyleSheet('border : 0px')
            self.accounts_layout.addWidget(
                lb_account_number, 2, 2, Qt.AlignRight)

            self.account_number = QLineEdit(main_program_win)
            self.account_number.setFont(QFont('B Koodak', 12))
            self.account_number.setAlignment(Qt.AlignCenter)
            self.account_number.setStyleSheet(self.le_style)
            self.account_number.setMinimumWidth(170)
            self.account_number.setMaxLength(16)
            self.accounts_layout.addWidget(
                self.account_number, 2, 3, Qt.AlignLeft)

            #############################################
            self.name.returnPressed.connect(lambda: self.cb_banks.showPopup())
            self.cb_banks.activated.connect(
                lambda: self.account_number.setFocus())

        def make_owner_name_account_type(self):
            lb_owner_name = QLabel(main_program_win)
            lb_owner_name.setText('نام صاحب حساب')
            lb_owner_name.setAlignment(Qt.AlignRight)
            lb_owner_name.setFont(QFont('B Titr', 12))
            lb_owner_name.setStyleSheet('border : 0px')
            self.accounts_layout.addWidget(lb_owner_name, 3, 0, Qt.AlignRight)

            self.owner_name = QLineEdit(main_program_win)
            self.owner_name.setFont(QFont('B Koodak', 12))
            self.owner_name.setAlignment(Qt.AlignCenter)
            self.owner_name.setStyleSheet(self.le_style)
            self.accounts_layout.addWidget(self.owner_name, 3, 1, Qt.AlignLeft)

            #########################################################

            lb_account_type = QLabel(main_program_win)
            lb_account_type.setText('نوع حساب')
            lb_account_type.setAlignment(Qt.AlignRight)
            lb_account_type.setFont(QFont('B Titr', 12))
            lb_account_type.setStyleSheet('border : 0px')
            self.accounts_layout.addWidget(
                lb_account_type, 3, 2, Qt.AlignRight)

            self.account_type = QComboBox(main_program_win)
            self.account_type.setFont(QFont('B Koodak', 12))
            self.account_type.addItems(
                ['جاری', 'قرض الحسنه', 'سپرده ی کوتاه مدت', 'سپرده ی بلند مدت'])
            self.account_type.setCurrentIndex(0)
            self.account_type.setLayoutDirection(Qt.RightToLeft)
            self.account_type.setStyleSheet(self.cb_style)
            self.accounts_layout.addWidget(
                self.account_type, 3, 3, Qt.AlignLeft)

            self.account_number.returnPressed.connect(
                lambda: self.owner_name.setFocus())
            self.owner_name.returnPressed.connect(
                lambda: self.account_type.showPopup())

        def make_telephone_address_desc(self):
            lb_telephone = QLabel(main_program_win)
            lb_telephone.setText('تلفن بانک')
            lb_telephone.setAlignment(Qt.AlignRight)
            lb_telephone.setFont(QFont('B Titr', 12))
            lb_telephone.setStyleSheet('border : 0px')
            self.accounts_layout.addWidget(lb_telephone, 4, 0, Qt.AlignRight)

            self.telephone = QLineEdit(main_program_win)
            self.telephone.setFont(QFont('B Koodak', 12))
            self.telephone.setAlignment(Qt.AlignCenter)
            self.telephone.setStyleSheet(self.le_style)
            self.telephone.setMaxLength(11)
            self.telephone.setPlaceholderText('اختیاری')
            self.accounts_layout.addWidget(self.telephone, 4, 1, Qt.AlignLeft)

            ##########################################################

            lb_address = QLabel(main_program_win)
            lb_address.setText('آدرس بانک')
            lb_address.setAlignment(Qt.AlignRight)
            lb_address.setFont(QFont('B Titr', 12))
            lb_address.setStyleSheet('border : 0px')
            self.accounts_layout.addWidget(lb_address, 4, 2, Qt.AlignRight)

            self.address = QLineEdit(main_program_win)
            self.address.setFont(QFont('B Koodak', 12))
            self.address.setAlignment(Qt.AlignCenter)
            self.address.setStyleSheet(self.le_style)
            self.address.setPlaceholderText('اختیاری')
            self.accounts_layout.addWidget(self.address, 4, 3, Qt.AlignLeft)

            ##########################################################

            lb_desc = QLabel(main_program_win)
            lb_desc.setText('توضیحات')
            lb_desc.setAlignment(Qt.AlignRight)
            lb_desc.setFont(QFont('B Titr', 12))
            lb_desc.setStyleSheet('border : 0px')
            self.accounts_layout.addWidget(lb_desc, 5, 0, Qt.AlignRight)

            self.desc = QLineEdit(main_program_win)
            self.desc.setFont(QFont('B Koodak', 12))
            self.desc.setAlignment(Qt.AlignCenter)
            self.desc.setStyleSheet(self.le_style)
            self.desc.setMinimumWidth(370)
            self.desc.setPlaceholderText('اختیاری')
            self.accounts_layout.addWidget(self.desc, 5, 1, 1, 3, Qt.AlignLeft)

            ##########################################
            self.account_type.activated.connect(
                lambda: self.telephone.setFocus())
            self.telephone.returnPressed.connect(
                lambda: self.address.setFocus())
            self.address.returnPressed.connect(lambda: self.desc.setFocus())

        def make_toolbar(self):
            toolbar = QToolBar(main_program_win)
            toolbar.setStyleSheet(
                'QToolBar {border : 1.5px solid %s; border-radius : 5px}' % light_blue_color)
            self.accounts_layout.addWidget(toolbar, 6, 1, 1, 2, Qt.AlignCenter)
            toolbar.setFixedSize(310, 65)

            tool_style = 'QToolButton:hover {background-color: #abf8ff;}'

            def delete_account():
                button = main_program_win.sender()
                if button:
                    title = 'حذف حساب بانکی انتخاب شده'
                    text = 'آیا مایل به حذف حساب بانکی انتخاب شده\nاز لیست حساب های ثبت شده هستید؟'
                    msg = QMessageBox(QMessageBox.Warning, title,
                                      text, QMessageBox.Yes | QMessageBox.No)
                    msg.setWindowIcon(QIcon(file_logo))
                    msg.setGeometry(650, 400, 100, 100)
                    if msg.exec() == 16384:
                        try:
                            row = self.tb_accounts.currentRow()
                            self.tb_accounts.removeRow(row)
                            account_number = self.accounts[len(
                                self.accounts)-row-1][2]
                            Information.remove_account(
                                account_number, self.user_id)
                        except:
                            title = 'حذف حساب بانکی انتخاب شده'
                            text = 'ناموفق در حذف حساب بانکی انتخاب شده'
                            msg = QMessageBox(QMessageBox.Information, title,
                                              text, QMessageBox.Ok)
                            msg.setWindowIcon(QIcon(file_logo))
                            msg.setGeometry(650, 400, 100, 100)

            def add_account():
                title = 'افزودن حساب بانکی'
                text = 'آیا مایل به افزودن حساب بانکی\nبه لیست حساب های ثبت شده هستید؟'
                msg = QMessageBox(QMessageBox.Warning, title,
                                  text, QMessageBox.Yes | QMessageBox.No)
                msg.setWindowIcon(QIcon(file_logo))
                msg.setGeometry(650, 400, 100, 100)
                if msg.exec() == 16384:
                    if self.correct_info() == True:
                        try:
                            Information.add_account(self.user_id, self.name.text(), self.cb_banks.currentText(),
                                                    self.account_number.text(), self.owner_name.text(),
                                                    self.account_type.currentText(), self.telephone.text(),
                                                    self.address.text(), self.desc.text())

                            self.tb_accounts.insertRow(0)
                            item1 = QTableWidgetItem(self.name.text())
                            item2 = QTableWidgetItem(
                                self.cb_banks.currentText())
                            item3 = QTableWidgetItem(
                                self.account_number.text())
                            item4 = QTableWidgetItem(self.owner_name.text())
                            item5 = QTableWidgetItem(
                                self.account_type.currentText())
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
                        except:
                            title = 'افزودن حساب بانکی'
                            text = 'ناموفق در افزودن حساب بانکی\nبه لیست حساب های ثبت شده در برنامه'
                            msg = QMessageBox(QMessageBox.Information, title,
                                              text, QMessageBox.Ok)
                            msg.setWindowIcon(QIcon(file_logo))
                            msg.setGeometry(650, 400, 100, 100)

                    else:
                        title = self.correct_info()[0]
                        text = self.correct_info()[1]
                        msg = QMessageBox(QMessageBox.Warning, title,
                                          text, QMessageBox.Ok)
                        msg.setWindowIcon(QIcon(file_logo))
                        msg.setGeometry(650, 400, 100, 100)
                        msg.exec()

            self.delete_btn = QToolButton(main_program_win)
            self.delete_btn.setText('حذف حساب انتخاب شده')
            self.delete_btn.setFont(QFont('B Koodak', 12))
            self.delete_btn.clicked.connect(delete_account)
            self.delete_btn.setIcon(QIcon(file_delete))
            self.delete_btn.setLayoutDirection(Qt.RightToLeft)
            self.delete_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            self.delete_btn.setCursor(Qt.PointingHandCursor)
            self.delete_btn.setEnabled(False)
            self.delete_btn.setStyleSheet(tool_style)
            toolbar.addWidget(self.delete_btn)

            toolbar.addSeparator()

            self.add_btn = QToolButton(main_program_win)
            self.add_btn.setText('افزودن حساب')
            self.add_btn.setFont(QFont('B Koodak', 12))
            self.add_btn.clicked.connect(add_account)
            self.add_btn.setIcon(QIcon(file_new3))
            self.add_btn.setLayoutDirection(Qt.RightToLeft)
            self.add_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            self.add_btn.setCursor(Qt.PointingHandCursor)
            self.add_btn.setStyleSheet(tool_style)
            toolbar.addWidget(self.add_btn)

            self.desc.returnPressed.connect(lambda: self.add_btn.click())

        def make_tb_accounts(self):
            self.tb_accounts = QTableWidget(0, 8, main_program_win)
            self.accounts_layout.addWidget(self.tb_accounts, 7, 0, 1, 4)
            self.tb_accounts.setStyleSheet(
                'border : 1.5px solid %s' % light_blue_color)
            self.tb_accounts.horizontalHeader().setStyleSheet(
                'border : 0px solid white; border-right : 1px solid %s; border-bottom : 1px solid %s;' % (light_blue_color, light_blue_color))
            self.tb_accounts.verticalHeader().setStyleSheet(
                'border : 0px solid white; border-left : 1px solid %s; border-top : 1px solid %s;' % (light_blue_color, light_blue_color))

            self.tb_accounts.setFont(QFont('B Koodak', 12))
            self.tb_accounts.setFixedSize(720, 270)
            self.tb_accounts.setEditTriggers(QTableWidget.NoEditTriggers)
            self.tb_accounts.horizontalHeader().setMinimumHeight(30)
            self.tb_accounts.horizontalHeader().setFont(QFont('B Koodak', 12))
            self.tb_accounts.verticalHeader().setMinimumWidth(20)
            self.tb_accounts.setSelectionMode(QTableWidget.SingleSelection)
            self.tb_accounts.itemClicked.connect(
                lambda: self.delete_btn.setEnabled(True))

            self.tb_accounts.setColumnWidth(0, 100)
            self.tb_accounts.setColumnWidth(1, 100)
            self.tb_accounts.setColumnWidth(2, 120)
            self.tb_accounts.setColumnWidth(3, 100)
            self.tb_accounts.setColumnWidth(4, 100)
            self.tb_accounts.setColumnWidth(5, 100)
            self.tb_accounts.setColumnWidth(6, 100)
            self.tb_accounts.setColumnWidth(7, 100)
            self.tb_accounts.setHorizontalHeaderLabels(
                ['نام نمایشی', 'نام بانک', 'شماره ی حساب', 'نام صاحب', 'نوع حساب', 'تلفن بانک', 'آدرس بانک', 'توضیحات'])

            if Path(file_accounts % self.user_id).exists():
                self.accounts = Information.load_accounts(self.user_id)

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

        def correct_info(self):
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

    class Analyze:
        def __init__(self, user_id):
            connector = sqlite3.connect(file_costs % user_id)
            cursor = connector.cursor()
            cursor.execute('SELECT * FROM costs')
            data = cursor.fetchall()
            if data == []:
                title = 'ناموفق در باز کردن منوی آنالیز'
                text = 'دسترسی به این منو امکان پذیر نیست.\nزیرا شما تاکنون هزینه ای در برنامه ثبت نکرده اید'
                msg = QMessageBox(QMessageBox.Warning, title,
                                  text, QMessageBox.Ok)
                msg.setWindowIcon(QIcon(file_logo))
                msg.exec()
            else:
                self.cb_style = 'QComboBox {font-family: B Koodak; font-size: 12pt; border : 2px solid %s; border-radius: 5px;}' % light_blue_color + \
                    'QComboBox:Hover {border : 2px solid darkblue; background-color : #EAEAEA;}' + \
                    'QComboBox:Focus {border : 2px solid darkblue; background-color : #EAEAEA;}'

                self.date_style = 'QDateEdit {font-family: B Koodak; font-size: 12pt; border : 2px solid %s; border-radius: 5px;}' % light_blue_color + \
                    'QDateEdit::Hover {border : 2px solid darkblue; background-color : #EAEAEA}' + \
                    'QDateEdit:Focus {border : 2px solid darkblue; background-color : #EAEAEA;}'

                self.user_id = user_id
                self.make_frame()
                self.make_option1()
                self.make_option2()
                self.make_btn()
                self.on_click()
                self.make_labels()
                self.update_labels()

        def make_frame(self):
            self.analyze_frame = QFrame(main_program_win)
            self.analyze_frame.setStyleSheet(
                'QFrame {background-color : white; border: 2px solid %s;}' % light_blue_color)
            self.analyze_frame.setLayoutDirection(Qt.RightToLeft)
            self.analyze_frame.setFixedWidth(740)
            self.analyze_frame.show()

            self.analyze_layout = QGridLayout(self.analyze_frame)
            self.analyze_layout.setAlignment(Qt.AlignCenter)
            self.analyze_layout.setSpacing(35)
            self.analyze_frame.setLayout(self.analyze_layout)

            main_program_layout.addWidget(
                self.analyze_frame, 1, 1, 1, 1, Qt.AlignLeft)
            global selected_frame
            selected_frame = self.analyze_frame

            lb_analyze = QLabel(self.analyze_frame)
            lb_analyze.setText('نمایش آنالیز هزینه های ثبت شده')
            lb_analyze.setAlignment(Qt.AlignRight)
            lb_analyze.setFont(QFont('B Titr', 16))
            lb_analyze.setStyleSheet('border : 0px; color: darkblue')
            self.analyze_layout.addWidget(
                lb_analyze, 0, 0, Qt.AlignCenter)

            self.group_options = QGroupBox(
                'بازه ی زمانی هزینه ها برای آنالیز', self.analyze_frame)
            self.analyze_layout.addWidget(
                self.group_options, 1, 0, Qt.AlignCenter)
            self.group_options.setFixedSize(710, 180)
            self.group_options.setFont(QFont('B Titr', 12))
            self.group_options.setStyleSheet('QGroupBox {color: darkgray;}')
            self.vbox_group = QVBoxLayout(self.group_options)

        def make_option1(self):
            self.hbox1 = QHBoxLayout()
            self.vbox_group.addLayout(self.hbox1)

            self.rdbtn1 = QRadioButton('آنالیز و گزارش ماهانه')
            self.hbox1.addWidget(self.rdbtn1)
            self.rdbtn1.setFont(QFont('B Yekan', 13))
            self.rdbtn1.setChecked(True)
            self.rdbtn1.toggled.connect(lambda: self.on_click())

            self.lb_year = QLabel()
            self.hbox1.addWidget(self.lb_year)
            self.lb_year.setText('سال گزارش')
            self.lb_year.setFont(QFont('B Titr', 12))
            self.lb_year.setAlignment(Qt.AlignCenter)
            self.lb_year.setStyleSheet('border : 0px')

            min_year = Information.get_min_max_date_costs(self.user_id)[
                0].year()
            max_year = Information.get_min_max_date_costs(self.user_id)[
                1].year()
            self.cb_year = QComboBox()
            self.hbox1.addWidget(self.cb_year)
            self.cb_year.addItems([str(i)
                                  for i in range(min_year, max_year+1)])
            self.cb_year.setStyleSheet(self.cb_style)
            self.cb_year.setMinimumSize(100, 40)
            self.cb_year.setLayoutDirection(Qt.RightToLeft)
            self.cb_year.activated.connect(self.update_labels)

            self.lb_month = QLabel()
            self.hbox1.addWidget(self.lb_month)
            self.lb_month.setText('ماه گزارش')
            self.lb_month.setFont(QFont('B Titr', 12))
            self.lb_month.setAlignment(Qt.AlignCenter)
            self.lb_month.setStyleSheet('border : 0px')

            self.month_of_year = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                                  'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']

            self.cb_month = QComboBox()
            self.hbox1.addWidget(self.cb_month)
            self.cb_month.addItems(self.month_of_year)
            self.cb_month.setStyleSheet(self.cb_style)
            self.cb_month.setMinimumSize(100, 40)
            self.cb_month.setLayoutDirection(Qt.RightToLeft)
            self.cb_month.activated.connect(self.update_labels)

        def make_option2(self):
            self.hbox2 = QHBoxLayout()
            self.hbox2.setSpacing(30)
            self.vbox_group.addLayout(self.hbox2)

            self.rdbtn2 = QRadioButton('آنالیز و گزارش سالانه')
            self.hbox2.addWidget(self.rdbtn2)
            self.rdbtn2.setChecked(False)
            self.rdbtn2.setFont(QFont('B Yekan', 13))
            self.rdbtn2.toggled.connect(lambda: self.on_click())

            self.lb_year2 = QLabel()
            self.hbox2.addWidget(self.lb_year2, 1, Qt.AlignRight)
            self.lb_year2.setText('سال گزارش')
            self.lb_year2.setFont(QFont('B Titr', 12))
            self.lb_year2.setAlignment(Qt.AlignCenter)
            self.lb_year2.setStyleSheet('border : 0px')

            min_year = Information.get_min_max_date_costs(self.user_id)[
                0].year()
            max_year = Information.get_min_max_date_costs(self.user_id)[
                1].year()
            self.cb_year2 = QComboBox()
            self.hbox2.addWidget(self.cb_year2, 1, Qt.AlignLeft)
            self.cb_year2.addItems([str(i)
                                    for i in range(min_year, max_year+1)])
            self.cb_year2.setStyleSheet(self.cb_style)
            self.cb_year2.setMinimumSize(120, 40)
            self.cb_year2.setLayoutDirection(Qt.RightToLeft)
            self.cb_year2.activated.connect(self.update_labels)

            self.hbox2.addItem(QSpacerItem(260, 40))

        def on_click(self):
            lst_rdbtn1 = [self.lb_year, self.lb_month,
                          self.cb_year, self.cb_month]
            lst_rdbtn2 = [self.lb_year2, self.cb_year2]

            if self.rdbtn1.isChecked():
                for widget in lst_rdbtn2:
                    widget.setEnabled(False)
                for widget in lst_rdbtn1:
                    widget.setEnabled(True)
            else:
                for widget in lst_rdbtn1:
                    widget.setEnabled(False)
                for widget in lst_rdbtn2:
                    widget.setEnabled(True)

        def make_btn(self):
            self.hbox3 = QHBoxLayout()
            self.analyze_layout.addLayout(self.hbox3, 2, 0, Qt.AlignCenter)

            self.analyze_btn = QPushButton(self.analyze_frame)
            self.analyze_btn.setText('نمودار تغییرات مجموع هزینه ها')
            self.analyze_btn.setFont(QFont('B Koodak', 14))
            self.analyze_btn.setStyleSheet('''QPushButton {background-color: %s; border: 2px solid #16646C; border-radius : 5px}
                                            QPushButton:Hover {background-color: #599cff; color: white}''' % (light_blue_color))
            self.analyze_btn.setFixedSize(270, 50)
            self.analyze_btn.setCursor(Qt.PointingHandCursor)
            self.analyze_btn.clicked.connect(lambda: self.analyze1())
            self.hbox3.addWidget(self.analyze_btn)

            ################################################################

            self.analyze_btn = QPushButton(self.analyze_frame)
            self.analyze_btn.setText('نمودار مقایسه ی نوع هزینه ها')
            self.analyze_btn.setFont(QFont('B Koodak', 14))
            self.analyze_btn.setStyleSheet('''QPushButton {background-color: %s; border: 2px solid #16646C; border-radius : 5px}
                                            QPushButton:Hover {background-color: #599cff; color: white}''' % (light_blue_color))
            self.analyze_btn.setFixedSize(270, 50)
            self.analyze_btn.setCursor(Qt.PointingHandCursor)
            self.analyze_btn.clicked.connect(lambda: self.analyze2())
            self.hbox3.addWidget(self.analyze_btn)

        def analyze1(self):
            if self.rdbtn1.isChecked():
                try:
                    year = self.cb_year.currentText()
                    month = str(date.j_month_fa_to_num(
                        self.cb_month.currentText()))

                    self.costs_of_month = Information.get_costs_of_month(
                        self.user_id, int(year), int(month))

                    ######################################################

                    xpoint = [i for i in range(1, 32)]
                    ypoint = []
                    for day in self.costs_of_month:
                        sum_of_month_costs = 0
                        for cost in self.costs_of_month[day]:
                            sum_of_month_costs += cost[0]
                        ypoint.append(sum_of_month_costs)

                    xpoint_array = array(xpoint)
                    ypoint_array = array(ypoint)
                    font1 = {'family': 'B Yekan', 'color': 'black', 'size': 15}
                    font2 = {'family': 'B Titr', 'color': 'black', 'size': 20}

                    plt.plot(xpoint_array, ypoint_array, marker='o', markersize=8,
                             markerfacecolor='c', markeredgecolor='r', color='darkblue')
                    plt.xlabel(self.get_persion('روز'), font1, loc='right')
                    plt.ylabel(self.get_persion('مجموع هزینه های هر روز'),
                               font1, loc='top')
                    plt.title(self.get_persion('نمودار تغییرات مجموع هزینه های ماهانه (%s)' % self.cb_month.currentText()),
                              font2, 'right')
                    plt.grid()
                    plt.yticks(ypoint_array)
                    plt.ticklabel_format(style='plain')
                    plt.show()

                    title = 'نمودار مجموع هزینه ها'
                    text = 'توجه: برای نمایش بهتر شماره ی روز ها (محور افقی)\nو مجموع هزینه های هر روز (محور عمودی) با استفاده از\nگزینه ی بزرگنمایی در نوار بالا، عمل بزرگنمایی را انجام دهید'
                    msg = QMessageBox(QMessageBox.Information,
                                      title, text, QMessageBox.Ok)
                    msg.setWindowIcon(QIcon(file_logo))
                    msg.exec()
                except:
                    title = 'نمودار مجموع هزینه های ماهانه'
                    text = 'ناموفق در ایجاد "نمودار تغییرات مجموع هزینه های ماهانه"'
                    msg = QMessageBox(QMessageBox.Information, title,
                                      text, QMessageBox.Ok)
                    msg.setWindowIcon(QIcon(file_logo))
                    msg.exec()

            else:
                try:
                    year = self.cb_year2.currentText()

                    self.costs_of_year = Information.get_costs_of_year(
                        self.user_id, year)

                    xpoint = list(map(self.get_persion, self.month_of_year))
                    ypoint = []
                    for month in self.costs_of_year:
                        sum_of_month_costs = 0
                        for day in self.costs_of_year[month]:
                            for cost in self.costs_of_year[month][day]:
                                sum_of_month_costs += cost[0]
                        ypoint.append(sum_of_month_costs)

                    xpoint_array = array(xpoint)
                    ypoint_array = array(ypoint)
                    font1 = {'family': 'B Yekan', 'color': 'black', 'size': 15}
                    font2 = {'family': 'B Titr', 'color': 'black', 'size': 20}

                    plt.plot(xpoint_array, ypoint_array, marker='o', markersize=8,
                             markerfacecolor='c', markeredgecolor='r', color='darkblue')
                    plt.xlabel(self.get_persion('ماه'), font1, loc='right')
                    plt.ylabel(self.get_persion('مجموع هزینه های هر ماه'),
                               font1, loc='top')
                    plt.title(self.get_persion('نمودار تغییرات مجموع هزینه های سالانه (%s)' % year),
                              font2, 'right')
                    plt.grid()
                    plt.yticks(ypoint_array)
                    plt.ticklabel_format(axis='y', style='plain')
                    plt.show()

                    title = 'نمودار مجموع هزینه ها'
                    text = 'توجه: برای نمایش بهتر مجموع هزینه های هر ماه (محور عمودی)\nبا استفاده از گزینه ی بزرگنمایی در نوار بالا، عمل بزرگنمایی را انجام دهید'
                    msg = QMessageBox(QMessageBox.Information,
                                      title, text, QMessageBox.Ok)
                    msg.setWindowIcon(QIcon(file_logo))
                    msg.exec()
                except:
                    title = 'نمودار مجموع هزینه های سالانه'
                    text = 'ناموفق در ایجاد "نمودار تغییرات مجموع هزینه های سالانه"'
                    msg = QMessageBox(QMessageBox.Information, title,
                                      text, QMessageBox.Ok)
                    msg.setWindowIcon(QIcon(file_logo))
                    msg.exec()

        def analyze2(self):
            if self.rdbtn1.isChecked():
                try:
                    year = self.cb_year.currentText()
                    month = str(date.j_month_fa_to_num(
                        self.cb_month.currentText()))

                    self.percentages = Information.get_percentages_month(
                        self.user_id, year, month)
                    mylabels = list(
                        map(self.get_persion, self.percentages.keys()))
                    points = array(list(self.percentages.values()))

                    mypercentages = []
                    for point in points:
                        mypercentages.append(self.get_persion(point) + '%')

                    plt.pie(points, labels=mypercentages, startangle=90)
                    plt.legend(labels=mylabels, title=self.get_persion('انواع هزینه ها'),
                               loc="upper right", ncol=1, bbox_to_anchor=(1.35, 1.1))
                    plt.show()
                except:
                    title = 'نمودار ماهانه انواع هزینه ها'
                    text = 'ناموفق در ایجاد "نمودار ماهانه انواع هزینه ها"'
                    msg = QMessageBox(QMessageBox.Information, title,
                                      text, QMessageBox.Ok)
                    msg.setWindowIcon(QIcon(file_logo))
                    msg.exec()
            else:
                try:
                    year = self.cb_year2.currentText()

                    self.percentages = Information.get_percentages_month(
                        self.user_id, year, 'all')
                    mylabels = list(
                        map(self.get_persion, self.percentages.keys()))
                    points = array(list(self.percentages.values()))

                    mypercentages = []
                    for poin in points:
                        mypercentages.append(self.get_persion(poin) + '%')

                    plt.pie(points, labels=mypercentages, startangle=90)
                    plt.legend(labels=mylabels, title=self.get_persion('انواع هزینه ها'),
                               loc="upper right", ncol=1, bbox_to_anchor=(1.35, 1.1))
                    plt.show()
                except:
                    title = 'نمودار سالانه انواع هزینه ها'
                    text = 'ناموفق در ایجاد "نمودار سالانه انواع هزینه ها"'
                    msg = QMessageBox(QMessageBox.Information, title,
                                      text, QMessageBox.Ok)
                    msg.setWindowIcon(QIcon(file_logo))
                    msg.exec()

        def get_persion(self, text):
            return get_display(arabic_reshaper.reshape(u'%s' % str(text)))

        def make_labels(self):
            lb_style = 'border : 2px solid %s; color: darkblue; border-radius: 5px;' % light_blue_color

            self.lb_sum_costs = QLabel()
            self.analyze_layout.addWidget(
                self.lb_sum_costs, 3, 0, Qt.AlignCenter)
            self.lb_sum_costs.setText('مجموع هزینه ها: ')
            self.lb_sum_costs.setFont(QFont('B Koodak', 15))
            self.lb_sum_costs.setAlignment(Qt.AlignCenter)
            self.lb_sum_costs.setStyleSheet(lb_style)
            self.lb_sum_costs.setMinimumSize(300, 50)

            self.lb_sum_income = QLabel()
            self.analyze_layout.addWidget(
                self.lb_sum_income, 4, 0, Qt.AlignCenter)
            self.lb_sum_income.setText('مجموع درآمد: ')
            self.lb_sum_income.setFont(QFont('B Koodak', 15))
            self.lb_sum_income.setAlignment(Qt.AlignCenter)
            self.lb_sum_income.setStyleSheet(lb_style)
            self.lb_sum_income.setMinimumSize(300, 50)

            self.lb_sum_saving = QLabel()
            self.analyze_layout.addWidget(
                self.lb_sum_saving, 5, 0, Qt.AlignCenter)
            self.lb_sum_saving.setText('مجموع پس انداز: ')
            self.lb_sum_saving.setFont(QFont('B Koodak', 15))
            self.lb_sum_saving.setAlignment(Qt.AlignCenter)
            self.lb_sum_saving.setStyleSheet(lb_style)
            self.lb_sum_saving.setMinimumSize(300, 50)

            self.lb_status = QLabel()
            self.analyze_layout.addWidget(
                self.lb_status, 6, 0, Qt.AlignCenter)
            self.lb_status.setText('وضعیت پس انداز: ')
            self.lb_status.setFont(QFont('B Koodak', 15))
            self.lb_status.setAlignment(Qt.AlignCenter)
            self.lb_status.setStyleSheet(lb_style)
            self.lb_status.setMinimumSize(350, 50)

            self.lb_sum_income_text = self.lb_sum_income.text()
            self.lb_sum_costs_text = self.lb_sum_costs.text()
            self.lb_sum_saving_text = self.lb_sum_saving.text()
            self.lb_status_text = self.lb_status.text()
            self.lb_status_style = self.lb_status.styleSheet()

        def update_labels(self):
            try:
                if main_program_win.sender() == self.cb_year2:
                    costs = Information.get_costs_of_year(
                        self.user_id, self.cb_year.currentText())
                    sum_costs = sum([cost[0] for month in costs.values() for day in month.values()
                                     for cost in day])

                    sum_income = Information.load_information(self.user_id)[
                        2] * 12
                else:
                    costs = Information.get_costs_of_month(
                        self.user_id, self.cb_year.currentText(), date.j_month_fa_to_num(self.cb_month.currentText()))
                    sum_costs = sum([cost[0] for day in costs.values()
                                     for cost in day])

                    sum_income = Information.load_information(self.user_id)[2]

                self.lb_sum_income.setText(
                    self.lb_sum_income_text + str(sum_income))

                self.lb_sum_costs.setText(
                    self.lb_sum_costs_text + str(sum_costs))

                self.lb_sum_saving.setText(
                    self.lb_sum_saving_text + str(sum_income - sum_costs))

                if sum_costs == 0:
                    sum_costs = 1
                if sum_income == 0:
                    sum_income = 1

                if int(sum_income) > sum_costs:
                    if int(sum_income) / sum_costs == 2:
                        status = 'بسیار خوب'
                        color = 'lightgreen'
                    elif int(sum_income) / sum_costs > 2:
                        status = 'عالی'
                        color = '#139a26'
                    elif int(sum_income) / sum_costs > 1.5:
                        status = 'خوب'
                        color = '#b8ca3c'
                    else:
                        status = 'متوسط'
                        color = 'yellow'
                elif int(sum_income) < sum_costs:
                    if sum_costs / int(sum_income) == 2:
                        status = 'ضعیف'
                        color = 'orange'
                    elif sum_costs / int(sum_income) > 2:
                        status = 'بسیار ضعیف'
                        color = 'red'
                    elif sum_costs / int(sum_income) > 1.5:
                        status = 'بد'
                        color = '#ffc000'
                    else:
                        status = 'متوسط'
                        color = 'yellow'
                else:
                    status = 'متوسط'
                    color = 'yellow'

                self.lb_status.setText(self.lb_status_text + status)
                self.lb_status.setStyleSheet(
                    self.lb_status_style + 'background-color: %s' % color)
            except:
                title = 'گزارش وضعیت ماهانه و سالانه'
                text = 'ناموفق در ایجاد "گزارش وضعیت ماهانه و سالانه"'
                msg = QMessageBox(QMessageBox.Information, title,
                                  text, QMessageBox.Ok)
                msg.setWindowIcon(QIcon(file_logo))
                msg.exec()

    class UsersManager:
        def __init__(self, mode, user_id, username):
            main_program_win.close()

            if mode == 'signup':
                signup_win = Signup(user_id)
                signup_win.show()
            elif mode == 'signin':
                signin_win = Signin(user_id)
                signin_win.show()
            else:
                self.remove_user(user_id, username)

        def remove_user(self, user_id, username):
            title = 'حذف کاربر از برنامه'
            text = 'توجه: با حذف کاربر "%s" از برنامه، تمام اطلاعات وارد شده\n از کاربر در برنامه حذف خواهند شد. آیا مایل به ادامه هستید؟' % username
            msg = QMessageBox(QMessageBox.Warning, title,
                              text, QMessageBox.Yes | QMessageBox.No)
            msg.setWindowIcon(QIcon(file_logo))
            msg.setGeometry(650, 400, 100, 100)
            result = msg.exec()

            if result == 16384:
                try:
                    Information.remove_user(user_id)

                    title = 'حذف کاربر از برنامه'
                    text = 'کاربر "%s" با موفقیت از برنامه حذف شد' % username
                    msg = QMessageBox(QMessageBox.Information, title,
                                      text, QMessageBox.Ok)
                    msg.setWindowIcon(QIcon(file_logo))
                    msg.setGeometry(650, 400, 100, 100)
                    msg.exec()
                    if Path(file_information).exists():
                        signin_win = Signin(user_id)
                        signin_win.show()
                    else:
                        signup_win = Signup(user_id)
                        signup_win.show()
                except:
                    title = 'حذف کاربر از برنامه'
                    text = 'ناموفق در حذف کاربر "%s"' % username
                    msg = QMessageBox(QMessageBox.Information, title,
                                      text, QMessageBox.Ok)
                    msg.setWindowIcon(QIcon(file_logo))
                    msg.setGeometry(650, 400, 100, 100)
                    result = msg.exec()

                    main = User(user_id)
            else:
                main = User(user_id)

    class About:
        def __init__(self):

            self.make_frame()
            self.make_about()

        def make_frame(self):
            self.about_frame = QFrame(main_program_win)
            self.about_frame.setStyleSheet(
                'background-color : white; border: 2px solid %s;' % light_blue_color)
            self.about_frame.show()

            main_program_layout.addWidget(self.about_frame, 1, 1)
            global selected_frame
            selected_frame = self.about_frame

            self.about_layout = QGridLayout(self.about_frame)
            self.about_frame.setLayout(self.about_layout)

        def make_about(self):
            lb_about = QLabel(self.about_frame)
            self.about_layout.addWidget(lb_about, 0, 0, Qt.AlignCenter)

            with open(file_text_about, 'r', encoding='UTF8') as file:
                text_about = file.read()
            lb_about.setText(text_about)
            lb_about.setWordWrap(True)
            lb_about.setStyleSheet('border: 0px')
            lb_about.setFixedSize(730, 520)
            lb_about.setAlignment(Qt.AlignCenter)
            lb_about.setLayoutDirection(Qt.RightToLeft)
            lb_about.setFont(QFont('B Koodak', 15))

            ################################################################
            def connect_sites(url):
                try:
                    WindowsDefault().open_new_tab(url)
                except:
                    pass

            btn_style = '''QPushButton {border: 0px; color: darkblue;}
                        QPushButton::ToolTip {background-color: white; font-family: B Koodak;}'''

            btn_email = QPushButton(self.about_frame)
            self.about_layout.addWidget(btn_email, 1, 0, Qt.AlignCenter)
            btn_email.setText(
                'tavallaei.14@gmail.com :ایمیل')
            btn_email.setStyleSheet(btn_style)
            btn_email.setFixedSize(500, 35)
            btn_email.setLayoutDirection(Qt.RightToLeft)
            btn_email.setFont(QFont('B Koodak', 15))
            btn_email.setCursor(Qt.PointingHandCursor)
            btn_email.setToolTip('برای ارسال ایمیل به برنامه نویس صربه بزنید')
            btn_email.clicked.connect(
                lambda: connect_sites('https://mail.google.com/mail/u/0/#sent?compose=GTvVlcSMScWCcMczQrXxTjNjSDdcLSnnFwKqMZMVXzchTCNqRGfMBLmmtXhDSbffczjnLFMzjXcJG'))

            btn_github = QPushButton(self.about_frame)
            self.about_layout.addWidget(btn_github, 2, 0, Qt.AlignCenter)
            btn_github.setText(
                'https://github.com/AR-Tavallaei :گیت هاب')
            btn_github.setStyleSheet(btn_style)
            btn_github.setFixedSize(500, 35)
            btn_github.setLayoutDirection(Qt.RightToLeft)
            btn_github.setFont(QFont('B Koodak', 15))
            btn_github.setCursor(Qt.PointingHandCursor)
            btn_github.setToolTip(
                'برای نمایش حساب گیت هاب برنامه نویس صربه بزنید')
            btn_github.clicked.connect(
                lambda: connect_sites('https://github.com/AR-Tavallaei'))

            ################################################################

            lb_logo = QPushButton(self.about_frame)
            lb_logo.setStyleSheet('border: 0px')
            self.about_layout.addWidget(lb_logo, 3, 0, Qt.AlignCenter)
            lb_logo.setIcon(QIcon(file_logo))
            lb_logo.setFixedSize(140, 140)
            lb_logo.setIconSize(QSize(140, 140))


app = QApplication(sys.argv)
fonts = QFontDatabase()
for font in listdir(file_fonts):
    fonts.addApplicationFont(path.join(file_fonts, font))
win = InitProgram()
sys.exit(app.exec())
