import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QCheckBox,
    QVBoxLayout, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QHBoxLayout, QHeaderView, QApplication
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

        # Заголовок с пояснением
        title = QLabel("Укажите статус каждой буквы:")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Создаем таблицу с 3 колонками
        self.table = QTableWidget(len(self.word), 3, self)
        self.table.setHorizontalHeaderLabels([
            "Буква",
            "Позиция",
            "Не на позиции"
        ])

        # Настройка внешнего вида таблицы
        self.table.setStyleSheet("font-size: 16px;")

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)


        # это таблица выбора букв
        for row, letter in enumerate(self.word):
            # Колонка с буквой
            item = QTableWidgetItem(letter)
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.ItemIsEnabled)
            self.table.setItem(row, 0, item)

            # Колонка 1: Выбор позиции (добавили "нет в слове" и "есть в слове")
            position_combobox = QComboBox()
            position_combobox.addItems(["нет в слове", "есть в слове", "1", "2", "3", "4", "5"])
            position_combobox.setStyleSheet("font-size: 16px;")
            position_combobox.currentTextChanged.connect(lambda value, r=row: self.update_position(r, value))
            self.table.setCellWidget(row, 1, position_combobox)

            # Колонка 2: Не на позиции (выпадающее меню)
            exclude_combobox = QComboBox()
            exclude_combobox.addItems(["0", "1", "2", "3", "4", "5"])
            exclude_combobox.setStyleSheet("font-size: 16px;")
            exclude_combobox.currentTextChanged.connect(lambda value, r=row: self.update_excluded_position(r, value))
            self.table.setCellWidget(row, 2, exclude_combobox)

            self.excluded_positions[letter] = set()
            self.no_list.append(letter)

        layout.addWidget(self.table)

        # кнопки внизу
        button_box = QHBoxLayout()

        btn_ok = QPushButton("Подтвердить")
        btn_ok.setStyleSheet("""
            QPushButton {
                font-size: 16px; 
                padding: 8px;
                min-width: 120px;
                background-color: #4CAF50;
                color: white;
            }
        """)
        btn_ok.clicked.connect(self.accept)

        btn_reset = QPushButton("Сбросить")
        btn_reset.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 8px;
                min-width: 120px;
            }
        """)
        btn_reset.clicked.connect(self.reset_choices)

        btn_cancel = QPushButton("Отмена")
        btn_cancel.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 8px;
                min-width: 120px;
                background-color: #f44336;
                color: white;
            }
        """)
        btn_cancel.clicked.connect(self.reject)

        button_box.addWidget(btn_ok)
        button_box.addWidget(btn_reset)
        button_box.addWidget(btn_cancel)
        layout.addLayout(button_box)

        self.setLayout(layout)

    def update_position(self, row, value):
        letter = self.word[row]
        logger.debug(f"letter: {letter}")

        # Получаем элементы управления для строки
        exclude_combobox = self.table.cellWidget(row, 2)

        if value == "нет в слове":
            # Сбрасываем позицию
            for key, val in list(self.result_dict.items()):
                if val == letter:
                    del self.result_dict[key]

            # Сбрасываем исключенные позиции
            exclude_combobox.setCurrentText("0")
            self.excluded_positions[letter] = set()

            # Добавляем в список "не в слове"
            if letter not in self.no_list:
                self.no_list.append(letter)

            # Убираем из "есть в слове"
            if letter in self.yes_set:
                self.yes_set.remove(letter)

        elif value == "есть в слове":
            # Убираем из "не в слове"
            if letter in self.no_list:
                self.no_list.remove(letter)

            # Добавляем в "есть в слове"
            self.yes_set.add(letter)

            # Сбрасываем известную позицию
            for key, val in list(self.result_dict.items()):
                if val == letter:
                    del self.result_dict[key]
        else:
            # Устанавливаем известную позицию
            number = int(value)
            self.result_dict[number - 1] = letter

            # Убираем из "не в слове"
            if letter in self.no_list:
                self.no_list.remove(letter)

            # Добавляем в "есть в слове"
            self.yes_set.add(letter)

            # Сбрасываем исключенные позиции
            exclude_combobox.setCurrentText("0")
            self.excluded_positions[letter] = set()

    def update_excluded_position(self, row, value):
        letter = self.word[row]
        position = int(value) - 1  # Преобразуем в 0-based индекс

        # Получаем элементы управления для строки
        position_combobox = self.table.cellWidget(row, 1)

        if position >= 0:  # Если выбрана реальная позиция (не 0)
            # Устанавливаем "есть в слове" в позиции
            position_combobox.setCurrentText("есть в слове")

            # Обновляем множество исключенных позиций
            self.excluded_positions[letter] = {position}

            # Убираем букву из списка "не в слове"
            if letter in self.no_list:
                self.no_list.remove(letter)

            # Добавляем в "есть в слове"
            self.yes_set.add(letter)
        else:
            # Если выбрано "0" - сбрасываем исключенные позиции
            self.excluded_positions[letter] = set()

    def get_results(self):
        results = {
            'known_positions': self.result_dict,
            'used_letters': list(self.yes_set),
            'excluded_positions': self.excluded_positions,
            'unused_letters': self.no_list,
            'word': self.word
        }

        # Логирование
        logger.info("Пользователь подтвердил настройки букв для слова: '{}'", self.word)
        logger.info("Известные позиции: {}", self.result_dict)
        logger.info("Буквы в слове: {}", list(self.yes_set))
        logger.info("Исключенные позиции: {}", self.excluded_positions)
        logger.info("Буквы не в слове: {}", self.no_list)

        return results

    def reset_choices(self):
        self.yes_set.clear()
        self.no_list.clear()
        self.result_dict.clear()
        self.excluded_positions = {letter: set() for letter in self.word}
        logger.debug(f'self.excluded_positions{self.excluded_positions}')

        for row in range(self.table.rowCount()):
            # Сбрасываем позицию на "нет в слове"
            self.table.cellWidget(row, 1).setCurrentText("нет в слове")

            # Сбрасываем поле исключенных позиций
            self.table.cellWidget(row, 2).setCurrentText("0")

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    result = get_letter_settings(app)
    print(result)
    sys.exit(app.exec_())