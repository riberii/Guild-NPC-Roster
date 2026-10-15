import csv
import os
import tkinter as tk
from tkinter import messagebox

# Pastikan program selalu membaca npc.csv di folder yang sama dengan file ini,
# walaupun dijalankan dari folder lain.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from models import NPC
from tampil_npc import muat_data, simpan_data
from rekrut_npc import DAFTAR_PERAN, MAKS_PASUKAN

# ---------- Palet warna (gelap lembut, nyaman di mata) ----------
BG = "#161b2e"
BG_GELAP = "#0f1324"
PANEL = "#20263d"
KARTU = "#283050"
KARTU_HOVER = "#323c66"
GARIS = "#3a4470"
INPUT = "#121629"
TEKS = "#e8ecf8"
REDUP = "#9aa5c6"
EMAS = "#f4c95d"
BIRU = "#4f8cff"
BIRU_HOVER = "#6aa0ff"
MERAH = "#e5655e"
MERAH_HOVER = "#f0807a"
HIJAU = "#4ecb8f"
UNGU = "#a98bff"
ORANYE = "#f39c5a"

# Urutan warna sama dengan urutan DAFTAR_PERAN: Prajurit, Penyihir, Tabib
WARNA_PERAN = [MERAH, UNGU, HIJAU]

FONT = "Segoe UI"
FONT_JUDUL = "Georgia"

LEBAR_KARTU = 540
TINGGI_KARTU = 68
LEBAR_BAR = 140

def kotak_bulat(kanvas, x1, y1, x2, y2, r, **opsi):
    titik = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
             x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
             x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return kanvas.create_polygon(titik, smooth=True, **opsi)

def gambar_ikon(kanvas, peran, cx, cy):
    if peran == "Prajurit":      # perisai
        pola = [(0, -17), (14, -12), (12, 4), (0, 17), (-12, 4), (-14, -12)]
    elif peran == "Penyihir":    # bintang
        pola = [(0, -17), (4, -5), (16, 0), (4, 5),
                (0, 17), (-4, 5), (-16, 0), (-4, -5)]
    else:                        # Tabib: tanda tambah
        pola = [(-4, -15), (4, -15), (4, -4), (15, -4), (15, 4),
                (4, 4), (4, 15), (-4, 15), (-4, 4), (-15, 4), (-15, -4), (-4, -4)]
    titik = []
    for dx, dy in pola:
        titik.append(cx + dx)
        titik.append(cy + dy)
    kanvas.create_polygon(titik, fill=BG, outline="")

