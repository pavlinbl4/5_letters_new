from pathlib import Path
import os
import sys

# Получаем абсолютный путь к модулю
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from other_tools.nouns_from_csv import read_column

# Получаем абсолютный путь к файлу словаря
csv_path = os.path.join(parent_dir, 'data', 'nouns_5.csv')
dictionary = read_column(csv_path)

def find_words_with_letters(known_positions, unused_letters, used_letters, excluded_positions):
    possible_words = []
    
    for word in dictionary:
        if not is_word_valid(
            word, 
            known_positions, 
            unused_letters, 
            used_letters, 
            excluded_positions
        ):
            continue
        possible_words.append(word)
    
    return possible_words

def is_word_valid(
    word, 
    known_positions, 
    unused_letters, 
    used_letters, 
    excluded_positions
):
    # Проверка 1: Известные позиции букв
    for pos, letter in known_positions.items():
        if word[pos] != letter:
            return False
    
    # Проверка 2: Буквы, которых не должно быть в слове
    for letter in unused_letters:
        if letter in word:
            # Проверяем, не указана ли буква как исключенная только на некоторых позициях
            if letter in excluded_positions:
                # Буква есть в исключенных позициях, значит она может быть в слове на других позициях
                continue
            return False
    
    # Проверка 3: Буквы, которые должны быть в слове
    for letter in used_letters:
        if letter not in word:
            return False
    
    # Проверка 4: Исключенные позиции для букв
    for letter, positions in excluded_positions.items():
        if letter not in word:
            continue  # Буквы нет в слове - проверка не нужна
            
        for pos in positions:
            if 0 <= pos < len(word) and word[pos] == letter:
                return False
    
    # Проверка 5: Буквы с исключенными позициями, но без указания, что они есть в слове
    for letter, positions in excluded_positions.items():
        if letter not in used_letters and letter in word:
            # Проверяем, не находится ли буква на исключенной позиции
            for pos in positions:
                if 0 <= pos < len(word) and word[pos] == letter:
                    return False
    
    return True