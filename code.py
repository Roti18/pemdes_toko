import os
import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableView, QTabWidget

basedir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(basedir, "toko.db")


def setup_database(db):
    """Setup tabel & data awal sekali saja saat file database baru dibuat.
    Bersih tanpa 'IF NOT EXISTS' dan tanpa percabangan 'if count == 0'."""
    query = QSqlQuery(db)
    query.exec("PRAGMA foreign_keys = ON")

    query.exec("""CREATE TABLE kategori (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT NOT NULL)""")

    query.exec("""CREATE TABLE barang (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT NOT NULL,
        harga INTEGER,
        id_kategori INTEGER NOT NULL REFERENCES kategori(id))""")

    # --- Tabel penjaga (bagian: penjaga) ---------------------------------
    # Dibuat sebelum tabel transaksi, karena transaksi akan memakai
    # id_penjaga sebagai foreign key.
    query.exec("""CREATE TABLE penjaga (
        id_penjaga INTEGER PRIMARY KEY AUTOINCREMENT,
        nama       VARCHAR(100) NOT NULL,
        no_telp    VARCHAR(20),
        shift      VARCHAR(20))""")

    query.exec("""INSERT INTO kategori (nama) VALUES
        ('Makanan'),
        ('Minuman'),
        ('Sembako'),
        ('Snack'),
        ('Lainnya')""")

    query.exec("""INSERT INTO barang (nama, harga, id_kategori) VALUES
        ('Indomie', 3500, 1),
        ('Teh Botol', 5000, 2),
        ('Beras 5kg', 70000, 3),
        ('Chitato', 11000, 4),
        ('Sabun', 4500, 5)""")

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

        # --- Tab Barang (kode rekan, tidak diubah) ---
        self.table = QTableView()
        self.model = QSqlTableModel(self, db=db)
        self.model.setTable("barang")
        self.model.select()  # Fetch data dari database

        self.model.setHeaderData(0, Qt.Orientation.Horizontal, "ID")
        self.model.setHeaderData(1, Qt.Orientation.Horizontal, "Nama Barang")
        self.model.setHeaderData(2, Qt.Orientation.Horizontal, "Harga (Rp)")
        self.model.setHeaderData(3, Qt.Orientation.Horizontal, "ID Kategori")

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

    # Jika file toko.db baru pertama kali dibuat, inisialisasi tabel & datanya
    if db_is_new:
        setup_database(db)

    window = MainWindow(db)
    window.show()
    sys.exit(app.exec())