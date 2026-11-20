# Sistem Manajemen Toko Kelontong
Aplikasi Desktop Pengelolaan Toko Kelontong Berbasis Python & PyQt6 (UAS Pemrograman Desktop).

---

## Pembagian Tugas

| No | Anggota | Tugas / Modul |
| :---: | :--- | :--- |
| 1 | Sifa | Kasir |
| 2 | Rendi | Barang |
| 3 | Roni | Transaksi |

---

## Cara Menjalankan

```powershell
.\.venv\Scripts\activate
pip install -r requirements.txt
python code.py
```

---

## Entity Relationship Diagram (ERD)

```mermaid
erDiagram
  BARANG ||--o{ TRANSAKSI : terjual_dalam
  PENJAGA ||--o{ TRANSAKSI : melayani

  BARANG {
    int id_barang PK
    varchar nama_barang
    int harga
    varchar satuan
    int stok
  }
  PENJAGA {
    int id_penjaga PK
    varchar nama
    varchar no_telp
    varchar shift
  }
  TRANSAKSI {
    int id_transaksi PK
    int id_barang FK
    int id_penjaga FK
    varchar no_nota
    date tanggal
    int qty
    int total_harga
  }
```
