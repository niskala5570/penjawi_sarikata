import csv
import os
import json

SETTINGS_FILE = 'tetapan_pengubah.json'


def read_tsv_file(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8', newline='') as tsv_file:
        reader = csv.DictReader(tsv_file, delimiter='\t')
        for row in reader:
            data.append(row)
    return data


def write_tsv_file(file_path, data):
    with open(file_path, 'w', encoding='utf-8', newline='') as tsv_file:
        writer = csv.DictWriter(tsv_file, fieldnames=data[0].keys(), delimiter='\t')
        writer.writeheader()
        writer.writerows(data)


def find_matching_data(data, keyword):
    matching_data = []
    for row in data:
        if keyword.lower() in row['rumi'].lower() or keyword.lower() in row['jawi'].lower():
            matching_data.append(row)
    return matching_data


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as settings_file:
            return json.load(settings_file)
    return {}


def save_settings(file_location):
    settings = {'laluan_terakhir_fail': file_location}
    with open(SETTINGS_FILE, 'w') as settings_file:
        json.dump(settings, settings_file)


def edit_existing_data():
    settings = load_settings()
    last_edited_file = settings.get('laluan_terakhir_fail', '')
    use_last_edited_file = False

    if last_edited_file:
        choice = input(f'Adakah anda ingin menggunakan tetapan terakhir? (y/n): ')
        if choice.lower() == 'y':
            file_location = last_edited_file
            use_last_edited_file = True

    if not use_last_edited_file:
        file_location = input('Masukkan laluan fail: ')

        if not os.path.isfile(file_location):
            print('Laluan fail tidak sah. Sila cuba lagi.')
            return

    output_file_path = os.path.join(os.path.dirname(file_location), '[Diubah]' + os.path.basename(file_location))

    data = read_tsv_file(file_location)
    num_lines = len(data)
    print(f'Jumlah baris dalam fail TSV: {num_lines}')

    while True:
        keyword = input('Masukkan perkataan yang ingin disunting (atau "batal"/"b" untuk membatalkan): ')

        if keyword.lower() == 'batal' or keyword.lower() == 'b' or keyword.lower() == 'ب':
            break

        matching_data = find_matching_data(data, keyword)

        if not matching_data:
            print('Tiada katan yang ditemukan dengan perkataan yang diberikan.')
            continue

        selected_data = None

        if len(matching_data) == 1:
            print('Hanya satu katan sepadan dengan perkataan yang diberikan.')
            print(f'rumi: {matching_data[0]["rumi"]}, jawi: {matching_data[0]["jawi"]}')
            choice = input('Taip "batal" / "b" untuk membatalkan, atau tekan enter untuk teruskan: ')
            if choice.lower() == 'batal' or choice.lower() == 'b':
                continue
            selected_data = matching_data[0]

        else:
            print(f'{len(matching_data)} katan sepadan dengan perkataan yang diberikan:')
            for i, row in enumerate(matching_data):
                print(f'{i + 1}: rumi: {row["rumi"]}, jawi: {row["jawi"]}')

            choice = input('Masukkan nombor katan yang ingin diubah, atau "batal" / "b" untuk membatalkan: ')
            if choice.lower() == 'batal' or choice.lower() == 'b':
                continue

            try:
                index = int(choice) - 1
                selected_data = matching_data[index]
                print(f'Katan yang dipilih: rumi: {selected_data["rumi"]}, jawi: {selected_data["jawi"]}')
            except (ValueError, IndexError):
                print('Input tidak sah.')
                continue

        new_rumi = input('Masukkan data Rumi yang baru: ')
        new_jawi = input('Masukkan data Jawi yang baru: ')

        selected_data['rumi'] = new_rumi
        selected_data['jawi'] = new_jawi

        write_tsv_file(output_file_path, data)
        print(f'Fail TSV dengan katan yang telah diubah telah disimpan di: {output_file_path}')

        save_settings(file_location)  # Update the last edited file in the settings
        break


if __name__ == '__main__':
    edit_existing_data()
