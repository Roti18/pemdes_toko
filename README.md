# Pemrograman Desktop - Toko Kelontong

## Cara Menjalankan

```powershell
.\.venv\Scripts\activate
pip install -r requirements.txt
python code.py
```

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

Tugas:
Sifa -> Kasir
Rendi -> Barang
Roni -> Transaksi
