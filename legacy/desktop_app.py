from __future__ import annotations

import sys
from datetime import date

import pandas as pd
from PySide6 import QtCore, QtGui, QtWidgets

from api.scanner.config import load_config
from api.scanner.engine import run_scan
from api.scanner.universes import load_universe

APP_TITLE = "Morning Uptrend Scanner (Legacy Desktop)"


class ResultsModel(QtCore.QAbstractTableModel):
    HEADERS = ["Rank", "Ticker", "Score", "Gap %", "Rel $Vol", "Avg $Vol", "Reasons"]

    def __init__(self, rows: list[dict[str, object]] | None = None):
        super().__init__()
        self.rows = rows or []

    def rowCount(self, parent=None):  # type: ignore[override]
        return len(self.rows)

    def columnCount(self, parent=None):  # type: ignore[override]
        return len(self.HEADERS)

    def data(self, index, role=QtCore.Qt.DisplayRole):  # type: ignore[override]
        if not index.isValid():
            return None
        row = self.rows[index.row()]
        col = index.column()
        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return str(index.row() + 1)
            if col == 1:
                return row.get("ticker", "")
            if col == 2:
                return str(row.get("score", ""))
            if col == 3:
                value = row.get("gap_pct", None)
                return f"{float(value):.2f}" if value is not None and pd.notna(value) else "na"
            if col == 4:
                value = row.get("rel_dollar_vol", None)
                return f"{float(value):.2f}" if value is not None and pd.notna(value) else "na"
            if col == 5:
                value = row.get("avg20_dollar_vol", None)
                return f"{float(value):.0f}" if value is not None and pd.notna(value) else "na"
            if col == 6:
                reasons = row.get("reasons", [])
                return "; ".join(reasons) if isinstance(reasons, list) else reasons
        if role == QtCore.Qt.BackgroundRole:
            score = row.get("score", 0)
            if score >= 9:
                return QtGui.QBrush(QtGui.QColor(0, 80, 0))
            if score >= 6:
                return QtGui.QBrush(QtGui.QColor(0, 55, 0))
            if score >= 3:
                return QtGui.QBrush(QtGui.QColor(0, 35, 0))
            if score <= 0:
                return QtGui.QBrush(QtGui.QColor(30, 30, 30))
        if role == QtCore.Qt.ForegroundRole:
            return QtGui.QBrush(QtGui.QColor(230, 230, 230))
        return None

    def headerData(self, section, orientation, role):  # type: ignore[override]
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return self.HEADERS[section]
        return None


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1100, 650)
        self.cfg = load_config()
        self._build_ui()
        self._apply_dark_theme()

    def _build_ui(self) -> None:
        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)
        self.setCentralWidget(central)

        top = QtWidgets.QHBoxLayout()
        layout.addLayout(top)
        top.addWidget(QtWidgets.QLabel("Universe:"))

        self.universe_combo = QtWidgets.QComboBox()
        self.universe_combo.addItems(["sp500", "nasdaq100", "tech_sample.csv", "healthcare_sample.csv"])
        self.universe_combo.setCurrentText(self.cfg.get("universe_default", "sp500"))
        top.addWidget(self.universe_combo)

        top.addWidget(QtWidgets.QLabel("Data Source:"))
        self.data_combo = QtWidgets.QComboBox()
        self.data_combo.addItems(["Live (yfinance)", "Sample Data (offline)"])
        self.data_combo.setCurrentText("Live (yfinance)")
        top.addWidget(self.data_combo)

        self.run_btn = QtWidgets.QPushButton("Run Scan")
        self.run_btn.clicked.connect(self.on_run)
        top.addWidget(self.run_btn)

        self.export_btn = QtWidgets.QPushButton("Export CSV")
        self.export_btn.clicked.connect(self.on_export)
        self.export_btn.setEnabled(False)
        top.addWidget(self.export_btn)
        top.addStretch()

        self.status_label = QtWidgets.QLabel("Ready.")
        layout.addWidget(self.status_label)

        self.table = QtWidgets.QTableView()
        self.model = ResultsModel([])
        self.table.setModel(self.model)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)

    def _apply_dark_theme(self) -> None:
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(18, 18, 18))
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(24, 24, 24))
        palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(28, 28, 28))
        palette.setColor(QtGui.QPalette.Text, QtGui.QColor(230, 230, 230))
        palette.setColor(QtGui.QPalette.Button, QtGui.QColor(40, 40, 40))
        palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(230, 230, 230))
        self.setPalette(palette)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QHeaderView::section { background-color: #2c2c2c; color: #e6e6e6; }")

    def on_run(self) -> None:
        tickers = load_universe(self.universe_combo.currentText())
        mode = "sample" if "Sample" in self.data_combo.currentText() else "live"
        self.status_label.setText(f"Running scan on {len(tickers)} symbols...")
        QtWidgets.QApplication.processEvents()
        dataframe = run_scan(tickers, self.cfg, mode=mode)
        rows = dataframe.to_dict(orient="records")
        self.model = ResultsModel(rows)
        self.table.setModel(self.model)
        self.export_btn.setEnabled(bool(rows))
        self.status_label.setText(f"Scan complete: {len(rows)} rows")

    def on_export(self) -> None:
        dataframe = pd.DataFrame(self.model.rows)
        if dataframe.empty:
            return
        dataframe["reasons"] = dataframe["reasons"].apply(lambda value: "; ".join(value) if isinstance(value, list) else value)
        output_name = self.cfg.get("output", {}).get("csv_path", "watchlist_{date}.csv").format(date=date.today().isoformat())
        dataframe.to_csv(output_name, index=False)
        QtWidgets.QMessageBox.information(self, "Export", f"Saved: {output_name}")


def main() -> None:
    application = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(application.exec())


if __name__ == "__main__":
    main()
