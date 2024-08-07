import pysubs2
import os
import re
import csv
import msvcrt

IN_FOLDER = "Masuk"  # Folder sari kata yang hendak diproses.
OUT_FOLDER = "Keluar"  # Folder sari kata dan tsv keluar.
DICT_FOLDER = "Kamus"  # Folder kamus .tsv .
EXCLUDED_STYLES = ["Lagu", "EDR", "OPR"]  # Mengabaikan baris yang mempunyai gaya bernama 'sekian-sekian'.
EXCLUDED_ACTORS = ["Actor1", "Actor2"]  # Mengabaikan baris yang mempunyai nama pelakon 'sekian-sekian'.
EXCLUDED_EFFECTS = ["fx", "KEKAL", "ABAI"]  # Mengabaikan baris yang mempunyai teks 'sekian-sekian' pada ruang "Effect".
NON_RTL_STYLES = ["Masachika - Yuki"]  # Nama gaya untuk pengekodannya dikekalkan drpd ditukar kpd -1 untuk menyokong RTL. https://github.com/libass/libass/wiki/Libass'-ASS-Extensions#encoding-1

ENABLE_RTL_DISPLAY = 1  # Tetapkan ke 1 hidupkan paparan RTL, 0 untuk matikan jikalau terminal sudahpun menyokong RTL.

LANGUAGE = "ms" # ms = B.Melayu | ms-arab = B.Melayu Jawi بهاس ملايو جاوي | en = English

