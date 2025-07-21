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
            
        # Обновляем состояние с новыми данными
        self.state.update_state(settings)
        
        # Ищем возможные слова с учетом ВСЕХ накопленных данных
        self.state.possible_words = find_words_with_letters(
            known_positions=self.state.known_positions,
            unused_letters=self.state.unused_letters,
            used_letters=self.state.used_letters,
            excluded_positions=self.state.excluded_positions
        )
        
        if not self.state.possible_words:
            QMessageBox.information(None, "Результат", "Нет подходящих слов!")
            self.run_iteration()
            return
            
        if self.result_window:
            self.result_window.close()
            
        self.result_window = ResultWindow(
            self.state.possible_words,
            self.run_iteration,
            self.app.quit
        )
        self.result_window.show()