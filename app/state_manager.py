from loguru import logger

class GameState:
    def __init__(self):
        self.known_positions = {}      # Позиция → буква
        self.unused_letters = set()    # Буквы, которых нет в слове (множество)
        self.used_letters = set()      # Буквы, которые есть в слове (множество)
        self.excluded_positions = {}   # Буква → множество позиций, где ее быть не может
        self.possible_words = []

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
                logger.debug(f"Добавлена новая известная позиция: позиция {pos} - буква '{letter}'")

        # Обновляем множества букв
        new_used = set(new_data.get('used_letters', []))
        added_used = new_used - self.used_letters
        if added_used:
            logger.debug(f"Добавлены новые используемые буквы: {', '.join(added_used)}")
        self.used_letters |= new_used

        # Обновляем исключенные позиции
        for letter, positions in new_data.get('excluded_positions', {}).items():
            new_positions = set(positions)
            if letter in self.excluded_positions:
                added_positions = new_positions - self.excluded_positions[letter]
                if added_positions:
                    logger.debug(f"Добавлены новые исключенные позиции для '{letter}': {', '.join(map(str, added_positions))}")
                self.excluded_positions[letter] |= new_positions
            else:
                self.excluded_positions[letter] = new_positions
                if new_positions:
                    logger.debug(f"Добавлена буква с исключенными позициями: '{letter}' - позиции {', '.join(map(str, new_positions))}")

        # Обновляем неиспользуемые буквы
        new_unused = set(new_data.get('unused_letters', []))
        added_unused = new_unused - self.unused_letters
        if added_unused:
            logger.debug(f"Добавлены новые неиспользуемые буквы: {', '.join(added_unused)}")
        self.unused_letters |= new_unused

        # Удаляем конфликтующие буквы
        self.unused_letters -= self.used_letters

        # Удаляем буквы, позиции которых известны
        self.unused_letters -= set(self.known_positions.values())

        # Логируем итоговое состояние
        logger.info("Текущее состояние игры:")
        logger.info(f"Известные позиции: {self.known_positions}")
        logger.info(f"Используемые буквы: {', '.join(self.used_letters) if self.used_letters else 'нет'}")

        # Форматируем исключенные позиции для логов
        excluded_log = []
        for letter, positions in self.excluded_positions.items():
            if positions:
                pos_str = ', '.join(map(str, sorted(positions)))
                excluded_log.append(f"'{letter}': [{pos_str}]")
        logger.info(f"Исключенные позиции: {', '.join(excluded_log) if excluded_log else 'нет'}")

        logger.info(f"Неиспользуемые буквы: {', '.join(self.unused_letters) if self.unused_letters else 'нет'}")