# Bahasa // Languages
translations = {
    "en": {
        # Masalah ralat // Error message
        "ERROR_READ_FILE": "Failed to read file {}: {}",
        "ERROR_SETTING_ENCODING": "Failed to set text encoding to RTL -1: {}",
        "ERROR_SAVING_SUBTITLE": "Failed to save subtitle file {}: {}",
        "ERROR_UPDATING_SUBTITLE": "Failed to update subtitle file {}: {}",
        "ERROR_LOADING_SUBTITLE": "Failed to load subtitle file {file_path}: {e}",
        "ERROR_PROCESSING_DIALOG": "Error processing dialog at index {}: {}",
        "ERROR_INVALID_CHOICE": "Invalid choice, please re-enter (or 0 to skip): ",
        "ERROR_FILE_PROCESSING": "Error processing file {}: {}",
        
        # Info
        "LOADING_DICTIONARY": "{} [Loaded]",
        "PROCESSED_FILE": "Processed file: {}",
        "CONVERTING_MESSAGE": "Currently converting: {}",
        "SUCCESSFUL_MESSAGE": "Successfully converted file",
        "WORD_AMBIGUITY": "Ambiguity on [{}]",
        "WORD_AMBIGUITY_CONTEXT": "['{}']",
        "INFO_UNTRANSLATED_SAVED": "Untranslated words in:\n\"{}\"",
        "INFO_UNTRANSLATED_LINE" : "Line",
        "INFO_SAVED_TSV": "Untranslated words in {file} have been saved to {tsv_file_path}",
        "INFO_TRANSLATION_CHOICE": "Enter choice (or 0 to skip): ",
        "INFO_CUSTOM_TRANSLATION": "Enter custom: ",
        "PERLU_SENTUHAN_MANUSIA": "This transliteration is not perfect, human touch is still needed.",
        
        "LONG_BAR": "-------------------------------------------",
        
        # Ask for input
        "ENTER_CHOICE": "Choose one (or 0 to skip): ",
        "CUSTOM_TRANSLITERATION": "{index}. Write custom Jawi",
        "CUSTOM_ENTER_TRANSLITERATION": "Write Jawi: ",
        "ENTER_CHOICE_INVALID": "Invalid value, please re-enter (or 0 to skip): ",
        
        # Splash screen
        "SPLASH_SCREEN": """
\033[1;36m         _____  __  __ ____            __ ___  _       __ ____ ________  __
 \033[1;34m       / ___/ / / / // __ )          / //   || |     / //  _// ____/\ \/ /
 \033[1;33m       \__ \ / / / // __  |     __  / // /| || | /| / / / / / /_     \  / 
 \033[1;33m      ___/ // /_/ // /_/ /     / /_/ // ___ || |/ |/ /_/ / / __/     / /  
\033[1;32m      /____/ \____//_____/______\____//_/  |_||__/|__//___//_/       /_/   
\033[1;36m                        /_____/                                           
\033[0m
""",
        "SPLASH_SCREEN_TEXT": "Subtitile Jawify v3 by Niskala5570", #
        "WAIT_KEY_PRESS": "Press any key to continue..."
    },
    "ms": {
        # Masalah ralat
        "ERROR_READ_FILE": "Gagal membaca fail {}: {}",
        "ERROR_SETTING_ENCODING": "Gagal menetapkan pengekodan teks kepada RTL -1: {}",
        "ERROR_SAVING_SUBTITLE": "Gagal menyimpan fail sari kata {}: {}",
        "ERROR_UPDATING_SUBTITLE": "Gagal mengemas kini fail sari kata {}: {}",
        "ERROR_LOADING_SUBTITLE": "Gagal memuatkan fail sari kata {file_path}: {e}",
        "ERROR_PROCESSING_DIALOG": "Ralat memproses dialog pada indeks {}: {}",
        "ERROR_INVALID_CHOICE": "Tidak sah, masukkan semula (atau 0 utk melangkau): ",
        "ERROR_FILE_PROCESSING": "Ralat memproses fail {}: {}",
        
        # Info
        "LOADING_DICTIONARY": "{} [Dimuatkan]",
        "PROCESSED_FILE": "Fail yang diproses: {}",
        "CONVERTING_MESSAGE": "Sekarang menukarkan: {}",
        "SUCCESSFUL_MESSAGE": "Fail yang berjaya ditukar",
        "WORD_AMBIGUITY": "Kesamaran pada [{}]", #
        "WORD_AMBIGUITY_CONTEXT": "['{}']", #
        "INFO_UNTRANSLATED_SAVED": "Perkataan yang tidak diterjemah pada:\n\"{}\"",
        "INFO_UNTRANSLATED_LINE" : "Baris",
        "INFO_SAVED_TSV": "Perkataan tidak ditukar dalam {file} telah disimpan ke {tsv_file_path}",
        "INFO_TRANSLATION_CHOICE": "Masukkan pilihan (atau 0 untuk melangkau): ",
        "INFO_CUSTOM_TRANSLATION": "Masukkan ejaan: ",
        "PERLU_SENTUHAN_MANUSIA": "Pengalih tulisan ini tidaklah sempurna, sentuhan manusia tetap juga diperlukan.",
        
        "LONG_BAR": "-------------------------------------------",
        
        # Minta input
        "ENTER_CHOICE": "Pilih salah satu (0 utk langkau): ", #
        "CUSTOM_TRANSLITERATION": "{index}. Tulis Jawi sendiri", #
        "CUSTOM_ENTER_TRANSLITERATION": "Tulis Jawi: ", #
        "ENTER_CHOICE_INVALID": "Nilai tidak sah, masukkan semula (0 utk langkau): ",
        
        # Layar tampil
        "SPLASH_SCREEN": """
\033[1;36m     ___  _____  __   _____ _      ______   _______   ___  ______ _____ _________ 
 \033[1;34m   / _ \/ __/ |/ /_ / / _ | | /| / /  _/  / __/ _ | / _ \/  _/ //_/ _ /_  __/ _ |
 \033[1;32m  / ___/ _//    / // / __ | |/ |/ // /   _\ \/ __ |/ , _// // ,< / __ |/ / / __ |
 \033[1;33m /_/  /___/_/|_/\___/_/ |_|__/|__/___/__/___/_/ |_/_/|_/___/_/|_/_/ |_/_/ /_/ |_|
\033[1;36m                                    /___/                                         
\033[0m        
""",
        "SPLASH_SCREEN_TEXT": "Penjawi Sari Kata v3 oleh Niskala5570", #
        "WAIT_KEY_PRESS": "Tekan sebarang kekunci untuk teruskan..."
    },
    "ms-arab": {
        # مسئله رالت
        "ERROR_READ_FILE": "ݢاݢل ممباچ فاءيل {}: {}",
        "ERROR_SETTING_ENCODING": "ݢاݢل منتڤکن ڤڠکودن تيک‌س کڤد [LTR]RTL -1[/LTR]: {}",
        "ERROR_SAVING_SUBTITLE": "ݢاݢل مڽيمڤن فاءيل ساري کات [LTR]{}: {}[/LTR]",
        "ERROR_UPDATING_SUBTITLE": "ݢاݢل مڠمسکيني فاءيل ساري کات [LTR]{}: {}[/LTR]",
        "ERROR_LOADING_SUBTITLE": "ݢاݢل ممواتکن فاءيل ساري کات [LTR]{file_path}: {e}[/LTR]",
        "ERROR_PROCESSING_DIALOG": "رالت ممڤروسيس ديالوݢ ڤد اينديک‌س [LTR]{}: {}[/LTR]",
        "ERROR_INVALID_CHOICE": "تيدق صح⹁ ماسوقکن سمولا (اتاو 0 اونتوق ملڠکاو): ",
        "ERROR_FILE_PROCESSING": "رالت ممڤروسيس فاءيل [LTR]{}: {}[/LTR]",
        
        # اينفو
        "LOADING_DICTIONARY": "]دمواتکن[ [LTR]{}[/LTR]",
        "PROCESSED_FILE": "فاءىل يڠ دڤروسيس: [LTR]{}[/LTR]",
        "CONVERTING_MESSAGE": "سکارڠ منوکرکن: [LTR]{}[/LTR]",
        "SUCCESSFUL_MESSAGE": "فاءيل يڠ برجاي دتوکر",
        "WORD_AMBIGUITY": "کسامرن ڤد [LTR][{}][/LTR]", #
        "WORD_AMBIGUITY_CONTEXT": "[LTR]['{}'][/LTR]", #
        "INFO_UNTRANSLATED_SAVED": "ڤرکاتاءن يڠ تيدق دتوکر ڤد[LTR][/LTR]]:\n\"{}\"",
        "INFO_UNTRANSLATED_LINE" : "باريس",
        "INFO_SAVED_TSV": "ڤرکاتاءن يڠ تيدق دتوکر دالم [LTR]{file}[/LTR] تله دسيمڤن کـ [LTR]{tsv_file_path}[/LTR]",
        "INFO_TRANSLATION_CHOICE": "ماسوقکن ڤيليهن )اتاو 0 اونتوق ملڠکاو()): ",
        "INFO_CUSTOM_TRANSLATION": "ماسوقکن ايجاءن: ",
        "PERLU_SENTUHAN_MANUSIA": "[ALL_LTR]Pengalih tulisan ini tidaklah sempurna, sentuhan manusia tetap juga diperlukan.",
        
        "LONG_BAR": "-------------------------------------------",
        
        # مينتا اينڤوت
        "ENTER_CHOICE": "ڤيليه ساله ساتو )0 اونتوق لڠکاو(: ", #
        "CUSTOM_TRANSLITERATION": "توليس جاوي سنديري [LTR]{index}.[/LTR]", #
        "CUSTOM_ENTER_TRANSLITERATION": "توليس جاوي: ", #
        "ENTER_CHOICE_INVALID": "نيلاي تيدق صح⹁ ماسوقکن سمولا [LTR]([/LTR]0 اونتق لڠکاو[LTR]):[/LTR] ",

        # لاير رمڤيل
        "SPLASH_SCREEN" : """[ALL_LTR]
\033[1;34m                                                                          __  __  __
\033[1;34m                            ___                      __                  / / / / / /                  
\033[1;34m                           /__ \                    / /                      _____       
\033[1;34m                          ((  \ \         _______  / /                 __   / ___ \            
\033[1;32m                          \ \  \ \__/\   / ___  / / /________         / /  / /__/ /  
\033[1;32m                           \ \  \____/  / /__/ / / / \_____  \        __   \__   / 
\033[1;32m                      __    \ \        (____  / / /_________\ \______/ /_____/  /       
\033[1;32m                     / /_____\ \      _____/ / /______________  _______________/      
\033[1;33m                    /___________\    /_____ /           __    \ \            
\033[1;33m                       __  __                          / /     \_\                       
\033[1;33m                      / / / /           aku mls wrna               
\033[1;36m                        __                      ___                     ___
\033[1;36m                       / /  ______________     /__ \                   /  /   
\033[1;34m                      / / /  ____________/    ((  \ \                 /  /     
\033[1;34m       __  __    __  / / / /___________       \ \  \ \__/\           /  /                          
\033[1;34m      / / / /   / / / / /___________   )       \ \  \____/     __   /  /                ___                     
\033[1;32m  _____________/ / / /_______________\ /   __   \ \           / /  /  /    ___   ___   /  /                       
\033[1;32m /______________/ /___________________/   / /_____\ \        / /  /  /    /  /  /  /  /  /                           
\033[1;33m                                         /___________\  ___ / /  /  /____/  /__/  /__/  /              
\033[1;36m                                            __  __     /_____)  /______________________/
\033[1;36m                                           / / / /         
\033[0m
             """,
        "SPLASH_SCREEN_TEXT" : "ڤنجاوي ساري کات ۏ.3 اوليه نيسکالا[LTR]5570[/LTR]",

        "WAIT_KEY_PRESS": "تکن سبارڠ ککونچي اونتوق تروسکن..."
    }
}

