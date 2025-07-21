import sys
import re
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QCheckBox,
    QVBoxLayout, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QHBoxLayout, QHeaderView
)
from loguru import logger


class WordInputDialog(QDialog):
    def __init__(self, pre_selected_word=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Введите слово")
        self.setFixedSize(500, 300)
        self.word = None
        self.pre_selected_word = pre_selected_word
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("Введите слово (ровно 5 букв):")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 18px;")
        layout.addWidget(self.label)

        self.word_input = QLineEdit(self)
        self.word_input.setAlignment(Qt.AlignCenter)
        self.word_input.setStyleSheet("font-size: 16px;")

        if self.pre_selected_word:
            self.word_input.setText(self.pre_selected_word)

        layout.addWidget(self.word_input)

        self.submit_button = QPushButton("Подтвердить", self)
        self.submit_button.setStyleSheet("font-size: 16px;")
        self.submit_button.clicked.connect(self.submit_word)
        layout.addWidget(self.submit_button)

        self.reset_button = QPushButton("Сброс", self)
        self.reset_button.setStyleSheet("font-size: 16px;")
        self.reset_button.clicked.connect(self.reset_input)
        layout.addWidget(self.reset_button)

        self.setLayout(layout)

    def submit_word(self):
        word = self.word_input.text().strip()
        if len(word) != 5:
            QMessageBox.critical(self, "Ошибка", "Слово должно состоять ровно из 5 букв!")
        else:
            self.word = word
            logger.debug(f"word: {self.word}")
            self.accept()

    def reset_input(self):
        self.word_input.clear()


class LetterSelectionDialog(QDialog):
    def __init__(self, word, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка букв")
        self.setFixedSize(800, 500)
        self.word = word
        self.yes_set = set()
        self.no_list = []
        self.result_dict = {}
        self.excluded_positions = {}

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.table = QTableWidget(len(self.word), 5, self)
        self.table.setHorizontalHeaderLabels([
            "Буква",
            "Позиция (1-5)",
            "Есть в слове",
            "Не на позиции",
            "Не в слове"
        ])

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.table.setStyleSheet("font-size: 16px;")

        for row, letter in enumerate(self.word):
            # Колонка 0: Буква
            self.table.setItem(row, 0, QTableWidgetItem(letter))

            # Колонка 1: Выбор позиции (1-5)
            number_combobox = QComboBox()
            number_combobox.addItems([str(i) for i in range(6)])
            number_combobox.setStyleSheet("font-size: 16px;")
            number_combobox.currentTextChanged.connect(lambda value, r=row: self.update_position(r, value))
            self.table.setCellWidget(row, 1, number_combobox)

            # Колонка 2: Есть в слове (чекбокс)
            in_word_checkbox = QCheckBox()
            in_word_checkbox.setStyleSheet("font-size: 16px;")
            in_word_checkbox.stateChanged.connect(lambda state, r=row: self.update_in_word(r, state))
            self.table.setCellWidget(row, 2, in_word_checkbox)

            # Колонка 3: Не на позиции (поле ввода)
            exclude_edit = QLineEdit()
            exclude_edit.setPlaceholderText("Через запятую")
            exclude_edit.setStyleSheet("font-size: 16px;")
            exclude_edit.textChanged.connect(lambda text, r=row: self.update_excluded_positions(r, text))
            self.table.setCellWidget(row, 3, exclude_edit)

            # Колонка 4: Не в слове (чекбокс) - ПО УМОЛЧАНИЮ ВКЛЮЧЕН
            not_in_word_checkbox = QCheckBox()
            not_in_word_checkbox.setStyleSheet("font-size: 16px;")
            not_in_word_checkbox.setChecked(True)  # ПО УМОЛЧАНИЮ ВКЛЮЧЕН
            not_in_word_checkbox.stateChanged.connect(lambda state, r=row: self.update_not_in_word(r, state))
            self.table.setCellWidget(row, 4, not_in_word_checkbox)

            self.excluded_positions[letter] = set()
            self.no_list.append(letter)

        layout.addWidget(self.table)

        button_layout = QHBoxLayout()

        self.submit_button = QPushButton("Подтвердить", self)
        self.submit_button.setStyleSheet("font-size: 16px;")
        self.submit_button.clicked.connect(self.accept)
        button_layout.addWidget(self.submit_button)

        self.reset_button = QPushButton("Сброс", self)
        self.reset_button.setStyleSheet("font-size: 16px;")
        self.reset_button.clicked.connect(self.reset_choices)
        button_layout.addWidget(self.reset_button)

        self.cancel_button = QPushButton("Отмена", self)
        self.cancel_button.setStyleSheet("font-size: 16px;")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def update_position(self, row, value):
        letter = self.word[row]
        logger.debug(f"letter: {letter}")
        number = int(value)
        logger.debug(f"number: {number}")

        # Получаем элементы управления для строки
        in_word_checkbox = self.table.cellWidget(row, 2)
        not_in_checkbox = self.table.cellWidget(row, 4)
        exclude_edit = self.table.cellWidget(row, 3)

        # Сбрасываем исключенные позиции при изменении основной позиции
        exclude_edit.clear()
        self.excluded_positions[letter] = set()

        if number > 0:
            # Устанавливаем известную позицию ТОЛЬКО если она еще не известна
            if (number - 1) not in self.result_dict:
                self.result_dict[number - 1] = letter

            # Автоматически включаем "Есть в слове"
            in_word_checkbox.setChecked(True)
            in_word_checkbox.setEnabled(False)

            # Автоматически выключаем "Не в слове"
            not_in_checkbox.setChecked(False)

            # Убираем букву из списка "не в слове"
            if letter in self.no_list:
                self.no_list.remove(letter)
        else:
            # Сбрасываем позицию только если она была установлена в текущей сессии
            for key, val in list(self.result_dict.items()):
                if val == letter:
                    del self.result_dict[key]

            in_word_checkbox.setEnabled(True)

            if not in_word_checkbox.isChecked():
                not_in_checkbox.setChecked(True)

    def update_in_word(self, row, state):
        letter = self.word[row]
        logger.debug(f"letter: {letter}")
        not_in_checkbox = self.table.cellWidget(row, 4)
        number_combobox = self.table.cellWidget(row, 1)

        # Если установлен чекбокс "Есть в слове"
        if state == Qt.Checked:
            # Выключаем "Не в слове"
            not_in_checkbox.setChecked(False)

            # Убираем букву из списка "не в слове"
            if letter in self.no_list:
                self.no_list.remove(letter)
            self.yes_set.add(letter)
        else:
            # Убираем букву из множества "есть в слове"
            if letter in self.yes_set:
                self.yes_set.remove(letter)

            # Если позиция не указана, включаем "Не в слове"
            if number_combobox.currentText() == "0":
                not_in_checkbox.setChecked(True)

    def update_excluded_positions(self, row, text):
        letter = self.word[row]
        excluded = set()

        if text.strip():
            try:
                positions = [int(pos.strip()) - 1 for pos in text.split(",")
                             if pos.strip().isdigit() and 1 <= int(pos.strip()) <= 5]
                excluded = set(positions)
            except:
                pass

        self.excluded_positions[letter] = excluded

    def update_not_in_word(self, row, state):
        letter = self.word[row]
        in_word_checkbox = self.table.cellWidget(row, 2)
        number_combobox = self.table.cellWidget(row, 1)
        exclude_edit = self.table.cellWidget(row, 3)

        # Если установлен чекбокс "Не в слове"
        if state == Qt.Checked:
            # Выключаем "Есть в слове"
            in_word_checkbox.setChecked(False)

            # Сбрасываем позицию
            number_combobox.setCurrentText("0")

            # Очищаем исключенные позиции
            exclude_edit.clear()
            self.excluded_positions[letter] = set()

            # Добавляем в список "не в слове"
            if letter not in self.no_list:
                self.no_list.append(letter)

            # Убираем из "есть в слове"
            if letter in self.yes_set:
                self.yes_set.remove(letter)
        else:
            # Убираем букву из списка "не в слове"
            if letter in self.no_list:
                self.no_list.remove(letter)

    def get_results(self):
        return {
            'known_positions': self.result_dict,
            'used_letters': list(self.yes_set),
            'excluded_positions': self.excluded_positions,
            'unused_letters': self.no_list
        }

    def reset_choices(self):
        self.yes_set.clear()
        self.no_list.clear()
        self.result_dict.clear()
        self.excluded_positions = {letter: set() for letter in self.word}
        logger.debug(f'self.excluded_positions{self.excluded_positions}')


        for row in range(self.table.rowCount()):
            # Сбрасываем позицию
            self.table.cellWidget(row, 1).setCurrentText("0")

            # Сбрасываем чекбокс "Есть в слове"
            in_word_checkbox = self.table.cellWidget(row, 2)
            in_word_checkbox.setChecked(False)
            in_word_checkbox.setEnabled(True)

            # Сбрасываем поле исключенных позиций
            self.table.cellWidget(row, 3).clear()

            # Устанавливаем "Не в слове" по умолчанию
            not_in_checkbox = self.table.cellWidget(row, 4)
            not_in_checkbox.setChecked(True)

            # Добавляем букву в список "не в слове"
            letter = self.word[row]
            if letter not in self.no_list:
                self.no_list.append(letter)


def get_letter_settings(app, pre_selected_word=None):
    """Функция для вызова GUI и получения результатов."""
    # Диалог ввода слова
    word_dialog = WordInputDialog(pre_selected_word)
    if word_dialog.exec_() != QDialog.Accepted or not word_dialog.word:
        return None

    word = word_dialog.word
    # logger.info(f'Введенное слово: {word}')

    # Диалог настройки букв
    letter_dialog = LetterSelectionDialog(word)
    if letter_dialog.exec_() != QDialog.Accepted:
        return None

    return letter_dialog.get_results()