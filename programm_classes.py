from design_classes import *
from PyQt5.QtWidgets import QMessageBox, QDialog, QTreeWidgetItem, QMainWindow, qApp, QFileDialog, QApplication
from encription_functions import *
import sqlite3
import os.path


class DeveloperDial(QDialog, Ui_Developer):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)


class UserGuideDial(QDialog, Ui_UserGuide):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)


class CreateKeyDial(QDialog, Ui_CreateKey):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

    def accept(self):
        # Если пароли не совпадают или пароль не введен вывести окно с ошибкой
        error_text = None
        if self.le_create_password.text() == self.le_repeat_password.text() == '':
            error_text = "Пароль не может быть пустой строкой"
        elif self.le_create_password.text() != self.le_repeat_password.text():
            error_text = "Пароли не совпадают"
        if error_text is None:
            super().accept()
        else:
            msg = QMessageBox()
            msg.setWindowIcon(QIcon(r"Images/Main_icon.png"))
            msg.setWindowTitle("Ошибка")
            msg.setIcon(QMessageBox.Critical)
            msg.setText(error_text)
            msg.exec_()

    def get_key(self):
        return self.le_create_password.text()


class CreateGroupDial(QDialog, Ui_CreateGroup):
    def __init__(self, database, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.db = database

    def accept(self) -> None:
        if self.get_name() in self.db.get_groups() or not self.get_name():
            msg = QMessageBox()
            msg.setWindowIcon(QIcon(r"Images/Main_icon.png"))
            msg.setWindowTitle("Error")
            msg.setIcon(QMessageBox.Critical)
            if not self.get_name():
                msg.setText("The password must not be empty.")
            else:
                msg.setText("This group exists now")
            msg.exec_()
            self.le_group_name.setText("")
        else:
            super().accept()

    def get_name(self):
        return self.le_group_name.text()


class CheckPasswordDial(QDialog, Ui_CheckPassword):
    def __init__(self, password, salt, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.password = password
        self.salt = salt

    def accept(self):
        if not check_password_hash(self.le_password.text(), self.salt, self.password):
            # Если пароли не совпадают вывести ошибку
            msg = QMessageBox()
            msg.setWindowIcon(QIcon(r"Images/Main_icon.png"))
            msg.setWindowTitle("Ошибка")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Неправильный пароль")
            msg.exec_()
            self.le_password.setText("")
        else:
            super().accept()


class AddEntryDial(QDialog, Ui_AddEntry):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.view_password = False
        self.btn_generate.clicked.connect(self.generate)
        self.btn_view.clicked.connect(self.change_view)

    def change_view(self):
        if self.view_password:
            self.le_password.setEchoMode(QLineEdit.Password)
            self.le_repeat.setEchoMode(QLineEdit.Password)
        else:
            self.le_password.setEchoMode(QLineEdit.Normal)
            self.le_repeat.setEchoMode(QLineEdit.Normal)
        self.view_password = not self.view_password

    def generate(self):
        password = generate_password()
        self.le_password.setText(password)
        self.le_repeat.setText(password)
        if not self.view_password:
            self.change_view()

    def accept(self):
        failed = False
        message = None
        if not (self.le_title.text() and self.le_user_name.text() and self.le_url.text()):
            failed = True
            message = "Заполните пустые поля"
        elif self.le_password.text() != self.le_repeat.text():
            failed = True
            message = "Пароли не совпадают"
        elif not self.le_password.text():
            failed = True
            message = "Пароль не может быть пустой строкой"
        if failed:
            msg = QMessageBox()
            msg.setWindowIcon(QIcon(r"Images/Main_icon.png"))
            msg.setWindowTitle("Ошибка")
            msg.setIcon(QMessageBox.Critical)
            msg.setText(message)
            msg.exec_()
        else:
            super().accept()

    def get_password(self):
        return self.le_password.text()

    def get_data(self):
        return [self.le_title.text(), self.le_user_name.text(), self.le_url.text(), self.textEdit.toPlainText()]

    def set_line_edit(self, password, title, user_name, url, notes):
        self.le_title.setText(title)
        self.le_user_name.setText(user_name)
        self.le_password.setText(password)
        self.le_repeat.setText(password)
        self.le_url.setText(url)
        self.textEdit.setText(notes)


class MyTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, id_el, parent=None):
        super(MyTreeWidgetItem, self).__init__(parent)
        self.id = id_el

    def get_id(self):
        return self.id


class KeysManager(QMainWindow, Ui_KeysManager):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.set_resent_files()
        self.set_connections()
        self.db = None
        self.clicked_group_name = None
        self.clicked_entry = None

    def set_resent_files(self):
        if not os.path.exists("resent_files.txt"):
            file = open("resent_files.txt", "w", encoding="utf-8")
            file.close()
        with open("resent_files.txt", encoding="utf-8") as file:
            self.file_actions[3].clear()
            for el in file.readlines():
                action = QAction(el.rstrip(), self)
                action.triggered.connect(self.open_resent_file)
                self.file_actions[3].addAction(action)

    def set_connections(self):
        # Подключает функции к выподающему меню
        self.file_actions[0].triggered.connect(self.create_file)  # Создание файла
        self.file_actions[1].triggered.connect(self.open_file)  # Открытие файла
        self.file_actions[2].triggered.connect(self.close_file)  # Закрытие файла
        self.file_actions[4].triggered.connect(self.change_master_key)  # Изменение масет ключа
        self.file_actions[5].triggered.connect(qApp.quit)  # Закрытие программы

        self.group_actions[0].triggered.connect(self.add_group)  # Создает кнопку
        self.group_actions[1].triggered.connect(self.del_group)  # Удаляет групу
        self.group_actions[2].triggered.connect(self.edit_group)  # Изменяет группу
        self.tree_groups.setContextMenuPolicy(Qt.CustomContextMenu)  # Контекстое меню для показа директории
        self.tree_groups.customContextMenuRequested.connect(self.tree_context)
        self.tree_groups.itemClicked.connect(self.tree_item_clicked)  # Нажатие на группу

        self.entry_actions[0].triggered.connect(self.copy_user_name)  # Добавление логина в буфер обмена
        self.entry_actions[1].triggered.connect(self.copy_password)  # Добавление пароля в буфер обмена
        self.entry_actions[2].triggered.connect(self.copy_url)  # Добавление ссылки в буфер обмена
        self.entry_actions[3].triggered.connect(self.add_entry)  # Создание пароля
        self.entry_actions[4].triggered.connect(self.edit_entry)  # Редактирование пароля
        self.entry_actions[5].triggered.connect(self.del_entry)  # Удаление пароля
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)  # Контекстое меню для показа директории
        self.table.customContextMenuRequested.connect(self.table_context)
        self.table.itemClicked.connect(self.table_clicked)  # Нажатие на пароль

        self.help_actions[0].triggered.connect(self.user_guide)  # Справка пользователя
        self.help_actions[1].triggered.connect(self.developer)  # Автор

    def create_file(self):
        # Поучаем путь по которому нужно сохранить файл
        patch, ok = QFileDialog.getSaveFileName(self, "Создать файл базы данных", '', "База данных (*.SQLITE)")
        if ok:
            dlg = CreateKeyDial(self)
            dlg.lbl_dir.setText(patch)
            if dlg.exec():
                salt, master_key = create_password_hash(dlg.get_key())
                self.db = DataBase(patch, create=True, master=master_key, salt=salt)  # Подключаемся к базе данных
                self.db.clear()  # Очищаем бд перед созданием
                self.db.add_group("Главная")  # Создание главной папки
                self.set_status_menu_file(True)  # Активируем виджеты которые доступны после открытия файла
                self.show_dir()  # Показываем директорию папок с таблицами
                self.add_resent_file(patch)

    def open_file(self):
        # Поучаем путь по которому нужно открыть файл
        patch, ok = QFileDialog.getOpenFileName(self, "", 'Открываем файл базы данных', "База данных (*.SQLITE)")
        if ok:
            self.db = DataBase(patch, create=False)  # Подключаемся к базе данных
            dlg = CheckPasswordDial(*self.db.get_master(), parent=self)
            if dlg.exec():
                # Если пользователь ввел правильный пароль
                self.set_status_menu_file(True)  # Активируем виджеты которые доступны после открытия файла
                self.show_dir()  # Показываем директорию папок с таблицами
                self.add_resent_file(patch)  # Добавляем файл в недавно открытые

    def close_file(self):
        self.set_status_menu_file(False)  # Выключаем функции файла
        self.tree_groups.clear()  # Очищения таблиц
        self.table.clear()
        self.group_actions[1].setEnabled(False)  # Выключаем кнопку удаления группы
        self.db = None

    def open_resent_file(self):
        if os.path.exists(self.sender().text()):
            self.db = DataBase(self.sender().text(), create=False)  # Подключаемся к базе данных
            dlg = CheckPasswordDial(*self.db.get_master(), parent=self)
            if dlg.exec():
                # Если пользователь ввел правильный пароль
                self.set_status_menu_file(True)  # Активируем виджеты которые доступны после открытия файла
                self.show_dir()  # Показываем директорию папок с таблицами
                self.add_resent_file(self.sender().text())  # Добавляем файл в недавно открытые
        else:
            msg = QMessageBox()
            msg.setWindowIcon(QIcon(r"Images/Main_icon.png"))
            msg.setWindowTitle("Ошибка")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Файл был удален или перемещен в другую директорию")
            msg.exec_()
            self.del_resent_file(self.sender().text())

    def change_master_key(self):
        dlg = CreateKeyDial()
        dlg.setWindowTitle("Изменить главный пароль")
        if dlg.exec():
            # Перезаписываем мастер ключ в базе данных
            salt, key = create_password_hash(dlg.le_create_password.text())
            self.db.set_master(key, salt)

    def add_group(self):
        dlg = CreateGroupDial(self.db, self)
        if dlg.exec():
            self.db.add_group(dlg.get_name())  # Добавляем таблицу в бд
            self.show_dir()  # Перепоказываем директорию
            self.group_actions[1].setEnabled(False)  # Выключаем кнопку удаления группы
            self.clicked_group_name = None  # Убираем нажатую группу
            # Выключаем функции связанные с таблицей паролей
            for el in self.entry_actions:
                el.setEnabled(False)

    def del_group(self):
        if self.clicked_group_name == "Главная":
            msg = QMessageBox()
            msg.setWindowIcon(QIcon(r"Images/Main_icon.png"))
            msg.setWindowTitle("Ошибка")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Вы не можете удалить главную папку")
            msg.exec_()
        else:
            # Удаляем таблицу и перепоказываем группы
            self.db.del_group(self.clicked_group_name)
            self.show_dir()
            self.entry_actions[3].setEnabled(False)  # Выключаем кнопку создания таблицы
            self.clicked_group_name = None  # Убираем нажатую группу
            self.table.clear()
        self.group_actions[1].setEnabled(False)  # Выключаем возможность удаления групп
        self.group_actions[2].setEnabled(False)  # Выключаем возможность изменения групп
        for el in self.entry_actions:
            el.setEnabled(False)

    def edit_group(self):
        last_name = self.clicked_group_name
        if last_name != "Главная":
            dlg = CreateGroupDial(self.db, self)
            dlg.setWindowTitle("Редактировать группу")
            dlg.le_group_name.setText(last_name)
            if dlg.exec():
                self.db.edit_group(last_name, dlg.get_name())  # Добавляем таблицу в бд
                self.show_dir()  # Перепоказываем директорию
                self.group_actions[1].setEnabled(False)  # Выключаем кнопку удаления группы
                self.group_actions[2].setEnabled(False)  # Выключаем кнопку изменения группы
                self.clicked_group_name = None  # Убираем нажатую группу
                # Выключаем функции связанные с таблицей паролей
                for el in self.entry_actions:
                    el.setEnabled(False)
        else:
            msg = QMessageBox()
            msg.setWindowIcon(QIcon(r"Images/Main_icon.png"))
            msg.setWindowTitle("Ошибка")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Вы не можете редактировать главную папку")
            msg.exec_()

    def tree_context(self, point):
        menu = QMenu()
        actions = [self.group_actions[0]]
        if self.tree_groups.itemAt(point):
            # Если попали на группу то добавить возможность удалить группу
            self.clicked_group_name = self.tree_groups.itemAt(point).text(0)
            del_group = QAction("Удалить группу", menu)
            del_group.setIcon(QIcon(r"Images\Delete_group.png"))
            del_group.triggered.connect(self.del_group)
            edit_group = QAction("Редактировать группу", menu)
            edit_group.triggered.connect(self.edit_group)
            actions.extend([del_group, edit_group])
        menu.addActions(actions)
        # Расположить выпадающее меню там где его вызвали
        menu.exec(self.tree_groups.mapToGlobal(point))

    def tree_item_clicked(self, it):
        for el in self.entry_actions:
            el.setEnabled(False)
        self.group_actions[1].setEnabled(True)  # Включаем кнопку удалени группы
        self.group_actions[2].setEnabled(True)  # Включаем кнопку изменения группы
        self.entry_actions[3].setEnabled(True)  # Включаем кнопку создания пароля
        self.clicked_group_name = it.text(0)
        self.show_table()  # Показываем таблицу с паролями

    def copy_user_name(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.clicked_entry.text(1))
        msg = QMessageBox()
        msg.setWindowIcon(QIcon(r"Images/Main_icon.png"))
        msg.setWindowTitle("Информация")
        msg.setIcon(QMessageBox.Information)
        msg.setText("Логин скопирован")
        msg.exec_()

    def copy_password(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.clicked_entry.text(2).rstrip())
        msg = QMessageBox()
        msg.setWindowIcon(QIcon(r"Images/Main_icon.png"))
        msg.setWindowTitle("Информация")
        msg.setIcon(QMessageBox.Information)
        msg.setText("Пароль скпирован")
        msg.exec_()

    def copy_url(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.clicked_entry.text(3))
        msg = QMessageBox()
        msg.setWindowIcon(QIcon(r"Images/Main_icon.png"))
        msg.setWindowTitle("Информация")
        msg.setIcon(QMessageBox.Information)
        msg.setText("Ссылка скопирована")
        msg.exec_()

    def add_entry(self):
        dlg = AddEntryDial(self)
        if dlg.exec():
            key, password = encrypt_password(dlg.get_password())
            self.db.add_key(self.clicked_group_name, password, key, dlg.get_data())
            self.show_table()

    def edit_entry(self):
        dlg = AddEntryDial(self)
        data = self.db.get_key(self.clicked_entry.get_id())
        dlg.set_line_edit(decrypt_password(data[1], data[0]), *data[2:])
        if dlg.exec():
            key, password = encrypt_password(dlg.get_password())
            self.db.change_key(self.clicked_entry.get_id(), dlg.get_data(), password, key)
            self.show_table()

    def del_entry(self):
        self.db.del_key(self.clicked_entry.get_id())
        self.show_table()

    def table_context(self, point):
        menu = QMenu()
        actions = [self.entry_actions[3]]
        if self.table.itemAt(point):
            # Если попали на пароль то добавить возможность работать с паролем
            self.clicked_entry = self.table.itemAt(point)
            actions = self.entry_actions
        menu.addActions(actions)
        # Расположить выпадающее меню там где его вызвали
        menu.exec(self.table.mapToGlobal(point))

    def table_clicked(self, it):
        self.clicked_entry = it
        self.group_actions[1].setEnabled(False)  # Выключаем возможность удалить группу
        self.group_actions[2].setEnabled(False)  # Выключаем возможность изменить группу
        for el in self.entry_actions:
            el.setEnabled(True)  # Включаем возможности связанные с паролями

    def show_table(self):
        self.table.clear()  # Предварительно очищаем таблицу
        for el in self.db.get_keys(self.clicked_group_name):
            part = MyTreeWidgetItem(el[0], self.table)
            part.setText(0, el[1])
            part.setText(1, el[2])
            part.setText(2, decrypt_password(el[4], el[3]))
            part.setText(3, el[5])
            part.setText(4, el[6])
            self.table.addTopLevelItem(part)
        for i in range(5):
            self.table.resizeColumnToContents(i)

    def show_dir(self):
        self.tree_groups.clear()  # Очищаем таблицу с группами паролей
        for el in self.db.get_groups():
            part = QTreeWidgetItem(self.tree_groups)
            part.setText(0, el)
            self.tree_groups.addTopLevelItem(part)

    def set_status_menu_file(self, status):
        self.tree_groups.setEnabled(status)  # Таблица с группами
        self.table.setEnabled(status)  # Таблища с паролями
        self.file_actions[2].setEnabled(status)  # Кнопка отвечающая за закрытие файла
        self.file_actions[4].setEnabled(status)  # Кнопка отвечающая за изменение мастер ключа
        self.group_actions[0].setEnabled(status)  # Кнопка создания новой группы

    def del_resent_file(self, file_name):
        with open("resent_files.txt", encoding='utf-8') as file:
            data = [el.rstrip() for el in file.readlines()]
            file.close()
        with open("resent_files.txt", 'w', encoding='utf-8') as file:
            for el in data:
                if el != file_name:
                    print(el, file=file)
            file.close()
        self.set_resent_files()

    def add_resent_file(self, file_name):
        with open("resent_files.txt", encoding='utf-8') as file:
            data = [el.rstrip() for el in file.readlines()]
            if file_name not in data:
                data.insert(0, file_name)  # Добавляем файл в начало
                for i in range(1, len(data)):  # Ищем такойже файл и если находим то удаляем
                    if i >= len(data):
                        break
                    if data[i] == file_name:
                        data.pop(i)
                data = data[:10]  # Будем зранить максимум 10 новых записей
            file.close()
        with open("resent_files.txt", 'w', encoding='utf-8') as file:
            for el in data:
                print(el, file=file)
            file.close()
        self.set_resent_files()

    def user_guide(self):
        dlg = UserGuideDial(self)
        dlg.exec()

    def developer(self):
        dlg = DeveloperDial(self)
        dlg.exec()


