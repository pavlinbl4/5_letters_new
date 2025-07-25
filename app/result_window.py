from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QPushButton,
    QHBoxLayout, QLabel, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt

class ResultWindow(QWidget):
    def __init__(self, words, continue_callback, quit_callback, all_used_words):
        super().__init__()
        self.continue_callback = continue_callback
        self.quit_callback = quit_callback
        self.selected_word = None
        self.setWindowTitle("Результаты поиска")
        self.setFixedSize(600, 500)

        # Фильтруем слова, исключая уже использованные
        self.words = [word for word in words if word not in all_used_words]
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Найденные возможные слова (выберите одно):")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.table_widget = QTableWidget(len(self.words), 2, self)
        self.table_widget.setHorizontalHeaderLabels(["Выбрать", "Слово"])
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setStyleSheet("font-size: 16px;")
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)

        for row, word in enumerate(self.words):
            item = QTableWidgetItem()
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Unchecked)
            self.table_widget.setItem(row, 0, item)
            self.table_widget.setItem(row, 1, QTableWidgetItem(word))

        layout.addWidget(self.table_widget)

        button_layout = QHBoxLayout()

        continue_btn = QPushButton("Продолжить")
        continue_btn.setStyleSheet("font-size: 16px; padding: 10px;")
        continue_btn.clicked.connect(self.continue_game)
        button_layout.addWidget(continue_btn)

        quit_btn = QPushButton("Закончить")
        quit_btn.setStyleSheet("font-size: 16px; padding: 10px; background-color: #f44336; color: white;")
        quit_btn.clicked.connect(self.quit_game)
        button_layout.addWidget(quit_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def continue_game(self):
        for row in range(self.table_widget.rowCount()):
            if self.table_widget.item(row, 0).checkState() == Qt.Checked:
                self.selected_word = self.table_widget.item(row, 1).text()
                break

        self.close()
        self.continue_callback(self.selected_word)

    def quit_game(self):
        self.close()
        self.quit_callback()