# Memuatkan segala fail kamus .tsv dari DICT_FOLDER
def load_dictionary(file_path):
    data = {}
    try:
        print(translate("LOADING_DICTIONARY", file_path))
        with open(file_path, encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                columns = line.strip().split("\t")
                if len(columns) >= 2:
                    rumi, jawi = columns[:2]
                    rumi = rumi.lower()
                    if rumi in data:
                        data[rumi].append(jawi)
                    else:
                        data[rumi] = [jawi]
    except Exception as e:
        print(translate("ERROR_READ_FILE", file_path, e))
    return data

# Terjemah kod
def translate(key, *args, **kwargs):
    template = translations.get(LANGUAGE, {}).get(key, key)
    
    # Kalau kwargs diberi, guna untuk format (susun) terjemahan
    if kwargs:
        translated_text = template.format(**kwargs)
    else:
        translated_text = template.format(*args)
        
    # Jika bahasa Melayu Jawi, terbalikkan perkataan
    if LANGUAGE == "ms-arab":
        translated_text = reverse_jawi(translated_text)
    
    return translated_text

# Menterbalikkan teks arab supaya dipaparkan dengan benar
def reverse_jawi(text):
    if not ENABLE_RTL_DISPLAY:
        return text

    # Check if the string starts with [ALL_LTR]
    if text.startswith("[ALL_LTR]"):
        # Remove [ALL_LTR] marker and return the text without reversing
        return text[len("[ALL_LTR]"):].replace("[ALL_LTR]", "")

    # This pattern matches text enclosed in [LTR] and [/LTR] tags
    ltr_segments = re.findall(r'\[LTR\](.*?)\[/LTR\]', text, re.DOTALL)

    # Remove [LTR] and [/LTR] markers from the text
    cleaned_text = re.sub(r'\[LTR\]|\[/LTR\]', '', text)

    # Reverse the cleaned text
    reversed_text = cleaned_text[::-1]

    # Restore the [LTR] ... [/LTR] segments to their original positions
    for segment in ltr_segments:
        reversed_text = reversed_text.replace(segment[::-1], segment)

    # Return the text with [ALL_LTR] marker removed if present
    return reversed_text

def select_translation(word, translations, context, chosen_translations):
    if word in chosen_translations:
        return chosen_translations[word]
    print(translate("LONG_BAR"))
    print(translate("WORD_AMBIGUITY", word))
    print(translate("WORD_AMBIGUITY_CONTEXT", context))
    for i, translation in enumerate(translations):
        reversed_translation = reverse_jawi(translation)
        print(f"{i + 1}. {reversed_translation}")
    
    # Add an option for custom translation
    index = len(translations) + 1 # Tambah {nombor} belakang perkataan.
    print(translate('CUSTOM_TRANSLITERATION', index=index)) # "{nombor}. Tulis Jawi sendiri"

    choice = input(translate("ENTER_CHOICE")) 
    while not choice.isdigit() or int(choice) < 0 or int(choice) > len(translations) + 1:
        choice = input(translate("ENTER_CHOICE_INVALID"))
    
    if int(choice) == 0:
        # Skip selection and use the first translation option
        chosen_translation = translations[0]
    elif int(choice) == len(translations) + 1:
        # Get custom translation from user
        custom_translation = input(translate("CUSTOM_ENTER_TRANSLITERATION")).strip()
        chosen_translation = custom_translation
    else:
        chosen_translation = translations[int(choice) - 1]
    
    chosen_translations[word] = chosen_translation
    return chosen_translation

def translate_word(match, translations, chosen_translations, context):
    word = match.group(0)
    lower_word = word.lower()
    if lower_word in translations:
        translation_list = translations[lower_word]
        if len(translation_list) > 1:
            return select_translation(word, translation_list, context, chosen_translations)
        return translation_list[0]
    return word

def replace_punctuation(match, punctuation_map):
    punctuation = match.group(0)
    return punctuation_map.get(punctuation, punctuation)

def translate_sentence(sentence, translations, punctuation_map, chosen_translations):
    # Use regex to preserve text within {} and comment lines
    def replace_text(m):
        text = m.group(0)
        if text.startswith('{') and text.endswith('}'):
            return text
        return translate_word(m, translations, chosen_translations, sentence)
    
    sentence = re.sub(r'(?<!\\)(\\[Nnh])', r' {\1} ', sentence)
    sentence = re.sub(r'(?<!{){[^}]+}|[A-Za-z\-]+', replace_text, sentence)
    sentence = re.sub(r'[?,;,.]', lambda m: replace_punctuation(m, punctuation_map), sentence)
    sentence = sentence.replace('{\\N}', '\\N').replace('{\\n}', '\\n').replace('{\\h}', '\\h')
    return sentence

def fix_spelling(text):
    text = re.sub(r'\bد\s', 'د', text)
    text = re.sub(r'\bک\s', 'ک', text)
    return text

def save_untranslated_words(file_path, untranslated_words):
    with open(file_path, 'w', newline='', encoding='utf-8') as tsvfile:
        writer = csv.writer(tsvfile, delimiter='\t')
        writer.writerow(['rumi', 'jawi', 'jawi_niskala'])
        for word in untranslated_words:
            writer.writerow([word.lower(), '', ''])

def update_style_encoding(file_path, non_rtl_styles):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        with open(file_path, 'w', encoding='utf-8') as file:
            in_styles = False
            for line in lines:
                if line.startswith('[V4+ Styles]'):
                    in_styles = True
                    file.write(line)
                    continue
                elif line.startswith('['):
                    in_styles = False

                if in_styles and line.startswith('Style:'):
                    parts = line.split(',')
                    if len(parts) > 22:
                        style_name = parts[0].split(':')[1].strip()
                        if style_name in non_rtl_styles:
                            parts[22] = '1'  # Set encoding to RTL (1) for non-RTL styles
                        else:
                            parts[22] = '-1'  # Set encoding to non-RTL (-1) for others
                    line = ','.join(parts) + '\n'
                file.write(line)
    except Exception as e:
        print(translate("ERROR_SETTING_ENCODING", e))

def save_subtitle(subtitles, file_path):
    try:
        output_path = os.path.join(OUT_FOLDER, "[JAWI]" + os.path.basename(file_path))
        subtitles.save(output_path)
    except Exception as e:
        print(translate("ERROR_SAVING_SUBTITLE", output_path, e))

def update_subtitles_with_translation(file_path, translations):
    try:
        subtitle = pysubs2.load(file_path)
        for dialog in subtitle.events:
            if dialog.is_comment or dialog.style in EXCLUDED_STYLES or dialog.effect in EXCLUDED_EFFECTS or dialog.name in EXCLUDED_ACTORS:
                continue

            updated_text = translate_sentence(dialog.text, translations, tanda_baca(), {})
            dialog.text = updated_text
        
        output_file_path = os.path.join(OUT_FOLDER, os.path.basename(file_path))
        subtitle.save(output_file_path)
        # print(f"Sari kata yang dikemas kini disimpan di {output_file_path}")
    except Exception as e:
        print(translate("ERROR_UPDATING_SUBTITLE", file_path, e))

def translate_subtitle(file_path, translations, punctuation_map, suffix_map, prefix_map):
    try:
        update_style_encoding(file_path, NON_RTL_STYLES)
    except Exception as e:
        print(translate("ERROR_SETTING_ENCODING", e))

    try:
        subtitles = pysubs2.load(file_path)
    except Exception as e:
        print(translate("ERROR_LOADING_SUBTITLE", file_path=file_path, e=e))
        return 0, []

    untranslated = []
    chosen_translations = {}
    extracted_content = {}

    for i, dialog in enumerate(subtitles.events):
        if dialog.is_comment or dialog.style in EXCLUDED_STYLES or dialog.effect in EXCLUDED_EFFECTS or dialog.name in EXCLUDED_ACTORS:
            continue

        try:
            text = dialog.text
            extracted = re.findall(r'{(.*?)}', text)
            for extract in extracted:
                placeholder = f'__{len(extracted_content)}__'
                extracted_content[placeholder] = '{' + extract + '}'
                text = text.replace('{' + extract + '}', placeholder)

            translated_dialog = fix_spelling(translate_sentence(text, translations, punctuation_map, chosen_translations))

            for placeholder, content in extracted_content.items():
                translated_dialog = translated_dialog.replace(placeholder, content)

            dialog.text = translated_dialog

            rumi_jawi_words = re.findall(r'(?<!{)(?<!\\)(?:\\\\)*(?<!\\[Nnh])\b[A-Za-z\-]+(?<!\\)(?!})(?<!\\[Nnh])', text)
            for word in rumi_jawi_words:
                if word.lower() not in translations and not re.search(r'(?<!\\){[^}]+}', text):
                    translated_word = translate_word(re.search(word, text), translations, chosen_translations, text)
                    if translated_word == word:
                        for suffix in suffix_map:
                            if word.lower().endswith(suffix):
                                translated_word = translate_word(re.search(word[:-len(suffix)], text), translations, chosen_translations, text) + suffix_map[suffix]
                                break
                    if translated_word == word:
                        for prefix in prefix_map:
                            if word.lower().startswith(prefix):
                                translated_word = prefix_map[prefix] + translate_word(re.search(word[len(prefix):], text), translations, chosen_translations, text)
                                break
                    if translated_word != word:
                        translated_dialog = translated_dialog.replace(word, translated_word)
                    else:
                        untranslated.append((i, word))

            subtitles.events[i].text = translated_dialog
        except Exception as e:
            print(translate("ERROR_PROCESSING_DIALOG", i, e))

    save_subtitle(subtitles, file_path)
    return len(untranslated), untranslated

def load_dictionary_from_folder(folder_path):
    word_dict = {}
    for file in os.listdir(folder_path):
        if file.endswith(".tsv"):
            file_path = os.path.join(folder_path, file)
            word_dict = {**word_dict, **load_dictionary(file_path)}
    return word_dict

def tanda_baca():
    return {"?": "؟", ";": "⁏", ",": "⹁", ".": "."}

def imbuhan_akhiran():
    imbuhan_akhiran = {"lah": "له", "kah": "که", "kan": "کن", "i": "ي", "ku": "کو", "mu": "مو", "nya": "ڽ"}
    imbuhan_akhiran_2 = {"":""}
    gabung_imbuhan_akhiran = {**imbuhan_akhiran, **imbuhan_akhiran_2}
    return gabung_imbuhan_akhiran

def imbuhan_awalan():
    imbuhan_awalan = {"ber": "بر", "mem": "مم", "meng": "مڠ", "se": "س", "tak": "تق", "per": "ڤر", "pe": "ڤ", "pen": "ڤن"}
    imbuhan_awalan_2 = {"": ""}
    gabung_imbuhan_awalan = {**imbuhan_awalan, **imbuhan_awalan_2}
    return gabung_imbuhan_awalan

def process_files(folder_path, translations, punctuation_map, suffix_map, prefix_map, select_translation):
    untranslated_files = {}
    processed_files = []  # Track processed files
    
    for file in os.listdir(folder_path):
        if file.endswith((".ass", ".ssa", ".srt")):
            print(translate("CONVERTING_MESSAGE", file))
            file_path = os.path.join(folder_path, file)
            
            if select_translation:
                untranslated_count, untranslated = translate_subtitle(file_path, translations, punctuation_map, suffix_map, prefix_map)
                if untranslated_count > 0:
                    untranslated_files[file] = untranslated
                processed_files.append(file)  # Track processed file
            else:
                processed_files.append(file)  # Track processed file
    
    return untranslated_files, processed_files

def print_untranslated_words(untranslated_files):
    untranslated_words_set = set()
    for file, untranslated in untranslated_files.items():
        print(translate("INFO_UNTRANSLATED_SAVED", file,))
        dialog_lines = {}
        for dialog_index, dialog_word in untranslated:
            untranslated_words_set.add(dialog_word.lower())
            if dialog_index + 1 in dialog_lines:
                dialog_lines[dialog_index + 1].append(dialog_word)
            else:
                dialog_lines[dialog_index + 1] = [dialog_word]
        for line_num, dialog_words in dialog_lines.items():
            print(f"{translate('INFO_UNTRANSLATED_LINE')} {line_num}: {dialog_words}")
        print()
    return untranslated_words_set

def prompt_for_untranslated_update(untranslated_files):
    if untranslated_files:
        for file, untranslated in untranslated_files.items():
            print(translate("INFO_UNTRANSLATED_SAVED", file, ''))
            dialog_lines = {}
            for dialog_index, dialog_word in untranslated:
                if dialog_index + 1 in dialog_lines:
                    dialog_lines[dialog_index + 1].append(dialog_word)
                else:
                    dialog_lines[dialog_index + 1] = [dialog_word]
            for line_num, dialog_words in dialog_lines.items():
                print(f"{translate('INFO_UNTRANSLATED_LINE')} {line_num}: {dialog_words}")
            print()

        save_prompt = input(translate("INFO_TRANSLATION_CHOICE")).strip().lower()
        if save_prompt in ['yes', 'y']:
            for file, untranslated in untranslated_files.items():
                tsv_file_path = os.path.join(OUT_FOLDER, f"{os.path.splitext(file)[0]}_untranslated_words.tsv")
                save_untranslated_words(tsv_file_path, {word for _, word in untranslated})
                print(translate("INFO_SAVED_TSV", file=file, tsv_file_path=tsv_file_path))

def print_splash_screen():
    splash_art = translate("SPLASH_SCREEN")
    splash_art_text = translate("SPLASH_SCREEN_TEXT")
    print(splash_art)
    print(splash_art_text)
    print(translate("WAIT_KEY_PRESS"))
    print(translate("LONG_BAR"))
    msvcrt.getch()  # Wait for a key press

def main():
    print_splash_screen()  # Show the splash screen at the start

    translations = load_dictionary_from_folder(DICT_FOLDER)
    punctuation_map = tanda_baca()
    suffix_map = imbuhan_akhiran()
    prefix_map = imbuhan_awalan()

    # Process files and collect untranslated words
    untranslated_files, processed_files = process_files(IN_FOLDER, translations, punctuation_map, suffix_map, prefix_map, select_translation=True)

    # Print untranslated words and ask if user wants to save them as TSV
    prompt_for_untranslated_update(untranslated_files)

    # Display list of processed files
    if processed_files:
        print(f"========\n{translate('SUCCESSFUL_MESSAGE')}:")
        print("========")
        for file_name in processed_files:
            print(file_name)
        print("========")

    # Papar peringatan di akhir perisian
    if LANGUAGE == "ms-arab":
        print(translate("PERLU_SENTUHAN_MANUSIA"))
        print(reverse_jawi("ڤڠاليه توليسن اين تيدقله سمڤورنا⹁ سنتوهن ماءنوسي تتڤ جوݢ دڤرلوكن."))
    else:
        print(reverse_jawi("ڤڠاليه توليسن اين تيدقله سمڤورنا⹁ سنتوهن ماءنوسي تتڤ جوݢ دڤرلوكن."))   
        print(translate("PERLU_SENTUHAN_MANUSIA"))

if __name__ == "__main__":
    main()
