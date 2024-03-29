# Kod ni kebanyakkannya ditulis dengan ChatGPT sebab aku malas dan tak reti.
# Jadi aku camtum2 macam lego, kalau nampak cacat dan rajin nak tolong kemaskan, dipersilakan.
# Aku buat kod ni sebab nak percepatkan kerja sahaja, takdelah aku perlu tulis balik Jawi dari awal.
# Untuk perkataan bersengkang, kena buat masukan kamus baru sebab kod tak akan pisahkan(tokenize) Contohnya "Kazuki-kun"
# Ini supaya perkataan berganda seperti "apa-apa, اڤ٢" dapat dialih dengan sempurna

import pysubs2
import os
import re

folder_masuk = "Masuk"
folder_keluar = "Keluar"
folder_kamus = "Kamus"
gaya_dikecualikan = ["Lagu", "EDR", "OPR"] #Ulasan telah dikecualikan secara lalai

def muatKamus(file_path):
  data = {}
  with open(file_path) as file:
      lines = file.readlines()
      for line in lines:
          columns = line.strip().split("\t")
          if len(columns) >= 2:
              rumi, jawi = columns[:2]  # Use the first two columns
              rumi = rumi.lower()
              if rumi in data:
                  data[rumi].append(jawi)
              else:
                  data[rumi] = [jawi]
          else:
              print(f"Ignoring invalid line: {line}")
  
  return data

def alihKata(padanan, translations, chosen_translations, context):
    katan = padanan.group(0)
    if katan.lower() in translations:
        translations_list = translations[katan.lower()]
        if len(translations_list) > 1:
            if katan not in chosen_translations:
                print(f"Terdapat ketaksaan untuk perkataan '{katan}' dari '{context}':")
                for i, translation in enumerate(translations_list):
                    print(f"{i + 1}. {translation}")
                choice = input("Masukkan nilai: ")
                while not choice.isdigit() or int(choice) < 1 or int(choice) > len(translations_list):
                    choice = input("Nilai tidak sah, masukkan nilai semula: ")
                chosen_translation = translations_list[int(choice) - 1]
                chosen_translations[katan] = chosen_translation
            else:
                chosen_translation = chosen_translations[katan]
            return chosen_translation
        else:
            return translations_list[0]
    return katan

def alihAyat(ayat, translations, padanan_tanda, chosen_translations):
    def gantikan_tanda(padanan):
        tanda = padanan.group(0)
        if tanda in padanan_tanda:
            return padanan_tanda[tanda]
        return tanda

    ayat_diterjemah = re.sub(r'(?<!\\)(\\[Nnh])', r' {\1} ', ayat)

    ayat_diterjemah = re.sub(r'(?<!{){[^}]+}|[A-Za-z\-]+', lambda padanan: alihKata(padanan, translations, chosen_translations, ayat), ayat_diterjemah)
    ayat_diterjemah = re.sub(r'[?,;,.]', gantikan_tanda, ayat_diterjemah)

    ayat_diterjemah = ayat_diterjemah.replace('{\\N}', '\\N').replace('{\\n}', '\\n').replace('{\\h}', '\\h')

    return ayat_diterjemah

def baikiEjaan(teks):
    # Cari dan ganti 'د ' dan 'ک ' yang berjarak untuk membetulkan perkataan cthnya 'د سکوله'
    teks = re.sub(r'\bد\s', 'د', teks)
    teks = re.sub(r'\bک\s', 'ک', teks)

    return teks

