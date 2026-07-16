# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, QtCore, QtGui
# 🚀 徹底移除 pyplot，改用純物件導向的 Figure 確保零記憶體洩漏
from matplotlib.figure import Figure 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from scipy.optimize import curve_fit, minimize

# ==========================================
# 核心數學與電路邏輯
# ==========================================
def gaussian(x, amp, cen, wid):
    return amp * np.exp(-(x - cen)**2 / (2 * wid**2))

def multi_gaussian(x, *params):
    y = np.zeros_like(x)
    for i in range(0, len(params), 3):
        y += gaussian(x, params[i], params[i+1], params[i+2])
    return y

def ecm_circuit_solver(freq, R_ohm, L, peak_params):
    w = 2 * np.pi * freq
    Z = np.ones_like(freq, dtype=complex) * R_ohm
    Z += 1j * w * L
    for p in peak_params:
        R, Q, alpha = p['R'], p['Q'], p['alpha']
        if Q > 0 and R > 0:
            Z_CPE = 1.0 / (Q * (1j * w)**alpha)
            Z += 1.0 / (1.0 / R + 1.0 / Z_CPE)
    return Z


# ==========================================
# 模組 1: 數據匯入前處理 (DataImportPreprocessor)
# ==========================================
class DataImportPreprocessor(QtWidgets.QDialog):
    def __init__(self, parent_gui, file_path):
        super().__init__(parent_gui)
        self.parent_gui = parent_gui
        self.file_path = file_path
        self.setWindowTitle("EIS 數據導入前處理面板 (OpenEIS)")
        self.resize(850, 600)
        
        self.skip_rows = 0
        self.invert_z_imag = False
        self.raw_lines = []
        self.final_df = None
        
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            self.raw_lines = f.readlines()
            
        self.init_ui()
        self.preview_data()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        ctrl_layout = QtWidgets.QHBoxLayout()
        
        ctrl_layout.addWidget(QtWidgets.QLabel("跳過前排行數 (Skip Rows):"))
        self.spin_skip = QtWidgets.QSpinBox()
        self.spin_skip.setRange(0, max(0, len(self.raw_lines) - 5))
        self.spin_skip.setValue(0)
        self.spin_skip.valueChanged.connect(self.on_skip_changed)
        ctrl_layout.addWidget(self.spin_skip)
        
        ctrl_layout.addSpacing(20)
        
        self.btn_toggle_imag = QtWidgets.QPushButton("🔄 一鍵切換第3欄 (Z'') 正負號 (* -1)")
        self.btn_toggle_imag.setCheckable(True)
        self.btn_toggle_imag.setStyleSheet("background-color: #E0E0E0; font-weight: bold;")
        self.btn_toggle_imag.clicked.connect(self.on_toggle_invert)
        ctrl_layout.addWidget(self.btn_toggle_imag)
        
        ctrl_layout.addStretch()
        main_layout.addLayout(ctrl_layout)
        
        main_layout.addWidget(QtWidgets.QLabel("<b>數據解析實時預覽 (僅顯示前30行):</b>"))
        self.table_widget = QtWidgets.QTableWidget()
        main_layout.addWidget(self.table_widget)
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_cancel = QtWidgets.QPushButton("取消導入")
        btn_cancel.clicked.connect(self.reject)
        
        btn_confirm = QtWidgets.QPushButton("確定導入主程式 (Confirm)")
        btn_confirm.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; height: 30px;")
        btn_confirm.clicked.connect(self.on_confirm)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_confirm)
        main_layout.addLayout(btn_layout)

    def preview_data(self):
        try:
            active_lines = self.raw_lines[self.skip_rows:]
            parsed_data = []
            for line in active_lines[:30]:
                line_str = line.strip()
                if not line_str: continue
                delimiter = ',' if ',' in line_str else None
                parts = line_str.split(delimiter)
                if len(parts) >= 3:
                    parsed_data.append(parts[:3])
            
            if not parsed_data:
                self.table_widget.setRowCount(0)
                self.table_widget.setColumnCount(0)
                return
                
            self.table_widget.setRowCount(len(parsed_data))
            self.table_widget.setColumnCount(3)
            self.table_widget.setHorizontalHeaderLabels(["Col 1 (Freq)", "Col 2 (Z')", "Col 3 (Z'')"])
            
            for row_idx, row_data in enumerate(parsed_data):
                for col_idx, val in enumerate(row_data):
                    display_val = val
                    if col_idx == 2 and self.invert_z_imag:
                        try: display_val = f"{-1.0 * float(val):.6e}"
                        except ValueError: pass 
                    item = QtWidgets.QTableWidgetItem(display_val)
                    if col_idx == 2 and self.invert_z_imag:
                        item.setBackground(QtGui.QColor("#FFF9C4"))
                    self.table_widget.setItem(row_idx, col_idx, item)
            self.table_widget.resizeColumnsToContents()
        except Exception as e: print(f"預覽解析異常: {e}")

    def on_skip_changed(self):
        self.skip_rows = self.spin_skip.value()
        self.preview_data()

    def on_toggle_invert(self):
        self.invert_z_imag = self.btn_toggle_imag.isChecked()
        if self.invert_z_imag:
            self.btn_toggle_imag.setStyleSheet("background-color: #FFCDD2; color: #B71C1C; font-weight: bold;")
        else:
            self.btn_toggle_imag.setStyleSheet("background-color: #E0E0E0; font-weight: bold;")
        self.preview_data()

    def on_confirm(self):
        try:
            active_lines = self.raw_lines[self.skip_rows:]
            full_data = []
            for line in active_lines:
                line_str = line.strip()
                if not line_str: continue
                delimiter = ',' if ',' in line_str else None
                parts = line_str.split(delimiter)
                if len(parts) >= 3:
                    try:
                        f_val = float(parts[0])
                        z1_val = float(parts[1])
                        z2_val = float(parts[2])
                        if self.invert_z_imag: z2_val = -1.0 * z2_val
                        full_data.append([f_val, z1_val, z2_val])
                    except ValueError: continue
            
            if not full_data:
                QtWidgets.QMessageBox.warning(self, "錯誤", "未找到有效的數值阻抗數據，請檢查 Skip Rows 設定。")
                return
                
            self.final_df = pd.DataFrame(full_data, columns=['freq', 'Z_prime', 'Z_double_prime'])
            self.accept()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "異常", f"數據封裝失敗: {e}")


