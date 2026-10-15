# Guild NPC Roster

Aplikasi desktop berbasis Python (Tkinter) untuk mendata dan menganalisis pasukan NPC sebuah guild, dengan tampilan bertema game. Dibuat sebagai tugas Informatika kelas 11: fungsi, class/PBO, file CSV, dan program multi-file.

## Fitur

- **Rekrut NPC**: pilih peran lewat chip warna (Prajurit, Penyihir, Tabib), lengkap dengan validasi input, nama unik, dan batas 5 anggota.
- **Kartu pasukan**: tiap NPC tampil dengan ikon peran, bar HP/ATK beranimasi, dan status. Slot kosong ditampilkan sebagai kotak putus-putus.
- **Hapus NPC**: klik kartu lalu tombol hapus (atau tombol `Delete`), dengan konfirmasi.
- **Analisis pasukan**: total NPC, total HP, total ATK, rata-rata HP, jumlah per peran, dan NPC terkuat.
- **Data tersimpan** di `npc.csv`, jadi tetap ada setelah program ditutup.

## Struktur Proyek

```
guild-npc-roster/
├── main.py         # Titik awal: langsung membuka GUI (subprocess)
├── gui.py          # Tampilan grafis (Tkinter)
├── models.py       # Class NPC (PBO)
├── rekrut_npc.py   # Konstanta peran/batas pasukan + versi menu teks
├── tampil_npc.py   # Memuat/menyimpan data CSV + versi menu teks
└── npc.csv         # Data contoh (dibuat otomatis jika belum ada)
```

## Cara Menjalankan

Pastikan Python 3 sudah terpasang (Tkinter sudah termasuk di Windows dan macOS), lalu:

```bash
git clone https://github.com/USERNAME/guild-npc-roster.git
cd guild-npc-roster
python main.py
```

Jendela aplikasi langsung terbuka. Di Linux, jika Tkinter belum ada: `sudo apt install python3-tk`.

## Cara Pakai

1. Isi **Nama**, klik salah satu **Peran**, isi **HP** dan **ATK**, lalu klik **Rekrut NPC** (atau tekan Enter).
2. Klik sebuah kartu NPC, lalu **Hapus NPC Terpilih** untuk menghapusnya.
3. Panel **Analisis Pasukan** otomatis diperbarui setiap data berubah.

## Konsep yang Dipakai

Fungsi, class dan objek (`__init__`, `to_list`, `__str__`), percabangan, perulangan `for`, membaca/menulis file CSV, pemisahan program ke beberapa file, serta GUI dengan Tkinter (`Canvas`, `after`, event binding).
