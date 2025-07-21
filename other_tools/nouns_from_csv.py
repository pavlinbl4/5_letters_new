import csv


def write_5_letter_nouns(nouns_set: set):
    with open('/Users/evgeniy/_Python/word_guesser/data/nouns_5.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for noun in nouns_set:
            writer.writerow([noun])


def read_column(csv_file):
    # Открываем файл для чтения
    with open(csv_file, mode='r', newline='') as file:
        csv_reader = csv.reader(file, delimiter='\t')
        return [row[0] for row in csv_reader]


def left_only_5_letters(nouns_dist):
    return [noun for noun in nouns_dist if len(noun) == 5]


def five_letter_nouns(csv_file):
    # считываю колонку с существительными на русском
    all_nouns = read_column(csv_file)
    # беру леммы от существительных и помещаю их в коллекцию
    # return lemmatize_words_list(all_nouns)
    return left_only_5_letters(all_nouns)


if __name__ == '__main__':
    # print(len(read_column('nouns.csv')))
    # print(len(five_letter_nouns('nouns.csv')))
    # print(five_letter_nouns('nouns.csv'))
    # write_5_letter_nouns(five_letter_nouns('nouns_5.csv'))

    print(read_column('../data/nouns_5.csv')[:5])