# ==========================================
# 模組 2: 互動式噪聲點修飾 (DataCleaningWindow)
# ==========================================
class DataCleaningWindow(QtWidgets.QDialog):
    def __init__(self, parent_gui, eis_data):
        super().__init__(parent_gui)
        self.parent_gui = parent_gui
        self.data = eis_data
        self.setWindowTitle("EIS 實驗跳動點修飾介面 (Interactive Data Cleaner)")
        self.resize(1300, 800)
        
        self.freq_list = list(self.data.freq)
        self.z_prime_list = list(self.data.Z_exp.real)
        self.z_double_list = list(self.data.Z_exp.imag)
        self.deleted_points = []
        
        self.init_ui()
        self.refresh_plots_and_list()

    def init_ui(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        ctrl_layout = QtWidgets.QVBoxLayout()
        
        ctrl_layout.addWidget(QtWidgets.QLabel("<h3>互動式數據修飾控制</h3>"))
        ctrl_layout.addWidget(QtWidgets.QLabel("💡 <b>操作說明:</b><br>直接用滑鼠點擊右側 <b>Nyquist 圖</b>上的任意圓點即可剔除該噪聲點。"))
        
        self.lbl_count = QtWidgets.QLabel("當前剩餘點數: --")
        self.lbl_count.setStyleSheet("font-weight: bold; color: #1565C0;")
        ctrl_layout.addWidget(self.lbl_count)
        
        ctrl_layout.addWidget(QtWidgets.QLabel("<b>當前有效數據點清單:</b>"))
        self.list_widget = QtWidgets.QListWidget()
        ctrl_layout.addWidget(self.list_widget)
        
        btn_undo = QtWidgets.QPushButton("↩️ 復原上一步刪除 (Undo)")
        btn_undo.clicked.connect(self.undo_last_deletion)
        ctrl_layout.addWidget(btn_undo)
        
        btn_reset = QtWidgets.QPushButton("🔄 重置所有修改 (Reset)")
        btn_reset.clicked.connect(self.reset_data)
        ctrl_layout.addWidget(btn_reset)
        
        ctrl_layout.addSpacing(20)
        
        btn_confirm = QtWidgets.QPushButton("💾 完成修飾，儲存並返回主介面")
        btn_confirm.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; height: 35px;")
        btn_confirm.clicked.connect(self.on_confirm_save)
        ctrl_layout.addWidget(btn_confirm)
        main_layout.addLayout(ctrl_layout, stretch=1)
        
        plot_lay = QtWidgets.QVBoxLayout()
        # 🚀 使用純 OOP Figure
        self.figure = Figure(figsize=(8, 8))
        self.ax_nyq = self.figure.add_subplot(211)
        self.ax_bode = self.figure.add_subplot(212)
        
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        plot_lay.addWidget(self.toolbar)
        plot_lay.addWidget(self.canvas)
        main_layout.addWidget(self.canvas, stretch=2)
        
        self.canvas.mpl_connect('pick_event', self.on_pick)

    def refresh_plots_and_list(self):
        self.lbl_count.setText(f"當前有效數據點數: {len(self.freq_list)} 點")
        self.list_widget.clear()
        for i in range(len(self.freq_list)):
            self.list_widget.addItem(f"[{i+1}] Freq: {self.freq_list[i]:.2f} Hz | Z: {self.z_prime_list[i]:.2f} + j({self.z_double_list[i]:.2f})")
            
        self.ax_nyq.clear()
        self.ax_nyq.plot(self.z_prime_list, [-z for z in self.z_double_list], 'ro', label='Active Data', picker=5, markersize=6)
        if self.deleted_points:
            del_z1 = [p[1] for p in self.deleted_points]
            del_z2 = [-p[2] for p in self.deleted_points]
            self.ax_nyq.plot(del_z1, del_z2, 'o', color='#E0E0E0', label='Removed', markersize=5, alpha=0.5)
            
        self.ax_nyq.set_xlabel("Z' (Ohm)")
        self.ax_nyq.set_ylabel("-Z'' (Ohm)")
        self.ax_nyq.set_title("Interactive Nyquist Plot (Click to Remove)")
        self.ax_nyq.grid(True)
        self.ax_nyq.set_aspect('equal', adjustable='datalim')
        self.ax_nyq.legend()
        
        self.ax_bode.clear()
        mag = [np.sqrt(r**2 + i**2) for r, i in zip(self.z_prime_list, self.z_double_list)]
        self.ax_bode.loglog(self.freq_list, mag, 'b-o', markersize=4)
        self.ax_bode.set_xlabel("Frequency (Hz)")
        self.ax_bode.set_ylabel("|Z| (Ohm)")
        self.ax_bode.grid(True, which="both", ls="--", alpha=0.5)
        
        self.figure.tight_layout()
        self.canvas.draw()

    def on_pick(self, event):
        if len(event.ind) == 0: return
        idx = event.ind[0]
        f = self.freq_list.pop(idx)
        z1 = self.z_prime_list.pop(idx)
        z2 = self.z_double_list.pop(idx)
        self.deleted_points.append((f, z1, z2, idx))
        self.refresh_plots_and_list()

    def undo_last_deletion(self):
        if not self.deleted_points: return
        f, z1, z2, original_idx = self.deleted_points.pop()
        self.freq_list.insert(original_idx, f)
        self.z_prime_list.insert(original_idx, z1)
        self.z_double_list.insert(original_idx, z2)
        self.refresh_plots_and_list()

    def reset_data(self):
        self.freq_list = list(self.data.freq)
        self.z_prime_list = list(self.data.Z_exp.real)
        self.z_double_list = list(self.data.Z_exp.imag)
        self.deleted_points.clear()
        self.refresh_plots_and_list()

    def on_confirm_save(self):
        if len(self.freq_list) < 5:
            QtWidgets.QMessageBox.warning(self, "警告", "剩餘點數太少，無法進行後續運算！")
            return
            
        import numpy as np
        from scipy.interpolate import pchip_interpolate
        from .runs import EIS_object
        
        # 1. 取得用戶修剪後剩餘的「乾淨數據點」
        clean_f = np.array(self.freq_list)
        clean_z1 = np.array(self.z_prime_list)
        clean_z2 = np.array(self.z_double_list)
        
        # 2. 確保頻率從小到大排序 (插值演算法的嚴格要求)
        idx_sort = np.argsort(clean_f)
        clean_f = clean_f[idx_sort]
        clean_z1 = clean_z1[idx_sort]
        clean_z2 = clean_z2[idx_sort]
        
        # 3. 🚀 拯救矩陣的核心：建立「完美均勻」的對數頻率網格！
        # 我們維持與原始數據相同的點數，確保矩陣維度不變
        num_points = len(self.data.freq) 
        uniform_f = np.logspace(np.log10(clean_f[0]), np.log10(clean_f[-1]), num_points)
        
        # 4. 執行 PCHIP 保形插值 (PCHIP 不會在缺口處產生失真的物理震盪)
        log_clean_f = np.log10(clean_f)
        log_uniform_f = np.log10(uniform_f)
        
        uniform_z1 = pchip_interpolate(log_clean_f, clean_z1, log_uniform_f)
        uniform_z2 = pchip_interpolate(log_clean_f, clean_z2, log_uniform_f)
        
        # 5. EIS 的標準慣例：頻率通常由高到低排列
        # uniform_f 目前是由小到大，我們將其反轉
        uniform_f = uniform_f[::-1]
        uniform_z1 = uniform_z1[::-1]
        uniform_z2 = uniform_z2[::-1]
            
        # 6. 將這份絕對平滑、網格絕對等距的健康數據，重新灌入 pyDRTtools！
        self.parent_gui.data = EIS_object(uniform_f, uniform_z1, uniform_z2)
        self.parent_gui.inductance_callback()
        self.accept()


# ==========================================
# 模組 3: 高斯峰值物理拆解 (Stage2Window)
# ==========================================
class Stage2Window(QtWidgets.QDialog):
    def __init__(self, parent_gui, eis_data, initial_peaks=3):
        super().__init__(parent_gui)
        self.parent_gui = parent_gui
        self.data = eis_data
        self.initial_peaks = initial_peaks
        self.setWindowTitle("Stage 2: DRT Peak Fitting (OpenEIS)")
        self.resize(1200, 750)
        
        self.tau_data = self.data.out_tau_vec
        self.y_data = self.data.gamma
        self.x_data = np.log(self.tau_data) 
        self.ohmic_R = getattr(self.data, 'R', 0.0)
        self.inductance_L = getattr(self.data, 'L', 0.0)
        
        self.peak_widgets = []
        self.peak_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        self.init_ui()
        self.update_peak_table()

    def init_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        ctrl_layout = QtWidgets.QVBoxLayout()
        
        info_lbl = QtWidgets.QLabel(f"<b>Stage 1 基礎解耦</b><br>R_ohm: {self.ohmic_R:.4e} Ω<br>L: {self.inductance_L:.4e} H")
        ctrl_layout.addWidget(info_lbl)
        
        peak_cnt_lay = QtWidgets.QHBoxLayout()
        peak_cnt_lay.addWidget(QtWidgets.QLabel("設定峰值數量:"))
        self.spin_peaks = QtWidgets.QSpinBox()
        self.spin_peaks.setRange(1, 8)
        self.spin_peaks.setValue(self.initial_peaks)
        self.spin_peaks.valueChanged.connect(self.update_peak_table)
        peak_cnt_lay.addWidget(self.spin_peaks)
        
        # 🚀 變更點 1: 改為「CSV 匯出數據抽樣步長」，用來解決曲線數據過於冗長/精細的問題
        peak_cnt_lay.addWidget(QtWidgets.QLabel(" | CSV 匯出步長:"))
        self.spin_export_step = QtWidgets.QSpinBox()
        self.spin_export_step.setRange(1, 100)
        self.spin_export_step.setValue(1) # 預設 1 (匯出全部)
        self.spin_export_step.setToolTip("設定 CSV 匯出時的數據點跳躍間隔。設為 3 代表每 3 個點取 1 個，大幅縮減 CSV 表格行數。")
        peak_cnt_lay.addWidget(self.spin_export_step)
        
        ctrl_layout.addLayout(peak_cnt_lay)
        
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QtWidgets.QWidget()
        self.grid = QtWidgets.QGridLayout(self.scroll_content)
        self.scroll.setWidget(self.scroll_content)
        ctrl_layout.addWidget(self.scroll)
        
        btn_guess = QtWidgets.QPushButton("檢視初始猜測 (Plot Guess)")
        btn_guess.clicked.connect(self.plot_current_guess)
        ctrl_layout.addWidget(btn_guess)
        
        btn_fit = QtWidgets.QPushButton("執行高斯擬合 (Fit DRT)")
        btn_fit.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        btn_fit.clicked.connect(self.run_fitting)
        ctrl_layout.addWidget(btn_fit)
        
        btn_csv = QtWidgets.QPushButton("匯出 Stage 2 拆解報表 (.csv)")
        btn_csv.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; height: 30px;")
        btn_csv.clicked.connect(self.export_stage2_csv)
        ctrl_layout.addWidget(btn_csv)
        
        btn_next = QtWidgets.QPushButton("匯出至 Stage 3 (CPE 微調)")
        btn_next.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        btn_next.clicked.connect(self.export_to_stage3)
        ctrl_layout.addWidget(btn_next)
        layout.addLayout(ctrl_layout, stretch=1)
        
        plot_lay = QtWidgets.QVBoxLayout()
        self.figure = Figure(figsize=(8, 6))
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        plot_lay.addWidget(self.toolbar)
        plot_lay.addWidget(self.canvas)
        layout.addLayout(plot_lay, stretch=2)
        
        self.plot_raw_data()

    def update_peak_table(self):
        for w in self.peak_widgets:
            w['amp'].deleteLater(); w['cen'].deleteLater(); w['wid'].deleteLater()
            w['fix_amp'].deleteLater(); w['fix_cen'].deleteLater(); w['fix_wid'].deleteLater()
        self.peak_widgets.clear()
        headers = ["峰", "Amp", "Fix", "Pos(x)", "Fix", "Width", "Fix"]
        for col, h in enumerate(headers):
            self.grid.addWidget(QtWidgets.QLabel(f"<b>{h}</b>"), 0, col)
            
        num_peaks = self.spin_peaks.value()
        if len(self.x_data) >= 2:
            default_pos = np.linspace(self.x_data.min(), self.x_data.max(), num_peaks + 2)[1:-1]
        else:
            default_pos = [0.0] * num_peaks
            
        for i in range(num_peaks):
            color = self.peak_colors[i % len(self.peak_colors)]
            lbl = QtWidgets.QLabel(f"P{i+1}")
            lbl.setStyleSheet(f"color: {color}; font-weight: bold;")
            self.grid.addWidget(lbl, i+1, 0)
            w = {
                "amp": QtWidgets.QLineEdit("0.05"), "fix_amp": QtWidgets.QCheckBox(),
                "cen": QtWidgets.QLineEdit(f"{default_pos[i]:.3f}"), "fix_cen": QtWidgets.QCheckBox(),
                "wid": QtWidgets.QLineEdit("0.8"), "fix_wid": QtWidgets.QCheckBox()
            }
            self.grid.addWidget(w["amp"], i+1, 1); self.grid.addWidget(w["fix_amp"], i+1, 2)
            self.grid.addWidget(w["cen"], i+1, 3); self.grid.addWidget(w["fix_cen"], i+1, 4)
            self.grid.addWidget(w["wid"], i+1, 5); self.grid.addWidget(w["fix_wid"], i+1, 6)
            self.peak_widgets.append(w)

    def get_params(self):
        params, bounds_min, bounds_max = [], [], []
        eps = 1e-6
        for w in self.peak_widgets:
            a, c, wid = float(w["amp"].text()), float(w["cen"].text()), float(w["wid"].text())
            params.extend([a, c, wid])
            bounds_min.extend([a-eps if w["fix_amp"].isChecked() else 0.0,
                               c-eps if w["fix_cen"].isChecked() else -np.inf,
                               wid-eps if w["fix_wid"].isChecked() else 1e-3])
            bounds_max.extend([a+eps if w["fix_amp"].isChecked() else np.inf,
                               c+eps if w["fix_cen"].isChecked() else np.inf,
                               wid+eps if w["fix_wid"].isChecked() else np.inf])
        return np.array(params), (bounds_min, bounds_max)

    def plot_raw_data(self, fitted_y=None):
        self.ax.clear()
        self.ax.plot(self.x_data, self.y_data, 'k.', label='DRT Raw Data', alpha=0.5)
        self.ax.set_xlabel(r"$\ln(\tau)$") 
        self.ax.set_ylabel(r"$\gamma(\tau)$")
        if fitted_y is not None:
            self.ax.plot(self.x_data, fitted_y, 'r-', label='Total Fit', linewidth=2)
            params, _ = self.get_params()
            for i in range(0, len(params), 3):
                y_peak = gaussian(self.x_data, params[i], params[i+1], params[i+2])
                self.ax.plot(self.x_data, y_peak, '--', color=self.peak_colors[(i//3)%len(self.peak_colors)])
        self.ax.legend()
        self.canvas.draw()

    def plot_current_guess(self):
        try:
            params, _ = self.get_params()
            self.plot_raw_data(multi_gaussian(self.x_data, *params))
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "錯誤", f"參數讀取錯誤: {e}")

    def run_fitting(self):
        try:
            initial_guess, bounds = self.get_params()
            
            # 回歸全數據擬合，確保物理正確性與精度
            popt, _ = curve_fit(multi_gaussian, self.x_data, self.y_data, p0=initial_guess, bounds=bounds, maxfev=10000)
            
            triplets = []
            for i in range(0, len(popt), 3):
                triplets.append(popt[i:i+3])
            triplets.sort(key=lambda x: x[1]) 
            
            popt_sorted = []
            for t in triplets:
                popt_sorted.extend(t)
                
            for i, w in enumerate(self.peak_widgets):
                w["amp"].setText(f"{popt_sorted[i*3]:.4e}")
                w["cen"].setText(f"{popt_sorted[i*3+1]:.3f}")
                w["wid"].setText(f"{popt_sorted[i*3+2]:.3f}")
                
            self.plot_raw_data(multi_gaussian(self.x_data, *popt_sorted))
            QtWidgets.QMessageBox.information(self, "成功", "高斯自動擬合完成！（峰已依時間常數由小到大嚴格排序）")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "失敗", f"擬合未收斂: {e}")

    def export_stage2_csv(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "儲存 Stage 2 數據分層解耦報表", "", "CSV Files (*.csv)")
        if not path: return
        
        params, _ = self.get_params()
        triplets = []
        for i in range(0, len(params), 3):
            triplets.append(params[i:i+3])
        triplets.sort(key=lambda x: x[1]) 
        
        # 垂直排列的 Meta 資料區塊
        meta_rows = [
            ["--- Stage 1 Parameters ---"],
            ["R_ohm", f"{self.ohmic_R:.6e}"],
            ["L_ind", f"{self.inductance_L:.6e}"],
            ["--- Stage 2 Peak Parameters ---"]
        ]
        
        for idx, t in enumerate(triplets):
            amp, cen, wid = t
            r_n = amp * wid * np.sqrt(2 * np.pi)
            tau_n = np.exp(cen)
            c_n = tau_n / r_n if r_n != 0 else 0.0
            f_n = 1.0 / (2 * np.pi * tau_n) if tau_n != 0 else 0.0
            
            meta_rows.append([f"Peak_{idx+1}_R", f"{r_n:.6e}"])
            meta_rows.append([f"Peak_{idx+1}_C", f"{c_n:.6e}"])
            meta_rows.append([f"Peak_{idx+1}_frequency", f"{f_n:.6e}"])
            
        data_headers = ["tau (s)", "ln(tau)", "gamma_raw", "gamma_fitted_total"]
        for idx in range(len(triplets)):
            data_headers.append(f"gamma_peak_{idx+1}")
            
        flat_sorted_params = []
        for t in triplets: flat_sorted_params.extend(t)
        
        data_body = []
        # 🚀 變更點 2: 讀取介面上的「匯出步長」，大幅精簡生成的行數
        step = self.spin_export_step.value()
        
        for i in range(0, len(self.x_data), step):
            x_val = self.x_data[i]
            y_raw = self.y_data[i]
            y_fit_total = multi_gaussian(x_val, *flat_sorted_params)
            
            # 🚀 變更點 3: 強制限制所有小數位數為科學記號後 6 位，拒絕肥大數據
            row = [f"{np.exp(x_val):.6e}", f"{x_val:.6e}", f"{y_raw:.6e}", f"{y_fit_total:.6e}"]
            for t in triplets:
                amp, cen, wid = t
                y_peak = gaussian(x_val, amp, cen, wid)
                row.append(f"{y_peak:.6e}")
            data_body.append(row)
            
        try:
            import csv
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(meta_rows)
                writer.writerow([]) 
                writer.writerow(["--- Frequency-Time Domain Peak Fitting Curves Block ---"])
                writer.writerow(data_headers)
                writer.writerows(data_body)
            QtWidgets.QMessageBox.information(self, "成功", f"高級 DRT 峰值解耦報表已成功導出至:\n{path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "錯誤", f"儲存失敗: {e}")

    def export_to_stage3(self):
        params, _ = self.get_params()
        triplets = []
        for i in range(0, len(params), 3):
            triplets.append(params[i:i+3])
        triplets.sort(key=lambda x: x[1])
        
        converted_peaks = []
        for t in triplets:
            amp, cen, wid = t
            r_ohm = amp * wid * np.sqrt(2 * np.pi)
            tau = np.exp(cen) 
            q_val = tau / r_ohm if r_ohm != 0 else 1e-6
            converted_peaks.append({'R': r_ohm, 'Q': q_val, 'alpha': 1.0})
            
        self.accept()
        s3 = Stage3Window(self.parent_gui, self.data, self.ohmic_R, self.inductance_L, converted_peaks)
        s3.exec_()

# ==========================================
# 模組 4: 等效電路 ZView 級微調與優化 (Stage3Window)
# ==========================================
class Stage3Window(QtWidgets.QDialog):
    def __init__(self, parent_gui, eis_data, ohmic_r, induct_l, initial_peaks):
        super().__init__(parent_gui)    
        self.data = eis_data
        self.freq = eis_data.freq
        self.z_exp = eis_data.Z_exp
        
        self.peaks = initial_peaks
        self.param_widgets = {}
        self.z_sim_current = None
        
        self.setWindowTitle("Stage 3: ECM Fine-Tune Panel (ZView Error Mode)")
        self.resize(1600, 950)
        
        self.init_ui(ohmic_r, induct_l)
        self.run_simulation()

    def init_ui(self, r_val, l_val):
        layout = QtWidgets.QHBoxLayout(self)
        
        ctrl_lay = QtWidgets.QVBoxLayout()
        ctrl_lay.addWidget(QtWidgets.QLabel("<h3>ECM 參數微調與統計估算</h3>"))
        
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QtWidgets.QWidget()
        self.grid = QtWidgets.QGridLayout(self.scroll_content)
        self.scroll.setWidget(self.scroll_content)
        ctrl_lay.addWidget(self.scroll)
        
        headers = ["Element", "Freedom", "Value", "Error", "Error%"]
        for col, h in enumerate(headers):
            self.grid.addWidget(QtWidgets.QLabel(f"<b>{h}</b>"), 0, col)
            
        self.add_param_row("R_ohm", r_val, 1, is_fixed=True)
        self.add_param_row("L_ind", l_val, 2, is_fixed=True)
        
        row_idx = 3
        for i, p in enumerate(self.peaks):
            self.grid.addWidget(QtWidgets.QLabel(f"<b>-- Peak Branch {i+1} --</b>"), row_idx, 0, 1, 5)
            row_idx += 1
            self.add_param_row(f"R_{i+1}", p['R'], row_idx)
            self.add_param_row(f"Q_{i+1}", p['Q'], row_idx+1)
            self.add_param_row(f"n_{i+1}", p['alpha'], row_idx+2, is_fixed=True)
            row_idx += 3
            
        self.lbl_rmse = QtWidgets.QLabel("當前複數阻抗 RMSE: --")
        self.lbl_rmse.setStyleSheet("color: #D32F2F; font-weight: bold; font-size: 13px;")
        ctrl_lay.addWidget(self.lbl_rmse)
        
        btn_sim = QtWidgets.QPushButton("Simulation")
        btn_sim.clicked.connect(self.run_simulation)
        ctrl_lay.addWidget(btn_sim)
        
        btn_fit = QtWidgets.QPushButton("Fitting (Optimize Parameters)")
        btn_fit.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; height: 35px;")
        btn_fit.clicked.connect(self.run_fitting)
        ctrl_lay.addWidget(btn_fit)
        
        btn_export = QtWidgets.QPushButton("Export Datasheet (.csv)")
        btn_export.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold;")
        btn_export.clicked.connect(self.export_merged_report)
        ctrl_lay.addWidget(btn_export)
        
        layout.addLayout(ctrl_lay, stretch=4)
        
        plot_lay = QtWidgets.QVBoxLayout()
        # 保持上下排版，並提供足夠高度
        self.figure = Figure(figsize=(10, 12))
        self.ax_nyq = self.figure.add_subplot(211)
        self.ax_bode_m = self.figure.add_subplot(212)
        self.ax_bode_p = self.ax_bode_m.twinx()
        
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        plot_lay.addWidget(self.toolbar)
        plot_lay.addWidget(self.canvas)
        layout.addLayout(plot_lay, stretch=6)

    def add_param_row(self, name, val, row, is_fixed=False):
        self.grid.addWidget(QtWidgets.QLabel(name), row, 0)
        combo = QtWidgets.QComboBox()
        combo.addItems(["Free", "Fixed"])

        if is_fixed:
            combo.setCurrentIndex(1)
        else:
            combo.setCurrentIndex(0)
        
        #去除變更後自動計算功能
        #combo.currentIndexChanged.connect(self.run_simulation)
        ent = QtWidgets.QLineEdit(f"{val:.4e}")
        #ent.textChanged.connect(self.run_simulation)
        
        lbl_err = QtWidgets.QLabel("N/A")
        lbl_err_p = QtWidgets.QLabel("N/A")
        
        self.grid.addWidget(combo, row, 1)
        self.grid.addWidget(ent, row, 2)
        self.grid.addWidget(lbl_err, row, 3)
        self.grid.addWidget(lbl_err_p, row, 4)
        
        self.param_widgets[name] = {'mode': combo, 'val': ent, 'err': lbl_err, 'err_p': lbl_err_p}

    def read_ui_params(self):
        r_ohm = float(self.param_widgets["R_ohm"]['val'].text())
        l_ind = float(self.param_widgets["L_ind"]['val'].text())
        p_list = []
        for i in range(len(self.peaks)):
            p_list.append({
                'R': float(self.param_widgets[f"R_{i+1}"]['val'].text()),
                'Q': float(self.param_widgets[f"Q_{i+1}"]['val'].text()),
                'alpha': float(self.param_widgets[f"n_{i+1}"]['val'].text())
            })
        return r_ohm, l_ind, p_list

    def run_simulation(self):
        try:
            r_ohm, l_ind, p_list = self.read_ui_params()
            self.z_sim_current = ecm_circuit_solver(self.freq, r_ohm, l_ind, p_list)
            
            rmse = np.sqrt(np.mean(np.abs(self.z_exp - self.z_sim_current)**2))
            self.lbl_rmse.setText(f"當前複數阻抗加權 RMSE: {rmse:.5e} Ohm")
            self.refresh_plots()
        except Exception as e:
            pass

    def refresh_plots(self):
        if self.z_sim_current is None: return
        
        t_font, l_font, tk_font = 14, 12, 10
        peak_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        
        self.ax_nyq.clear()
        self.ax_nyq.plot(self.z_exp.real, -self.z_exp.imag, 'ko', label='Exp Data', alpha=0.5, markersize=5)
        self.ax_nyq.plot(self.z_sim_current.real, -self.z_sim_current.imag, 'r-', linewidth=2.5, label='Total ECM Model')
        
        r_ohm, l_ind, p_list = self.read_ui_params()
        w = 2 * np.pi * self.freq
        
        # 🚀 修正點：建立一個累計偏移量，起點為歐姆內阻
        current_offset = r_ohm
        
        for i, p in enumerate(p_list):
            R, Q, alpha = p['R'], p['Q'], p['alpha']
            if Q > 0 and R > 0:
                Z_CPE_single = 1.0 / (Q * (1j * w)**alpha)
                Z_branch = 1.0 / (1.0 / R + 1.0 / Z_CPE_single)
                
                color_idx = i % len(peak_colors)
                # 將該分支的實部加上目前的累計偏移量
                self.ax_nyq.plot(Z_branch.real + current_offset, -Z_branch.imag, '--', 
                                 color=peak_colors[color_idx], linewidth=1.5, label=f'Branch {i+1} (R//CPE)')
                
                # 🚀 畫完這個分支後，把它的電阻 R 加進偏移量，作為下一個分支的起點
                current_offset += R
        
        self.ax_nyq.set_xlabel("Z' (Ohm)", fontsize=l_font)
        self.ax_nyq.set_ylabel("-Z'' (Ohm)", fontsize=l_font)
        self.ax_nyq.set_title("Nyquist Plot Breakdown Comparison", fontsize=t_font, pad=10)
        self.ax_nyq.tick_params(axis='both', labelsize=tk_font)
        self.ax_nyq.grid(True, alpha=0.5)
        self.ax_nyq.set_aspect('equal', adjustable='datalim')
        self.ax_nyq.legend(fontsize=10, loc='best', framealpha=0.6)
        
        self.ax_bode_m.clear()
        self.ax_bode_p.clear()
        mag_exp = np.abs(self.z_exp)
        phase_exp = np.angle(self.z_exp, deg=True)
        mag_sim = np.abs(self.z_sim_current)
        phase_sim = np.angle(self.z_sim_current, deg=True)
        
        self.ax_bode_m.loglog(self.freq, mag_exp, 'ko', alpha=0.4, markersize=4)
        self.ax_bode_m.loglog(self.freq, mag_sim, 'r-', linewidth=1.5)
        self.ax_bode_m.set_xlabel("Frequency (Hz)", fontsize=l_font)
        self.ax_bode_m.set_ylabel("|Z| (Ohm)", color='black', fontsize=l_font)
        self.ax_bode_m.tick_params(axis='y', labelcolor='black', labelsize=tk_font)
        self.ax_bode_m.tick_params(axis='x', labelsize=tk_font)
        self.ax_bode_m.grid(True, which="both", ls="--", alpha=0.5)
        self.ax_bode_m.set_title("Bode Plot (Magnitude & Phase)", fontsize=t_font, pad=10)
        
        self.ax_bode_p.semilogx(self.freq, -phase_exp, 'bs', alpha=0.4, markersize=4)
        self.ax_bode_p.semilogx(self.freq, -phase_sim, 'b-', linewidth=1.5)
        self.ax_bode_p.set_ylabel("-Phase Angle (deg)", color='blue', fontsize=l_font)
        self.ax_bode_p.tick_params(axis='y', labelcolor='blue', labelsize=tk_font)
        
        self.ax_bode_p.yaxis.set_label_position("right")
        self.ax_bode_p.yaxis.tick_right()
        
        self.figure.tight_layout(pad=2.0)
        self.canvas.draw()

    def run_fitting(self):
        r_ohm_init, l_ind_init, p_init = self.read_ui_params()
        
        active_keys, x0, bounds = [], [], []
        for k, w in self.param_widgets.items():
            if w['mode'].currentText() == "Free":
                active_keys.append(k)
                x0.append(float(w['val'].text()))
                if 'n_' in k: bounds.append((0.2, 1.05))
                elif 'L_' in k: bounds.append((-np.inf, np.inf))
                else: bounds.append((0.0, np.inf))
                
        if not x0:
            QtWidgets.QMessageBox.information(self, "提示", "所有參數均被鎖定為 Fixed 狀態！")
            return
            
        def objective(x):
            tr, tl, tplist = r_ohm_init, l_ind_init, [dict(p) for p in p_init]
            for idx, key in enumerate(active_keys):
                if key == "R_ohm": tr = x[idx]
                elif key == "L_ind": tl = x[idx]
                else:
                    parts = key.split('_')
                    t, p_idx = parts[0], int(parts[1])-1
                    if t == 'n':
                        tplist[p_idx]['alpha'] = x[idx]
                    else:
                        tplist[p_idx][t] = x[idx]
            z_sim = ecm_circuit_solver(self.freq, tr, tl, tplist)
            return np.sum((self.z_exp.real - z_sim.real)**2 + (self.z_exp.imag - z_sim.imag)**2)

        res = minimize(objective, x0, bounds=bounds, method='L-BFGS-B', options={'ftol': 1e-12, 'gtol': 1e-12})
        
        if res.success:
            dof = len(self.freq)*2 - len(x0)
            mse = res.fun / dof if dof > 0 else 0.0
            
            # ── Proper error estimation via inverse Hessian ──
            try:
                if hasattr(res, 'hess_inv') and res.hess_inv is not None:
                    # L-BFGS-B returns inverse Hessian as LinearOperator → convert to dense
                    if hasattr(res.hess_inv, 'todense'):
                        H_inv = np.asarray(res.hess_inv.todense())
                    else:
                        H_inv = np.asarray(res.hess_inv)
                    cov = H_inv * mse if mse > 0 else H_inv
                else:
                    # Fallback: numerical Jacobian for Hessian approximation
                    eps_fd = 1e-6
                    J = np.zeros((len(self.freq)*2, len(x0)))
                    f0 = objective(res.x)
                    for i in range(len(x0)):
                        x_pert = res.x.copy()
                        x_pert[i] += eps_fd
                        fi = objective(x_pert)
                        J[:, i] = (fi - f0) / eps_fd
                    H_approx = J.T @ J
                    try:
                        cov = np.linalg.inv(H_approx) * mse if mse > 0 else np.linalg.inv(H_approx)
                    except np.linalg.LinAlgError:
                        cov = None
            except Exception:
                cov = None

            for k, w in self.param_widgets.items():
                if k in active_keys:
                    idx = active_keys.index(k)
                    optimized_val = res.x[idx]
                    w['val'].setText(f"{optimized_val:.4e}")
                    
                    if cov is not None and optimized_val != 0:
                        abs_err = np.sqrt(max(cov[idx, idx], 0))
                        rel_err_p = (abs_err / np.abs(optimized_val)) * 100.0
                        w['err'].setText(f"{abs_err:.4e}")
                        w['err_p'].setText(f"{rel_err_p:.2f}%")
                    else:
                        w['err'].setText("估算中")
                        w['err_p'].setText("＜15%")
                else:
                    w['err'].setText("N/A")
                    w['err_p'].setText("N/A")
                    
            self.run_simulation()
            QtWidgets.QMessageBox.information(self, "成功", "等效電路 CNLS 參數疊代優化完成！")
        else:
            QtWidgets.QMessageBox.warning(self, "失敗", "優化器未能在預期步數內收斂。")

    def export_merged_report(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "儲存全功能 EIS 分支拆解報表", "", "CSV Files (*.csv)")
        if not path: return
        
        r_ohm, l_ind, p_list = self.read_ui_params()
        w = 2 * np.pi * self.freq
        
        param_rows = [
            ["--- ECM Fitting Parameter Table (ZView Style) ---"],
            ["Element", "Freedom", "Value", "Error", "Error%"]
        ]
        for k, w_box in self.param_widgets.items():
            param_rows.append([
                k, w_box['mode'].currentText(), float(w_box['val'].text()), w_box['err'].text(), w_box['err_p'].text()
            ])
            
        param_rows.append([]) 
        
        data_headers = [
            "Frequency (Hz)", 
            "Z_raw_prime (Ohm)", "Z_raw_double_prime (Ohm)", "Magnitude_raw (Ohm)", "Theta_raw (deg)",
            "Total_Fitted_Z_prime (Ohm)", "Total_Fitted_Z_double_prime (Ohm)", "Magnitude_fitted (Ohm)", "Theta_fitted (deg)"
        ]
        
        for k in range(len(p_list)):
            data_headers.append(f"Branch_{k+1}_Z_prime (Ohm)")
            data_headers.append(f"Branch_{k+1}_Z_double_prime (Ohm)")
            
        mag_exp, theta_exp = np.abs(self.z_exp), -np.angle(self.z_exp, deg=True)
        mag_sim, theta_sim = np.abs(self.z_sim_current), -np.angle(self.z_sim_current, deg=True)
        
        # 🚀 修正點：在計算各分支矩陣時，同時記錄它專屬的 X 軸偏移量
        branch_z_matrices = []
        branch_offsets = []
        current_offset = r_ohm
        
        for p in p_list:
            R, Q, alpha = p['R'], p['Q'], p['alpha']
            if Q > 0 and R > 0:
                Z_CPE_single = 1.0 / (Q * (1j * w)**alpha)
                Z_branch = 1.0 / (1.0 / R + 1.0 / Z_CPE_single)
                branch_z_matrices.append(Z_branch)
                branch_offsets.append(current_offset)
                current_offset += R  # 累計下一個半圓的起點
            else:
                branch_z_matrices.append(np.zeros_like(self.freq, dtype=complex))
                branch_offsets.append(current_offset)
                
        data_body = []
        for i in range(len(self.freq)):
            row = [
                self.freq[i],
                self.z_exp[i].real, -self.z_exp[i].imag, mag_exp[i], theta_exp[i],
                self.z_sim_current[i].real, -self.z_sim_current[i].imag, mag_sim[i], theta_sim[i]
            ]
            for k in range(len(p_list)):
                # 寫入 CSV 時，實部加上該分支專屬的累計偏移量
                row.append(branch_z_matrices[k][i].real + branch_offsets[k])
                row.append(-branch_z_matrices[k][i].imag)
                
            data_body.append(row)
            
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                import csv
                writer = csv.writer(f)
                writer.writerows(param_rows)
                writer.writerow(["--- Merged Frequency Response Breakdown Data Block ---"])
                writer.writerow(data_headers)
                writer.writerows(data_body)
            QtWidgets.QMessageBox.information(self, "成功", f"包含單獨 RC 分支串聯拆解數據的報表已成功匯出至:\n{path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "錯誤", f"儲存失敗: {e}")