from __future__ import annotations
import sys
from datetime import date
import pandas as pd
from PySide6 import QtCore, QtGui, QtWidgets

from universes import load_universe         # ✅ correct place for load_universe
from scanner_core import run_scan           # scoring + data fetcher
import yaml

APP_TITLE = "Morning Uptrend Scanner (v3)"

class ResultsModel(QtCore.QAbstractTableModel):
    HEADERS = ["Rank", "Ticker", "Score", "Gap %", "Rel $Vol", "Avg $Vol", "Reasons"]
    def __init__(self, rows=None):
        super().__init__()
        self.rows = rows or []

    def rowCount(self, parent=None): return len(self.rows)
    def columnCount(self, parent=None): return len(self.HEADERS)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid(): return None
        r = self.rows[index.row()]
        col = index.column()
        if role == QtCore.Qt.DisplayRole:
            if col == 0: return str(index.row()+1)
            if col == 1: return r.get("ticker","")
            if col == 2: return str(r.get("score",""))
            if col == 3:
                v = r.get("gap_pct", None)
                return f"{float(v):.2f}" if v is not None and pd.notna(v) else "na"
            if col == 4:
                v = r.get("rel_dollar_vol", None)
                return f"{float(v):.2f}" if v is not None and pd.notna(v) else "na"
            if col == 5:
                v = r.get("avg20_dollar_vol", None)
                return f"{float(v):.0f}" if v is not None and pd.notna(v) else "na"
            if col == 6: return r.get("reasons","")
        if role == QtCore.Qt.BackgroundRole:
            s = r.get("score", 0)
            # subtle green gradient by score; gray for <=0
            if s >= 9:   return QtGui.QBrush(QtGui.QColor(0, 80, 0))
            if s >= 6:   return QtGui.QBrush(QtGui.QColor(0, 55, 0))
            if s >= 3:   return QtGui.QBrush(QtGui.QColor(0, 35, 0))
            if s <= 0:   return QtGui.QBrush(QtGui.QColor(30, 30, 30))
        if role == QtCore.Qt.ForegroundRole:
            return QtGui.QBrush(QtGui.QColor(230, 230, 230))
        return None

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return self.HEADERS[section]
        return None

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1100, 650)

        # load config.yaml (weights, filters, etc.)
        with open("config.yaml","r") as f:
            self.cfg = yaml.safe_load(f)

        self._build_ui()
        self._apply_dark_theme()

    def _build_ui(self):
        central = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(central)
        self.setCentralWidget(central)

        # Top controls
        top = QtWidgets.QHBoxLayout()
        v.addLayout(top)

        top.addWidget(QtWidgets.QLabel("Universe:"))
        self.universe_combo = QtWidgets.QComboBox()
        # You can add more CSVs into universes/ and select them here
        self.universe_combo.addItems(["sp500","nasdaq100","universes/tech_sample.csv","universes/healthcare_sample.csv"])
        self.universe_combo.setCurrentText(self.cfg.get("universe_default","sp500"))
        top.addWidget(self.universe_combo)

        top.addWidget(QtWidgets.QLabel("Data Source:"))
        self.data_combo = QtWidgets.QComboBox()
        self.data_combo.addItems(["Live (yfinance)","Sample Data (offline)"])
        self.data_combo.setCurrentText("Live (yfinance)")
        top.addWidget(self.data_combo)

        self.run_btn = QtWidgets.QPushButton("Run Scan")
        self.run_btn.clicked.connect(self.on_run)
        top.addWidget(self.run_btn)

        self.refresh_btn = QtWidgets.QPushButton("Refresh (F5)")
        self.refresh_btn.clicked.connect(self.on_run)
        top.addWidget(self.refresh_btn)

        self.export_btn = QtWidgets.QPushButton("Export CSV")
        self.export_btn.clicked.connect(self.on_export)
        self.export_btn.setEnabled(False)
        top.addWidget(self.export_btn)

        top.addStretch()

        self.status_label = QtWidgets.QLabel("Ready.")
        v.addWidget(self.status_label)

        # Table
        self.table = QtWidgets.QTableView()
        self.model = ResultsModel([])
        self.table.setModel(self.model)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        v.addWidget(self.table)

        # F5 shortcut for refresh
        shortcut = QtGui.QShortcut(QtGui.QKeySequence("F5"), self)
        shortcut.activated.connect(self.on_run)

    def _apply_dark_theme(self):
        pal = self.palette()
        pal.setColor(QtGui.QPalette.Window, QtGui.QColor(18,18,18))
        pal.setColor(QtGui.QPalette.Base, QtGui.QColor(24,24,24))
        pal.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(28,28,28))
        pal.setColor(QtGui.QPalette.Text, QtGui.QColor(230,230,230))
        pal.setColor(QtGui.QPalette.Button, QtGui.QColor(40,40,40))
        pal.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(230,230,230))
        self.setPalette(pal)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QHeaderView::section { background-color: #2c2c2c; color: #e6e6e6; }")

    def on_run(self):
        universe_sel = self.universe_combo.currentText()
        # --- Load tickers robustly (handles pandas objects) ---
        try:
            tk = load_universe(universe_sel)
            tickers = [str(t).strip().upper() for t in list(tk) if str(t).strip()]
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Universe Error", str(e))
            return

        mode = "sample" if "Sample" in self.data_combo.currentText() else "live"

        self.status_label.setText(f"Running scan on {len(tickers)} symbols ({universe_sel}, {mode})...")
        QtWidgets.QApplication.processEvents()

        try:
            df = run_scan(tickers, self.cfg, mode=mode)
        except Exception as e:
            # show full traceback in “Details”
            import traceback
            m = QtWidgets.QMessageBox(self)
            m.setIcon(QtWidgets.QMessageBox.Critical)
            m.setWindowTitle("Scan Error")
            m.setText(str(e))
            m.setDetailedText(traceback.format_exc())
            m.exec()
            return

        rows = df.to_dict(orient="records")
        self.model = ResultsModel(rows)
        self.table.setModel(self.model)
        self.export_btn.setEnabled(len(rows) > 0)
        self.status_label.setText(f"Scan complete: {len(rows)} rows")

    def on_export(self):
        df = pd.DataFrame(self.model.rows)
        if df.empty:
            QtWidgets.QMessageBox.information(self, "Export", "No rows to export.")
            return
        out = f"watchlist_{date.today().isoformat()}.csv"
        df.to_csv(out, index=False)
        QtWidgets.QMessageBox.information(self, "Export", f"Saved: {out}")

def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
