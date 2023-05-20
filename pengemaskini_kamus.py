import os
import requests
import hashlib

def calculate_md5(file_path):
    with open(file_path, 'rb') as file:
        data = file.read()
        return hashlib.md5(data).hexdigest()

def download_file(url, destination):
    response = requests.get(url)
    if response.status_code == 200:
        with open(destination, 'wb') as file:
            file.write(response.content)
            print(f"Dimuat turun: {destination}")
    else:
        print(f"Gagal memuat turun: {url}")

def update_files():
    base_url = "https://github.com/niskala5570/sari_kata-rumikejawi/raw/main/Kamus/"
    kamus_folder = "Kamus"

    # Buat folder "Kamus" kalau tiada
    if not os.path.exists(kamus_folder):
        os.makedirs(kamus_folder)

    # Dapatkan senarai fail yang sudahpun ada dalam folder Kamus
    existing_files = os.listdir(kamus_folder)

    # Muat turun / kemas kini dari simpanan Github
    file_list_url = "https://api.github.com/repos/niskala5570/sari_kata-rumikejawi/contents/Kamus"
    response = requests.get(file_list_url)
    if response.status_code == 200:
        file_list = response.json()
        for file_info in file_list:
            if file_info['type'] == 'file' and file_info['name'].endswith('.tsv'):
                file_name = file_info['name']
                file_url = base_url + file_name
                file_destination = os.path.join(kamus_folder, file_name)

                # Periksa kalau fail sudahpun tersedia di dalam folder "Kamus"
                if file_name in existing_files:
                    existing_file_path = os.path.join(kamus_folder, file_name)
                    existing_file_md5 = calculate_md5(existing_file_path)

                    # Dapatkan cincangan(hash) MD5 dari Github
                    response = requests.get(file_info['download_url'])
                    if response.status_code == 200:
                        github_file_md5 = hashlib.md5(response.content).hexdigest()

                        # Bandingkan cincangan(hash) MD5
                        if existing_file_md5 == github_file_md5:
                            print(f"Fail dilangkau: {file_name} sudahpun yang terkini.")
                            continue

                    # Nama semula fail lama
                    new_file_name = os.path.join(kamus_folder, f"[Lama] {file_name}")
                    os.rename(existing_file_path, new_file_name)
                    print(f"Dinamakan semula: {file_name} -> {new_file_name}")

                download_file(file_url, file_destination)
    else:
        print("Gagal mendapatkan senarai fail di dalam simpanan Github.")

update_files()