class AplikasiGuild:
    def __init__(self, jendela):
        self.jendela = jendela
        self.jendela.title("Guild Petualang NPC")
        self.jendela.configure(bg=BG)
        self.jendela.resizable(False, False)

        self.data = []
        self.terpilih = None
        self.hover = None
        self.kilat = None
        self.faktor = 1.0
        self.id_animasi = None
        self.maks_hp = 1
        self.maks_atk = 1
        self.peran_dipilih = DAFTAR_PERAN[0]

        self.buat_header()
        isi = tk.Frame(self.jendela, bg=BG)
        isi.pack(padx=18, pady=(10, 4))
        kiri = tk.Frame(isi, bg=BG)
        kiri.grid(row=0, column=0, sticky="n", padx=(0, 18))
        kanan = tk.Frame(isi, bg=BG)
        kanan.grid(row=0, column=1, sticky="n")
        self.buat_form(kiri)
        self.buat_analisis(kiri)
        self.buat_pasukan(kanan)
        self.buat_footer()

        self.entry_nama.bind("<Return>", self.tekan_enter)
        self.entry_hp.bind("<Return>", self.tekan_enter)
        self.entry_atk.bind("<Return>", self.tekan_enter)
        self.jendela.bind("<Delete>", self.tekan_delete)

        self.refresh_data()
        self.tengahkan_jendela()
        self.entry_nama.focus()

    # ---------- Komponen kecil ----------
    def tengahkan_jendela(self):
        self.jendela.update_idletasks()
        lebar = self.jendela.winfo_reqwidth()
        tinggi = self.jendela.winfo_reqheight()
        x = max(0, (self.jendela.winfo_screenwidth() - lebar) // 2)
        y = max(0, (self.jendela.winfo_screenheight() - tinggi) // 2 - 20)
        self.jendela.geometry(f"+{x}+{y}")

    def judul_bagian(self, induk, teks, warna_latar):
        return tk.Label(induk, text=teks, bg=warna_latar, fg=EMAS,
                        font=(FONT, 10, "bold"))

    def buat_tombol(self, induk, teks, warna, warna_hover, perintah, fg="white"):
        tombol = tk.Label(induk, text=teks, bg=warna, fg=fg, cursor="hand2",
                          font=(FONT, 10, "bold"), padx=16, pady=7)

        def masuk(event):
            tombol.config(bg=warna_hover)

        def keluar(event):
            tombol.config(bg=warna)

        def klik(event):
            perintah()

        tombol.bind("<Enter>", masuk)
        tombol.bind("<Leave>", keluar)
        tombol.bind("<Button-1>", klik)
        return tombol

    def buat_entry(self, induk, lebar):
        return tk.Entry(induk, width=lebar, bg=INPUT, fg=TEKS,
                        insertbackground=TEKS, relief="flat",
                        font=(FONT, 11), highlightthickness=1,
                        highlightbackground=GARIS, highlightcolor=BIRU)

    def warna_peran(self, peran):
        for i in range(len(DAFTAR_PERAN)):
            if DAFTAR_PERAN[i] == peran:
                return WARNA_PERAN[i]
        return REDUP

    # ---------- Susunan tampilan ----------
    def buat_header(self):
        header = tk.Frame(self.jendela, bg=BG_GELAP)
        header.pack(fill="x")
        tk.Label(header, text="GUILD PETUALANG NPC", bg=BG_GELAP, fg=EMAS,
                 font=(FONT_JUDUL, 20, "bold")).pack(pady=(8, 0))
        tk.Label(header, text="Rekrut, kelola, dan analisis pasukan petualangmu",
                 bg=BG_GELAP, fg=REDUP, font=(FONT, 10)).pack(pady=(0, 6))
        tk.Frame(self.jendela, bg=EMAS, height=2).pack(fill="x")

    def buat_form(self, induk):
        kartu = tk.Frame(induk, bg=PANEL, padx=16, pady=10)
        kartu.pack(fill="x")
        self.judul_bagian(kartu, "REKRUT NPC BARU", PANEL).pack(anchor="w")

        tk.Label(kartu, text="NAMA", bg=PANEL, fg=REDUP,
                 font=(FONT, 8, "bold")).pack(anchor="w", pady=(8, 2))
        self.entry_nama = self.buat_entry(kartu, 32)
        self.entry_nama.pack(fill="x", ipady=3)

        tk.Label(kartu, text="PERAN", bg=PANEL, fg=REDUP,
                 font=(FONT, 8, "bold")).pack(anchor="w", pady=(8, 2))
        baris_peran = tk.Frame(kartu, bg=PANEL)
        baris_peran.pack(fill="x")
        self.chip_peran = []
        for i in range(len(DAFTAR_PERAN)):
            self.buat_chip(baris_peran, i)
        self.warnai_chip()

        baris_angka = tk.Frame(kartu, bg=PANEL)
        baris_angka.pack(fill="x", pady=(8, 0))
        kolom_hp = tk.Frame(baris_angka, bg=PANEL)
        kolom_hp.pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Label(kolom_hp, text="HP", bg=PANEL, fg=REDUP,
                 font=(FONT, 8, "bold")).pack(anchor="w", pady=(0, 2))
        self.entry_hp = self.buat_entry(kolom_hp, 12)
        self.entry_hp.pack(fill="x", ipady=3)
        kolom_atk = tk.Frame(baris_angka, bg=PANEL)
        kolom_atk.pack(side="left", fill="x", expand=True, padx=(6, 0))
        tk.Label(kolom_atk, text="ATK", bg=PANEL, fg=REDUP,
                 font=(FONT, 8, "bold")).pack(anchor="w", pady=(0, 2))
        self.entry_atk = self.buat_entry(kolom_atk, 12)
        self.entry_atk.pack(fill="x", ipady=3)

        baris_tombol = tk.Frame(kartu, bg=PANEL)
        baris_tombol.pack(fill="x", pady=(10, 0))
        self.buat_tombol(baris_tombol, "Rekrut NPC", BIRU, BIRU_HOVER,
                         self.simpan_npc).pack(side="left", fill="x", expand=True,
                                               padx=(0, 6))
        self.buat_tombol(baris_tombol, "Kosongkan", GARIS, "#4a5690",
                         self.kosongkan_form).pack(side="left", padx=(6, 0))

    def buat_chip(self, induk, i):
        chip = tk.Label(induk, text=DAFTAR_PERAN[i], cursor="hand2",
                        font=(FONT, 10, "bold"), padx=10, pady=5)
        chip.pack(side="left", fill="x", expand=True, padx=2)

        def klik(event):
            self.pilih_peran(DAFTAR_PERAN[i])

        chip.bind("<Button-1>", klik)
        self.chip_peran.append(chip)

    def pilih_peran(self, peran):
        self.peran_dipilih = peran
        self.warnai_chip()

    def warnai_chip(self):
        for i in range(len(DAFTAR_PERAN)):
            if DAFTAR_PERAN[i] == self.peran_dipilih:
                self.chip_peran[i].config(bg=WARNA_PERAN[i], fg=BG)
            else:
                self.chip_peran[i].config(bg=INPUT, fg=WARNA_PERAN[i])

    def buat_analisis(self, induk):
        kartu = tk.Frame(induk, bg=PANEL, padx=16, pady=10)
        kartu.pack(fill="x", pady=(10, 0))
        self.judul_bagian(kartu, "ANALISIS PASUKAN", PANEL).pack(anchor="w")

        petak = tk.Frame(kartu, bg=PANEL)
        petak.pack(fill="x", pady=(6, 0))
        petak.columnconfigure(0, weight=1)
        petak.columnconfigure(1, weight=1)
        caption = ["Total NPC", "Total HP", "Total ATK", "Rata-rata HP"]
        warna_nilai = [TEKS, HIJAU, ORANYE, BIRU]
        self.nilai = []
        for i in range(len(caption)):
            kotak = tk.Frame(petak, bg=KARTU, padx=10, pady=3)
            kotak.grid(row=i // 2, column=i % 2, sticky="ew",
                       padx=3, pady=3)
            tk.Label(kotak, text=caption[i], bg=KARTU, fg=REDUP,
                     font=(FONT, 8)).pack(anchor="w")
            label_nilai = tk.Label(kotak, text="-", bg=KARTU, fg=warna_nilai[i],
                                   font=(FONT, 14, "bold"))
            label_nilai.pack(anchor="w")
            self.nilai.append(label_nilai)

        tk.Label(kartu, text="JUMLAH PERAN", bg=PANEL, fg=REDUP,
                 font=(FONT, 8, "bold")).pack(anchor="w", pady=(6, 2))
        baris_peran = tk.Frame(kartu, bg=PANEL)
        baris_peran.pack(fill="x")
        self.label_peran = []
        for i in range(len(DAFTAR_PERAN)):
            lp = tk.Label(baris_peran, text=f"{DAFTAR_PERAN[i]}  0", bg=KARTU,
                          fg=WARNA_PERAN[i], font=(FONT, 10, "bold"),
                          padx=6, pady=4)
            lp.pack(side="left", fill="x", expand=True, padx=2)
            self.label_peran.append(lp)

        self.label_terkuat = tk.Label(kartu, text="NPC Terkuat : -", bg="#3a3320",
                                      fg=EMAS, font=(FONT, 10, "bold"),
                                      padx=10, pady=6)
        self.label_terkuat.pack(fill="x", pady=(8, 0))

    def buat_pasukan(self, induk):
        atas = tk.Frame(induk, bg=BG)
        atas.pack(fill="x", pady=(0, 6))
        self.judul_bagian(atas, "DAFTAR PASUKAN", BG).pack(side="left")
        self.label_slot = tk.Label(atas, text="0 / 5", bg=BG, fg=REDUP,
                                   font=(FONT, 10, "bold"))
        self.label_slot.pack(side="right")

        self.kanvas = []
        for i in range(MAKS_PASUKAN):
            self.buat_kartu(induk, i)

        bawah = tk.Frame(induk, bg=BG)
        bawah.pack(fill="x", pady=(8, 0))
        tk.Label(bawah, text="Klik kartu untuk memilih NPC", bg=BG, fg=REDUP,
                 font=(FONT, 9)).pack(side="left")
        self.buat_tombol(bawah, "Hapus NPC Terpilih", MERAH, MERAH_HOVER,
                         self.hapus_npc).pack(side="right")

    def buat_kartu(self, induk, i):
        kanvas = tk.Canvas(induk, width=LEBAR_KARTU, height=TINGGI_KARTU,
                           bg=BG, highlightthickness=0, cursor="hand2")
        kanvas.pack(pady=4)

        def masuk(event):
            self.hover = i
            self.gambar_kartu(i)

        def keluar(event):
            self.hover = None
            self.gambar_kartu(i)

        def klik(event):
            self.klik_kartu(i)

        kanvas.bind("<Enter>", masuk)
        kanvas.bind("<Leave>", keluar)
        kanvas.bind("<Button-1>", klik)
        self.kanvas.append(kanvas)

    def buat_footer(self):
        tk.Frame(self.jendela, bg=GARIS, height=1).pack(fill="x")
        footer = tk.Frame(self.jendela, bg=BG_GELAP, padx=18, pady=6)
        footer.pack(fill="x")
        self.label_status = tk.Label(footer, text="Siap.", bg=BG_GELAP,
                                     fg=REDUP, font=(FONT, 10))
        self.label_status.pack(side="left")
        self.buat_tombol(footer, "Keluar", GARIS, MERAH,
                         self.jendela.destroy).pack(side="right", padx=(8, 0))
        self.buat_tombol(footer, "Refresh", GARIS, "#4a5690",
                         self.tekan_refresh).pack(side="right")

    def set_status(self, teks, warna=REDUP):
        self.label_status.config(text=teks, fg=warna)

    # ---------- Menggambar kartu NPC ----------
    def gambar_kartu(self, i):
        c = self.kanvas[i]
        c.delete("all")
        if i >= len(self.data):
            if self.hover == i:
                garis = BIRU
            else:
                garis = GARIS
            kotak_bulat(c, 2, 2, LEBAR_KARTU - 2, TINGGI_KARTU - 2, 12,
                        fill=BG, outline=garis, dash=(4, 4))
            c.create_text(LEBAR_KARTU // 2, TINGGI_KARTU // 2,
                          text=f"Slot {i + 1} masih kosong - klik untuk merekrut",
                          fill=REDUP, font=(FONT, 10))
            return

        npc = self.data[i]
        warna = self.warna_peran(npc.peran)
        if self.kilat == i:
            latar = "#4d4426"
        elif self.hover == i:
            latar = KARTU_HOVER
        else:
            latar = KARTU
        if self.terpilih == i:
            garis = EMAS
            tebal = 2
        else:
            garis = GARIS
            tebal = 1
        kotak_bulat(c, 2, 2, LEBAR_KARTU - 2, TINGGI_KARTU - 2, 12,
                    fill=latar, outline=garis, width=tebal)

        # ikon peran
        c.create_oval(15, 13, 57, 55, fill=warna, outline="")
        gambar_ikon(c, npc.peran, 36, 34)

        # nama dan peran
        nama = npc.nama
        if len(nama) > 13:
            nama = nama[:10] + "..."
        c.create_text(72, 24, text=nama, anchor="w", fill=TEKS,
                      font=(FONT, 12, "bold"))
        c.create_text(72, 46, text=npc.peran, anchor="w", fill=warna,
                      font=(FONT, 9, "bold"))

        # bar HP dan ATK (panjang bar dianimasikan lewat self.faktor)
        x0 = 236
        for baris in range(2):
            y = 22 + baris * 24
            if baris == 0:
                nama_stat = "HP"
                nilai = npc.hp
                maks = self.maks_hp
                warna_bar = HIJAU
            else:
                nama_stat = "ATK"
                nilai = npc.atk
                maks = self.maks_atk
                warna_bar = ORANYE
            c.create_text(x0 - 8, y, text=nama_stat, anchor="e", fill=REDUP,
                          font=(FONT, 8, "bold"))
            c.create_rectangle(x0, y - 5, x0 + LEBAR_BAR, y + 5,
                               fill=INPUT, outline="")
            panjang = int(LEBAR_BAR * nilai / maks * self.faktor)
            if panjang > 0:
                c.create_rectangle(x0, y - 5, x0 + max(panjang, 4), y + 5,
                                   fill=warna_bar, outline="")
            c.create_text(x0 + LEBAR_BAR + 8, y, text=str(nilai), anchor="w",
                          fill=TEKS, font=(FONT, 9, "bold"))

        # status
        kotak_bulat(c, LEBAR_KARTU - 82, 22, LEBAR_KARTU - 14, 46, 10,
                    fill="#1d3b33", outline="")
        c.create_text(LEBAR_KARTU - 48, 34, text=npc.status, fill=HIJAU,
                      font=(FONT, 9, "bold"))

    def gambar_semua(self):
        for i in range(MAKS_PASUKAN):
            self.gambar_kartu(i)

    def mulai_animasi(self):
        if self.id_animasi is not None:
            self.jendela.after_cancel(self.id_animasi)
        self.faktor = 0.0
        self.langkah_animasi()

    def langkah_animasi(self):
        self.faktor += 0.125
        if self.faktor > 1.0:
            self.faktor = 1.0
        self.gambar_semua()
        if self.faktor < 1.0:
            self.id_animasi = self.jendela.after(25, self.langkah_animasi)
        else:
            self.id_animasi = None

    def hentikan_kilat(self):
        self.kilat = None
        self.gambar_semua()

    # ---------- Logika ----------
    def tekan_enter(self, event):
        self.simpan_npc()

    def tekan_delete(self, event):
        # Jangan hapus NPC kalau tombol Delete dipakai saat mengetik di kolom isian
        if isinstance(event.widget, tk.Entry):
            return
        self.hapus_npc()

    def tekan_refresh(self):
        self.refresh_data()
        self.set_status(f"Data dimuat ulang: {len(self.data)} NPC.")

    def klik_kartu(self, i):
        if i < len(self.data):
            if self.terpilih == i:
                self.terpilih = None
            else:
                self.terpilih = i
            self.gambar_semua()
            if self.terpilih is not None:
                self.set_status(f"{self.data[i].nama} dipilih.")
        else:
            self.entry_nama.focus()

    def kosongkan_form(self):
        self.entry_nama.delete(0, tk.END)
        self.entry_hp.delete(0, tk.END)
        self.entry_atk.delete(0, tk.END)
        self.pilih_peran(DAFTAR_PERAN[0])
        self.entry_nama.focus()

    def refresh_data(self):
        self.data = muat_data()
        self.terpilih = None
        self.maks_hp = 1
        self.maks_atk = 1
        total_hp = 0
        total_atk = 0
        jumlah_peran = []
        for peran in DAFTAR_PERAN:
            jumlah_peran.append(0)
        for npc in self.data:
            total_hp += npc.hp
            total_atk += npc.atk
            if npc.hp > self.maks_hp:
                self.maks_hp = npc.hp
            if npc.atk > self.maks_atk:
                self.maks_atk = npc.atk
            for i in range(len(DAFTAR_PERAN)):
                if npc.peran == DAFTAR_PERAN[i]:
                    jumlah_peran[i] += 1

        self.label_slot.config(text=f"{len(self.data)} / {MAKS_PASUKAN}")
        for i in range(len(DAFTAR_PERAN)):
            self.label_peran[i].config(text=f"{DAFTAR_PERAN[i]}  {jumlah_peran[i]}")

        if len(self.data) == 0:
            self.nilai[0].config(text=f"0 / {MAKS_PASUKAN}")
            self.nilai[1].config(text="-")
            self.nilai[2].config(text="-")
            self.nilai[3].config(text="-")
            self.label_terkuat.config(text="NPC Terkuat : -")
            self.set_status("Belum ada NPC di guild. Rekrut NPC pertamamu!")
        else:
            terkuat = self.data[0]
            for npc in self.data:
                if npc.atk > terkuat.atk:
                    terkuat = npc
            rata_hp = total_hp / len(self.data)
            self.nilai[0].config(text=f"{len(self.data)} / {MAKS_PASUKAN}")
            self.nilai[1].config(text=str(total_hp))
            self.nilai[2].config(text=str(total_atk))
            self.nilai[3].config(text=f"{rata_hp:.1f}")
            self.label_terkuat.config(
                text=f"NPC Terkuat : {terkuat.nama}  (ATK {terkuat.atk})")
            self.set_status(f"Data dimuat: {len(self.data)} NPC.")
        self.mulai_animasi()

    def simpan_npc(self):
        nama = self.entry_nama.get().strip()
        peran = self.peran_dipilih
        hp = self.entry_hp.get().strip()
        atk = self.entry_atk.get().strip()

        daftar_npc = muat_data()
        if len(daftar_npc) >= MAKS_PASUKAN:
            messagebox.showwarning("Peringatan", "Guild penuh! Maksimal 5 NPC.")
            return
        if not nama or not peran or not hp or not atk:
            messagebox.showwarning("Peringatan", "Semua kolom harus diisi!")
            return
        if peran not in DAFTAR_PERAN:
            messagebox.showwarning("Peringatan", "Peran tidak dikenal!")
            return
        if not hp.isdigit() or not atk.isdigit():
            messagebox.showwarning("Peringatan", "HP dan ATK harus berupa angka!")
            return
        if int(hp) <= 0 or int(atk) <= 0:
            messagebox.showwarning("Peringatan", "HP dan ATK harus lebih dari 0!")
            return
        for npc in daftar_npc:
            if npc.nama.lower() == nama.lower():
                messagebox.showwarning("Peringatan", "Nama NPC sudah dipakai!")
                return

        npc_baru = NPC(nama, peran, int(hp), int(atk))
        file_exists = os.path.exists("npc.csv")
        with open("npc.csv", "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Nama", "Peran", "HP", "ATK", "Status"])
            writer.writerow(npc_baru.to_list())

        self.kosongkan_form()
        self.refresh_data()
        self.kilat = len(self.data) - 1
        self.jendela.after(700, self.hentikan_kilat)
        self.set_status(f"{nama} berhasil direkrut.", HIJAU)

    def hapus_npc(self):
        if self.terpilih is None:
            messagebox.showwarning("Peringatan", "Pilih NPC dulu dengan mengklik kartunya!")
            return
        nama = self.data[self.terpilih].nama
        yakin = messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus {nama}?")
        if not yakin:
            return
        sisa = []
        for npc in muat_data():
            if npc.nama != nama:
                sisa.append(npc)
        simpan_data(sisa)
        self.refresh_data()
        self.set_status(f"{nama} berhasil dihapus.", MERAH)

def main():
    jendela = tk.Tk()
    AplikasiGuild(jendela)
    jendela.mainloop()

if __name__ == "__main__":
    main()
