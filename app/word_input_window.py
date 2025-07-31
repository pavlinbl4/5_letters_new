import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton,
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
        self.setFixedSize(600, 400)
        self.word = word
        self.no_list = []
        self.used_letters = set()
        self.result_dict = {}
        self.excluded_positions = {}

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Укажите статус каждой буквы:")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Создаем таблицу с 2 колонками
        self.table = QTableWidget(len(self.word), 2, self)
        self.table.setHorizontalHeaderLabels(["Буква", "Статус"])
        self.table.setStyleSheet("font-size: 16px;")

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)

        for row, letter in enumerate(self.word):
            # Колонка с буквой (с указанием текущей позиции)
            item_text = f"{letter} (поз. {row + 1})"
            item = QTableWidgetItem(item_text)
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.ItemIsEnabled)
            self.table.setItem(row, 0, item)

            # Колонка с выбором статуса
            status_combobox = QComboBox()
            status_combobox.addItems([
                "нет в слове",
                "есть в слове (не на этой позиции)",
                "точно на этой позиции"
            ])
            status_combobox.setStyleSheet("font-size: 16px;")
            status_combobox.currentTextChanged.connect(lambda value, r=row: self.update_status(r, value))
            self.table.setCellWidget(row, 1, status_combobox)

            self.excluded_positions[letter] = set()
            self.no_list.append(letter)  # По умолчанию все буквы "не в слове"

        layout.addWidget(self.table)

        # Кнопки управления
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

    def update_status(self, row, value):
        letter = self.word[row]
        current_position = row  # Текущая позиция буквы в слове (0-based)

        if value == "нет в слове":
            # Удаляем из известных позиций
            for key, val in list(self.result_dict.items()):
                if val == letter:
                    del self.result_dict[key]

            # Очищаем исключенные позиции
            self.excluded_positions[letter] = set()

            # Добавляем в список "не в слове"
            if letter not in self.no_list:
                self.no_list.append(letter)

            # Удаляем из используемых букв
            if letter in self.used_letters:
                self.used_letters.remove(letter)

        elif value == "есть в слове (не на этой позиции)":
            # Убираем из "не в слове"
            if letter in self.no_list:
                self.no_list.remove(letter)

            # Удаляем из известных позиций
            for key, val in list(self.result_dict.items()):
                if val == letter:
                    del self.result_dict[key]

            # Добавляем текущую позицию в исключенные
            self.excluded_positions[letter] = {current_position}

            # Добавляем в используемые буквы
            self.used_letters.add(letter)

        elif value == "точно на этой позиции":
            # Убираем из "не в слове"
            if letter in self.no_list:
                self.no_list.remove(letter)

            # Устанавливаем известную позицию
            self.result_dict[current_position] = letter

            # Очищаем исключенные позиции
            self.excluded_positions[letter] = set()

            # Добавляем в используемые буквы
            self.used_letters.add(letter)

    def get_results(self):
        results = {
            'known_positions': self.result_dict,
            'used_letters': list(self.used_letters),
            'excluded_positions': self.excluded_positions,
            'unused_letters': self.no_list,
            'word': self.word
        }

        logger.info("Настройки букв для слова: '{}'", self.word)
        logger.info("Известные позиции: {}", self.result_dict)
        logger.info("Используемые буквы: {}", list(self.used_letters))
        logger.info("Исключенные позиции: {}", self.excluded_positions)
        logger.info("Буквы не в слове: {}", self.no_list)

        return results

    def reset_choices(self):
        self.no_list.clear()
        self.used_letters.clear()
        self.result_dict.clear()
        self.excluded_positions = {letter: set() for letter in self.word}

        for row in range(self.table.rowCount()):
            # Сбрасываем статус на "нет в слове"
            self.table.cellWidget(row, 1).setCurrentText("нет в слове")

            # Добавляем букву в список "не в слове"
            letter = self.word[row]
            if letter not in self.no_list:
                self.no_list.append(letter)


def get_letter_settings(app, pre_selected_word=None):
    """Функция для вызова GUI и получения результатов."""
    word_dialog = WordInputDialog(pre_selected_word)
    if word_dialog.exec_() != QDialog.Accepted or not word_dialog.word:
        return None

    letter_dialog = LetterSelectionDialog(word_dialog.word)
    if letter_dialog.exec_() != QDialog.Accepted:
        return None

    return letter_dialog.get_results()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    result = get_letter_settings(app)
    print(result)
    sys.exit(app.exec_())