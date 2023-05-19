import pysubs2
import os
import re

folder_masuk = "Masuk"
folder_keluar = "Keluar"
folder_kamus = "Kamus"


def muat_katan(file_path):
    data = {}
    with open(file_path) as file:
        lines = file.readlines()
        for line in lines:
            rumi, jawi = line.strip().split("\t")
            rumi = rumi.lower()
            if rumi in data:
                data[rumi].append(jawi)
            else:
                data[rumi] = [jawi]
    return data


def alih_kata(padanan, translations):
    katan = padanan.group(0)
    if katan.lower() in translations:
        translations_list = translations[katan.lower()]
        return translations_list[0]
    return katan


def alih_ayat(ayat, translations, padanan_tanda):
    def gantikan_tanda(padanan):
        tanda = padanan.group(0)
        if tanda in padanan_tanda:
            return padanan_tanda[tanda]
        return tanda

    ayat_diterjemah = re.sub(r'(?<!\\)(\\[Nnh])', r' {\1} ', ayat)
    ayat_diterjemah = re.sub(
        r'(?<!{){[^}]+}|[A-Za-z]+',
        lambda padanan: alih_kata(padanan, translations),
        ayat_diterjemah)
    ayat_diterjemah = re.sub(r'[?,;,.]', gantikan_tanda, ayat_diterjemah)
    ayat_diterjemah = ayat_diterjemah.replace('{\\N}', '\\N').replace(
        '{\\n}', '\\n').replace('{\\h}', '\\h')
    return ayat_diterjemah


def alih_kata_sarikata(file_path, translations, padanan_tanda,
                       padanan_tanggaman_akhiran, padanan_tanggaman_awalan):
    sarikata = pysubs2.load(file_path)
    tidak_teralih = []

    for i, dialog in enumerate(sarikata.events):
        if dialog.is_comment:
            continue

        teks_dialog = dialog.text
        teks_dialog = re.sub(r'{[^}]+}', '', teks_dialog)

        dialog_terjemah = alih_ayat(teks_dialog, translations, padanan_tanda)
        dialog_terjemah = "{\\fe-1}" + dialog_terjemah

        dialog.text = dialog_terjemah

        katan_rumi_jawi = re.findall(
            r'(?<!{)(?<!\\)(?:\\\\)*(?<!\\[Nnh])\b[A-Za-z]+(?<!\\)(?!})(?<!\\[Nnh])',
            teks_dialog)
        for katan in katan_rumi_jawi:
            if katan.lower() not in translations and not re.search(
                    r'(?<!\\){[^}]+}', teks_dialog):
                katan_terjemah = alih_kata(
                    re.search(katan, teks_dialog), translations)
                if katan_terjemah == katan:
                    for tanggaman_akhiran in padanan_tanggaman_akhiran:
                        if katan.lower().endswith(tanggaman_akhiran):
                            katan_terjemah = alih_kata(
                                re.search(katan[:-len(tanggaman_akhiran)],
                                          teks_dialog), translations) + padanan_tanggaman_akhiran[
                                                  tanggaman_akhiran]
                            break
                    if katan_terjemah == katan:
                        for tanggaman_awalan in padanan_tanggaman_awalan:
                            if katan.lower().startswith(tanggaman_awalan):
                                katan_terjemah = padanan_tanggaman_awalan[
                                    tanggaman_awalan] + alih_kata(
                                    re.search(katan[len(tanggaman_awalan):],
                                              teks_dialog), translations)
                                break
                if katan_terjemah != katan:
                    dialog_terjemah = dialog_terjemah.replace(katan,
                                                              katan_terjemah)
                else:
                    tidak_teralih.append(katan)

        sarikata.events[i].text = dialog_terjemah

    laluan_sarikata = os.path.join(folder_keluar,
                                   "[Dialih kata]" + os.path.basename(file_path))
    sarikata.save(laluan_sarikata)

    return len(tidak_teralih), tidak_teralih


katan_kamus = {}

for file in os.listdir(folder_kamus):
    if file.endswith(".tsv"):
        file_path = os.path.join(folder_kamus, file)
        katan_kamus = {**katan_kamus, **muat_katan(file_path)}

padanan_tanda = {"?": "؟", ";": "⁏", ",": "⹁", ".": "."}
padanan_tanggaman_akhiran = {"lah": "له", "kah": "که", "nya": "ڽ", "kan": "کن"}
padanan_tanggaman_awalan = {"ber": "س", "mem": "س", "se": "س"}


files_untranslated = {}

for fail in os.listdir(folder_masuk):
    if fail.endswith((".ass", ".ssa", ".srt")):
        print(f"Selesai mengalih kata: {fail}\n---")
        laluan_fail = os.path.join(folder_masuk, fail)
        tidak_teralih_count, tidak_teralih = alih_kata_sarikata(
            laluan_fail, katan_kamus, padanan_tanda, padanan_tanggaman_akhiran,
            padanan_tanggaman_awalan)
        if tidak_teralih_count > 0:
            files_untranslated[fail] = tidak_teralih

for fail, tidak_teralih in files_untranslated.items():
    print(f"Perkataan yang tidak teralih dalam \"{fail}\":")
    untranslated_words = []
    for word in tidak_teralih:
        if word.startswith("{\\") and word.endswith("}"):
            untranslated_words.append(word[2:-1])
        else:
            untranslated_words.append(word)
    print(", ".join(untranslated_words))
    print()

print(
    "Perlu diingatkan bahawa tidak semua perkataan berimbuhan dapat dialihkan dan perlu ditambah sendiri di dalam kamus.\n\nKata sendi seperti \"di\" \"ke\" dan \"se\" dalam jawi dieja rapat.\nRAPATKAN SENDIRI, JANGAN TAK RAPATKAN"
)
