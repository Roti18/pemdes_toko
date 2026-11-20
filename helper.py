import os
import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTableView,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

basedir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(basedir, "toko.db")


def setup_database(db):
    """Inisialisasi tabel dan data awal berdasarkan ERD di README.md.
    Otomatis memperbarui jika database masih memakai skema lama.
    """
    query = QSqlQuery(db)
    query.exec("PRAGMA foreign_keys = OFF")

    # Periksa apakah tabel barang masih memakai skema lama (misal kolom 'id_kategori')
    query.exec("PRAGMA table_info(barang)")
    kolom_barang = []
    while query.next():
        kolom_barang.append(query.value(1))

    # Jika tabel barang belum ada atau masih skema lama (tanpa nama_barang), reset tabel
    if "nama_barang" not in kolom_barang:
        query.exec("DROP TABLE IF EXISTS transaksi")
        query.exec("DROP TABLE IF EXISTS barang")
        query.exec("DROP TABLE IF EXISTS penjaga")
        query.exec("DROP TABLE IF EXISTS kategori")

    # 1. Tabel BARANG / PRODUK
    query.exec("""CREATE TABLE IF NOT EXISTS barang (
        id_barang INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_barang TEXT NOT NULL,
        harga INTEGER NOT NULL,
        satuan TEXT NOT NULL,
        stok INTEGER NOT NULL DEFAULT 0
    )""")

    # 2. Tabel PENJAGA
    query.exec("""CREATE TABLE IF NOT EXISTS penjaga (
        id_penjaga INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT NOT NULL,
        no_telp TEXT,
        shift TEXT
    )""")

    # 3. Tabel TRANSAKSI
    query.exec("""CREATE TABLE IF NOT EXISTS transaksi (
        id_transaksi INTEGER PRIMARY KEY AUTOINCREMENT,
        id_barang INTEGER NOT NULL REFERENCES barang(id_barang),
        id_penjaga INTEGER NOT NULL REFERENCES penjaga(id_penjaga),
        no_nota TEXT NOT NULL,
        tanggal TEXT NOT NULL,
        qty INTEGER NOT NULL,
        total_harga INTEGER NOT NULL
    )""")

    query.exec("PRAGMA foreign_keys = ON")

    # Isi data awal jika tabel masih kosong
    query.exec("SELECT COUNT(*) FROM barang")
    if query.next() and query.value(0) == 0:
        query.exec("""INSERT INTO barang (id_barang, nama_barang, harga, satuan, stok) VALUES
            (1, 'Indomie Goreng', 3500, 'Bungkus', 50),
            (2, 'Teh Botol Sosro', 5000, 'Botol', 30),
            (3, 'Beras Ramos 5kg', 72000, 'Karung', 15),
            (4, 'Minyak Goreng 1L', 18000, 'Pouch', 20),
            (5, 'Telur Ayam 1kg', 28000, 'Kg', 25)""")

    query.exec("SELECT COUNT(*) FROM penjaga")
    if query.next() and query.value(0) == 0:
        query.exec("""INSERT INTO penjaga (id_penjaga, nama, no_telp, shift) VALUES
            (1, 'Budi Santoso', '081234567890', 'Pagi'),
            (2, 'Siti Rahma', '081298765432', 'Siang'),
            (3, 'Agus Prayitno', '081311223344', 'Malam'),
            (4, 'Dewi Lestari', '081355667788', 'Pagi'),
            (5, 'Eko Wahyudi', '081399887766', 'Siang')""")

    query.exec("SELECT COUNT(*) FROM transaksi")
    if query.next() and query.value(0) == 0:
        query.exec("""INSERT INTO transaksi (id_transaksi, id_barang, id_penjaga, no_nota, tanggal, qty, total_harga) VALUES
            (1, 1, 1, 'TRX-001', '2026-11-01', 3, 10500),
            (2, 2, 2, 'TRX-002', '2026-11-01', 2, 10000),
            (3, 3, 1, 'TRX-003', '2026-11-02', 1, 72000),
            (4, 4, 3, 'TRX-004', '2026-11-02', 2, 36000),
            (5, 5, 4, 'TRX-005', '2026-11-03', 1, 28000)""")


def buat_table_view(db, nama_tabel, headers, kolom_filter, aksi_record=None):
    widget = QWidget()

    model = QSqlTableModel(widget, db=db)
    model.setTable(nama_tabel)
    model.select()
    for i, judul in enumerate(headers):
        model.setHeaderData(i, Qt.Orientation.Horizontal, judul)

    table = QTableView()
    table.setModel(model)

    filter1 = QLineEdit()
    filter1.setPlaceholderText("Filter " + kolom_filter[0])
    filter2 = QLineEdit()
    filter2.setPlaceholderText("Filter " + kolom_filter[1])
    tombol = QPushButton("Buka Record")

    def terapkan_filter():
        kondisi = []
        isi1 = filter1.text().replace("'", "''").strip()
        isi2 = filter2.text().replace("'", "''").strip()
        if isi1 != "":
            kondisi.append(f"CAST({kolom_filter[0]} AS TEXT) LIKE '%{isi1}%'")
        if isi2 != "":
            kondisi.append(f"CAST({kolom_filter[1]} AS TEXT) LIKE '%{isi2}%'")

        filter_str = " AND ".join(kondisi)
        model.setFilter(filter_str)
        model.select()  # Refresh model agar hasil filter langsung tampil di tabel

    def klik_tombol():
        if aksi_record:
            baris = table.currentIndex().row()
            if baris < 0:
                baris = 0
            aksi_record(baris)

    filter1.textChanged.connect(terapkan_filter)
    filter2.textChanged.connect(terapkan_filter)
    tombol.clicked.connect(klik_tombol)

    atas = QHBoxLayout()
    atas.addWidget(filter1)
    atas.addWidget(filter2)
    atas.addWidget(tombol)

    layout = QVBoxLayout()
    layout.addLayout(atas)
    layout.addWidget(table)
    widget.setLayout(layout)

    return widget, model


class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.setWindowTitle("Uji Coba View Tabel Toko Kelontong")
        self.setMinimumSize(QSize(900, 550))

        tabs = QTabWidget()

        # 1. Tab Tabel Transaksi
        headers_transaksi = [
            "ID Transaksi",
            "ID Barang",
            "ID Penjaga",
            "No. Nota",
            "Tanggal",
            "Qty",
            "Total (Rp)",
        ]
        tab_transaksi, self.model_transaksi = buat_table_view(
            db,
            "transaksi",
            headers_transaksi,
            ["tanggal", "no_nota"],
            self.buka_record_transaksi,
        )
        tabs.addTab(tab_transaksi, "Tabel Transaksi")

        # 2. Tab Tabel Produk / Barang
        headers_barang = [
            "ID Barang",
            "Nama Barang",
            "Harga (Rp)",
            "Satuan",
            "Stok",
        ]
        tab_barang, self.model_barang = buat_table_view(
            db,
            "barang",
            headers_barang,
            ["nama_barang", "satuan"],
            self.buka_record_barang,
        )
        tabs.addTab(tab_barang, "Tabel Produk / Barang")

        self.setCentralWidget(tabs)

    def buka_record_transaksi(self, baris):
        print("Buka transaksi baris ke-", baris)

    def buka_record_barang(self, baris):
        print("Buka produk baris ke-", baris)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(DB_PATH)

    if not db.open():
        raise RuntimeError(f"Gagal membuka database: {db.lastError().text()}")

    setup_database(db)

    window = MainWindow(db)
    window.show()
    sys.exit(app.exec())