class DataBase:
    def __init__(self, patch, create=True, master=None, salt=None):
        self.db = sqlite3.connect(patch)
        self.cur = self.db.cursor()
        self.cur.execute("PRAGMA foreign_keys = 'on';")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS master_key (
                            [key] TEXT,
                            salt  TEXT);""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS [groups] (
                            id    INTEGER PRIMARY KEY,
                            title TEXT);""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS passwords (
                            id        INTEGER PRIMARY KEY,
                            title     TEXT,
                            user_name TEXT,
                            password  TEXT,
                            [key]     TEXT,
                            URL       TEXT,
                            notes     TEXT,
                            group_id  INTEGER,
                            FOREIGN KEY (
                                group_id
                            )
                            REFERENCES [groups] (id));""")
        self.db.commit()
        if create:
            # Если мы создаем новую базу данных и нужно переписать ключ
            self.set_master(master, salt)

    def set_master(self, master, salt):
        # Удаляем старый мастер ключ и записываем новый
        self.cur.execute("DELETE FROM master_key;")
        self.cur.execute("INSERT INTO master_key VALUES (?, ?);", (master, salt))
        self.db.commit()

    def get_master(self):
        return self.cur.execute("SELECT * FROM master_key;").fetchall()[0]

    def add_group(self, name):
        self.cur.execute("INSERT INTO groups (title) VALUES (?);", (name,))
        self.db.commit()

    def get_groups(self):
        return [el[0] for el in self.cur.execute("SELECT title FROM groups;").fetchall()]

    def del_group(self, name):
        id_group = self.cur.execute("SELECT id FROM groups WHERE title = ?;", (name,)).fetchall()[0][0]
        self.cur.execute("DELETE FROM passwords WHERE group_id = ?;", (id_group,))
        self.cur.execute("DELETE FROM groups WHERE id = ?;", (id_group,))
        self.db.commit()

    def edit_group(self, last_name, new_name):
        self.cur.execute("UPDATE groups SET title = ? WHERE title = ?", (new_name, last_name))
        self.db.commit()

    def add_key(self, group_name, password, key, data):
        id_group = self.cur.execute("SELECT id FROM groups WHERE title = ?;", (group_name,)).fetchall()[0][0]
        self.cur.execute(
            "INSERT INTO passwords (title, user_name, URL, notes, group_id, password, key)  VALUES (?,?,?,?,?,?,?);",
            data + [id_group, password, key])
        self.db.commit()

    def get_key(self, id_password):
        return self.cur.execute("SELECT password, key, title, user_name, URL, notes FROM passwords WHERE id = ?;",
                                (id_password,)).fetchall()[0]

    def change_key(self, id_password, data, password, key):
        self.cur.execute(
            "UPDATE passwords SET title = ?, user_name = ?, URL = ?, notes = ?, password = ?, key = ? WHERE id = ?;",
            data + [password, key, id_password])
        self.db.commit()

    def get_keys(self, name):
        id_group = self.cur.execute("SELECT id FROM groups WHERE title = ?;", (name,)).fetchall()[0][0]
        return self.cur.execute(
            "SELECT id, title, user_name, password, key, URL, notes FROM passwords WHERE group_id = ?;",
            (id_group,)).fetchall()

    def del_key(self, id_password):
        self.cur.execute("DELETE FROM passwords WHERE id = ?;", (id_password,))
        self.db.commit()

    def clear(self):
        self.cur.execute("DELETE FROM groups;")
        self.cur.execute("DELETE FROM passwords;")
        self.db.commit()
