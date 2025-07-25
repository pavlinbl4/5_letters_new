from loguru import logger

class GameState:
    def __init__(self):
        self.known_positions = {}      # Позиция → буква
        self.unused_letters = set()    # Буквы, которых нет в слове (множество)
        self.used_letters = set()      # Буквы, которые есть в слове (множество)
        self.excluded_positions = {}   # Буква → множество позиций, где ее быть не может
        self.possible_words = []
        self.all_used_words = set()  # Добавляем множество для хранения использованных слов

    def update_state(self, new_data):
        # Логируем входящие данные
        logger.info("Получены новые данные для обновления состояния:")
        logger.info(f"Известные позиции: {new_data.get('known_positions', {})}")
        logger.info(f"Используемые буквы: {new_data.get('used_letters', [])}")
        logger.info(f"Исключенные позиции: {new_data.get('excluded_positions', {})}")
        logger.info(f"Неиспользуемые буквы: {new_data.get('unused_letters', [])}")

        # Обновляем известные позиции
        for pos, letter in new_data.get('known_positions', {}).items():
            # Добавляем только новые позиции, не перезаписываем существующие
            if pos not in self.known_positions:
                self.known_positions[pos] = letter

        # Обновляем множества букв
        self.used_letters |= set(new_data.get('used_letters', []))

        # Обновляем исключенные позиции
        for letter, positions in new_data.get('excluded_positions', {}).items():
            if letter in self.excluded_positions:
                self.excluded_positions[letter] |= set(positions)
            else:
                self.excluded_positions[letter] = set(positions)

        # Обновляем неиспользуемые буквы
        new_unused = set(new_data.get('unused_letters', []))

        # Удаляем из новых неиспользуемых букв те, которые уже используются
        new_unused -= self.used_letters
        new_unused -= set(self.known_positions.values())

        # Добавляем новые неиспользуемые буквы к общему набору
        self.unused_letters |= new_unused

        # Добавляем текущее слово в использованные
        current_word = new_data.get('current_word', '')
        if current_word:
            self.all_used_words.add(current_word)