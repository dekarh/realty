from datetime import datetime
import time

from mysql.connector import MySQLConnection, Error
from PyQt5.QtCore import QDate, QDateTime, QSize, Qt, QByteArray, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QTableWidget, QTableWidgetItem, QLabel


from lib import l, lenl, read_config, fine_phone
from realty_win import Ui_Form

class MainWindowSlots(Ui_Form):   # Определяем функции, которые будем вызывать в слотах

    def setupUi(self, form):
        Ui_Form.setupUi(self,form)

        dbconfig = read_config(filename='realty.ini', section='mysql')
        self.dbconn = MySQLConnection(**dbconfig)  # Открываем БД из конфиг-файла
        self.first_setup_tableWidget()
        return

    def click_cbHTML(self):
        self.setup_tableWidget()
        return

    def first_setup_tableWidget(self):
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)        # Кол-во строк из таблицы
        sql = 'SELECT phone, tip, about, DATE_FORMAT(edit_date,"%d.%m %H:%i") FROM contacts'
        if lenl(self.leFilter.text()) > 0:
            sql += ' WHERE phone LIKE "%' + str(l(self.leFilter.text())) + '%"'
        self.dbconn.connect()
        read_cursor = self.dbconn.cursor()
        read_cursor.execute(sql)
        rows = read_cursor.fetchall()
        self.tableWidget.setColumnCount(4)             # Устанавливаем кол-во колонок
        self.tableWidget.setRowCount(len(rows))        # Кол-во строк из таблицы
        for i, row in enumerate(rows):
            for j, cell in enumerate(row):
                label = QLabel()
                if j == 0:
                    label.setText(fine_phone(str(cell)))
                else:
                    label.setText(str(cell))
                label.setAlignment(Qt.AlignCenter)
                self.tableWidget.setCellWidget(i, j, label)
 #               self.tableWidget.setItem(i, j, QTableWidgetItem(str(cell)))
        # Устанавливаем заголовки таблицы
        self.tableWidget.setHorizontalHeaderLabels(["телефон", "тип", "описание","дата"])

        # Устанавливаем выравнивание на заголовки
        self.tableWidget.horizontalHeaderItem(0).setTextAlignment(Qt.AlignCenter)
        self.tableWidget.horizontalHeaderItem(1).setTextAlignment(Qt.AlignCenter)
        self.tableWidget.horizontalHeaderItem(2).setTextAlignment(Qt.AlignCenter)

        # делаем ресайз колонок по содержимому
        self.tableWidget.resizeColumnsToContents()
        return

    def setup_tableWidget(self):
        self.first_setup_tableWidget()
        self.click_tableWidget()
        return

    def click_tableWidget(self, index=None):
        if index == None:
            index = self.tableWidget.model().index(0, 0)
        if index.row() < 0:
            return None
        self.leAbout.setText(self.tableWidget.cellWidget(index.row(),2).text())
        return None

    def click_pbFilter(self):  # Фильтровать
        a = self.leFilter.text().strip()
#        if lenl(a) > 0:
#            if str(l(a))[0] == '8':
#                a = '7' + str(lenl(a))[1:]
#            elif str(l(a))[0] != '7':
#                a = '7' + str(l(a))
#            self.leFilter.setText(a)
        self.setup_tableWidget()

    def click_pbAccept(self):  # Обновить/добавить
        a = self.leFilter.text().strip()
        if lenl(a) < 10 or lenl(a) > 11:
            return None
        elif lenl(a) == 10:
            a = l('7' + self.leFilter.text())
        else:
            if str(l(a))[0] == '8':
                a = '7' + str(l(a))[1:]
            elif str(l(a))[0] == '7':
                q = 0
            else:
                return None

        self.dbconn.connect()
        dbcursor = self.dbconn.cursor()
        dbcursor.execute('SELECT count(*) FROM contacts WHERE phone = %s', (a,))
        rows = dbcursor.fetchall()
        if rows[0][0] == 0:
            dbcursor.execute('INSERT contacts (phone, about, edit_date) VALUES(%s,%s,%s)',(a, self.leAbout.text().strip(),
                                                                                        datetime.now()))
        else:
            dbcursor.execute('UPDATE contacts SET about = %s, edit_date = %s WHERE phone = %s',(self.leAbout.text().strip(),
                                                                                        datetime.now(), a))
        self.dbconn.commit()

        self.leFilter.setText('')
        self.setup_tableWidget()
        return


