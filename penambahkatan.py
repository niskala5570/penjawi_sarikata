import csv
import os
import json

SETTINGS_FILE = 'tetapan_penambah.json'


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


def check_duplicates(data, new_rumi, new_jawi):
    duplicates = []
    for row in data:
        if row['rumi'] == new_rumi:
            duplicates.append(('rumi', new_rumi))
        if row['jawi'] == new_jawi:
            duplicates.append(('jawi', new_jawi))
    return duplicates


def add_data(data):
    new_data = data.copy()
    added_data = []
    rumi_list = []
    jawi_list = []
    
    while True:
        new_rumi = input('Masukkan katan Rumi baharu (taip "j" / "jawi" kalau sudah selesai): ')
        if new_rumi.lower() == 'j' or new_rumi.lower() == 'jawi':
            break
        rumi_list.append(new_rumi)
    
    for rumi in rumi_list:
        new_jawi = input(f'Masukkan katan Jawi untuk [{rumi}]: ')
        jawi_list.append(new_jawi)
    
    for rumi, jawi in zip(rumi_list, jawi_list):
        duplicates = check_duplicates(new_data, rumi, jawi)
        if duplicates:
            print('Alamak, ada katan yang sama:')
            for field, value in duplicates:
                print(f'{field}: {value}')
            choice = input('Batalkan perkataan ini? (y/n): ')
            if choice.lower() != 'y':
                continue
        new_row = {'rumi': rumi, 'jawi': jawi}
        new_data.append(new_row)
        added_data.append(new_row)
            
    return new_data, added_data


def sort_data(data):
    return sorted(data, key=lambda row: row['rumi'].lower())


def save_settings(file_location):
    settings = {'laluan_terakhir_fail': file_location}
    with open(SETTINGS_FILE, 'w') as settings_file:
        json.dump(settings, settings_file)


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as settings_file:
            settings = json.load(settings_file)
            return settings.get('laluan_terakhir_fail', '')
    return ''


def main():
    use_last_settings = input('Adakah anda ingin menggunakan tetapan terakhir? (y/n): ')
    if use_last_settings.lower() == 'y':
        file_location = load_settings()
    else:
        file_location = input('Masukkan laluan fail: ')

    if not os.path.isfile(file_location):
        print('Laluan fail tidak sah. Sila cuba lagi. (Jangan letak \"\")')
        return

    output_file_path = os.path.join(os.path.dirname(file_location), '[Diubah]' + os.path.basename(file_location))

    data = read_tsv_file(file_location)
    num_lines = len(data)
    print(f'Jumlah baris dalam fail TSV: {num_lines}')

    new_data, added_data = add_data(data)

    print(f'Katan baharu yang dimasukkan ({len(added_data)} perkataan):')
    for row in added_data:
        print(f'rumi: {row["rumi"]}, jawi: {row["jawi"]}')

    result_data_count = num_lines + len(added_data)
    print(f'Jumlah katan: {num_lines} + {len(added_data)} = {result_data_count}')

    choice = input('Adakah anda ingin menyusun semula data mengikut alfabet? (y/n): ')
    if choice.lower() == 'y':
        new_data = sort_data(new_data)

    write_tsv_file(output_file_path, new_data)
    print(f'Fail TSV dengan katan baru telah disimpan di: {output_file_path}')

    save_settings(file_location)


if __name__ == '__main__':
    main()