def alihKata_Sarikata(file_path, translations, padanan_tanda, padanan_tanggaman_akhiran, padanan_tanggaman_awalan):
    sarikata = pysubs2.load(file_path)
    tidak_teralih = []
    chosen_translations = {}  # Dictionary to store chosen translations
    extracted_content = {}  # Dictionary to store extracted content within {}

    for i, dialog in enumerate(sarikata.events):
        if dialog.is_comment or dialog.style in gaya_dikecualikan:
            continue

        teks_dialog = dialog.text

        extracted = re.findall(r'{(.*?)}', teks_dialog)
        for extract in extracted:
            placeholder = f'__{len(extracted_content)}__'
            extracted_content[placeholder] = '{' + extract + '}'
            teks_dialog = teks_dialog.replace('{' + extract + '}', placeholder)

        dialog_terjemah = baikiEjaan(alihAyat(teks_dialog, translations, padanan_tanda, chosen_translations))
        dialog_terjemah = "{\\fe-1}" + dialog_terjemah

        for placeholder, content in extracted_content.items():
            dialog_terjemah = dialog_terjemah.replace(placeholder, content)

        dialog.text = dialog_terjemah

        katan_rumi_jawi = re.findall(r'(?<!{)(?<!\\)(?:\\\\)*(?<!\\[Nnh])\b[A-Za-z\-]+(?<!\\)(?!})(?<!\\[Nnh])', teks_dialog)
        for katan in katan_rumi_jawi:
            if katan.lower() not in translations and not re.search(r'(?<!\\){[^}]+}', teks_dialog):
                katan_terjemah = alihKata(re.search(katan, teks_dialog), translations, chosen_translations, teks_dialog)
                if katan_terjemah == katan:
                    for tanggaman_akhiran in padanan_tanggaman_akhiran:
                        if katan.lower().endswith(tanggaman_akhiran):
                            katan_terjemah = alihKata(re.search(katan[:-len(tanggaman_akhiran)], teks_dialog), translations, chosen_translations, teks_dialog) + padanan_tanggaman_akhiran[tanggaman_akhiran]
                            break
                if katan_terjemah == katan:
                    for tanggaman_awalan in padanan_tanggaman_awalan:
                        if katan.lower().startswith(tanggaman_awalan):
                            katan_terjemah = padanan_tanggaman_awalan[tanggaman_awalan] + alihKata(re.search(katan[len(tanggaman_awalan):], teks_dialog), translations, chosen_translations, teks_dialog)
                            break
                if katan_terjemah != katan:
                    dialog_terjemah = dialog_terjemah.replace(katan, katan_terjemah)
                else:
                    tidak_teralih.append((i, katan))  # Store the index and untranslated word

        sarikata.events[i].text = dialog_terjemah

    laluan_sarikata = os.path.join(folder_keluar, "[Dialih Kata]" + os.path.basename(file_path))
    sarikata.save(laluan_sarikata)

    return len(tidak_teralih), tidak_teralih

katan_kamus = {}

for file in os.listdir(folder_kamus):
    if file.endswith(".tsv"):
        file_path = os.path.join(folder_kamus, file)
        katan_kamus = {**katan_kamus, **muatKamus(file_path)}

padanan_tanda = {"?": "؟", ";": "⁏", ",": "⹁", ".": "."}
padanan_tanggaman_akhiran = {"lah": "له", "kah": "که", "kan": "کن", "i": "ي", "ku": "کو", "mu": "مو", "nya": "ڽ"}
padanan_tanggaman_awalan = {"ber": "بر", "mem": "مم", "meng": "مڠ", "se": "س", "tak": "تق", "per": "ڤر"}

select_translation = True

files_untranslated = {}

for fail in os.listdir(folder_masuk):
    if fail.endswith((".ass", ".ssa", ".srt")):
        print(f"Mengalih kata: {fail}\n---")
        laluan_fail = os.path.join(folder_masuk, fail)
        if select_translation:
            tidak_teralih_count, tidak_teralih = alihKata_Sarikata(laluan_fail, katan_kamus, padanan_tanda, padanan_tanggaman_akhiran, padanan_tanggaman_awalan)
        else:
            tidak_teralih_count, tidak_teralih = 0, []
        if tidak_teralih_count > 0:
            files_untranslated[fail] = tidak_teralih

for fail, tidak_teralih in files_untranslated.items():
    print(f"Perkataan yang tidak teralih dalam \"{fail}\":")
    dialog_lines = {}
    for dialog_index, dialog_word in tidak_teralih:
        if dialog_index + 1 in dialog_lines:
            dialog_lines[dialog_index + 1].append(dialog_word)
        else:
            dialog_lines[dialog_index + 1] = [dialog_word]
    for line_num, dialog_words in dialog_lines.items():
        print(f"Baris {line_num}: {dialog_words}")
    print()

print(
    "Pengalih tulisan ini tidaklah sempurna, sentuhan manusia tetap juga diperlukan."
)
