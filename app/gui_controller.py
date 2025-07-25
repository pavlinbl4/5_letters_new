from PyQt5.QtWidgets import QApplication, QMessageBox
from .state_manager import GameState
from .word_input_window import get_letter_settings
from .result_window import ResultWindow
from .word_finder import find_words_with_letters


class GUIController:
    def __init__(self, app):
        self.state = GameState()
        self.app = app
        self.result_window = None
        self.pre_selected_word = None

    def start(self):
        self.run_iteration()

    def run_iteration(self, selected_word=None):
        self.pre_selected_word = selected_word

        settings = get_letter_settings(self.app, selected_word)
        if not settings:
            self.app.quit()
            return

        # Добавляем текущее слово в настройки
        if selected_word:
            settings['current_word'] = selected_word
        elif 'word' in settings:
            settings['current_word'] = settings['word']

        # Обновляем состояние с новыми данными
        self.state.update_state(settings)

        # Ищем возможные слова
        self.state.possible_words = find_words_with_letters(
            known_positions=self.state.known_positions,
            unused_letters=self.state.unused_letters,
            used_letters=self.state.used_letters,
            excluded_positions=self.state.excluded_positions,
            all_used_words=self.state.all_used_words
        )

        if not self.state.possible_words:
            QMessageBox.information(None, "Результат", "Нет подходящих слов!")
            self.run_iteration()
            return

        # Закрываем предыдущее окно результатов, если оно было
        if self.result_window:
            self.result_window.close()

        # Создаем и показываем новое окно результатов
        self.result_window = ResultWindow(
            self.state.possible_words,
            self.run_iteration,
            self.app.quit,
            self.state.all_used_words
        )
        self.result_window.show()