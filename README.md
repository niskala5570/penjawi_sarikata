[ملايو جاوي](README_ms.md) // [~~English~~](README_en.md)

<p style="text-align: center; margin: 10px;">
    <img src="gambar/penjawi_sarikata.png" width="auto" alt="Pasuan Jawi"></img>
</p>

---

## Cara Guna
Muat turun [python](https://www.python.org/downloads/)

Kemudian di terminal:
`pip install pysubs2`,
`py alih-kata.py` .dsb


Atau cuba dalam talian (perlu log masuk): [repl.it](https://replit.com/@niskala5570/sarikata-rumikejawi)

---
### alih-kata.py
- Akan mengalih tulisan semua fail di dalam folder "Masuk"
- Fail sari kata akan ada di folder "Keluar" beserta [Dialih Kata] di hadapannya.
- Kod ini akan ambil data rumi ke jawi dari semua fail `.tsv` yang ada di dalam folder `Kamus`
- Sebelum fail disimpan, kod ini juga akan berikan pengguna pilihan untuk memilih perkataan untuk yang bertaksa

### ~~alih-kata-tanpa-penyahtaksa.py~~
- ~~Sama seperti alih-kata.py~~
- ~~Cumanya ia akan langkau proses memilih perkataan bertaksa~~

### pengemaskini_kamus.py
- Akan memuat turun fail kamus dari folder `Kamus` simpanan Github ini.
- Selagi fail nama masih sama, ia akan bandingkan dengan cincangan(hash) MD5,
kalau sama, ia akan langkau, kalau tidak, ia akan namakan semula fail lama dan muat turun yang baharu.

### panambahkatan.py (nama mungkin akan diubah)
- Gunanya untuk menambah katan dalam fail kamus yang pengguna berikan.
- Dihujung, pengguna akan diminta samada mahu menyusunnya mengikut turutan alfabet pengepala `rumi`.
- Ini tidak wajib, boleh sahaja sunting kamus guna perisian GUI pilihan seperti LibreOffice .dll

### pengubahkatan.py (nama mungkin diubah)
- Gunanya untuk menyunting katan dalam fail kamus.
- Sama seperti penambahkatan.py, tidak wajib.

### Fail Kamus
- Diambil dari projek [rumi-jawi oleh Goodmami](https://github.com/goodmami/rumi-jawi/)
- Tapi diubah sedikit, macam hamzah setara ditukar kepada hamzah tiga suku,
pastikan pasuan menyokongnya. Atau boleh dapatkan di [Pasuan Jawi](https://github.com/niskala5570/pasuanjawi)
