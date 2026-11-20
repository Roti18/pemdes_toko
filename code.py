import os
import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QTableView

basedir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(basedir, "toko.db")


def setup_database(db):
    """Setup tabel & data awal sekali saja saat file database baru dibuat.
    Bersih tanpa 'IF NOT EXISTS' dan tanpa percabangan 'if count == 0'."""
    query = QSqlQuery(db)

    # --- Tabel Barang (sesuai ERD baru) ---
    query.exec("""CREATE TABLE barang (
        id_barang INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_barang VARCHAR(100) NOT NULL,
        harga INTEGER NOT NULL,
        satuan VARCHAR(20) NOT NULL,
        stok INTEGER NOT NULL DEFAULT 0)""")

    # --- Tabel Penjaga ---
    query.exec("""CREATE TABLE penjaga (
        id_penjaga INTEGER PRIMARY KEY AUTOINCREMENT,
        nama VARCHAR(100) NOT NULL,
        no_telp VARCHAR(20),
        shift VARCHAR(20))""")

    # --- Data Barang (10 item) ---
    query.exec("""INSERT INTO barang (nama_barang, harga, satuan, stok) VALUES
        ('Indomie', 3500, 'bungkus', 200),
        ('Teh Botol', 5000, 'botol', 100),
        ('Beras 5kg', 70000, 'karung', 40),
        ('Chitato', 11000, 'bungkus', 75),
        ('Sabun', 4500, 'pcs', 80),
        ('Roti Tawar', 15000, 'bungkus', 25),
        ('Aqua 600ml', 3000, 'botol', 150),
        ('Minyak Goreng 1L', 18000, 'botol', 60),
        ('Gula Pasir 1kg', 16000, 'kg', 50),
        ('Kopi Sachet', 1500, 'sachet', 300)""")

    # --- Data Penjaga (5 orang) ---
    query.exec("""INSERT INTO penjaga (nama, no_telp, shift) VALUES
        ('Siti Aminah',    '081234500001', 'Pagi'),
        ('Budi Santoso',   '081234500002', 'Siang'),
        ('Rina Wulandari', '081234500003', 'Pagi'),
        ('Agus Salim',     '081234500004', 'Malam'),
        ('Dewi Lestari',   '081234500005', 'Siang')""")


class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.setWindowTitle("Sistem Toko Kelontong")
        self.setMinimumSize(QSize(800, 500))

        # Tab: satu tab untuk tiap tabel
        self.tabs = QTabWidget()

        # --- Tab Barang ---
        self.table = QTableView()
        self.model = QSqlTableModel(self, db=db)
        self.model.setTable("barang")
        self.model.select()

        # Header kolom Barang
        self.model.setHeaderData(0, Qt.Orientation.Horizontal, "ID Barang")
        self.model.setHeaderData(1, Qt.Orientation.Horizontal, "Nama Barang")
        self.model.setHeaderData(2, Qt.Orientation.Horizontal, "Harga (Rp)")
        self.model.setHeaderData(3, Qt.Orientation.Horizontal, "Satuan")
        self.model.setHeaderData(4, Qt.Orientation.Horizontal, "Stok")

        self.table.setModel(self.model)
        self.tabs.addTab(self.table, "Barang")

        # --- Tab Penjaga (bagian: penjaga) ---
        self.table_penjaga = QTableView()
        self.model_penjaga = QSqlTableModel(self, db=db)
        self.model_penjaga.setTable("penjaga")
        self.model_penjaga.select()

        self.model_penjaga.setHeaderData(0, Qt.Orientation.Horizontal, "ID Penjaga")
        self.model_penjaga.setHeaderData(1, Qt.Orientation.Horizontal, "Nama")
        self.model_penjaga.setHeaderData(2, Qt.Orientation.Horizontal, "No. Telp")
        self.model_penjaga.setHeaderData(3, Qt.Orientation.Horizontal, "Shift")

        self.table_penjaga.setModel(self.model_penjaga)
        self.tabs.addTab(self.table_penjaga, "Penjaga")

        self.setCentralWidget(self.tabs)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Cek apakah file database toko.db sudah ada atau belum
    db_is_new = not os.path.exists(DB_PATH)

    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(DB_PATH)

    if not db.open():
        raise RuntimeError(f"Gagal membuka database: {db.lastError().text()}")

    # Jika file database baru pertama kali dibuat, inisialisasi tabel & datanya
    if db_is_new:
        setup_database(db)

    window = MainWindow(db)
    window.show()
    sys.exit(app.exec())
