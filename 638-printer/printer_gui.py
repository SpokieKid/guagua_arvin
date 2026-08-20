#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import shlex
import signal
import sys
from typing import Any, Optional

from PySide6.QtCore import QProcess, Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

try:
    import serial.tools.list_ports as serial_list_ports
except Exception:
    serial_list_ports = None

_GUI_SIGINT_REQUESTED = False


class PrinterGui(QMainWindow):
    """MY-638 图片打印上位机。

    该 GUI 不重复实现打印协议，而是组装参数后调用现有 print_pic.py，
    以便快速迭代参数并保持打印链路一致。
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MY-638 图片打印调参上位机")
        self.resize(1420, 900)

        self.script_path = Path(__file__).with_name("print_pic.py")
        self.config_path = Path(__file__).with_name("config.json")
        self.legacy_config_path = Path(__file__).with_name(".printer_gui_config.json")
        self._process: Optional[QProcess] = None
        self._last_pixmap: Optional[QPixmap] = None
        self._quit_when_process_stops = False
        self._sigint_handling = False
        self._config_loading = False
        self._auto_save_pending = False
        self._auto_save_timer = QTimer(self)
        self._auto_save_timer.setSingleShot(True)
        self._auto_save_timer.setInterval(350)
        self._auto_save_timer.timeout.connect(self._auto_save_if_needed)
        self._config_signature: Optional[tuple[int, int]] = None
        self._config_watch_defer_logged = False
        self._pending_config_reload = False
        self._last_watch_error_signature: Optional[tuple[int, int]] = None
        self._config_watch_timer = QTimer(self)
        self._config_watch_timer.setInterval(800)
        self._config_watch_timer.timeout.connect(self._check_external_config_change)

        self._build_ui()
        self._connect_signals()
        self._load_config()
        self._refresh_config_watch_snapshot()
        self._config_watch_timer.start()
        self._on_heat_toggle(self.enable_heat_check.isChecked())
        self._on_smooth_send_toggle(self.smooth_send_check.isChecked())
        self._on_manual_delay_toggle(self.manual_delay_check.isChecked())
        self._on_diag_toggle(self.diagnostic_check.isChecked())
        self._refresh_ports()
        self._refresh_preview()
        self._refresh_cmd_preview()

    # ========================= UI 构建 =========================
    def _build_ui(self) -> None:
        """构建主界面布局。"""
        root = QWidget(self)
        root_layout = QVBoxLayout(root)
        splitter = QSplitter(Qt.Orientation.Horizontal, root)

        left_scroll = QScrollArea(splitter)
        left_scroll.setWidgetResizable(True)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(8, 8, 8, 8)
        left_layout.setSpacing(8)

        left_layout.addWidget(self._build_group_file_device())
        left_layout.addWidget(self._build_group_image())
        left_layout.addWidget(self._build_group_speed_stability())
        left_layout.addWidget(self._build_group_heat())
        left_layout.addWidget(self._build_group_advanced())
        left_layout.addWidget(self._build_group_config())
        left_layout.addStretch(1)

        left_scroll.setWidget(left_panel)
        splitter.addWidget(left_scroll)

        right_panel = QWidget(splitter)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(8)

        self.preview_label = QLabel("未选择图片", right_panel)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(360)
        self.preview_label.setStyleSheet("border: 1px solid #bbb; background: #fafafa;")
        right_layout.addWidget(self.preview_label, stretch=4)

        action_row = QHBoxLayout()
        self.start_btn = QPushButton("开始打印")
        self.dry_run_btn = QPushButton("预处理测试（dry-run）")
        self.self_test_btn = QPushButton("打印自检页")
        self.self_test_btn.setToolTip("发送 ESC @ + DC2 T（1B 40 12 54）打印设备自检页。")
        self.stop_btn = QPushButton("停止打印（Ctrl+C）")
        self.stop_btn.setEnabled(False)
        self.clear_log_btn = QPushButton("清空日志")
        self.status_label = QLabel("状态：空闲")
        action_row.addWidget(self.start_btn)
        action_row.addWidget(self.dry_run_btn)
        action_row.addWidget(self.self_test_btn)
        action_row.addWidget(self.stop_btn)
        action_row.addWidget(self.clear_log_btn)
        action_row.addStretch(1)
        action_row.addWidget(self.status_label)
        right_layout.addLayout(action_row)

        self.cmd_preview = QPlainTextEdit()
        self.cmd_preview.setReadOnly(True)
        self.cmd_preview.setPlaceholderText("这里显示将要执行的命令")
        self.cmd_preview.setMaximumBlockCount(1000)
        self.cmd_preview.setMinimumHeight(90)
        right_layout.addWidget(self.cmd_preview, stretch=1)

        self.log_edit = QPlainTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setPlaceholderText("打印日志输出")
        self.log_edit.setMaximumBlockCount(8000)
        right_layout.addWidget(self.log_edit, stretch=4)

        splitter.addWidget(right_panel)
        splitter.setSizes([520, 900])

        root_layout.addWidget(splitter)
        self.setCentralWidget(root)

    def _build_group_file_device(self) -> QGroupBox:
        """文件与设备参数区域。"""
        g = QGroupBox("文件与设备")
        form = QFormLayout(g)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        image_row = QWidget()
        image_row_layout = QHBoxLayout(image_row)
        image_row_layout.setContentsMargins(0, 0, 0, 0)
        self.image_edit = QLineEdit()
        self.image_edit.setPlaceholderText("选择待打印图片")
        self.image_edit.setToolTip("待打印图片路径。支持 PNG/JPG/BMP。")
        self.image_btn = QPushButton("选择图片")
        self.image_btn.setToolTip("打开文件选择框。")
        image_row_layout.addWidget(self.image_edit, 1)
        image_row_layout.addWidget(self.image_btn)
        form.addRow(self._label_with_impact("图片路径", "输入源"), image_row)

        port_row = QWidget()
        port_row_layout = QHBoxLayout(port_row)
        port_row_layout.setContentsMargins(0, 0, 0, 0)
        self.port_combo = QComboBox()
        self.port_combo.setEditable(True)
        self.port_combo.setToolTip("串口设备路径，例如 /dev/cu.usbserial-0001。")
        self.refresh_port_btn = QPushButton("刷新串口")
        self.refresh_port_btn.setToolTip("重新扫描系统可用串口。")
        port_row_layout.addWidget(self.port_combo, 1)
        port_row_layout.addWidget(self.refresh_port_btn)
        form.addRow(self._label_with_impact("串口", "连接目标设备"), port_row)

        self.baud_spin = self._int_spin(1200, 921600, 9600)
        self.baud_spin.setToolTip("串口波特率。MY-638 常用 9600。")
        form.addRow(self._label_with_impact("波特率", "通讯稳定性与发送速度"), self.baud_spin)

        self.backend_combo = self._combo(["auto", "raw", "escpos"], "raw")
        self.backend_combo.setToolTip("打印后端。建议优先 raw。")
        form.addRow(self._label_with_impact("打印后端", "协议实现与兼容性"), self.backend_combo)

        self.width_spin = self._int_spin(1, 576, 576)
        self.width_spin.setToolTip("目标打印宽度（点）。80mm 机器常用 576。")
        form.addRow(self._label_with_impact("宽度（点）", "横向清晰度与耗时"), self.width_spin)

        self.upscale_check = QCheckBox("原图不足宽度时自动放大（影响：清晰度/锯齿）")
        self.upscale_check.setChecked(True)
        self.upscale_check.setToolTip("勾选后，小图会放大到目标宽度。")
        form.addRow("", self.upscale_check)

        self.feed_spin = self._int_spin(0, 255, 3)
        self.feed_spin.setToolTip("打印结束后额外走纸行数。")
        form.addRow(self._label_with_impact("走纸行数", "出纸留白长度"), self.feed_spin)

        self.feed_mode_combo = self._combo(["escd", "lf"], "escd")
        self.feed_mode_combo.setToolTip("走纸命令。escd 更稳定，lf 更传统。")
        form.addRow(self._label_with_impact("走纸命令", "走纸稳定性与兼容性"), self.feed_mode_combo)
        return g

    def _build_group_image(self) -> QGroupBox:
        """图像质量调参区域。"""
        g = QGroupBox("图像参数")
        form = QFormLayout(g)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.gray_depth_combo = self._combo(["1", "4", "8"], "8")
        self.gray_depth_combo.setToolTip("二值化前灰度级模拟。一般 8 细节更好。")
        form.addRow(self._label_with_impact("灰度级", "层次细节与计算量"), self.gray_depth_combo)

        self.dither_combo = self._combo(["sierra", "ordered", "none"], "sierra")
        self.dither_combo.setToolTip("抖动算法。sierra 条纹更轻；ordered 层次稳定；none 最干净但层次少。")
        form.addRow(self._label_with_impact("抖动算法", "纹理风格与细节保留"), self.dither_combo)

        self.threshold_spin = self._int_spin(0, 255, 170)
        self.threshold_spin.setToolTip("二值化阈值。越低越黑，越高越白。")
        form.addRow(self._label_with_impact("阈值", "整体黑白浓淡"), self.threshold_spin)

        self.gamma_spin = self._float_spin(0.1, 3.0, 1.08, 3, 0.01)
        self.gamma_spin.setToolTip("Gamma。>1 一般能提亮暗部细节。")
        form.addRow(self._label_with_impact("Gamma", "暗部提亮与层次"), self.gamma_spin)

        self.contrast_spin = self._float_spin(0.1, 3.0, 1.06, 3, 0.01)
        self.contrast_spin.setToolTip("对比度。>1 增强层次，<1 更柔和。")
        form.addRow(self._label_with_impact("对比度", "边缘反差与细节"), self.contrast_spin)

        self.invert_check = QCheckBox("黑白反相（影响：前景/背景互换）")
        self.invert_check.setToolTip("勾选后黑白颠倒打印。")
        form.addRow("", self.invert_check)
        return g

    def _build_group_speed_stability(self) -> QGroupBox:
        """速度与稳定性调参区域。"""
        g = QGroupBox("速度与稳定性")
        form = QFormLayout(g)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.speed_mode_combo = self._combo(["balanced", "quality", "fast"], "balanced")
        self.speed_mode_combo.setToolTip("速度档位。quality 更稳，fast 更快。")
        form.addRow(self._label_with_impact("速度档位", "打印速度与稳定性"), self.speed_mode_combo)

        self.chunk_size_spin = self._int_spin(8, 4096, 64)
        self.chunk_size_spin.setToolTip("串口每次写入的字节数。")
        form.addRow(self._label_with_impact("Chunk 大小", "串口吞吐与卡顿风险"), self.chunk_size_spin)

        chunk_delay_row = QWidget()
        chunk_delay_layout = QHBoxLayout(chunk_delay_row)
        chunk_delay_layout.setContentsMargins(0, 0, 0, 0)
        self.manual_delay_check = QCheckBox("手动覆盖（影响：发送节奏）")
        self.manual_delay_check.setToolTip("勾选后使用手动 chunk 延时，覆盖速度档位。")
        self.chunk_delay_spin = self._float_spin(0.0, 2000.0, 6.0, 1, 0.5)
        self.chunk_delay_spin.setEnabled(False)
        self.chunk_delay_spin.setToolTip("chunk 间隔毫秒。越小越快。")
        chunk_delay_layout.addWidget(self.manual_delay_check)
        chunk_delay_layout.addWidget(self.chunk_delay_spin, 1)
        form.addRow(self._label_with_impact("Chunk 延时(ms)", "越小越快但更容易丢稳"), chunk_delay_row)

        self.smooth_send_check = QCheckBox("启用恒速节拍模式（影响：稳定性/连续性）")
        self.smooth_send_check.setChecked(False)
        self.smooth_send_check.setToolTip("勾选=paced；不勾选=burst（推荐，连续吞吐优先）。")
        form.addRow("", self.smooth_send_check)

        self.target_bps_spin = self._int_spin(1000, 50000, 8500, 100)
        self.target_bps_spin.setToolTip("平滑发送目标速率（字节/秒）。值越大越快，过大易抖动。")
        form.addRow(self._label_with_impact("目标速率(B/s)", "发送节奏与连续性"), self.target_bps_spin)

        self.inter_band_gap_spin = self._float_spin(0.0, 500.0, 1.0, 2, 0.1)
        self.inter_band_gap_spin.setToolTip("条带之间额外间隔（毫秒），用于微调出纸节奏。")
        form.addRow(self._label_with_impact("条带间隔(ms)", "分段感与机械连贯性"), self.inter_band_gap_spin)

        self.band_height_spin = self._int_spin(8, 1024, 96)
        self.band_height_spin.setToolTip("光栅条带高度。")
        form.addRow(self._label_with_impact("条带高度", "分段感与底部稳定性"), self.band_height_spin)

        self.auto_band_height_check = QCheckBox("自动调整条带高度（影响：尾段断层概率）")
        self.auto_band_height_check.setChecked(True)
        self.auto_band_height_check.setToolTip("建议开启。可降低底部断层概率。")
        form.addRow("", self.auto_band_height_check)

        self.min_tail_rows_spin = self._int_spin(0, 512, 24)
        self.min_tail_rows_spin.setToolTip("自动调高条带时，允许的最小尾段行数。")
        form.addRow(self._label_with_impact("最小尾段行", "尾段补偿触发阈值"), self.min_tail_rows_spin)

        self.tail_bands_spin = self._int_spin(0, 64, 3)
        self.tail_bands_spin.setToolTip("最后 N 个条带额外保护。")
        form.addRow(self._label_with_impact("尾段保护数", "末尾条带稳定性"), self.tail_bands_spin)

        self.tail_delay_spin = self._float_spin(0.0, 3000.0, 120.0, 1, 1.0)
        self.tail_delay_spin.setToolTip("尾段每个条带额外延时（毫秒）。")
        form.addRow(self._label_with_impact("尾段延时(ms)", "末尾卡顿/稳定折中"), self.tail_delay_spin)

        self.pad_last_band_check = QCheckBox("补齐最后短条带（影响：底部错位概率）")
        self.pad_last_band_check.setChecked(True)
        self.pad_last_band_check.setToolTip("把尾段补白到整段高度，减少固件尾段异常。")
        form.addRow("", self.pad_last_band_check)
        return g

    def _build_group_heat(self) -> QGroupBox:
        """热敏加热参数区域。"""
        g = QGroupBox("热敏参数（ESC 7）")
        form = QFormLayout(g)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.enable_heat_check = QCheckBox("启用热敏加热参数（影响：黑度/速度/发热）")
        self.enable_heat_check.setToolTip("不启用时不发送 --heat-n1/n2/n3。")
        form.addRow("", self.enable_heat_check)

        self.heat_n1_spin = self._int_spin(0, 255, 9)
        self.heat_n1_spin.setToolTip("n1：最多加热点（单位 8dots）。")
        form.addRow(self._label_with_impact("n1", "最大加热点数与峰值电流"), self.heat_n1_spin)
        self.heat_n2_spin = self._int_spin(0, 255, 115)
        self.heat_n2_spin.setToolTip("n2：加热时间（单位 10us）。")
        form.addRow(self._label_with_impact("n2", "加热时间与黑度"), self.heat_n2_spin)
        self.heat_n3_spin = self._int_spin(0, 255, 3)
        self.heat_n3_spin.setToolTip("n3：加热间隔（单位 10us）。")
        form.addRow(self._label_with_impact("n3", "加热间隔与清晰度/速度"), self.heat_n3_spin)
        return g

    def _build_group_advanced(self) -> QGroupBox:
        """高级参数区域。"""
        g = QGroupBox("高级参数")
        form = QFormLayout(g)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.impl_combo = self._combo(
            ["bitImageRaster", "graphics", "bitImageColumn"],
            "bitImageRaster",
        )
        self.impl_combo.setToolTip("escpos 后端图像实现。")
        form.addRow(self._label_with_impact("escpos impl", "图像实现方式与兼容性"), self.impl_combo)

        self.fragment_height_spin = self._int_spin(1, 8192, 960)
        self.fragment_height_spin.setToolTip("escpos 后端分片高度。")
        form.addRow(self._label_with_impact("fragment_height", "escpos 分片尺寸与稳定性"), self.fragment_height_spin)

        self.low_density_v_check = QCheckBox("escpos 关闭纵向高密度（影响：纵向细节）")
        self.low_density_v_check.setToolTip("仅 escpos 后端生效。")
        form.addRow("", self.low_density_v_check)

        self.low_density_h_check = QCheckBox("escpos 关闭横向高密度（影响：横向细节）")
        self.low_density_h_check.setToolTip("仅 escpos 后端生效。")
        form.addRow("", self.low_density_h_check)

        self.read_reply_check = QCheckBox("读取串口回包（影响：诊断能力/异常风险）")
        self.read_reply_check.setChecked(False)
        self.read_reply_check.setToolTip("某些机型开了会增加异常输出概率。")
        form.addRow("", self.read_reply_check)

        self.status_check_check = QCheckBox("实时状态查询（影响：诊断能力/侵入性）")
        self.status_check_check.setChecked(False)
        self.status_check_check.setToolTip("某些机型开了会增加异常输出概率。")
        form.addRow("", self.status_check_check)

        self.diagnostic_check = QCheckBox("开启诊断模式（影响：可追溯性）")
        self.diagnostic_check.setChecked(False)
        self.diagnostic_check.setToolTip("记录每个条带的发送与回显信息，用于排查乱码/断层。")
        form.addRow("", self.diagnostic_check)

        self.diag_passive_rx_check = QCheckBox("诊断：每条带被动读取回显（影响：回包观测）")
        self.diag_passive_rx_check.setChecked(True)
        self.diag_passive_rx_check.setToolTip("仅读取串口收到的数据，不主动发状态指令。")
        form.addRow("", self.diag_passive_rx_check)

        self.diag_active_status_check = QCheckBox("诊断：主动查询 DLE EOT 状态（影响：侵入性）")
        self.diag_active_status_check.setChecked(False)
        self.diag_active_status_check.setToolTip("会主动发实时状态查询，侵入性更高，默认关闭。")
        form.addRow("", self.diag_active_status_check)

        self.diag_every_spin = self._int_spin(1, 512, 1)
        self.diag_every_spin.setToolTip("每 N 个条带做一次主动状态查询。")
        form.addRow(self._label_with_impact("状态采样频率", "状态变化捕获密度"), self.diag_every_spin)

        self.diag_rx_wait_spin = self._float_spin(0.0, 5000.0, 25.0, 1, 1.0)
        self.diag_rx_wait_spin.setToolTip("诊断回显读取最大等待时长（毫秒）。")
        form.addRow(self._label_with_impact("回显等待(ms)", "诊断完整性与时延"), self.diag_rx_wait_spin)

        self.diag_rx_quiet_spin = self._float_spin(0.0, 5000.0, 8.0, 1, 1.0)
        self.diag_rx_quiet_spin.setToolTip("诊断回显读取静默截止时长（毫秒）。")
        form.addRow(self._label_with_impact("回显静默(ms)", "回包截断灵敏度"), self.diag_rx_quiet_spin)

        self.diag_status_timeout_spin = self._float_spin(1.0, 5000.0, 180.0, 1, 1.0)
        self.diag_status_timeout_spin.setToolTip("主动状态查询超时（毫秒）。")
        form.addRow(self._label_with_impact("状态超时(ms)", "状态查询可靠性"), self.diag_status_timeout_spin)

        self.diag_file_edit = QLineEdit()
        self.diag_file_edit.setPlaceholderText("诊断日志文件路径（可空，空则自动生成）")
        self.diag_file_edit.setToolTip("可选：指定诊断 JSON 文件输出路径。")
        form.addRow(self._label_with_impact("诊断文件", "日志落盘位置"), self.diag_file_edit)
        return g

    def _build_group_config(self) -> QGroupBox:
        """参数配置管理区域。"""
        g = QGroupBox("参数配置")
        row = QHBoxLayout(g)
        self.save_cfg_btn = QPushButton("保存参数")
        self.save_cfg_btn.setToolTip("保存当前参数到本地 JSON。")
        self.load_cfg_btn = QPushButton("读取参数")
        self.load_cfg_btn.setToolTip("从本地 JSON 读取参数。")
        self.default_btn = QPushButton("恢复稳定预设")
        self.default_btn.setToolTip("恢复一套稳妥默认参数。")
        row.addWidget(self.save_cfg_btn)
        row.addWidget(self.load_cfg_btn)
        row.addWidget(self.default_btn)
        return g

    # ========================= 控件工厂 =========================
    def _combo(self, items: list[str], default: str) -> QComboBox:
        """创建并初始化下拉框。"""
        c = QComboBox()
        c.addItems(items)
        idx = c.findText(default)
        if idx >= 0:
            c.setCurrentIndex(idx)
        return c

    def _label_with_impact(self, title: str, impact: str) -> QLabel:
        """创建“参数名 + 小字影响说明”的表单标签。"""
        lbl = QLabel(
            f"{title} <span style='color:#7a7a7a; font-size:11px;'>（影响：{impact}）</span>"
        )
        lbl.setTextFormat(Qt.TextFormat.RichText)
        return lbl

    def _int_spin(self, min_v: int, max_v: int, default: int, step: int = 1) -> QSpinBox:
        """创建整数输入框。"""
        s = QSpinBox()
        s.setRange(min_v, max_v)
        s.setSingleStep(step)
        s.setValue(default)
        return s

    def _float_spin(
        self,
        min_v: float,
        max_v: float,
        default: float,
        decimals: int = 2,
        step: float = 0.01,
    ) -> QDoubleSpinBox:
        """创建浮点输入框。"""
        s = QDoubleSpinBox()
        s.setRange(min_v, max_v)
        s.setDecimals(decimals)
        s.setSingleStep(step)
        s.setValue(default)
        return s

    # ========================= 信号绑定 =========================
    def _connect_signals(self) -> None:
        """连接 UI 信号。"""
        self.image_btn.clicked.connect(self._choose_image)
        self.refresh_port_btn.clicked.connect(self._refresh_ports)

        self.start_btn.clicked.connect(self._start_print)
        self.dry_run_btn.clicked.connect(self._start_dry_run)
        self.self_test_btn.clicked.connect(self._start_self_test)
        self.stop_btn.clicked.connect(self._stop_print)
        self.clear_log_btn.clicked.connect(self.log_edit.clear)

        self.save_cfg_btn.clicked.connect(self._save_config)
        self.load_cfg_btn.clicked.connect(self._load_config)
        self.default_btn.clicked.connect(self._apply_stable_defaults)

        self.enable_heat_check.toggled.connect(self._on_heat_toggle)
        self.smooth_send_check.toggled.connect(self._on_smooth_send_toggle)
        self.manual_delay_check.toggled.connect(self._on_manual_delay_toggle)
        self.diagnostic_check.toggled.connect(self._on_diag_toggle)

        # 参数变化时刷新命令预览与图片预览
        self.image_edit.textChanged.connect(self._refresh_preview)
        self.image_edit.textChanged.connect(self._refresh_cmd_preview)
        self.image_edit.textChanged.connect(self._schedule_auto_save)
        self.port_combo.currentTextChanged.connect(self._refresh_cmd_preview)
        self.port_combo.currentTextChanged.connect(self._schedule_auto_save)

        change_slots = [
            self.backend_combo.currentTextChanged,
            self.width_spin.valueChanged,
            self.upscale_check.toggled,
            self.feed_spin.valueChanged,
            self.feed_mode_combo.currentTextChanged,
            self.gray_depth_combo.currentTextChanged,
            self.dither_combo.currentTextChanged,
            self.threshold_spin.valueChanged,
            self.gamma_spin.valueChanged,
            self.contrast_spin.valueChanged,
            self.invert_check.toggled,
            self.speed_mode_combo.currentTextChanged,
            self.chunk_size_spin.valueChanged,
            self.manual_delay_check.toggled,
            self.chunk_delay_spin.valueChanged,
            self.smooth_send_check.toggled,
            self.target_bps_spin.valueChanged,
            self.inter_band_gap_spin.valueChanged,
            self.band_height_spin.valueChanged,
            self.auto_band_height_check.toggled,
            self.min_tail_rows_spin.valueChanged,
            self.tail_bands_spin.valueChanged,
            self.tail_delay_spin.valueChanged,
            self.pad_last_band_check.toggled,
            self.enable_heat_check.toggled,
            self.heat_n1_spin.valueChanged,
            self.heat_n2_spin.valueChanged,
            self.heat_n3_spin.valueChanged,
            self.impl_combo.currentTextChanged,
            self.fragment_height_spin.valueChanged,
            self.low_density_v_check.toggled,
            self.low_density_h_check.toggled,
            self.read_reply_check.toggled,
            self.status_check_check.toggled,
            self.diagnostic_check.toggled,
            self.diag_passive_rx_check.toggled,
            self.diag_active_status_check.toggled,
            self.diag_every_spin.valueChanged,
            self.diag_rx_wait_spin.valueChanged,
            self.diag_rx_quiet_spin.valueChanged,
            self.diag_status_timeout_spin.valueChanged,
            self.diag_file_edit.textChanged,
            self.baud_spin.valueChanged,
        ]
        for slot in change_slots:
            slot.connect(self._refresh_cmd_preview)
            slot.connect(self._schedule_auto_save)

    # ========================= 预设与配置 =========================
    def _apply_stable_defaults(self) -> None:
        """恢复稳定预设参数。"""
        self.backend_combo.setCurrentText("raw")
        self.width_spin.setValue(576)
        self.upscale_check.setChecked(True)
        self.feed_spin.setValue(3)
        self.feed_mode_combo.setCurrentText("escd")
        self.gray_depth_combo.setCurrentText("8")
        self.dither_combo.setCurrentText("sierra")
        self.threshold_spin.setValue(170)
        self.gamma_spin.setValue(1.1)
        self.contrast_spin.setValue(1.0)
        self.invert_check.setChecked(False)
        self.speed_mode_combo.setCurrentText("fast")
        self.chunk_size_spin.setValue(1536)
        self.manual_delay_check.setChecked(False)
        self.chunk_delay_spin.setValue(0.0)
        self.smooth_send_check.setChecked(False)
        self.target_bps_spin.setValue(7800)
        self.inter_band_gap_spin.setValue(0.0)
        self.band_height_spin.setValue(192)
        self.auto_band_height_check.setChecked(True)
        self.min_tail_rows_spin.setValue(24)
        self.tail_bands_spin.setValue(0)
        self.tail_delay_spin.setValue(0.0)
        self.pad_last_band_check.setChecked(True)
        self.enable_heat_check.setChecked(True)
        self.heat_n1_spin.setValue(8)
        self.heat_n2_spin.setValue(72)
        self.heat_n3_spin.setValue(10)
        self.read_reply_check.setChecked(False)
        self.status_check_check.setChecked(False)
        self.diagnostic_check.setChecked(False)
        self.diag_passive_rx_check.setChecked(True)
        self.diag_active_status_check.setChecked(False)
        self.diag_every_spin.setValue(1)
        self.diag_rx_wait_spin.setValue(25.0)
        self.diag_rx_quiet_spin.setValue(8.0)
        self.diag_status_timeout_spin.setValue(180.0)
        self.diag_file_edit.setText("")
        self._append_log("已恢复稳定预设。")

    def _collect_config(self) -> dict[str, Any]:
        """收集当前界面参数用于保存。"""
        return {
            "image": self.image_edit.text(),
            "port": self.port_combo.currentText(),
            "baud": self.baud_spin.value(),
            "backend": self.backend_combo.currentText(),
            "width": self.width_spin.value(),
            "upscale": self.upscale_check.isChecked(),
            "feed": self.feed_spin.value(),
            "feed_mode": self.feed_mode_combo.currentText(),
            "gray_depth": self.gray_depth_combo.currentText(),
            "dither": self.dither_combo.currentText(),
            "threshold": self.threshold_spin.value(),
            "gamma": self.gamma_spin.value(),
            "contrast": self.contrast_spin.value(),
            "invert": self.invert_check.isChecked(),
            "speed_mode": self.speed_mode_combo.currentText(),
            "chunk_size": self.chunk_size_spin.value(),
            "manual_delay": self.manual_delay_check.isChecked(),
            "chunk_delay": self.chunk_delay_spin.value(),
            "send_mode": ("paced" if self.smooth_send_check.isChecked() else "burst"),
            "smooth_send": self.smooth_send_check.isChecked(),
            "target_bps": self.target_bps_spin.value(),
            "inter_band_gap_ms": self.inter_band_gap_spin.value(),
            "band_height": self.band_height_spin.value(),
            "auto_band_height": self.auto_band_height_check.isChecked(),
            "min_tail_rows": self.min_tail_rows_spin.value(),
            "tail_bands": self.tail_bands_spin.value(),
            "tail_delay_ms": self.tail_delay_spin.value(),
            "pad_last_band": self.pad_last_band_check.isChecked(),
            "enable_heat": self.enable_heat_check.isChecked(),
            "heat_n1": self.heat_n1_spin.value(),
            "heat_n2": self.heat_n2_spin.value(),
            "heat_n3": self.heat_n3_spin.value(),
            "impl": self.impl_combo.currentText(),
            "fragment_height": self.fragment_height_spin.value(),
            "low_density_v": self.low_density_v_check.isChecked(),
            "low_density_h": self.low_density_h_check.isChecked(),
            "read_reply": self.read_reply_check.isChecked(),
            "status_check": self.status_check_check.isChecked(),
            "diagnostic": self.diagnostic_check.isChecked(),
            "diag_passive_rx": self.diag_passive_rx_check.isChecked(),
            "diag_active_status": self.diag_active_status_check.isChecked(),
            "diag_every": self.diag_every_spin.value(),
            "diag_rx_wait_ms": self.diag_rx_wait_spin.value(),
            "diag_rx_quiet_ms": self.diag_rx_quiet_spin.value(),
            "diag_status_timeout_ms": self.diag_status_timeout_spin.value(),
            "diag_file": self.diag_file_edit.text(),
        }

    def _apply_config_data(self, data: dict[str, Any]) -> None:
        """把配置数据回填到界面。"""
        self.image_edit.setText(str(data.get("image", self.image_edit.text())))
        self.port_combo.setCurrentText(str(data.get("port", self.port_combo.currentText())))
        self.baud_spin.setValue(int(data.get("baud", self.baud_spin.value())))
        self.backend_combo.setCurrentText(str(data.get("backend", self.backend_combo.currentText())))
        self.width_spin.setValue(int(data.get("width", self.width_spin.value())))
        self.upscale_check.setChecked(bool(data.get("upscale", self.upscale_check.isChecked())))
        self.feed_spin.setValue(int(data.get("feed", self.feed_spin.value())))
        self.feed_mode_combo.setCurrentText(str(data.get("feed_mode", self.feed_mode_combo.currentText())))
        self.gray_depth_combo.setCurrentText(str(data.get("gray_depth", self.gray_depth_combo.currentText())))
        dither = str(data.get("dither", self.dither_combo.currentText())).strip().lower()
        if dither == "floyd":
            dither = "sierra"
            self._append_log("检测到旧配置 dither=floyd，已自动迁移为 sierra。")
        if dither not in ("sierra", "ordered", "none"):
            dither = self.dither_combo.currentText()
        self.dither_combo.setCurrentText(dither)
        self.threshold_spin.setValue(int(data.get("threshold", self.threshold_spin.value())))
        self.gamma_spin.setValue(float(data.get("gamma", self.gamma_spin.value())))
        self.contrast_spin.setValue(float(data.get("contrast", self.contrast_spin.value())))
        self.invert_check.setChecked(bool(data.get("invert", self.invert_check.isChecked())))
        self.speed_mode_combo.setCurrentText(str(data.get("speed_mode", self.speed_mode_combo.currentText())))
        self.chunk_size_spin.setValue(int(data.get("chunk_size", self.chunk_size_spin.value())))
        self.manual_delay_check.setChecked(bool(data.get("manual_delay", self.manual_delay_check.isChecked())))
        self.chunk_delay_spin.setValue(float(data.get("chunk_delay", self.chunk_delay_spin.value())))
        send_mode = str(data.get("send_mode", "")).strip().lower()
        if send_mode in ("burst", "paced"):
            self.smooth_send_check.setChecked(send_mode == "paced")
        else:
            self.smooth_send_check.setChecked(bool(data.get("smooth_send", self.smooth_send_check.isChecked())))
        self.target_bps_spin.setValue(int(data.get("target_bps", self.target_bps_spin.value())))
        self.inter_band_gap_spin.setValue(float(data.get("inter_band_gap_ms", self.inter_band_gap_spin.value())))
        self.band_height_spin.setValue(int(data.get("band_height", self.band_height_spin.value())))
        self.auto_band_height_check.setChecked(bool(data.get("auto_band_height", self.auto_band_height_check.isChecked())))
        self.min_tail_rows_spin.setValue(int(data.get("min_tail_rows", self.min_tail_rows_spin.value())))
        self.tail_bands_spin.setValue(int(data.get("tail_bands", self.tail_bands_spin.value())))
        self.tail_delay_spin.setValue(float(data.get("tail_delay_ms", self.tail_delay_spin.value())))
        self.pad_last_band_check.setChecked(bool(data.get("pad_last_band", self.pad_last_band_check.isChecked())))
        self.enable_heat_check.setChecked(bool(data.get("enable_heat", self.enable_heat_check.isChecked())))
        self.heat_n1_spin.setValue(int(data.get("heat_n1", self.heat_n1_spin.value())))
        self.heat_n2_spin.setValue(int(data.get("heat_n2", self.heat_n2_spin.value())))
        self.heat_n3_spin.setValue(int(data.get("heat_n3", self.heat_n3_spin.value())))
        self.impl_combo.setCurrentText(str(data.get("impl", self.impl_combo.currentText())))
        self.fragment_height_spin.setValue(int(data.get("fragment_height", self.fragment_height_spin.value())))
        self.low_density_v_check.setChecked(bool(data.get("low_density_v", self.low_density_v_check.isChecked())))
        self.low_density_h_check.setChecked(bool(data.get("low_density_h", self.low_density_h_check.isChecked())))
        self.read_reply_check.setChecked(bool(data.get("read_reply", self.read_reply_check.isChecked())))
        self.status_check_check.setChecked(bool(data.get("status_check", self.status_check_check.isChecked())))
        self.diagnostic_check.setChecked(bool(data.get("diagnostic", self.diagnostic_check.isChecked())))
        self.diag_passive_rx_check.setChecked(bool(data.get("diag_passive_rx", self.diag_passive_rx_check.isChecked())))
        self.diag_active_status_check.setChecked(bool(data.get("diag_active_status", self.diag_active_status_check.isChecked())))
        self.diag_every_spin.setValue(int(data.get("diag_every", self.diag_every_spin.value())))
        self.diag_rx_wait_spin.setValue(float(data.get("diag_rx_wait_ms", self.diag_rx_wait_spin.value())))
        self.diag_rx_quiet_spin.setValue(float(data.get("diag_rx_quiet_ms", self.diag_rx_quiet_spin.value())))
        self.diag_status_timeout_spin.setValue(float(data.get("diag_status_timeout_ms", self.diag_status_timeout_spin.value())))
        self.diag_file_edit.setText(str(data.get("diag_file", self.diag_file_edit.text())))

    def _schedule_auto_save(self) -> None:
        """计划自动保存配置（防抖）。"""
        if self._config_loading:
            return
        self._auto_save_pending = True
        self._auto_save_timer.start()

    def _auto_save_if_needed(self) -> None:
        """执行一次自动保存。"""
        if not self._auto_save_pending:
            return
        self._auto_save_pending = False
        self._save_config(silent=True, from_auto=True)

    def _save_config(self, silent: bool = False, from_auto: bool = False) -> None:
        """保存参数到本地文件。

        参数说明：
        - silent: True 时失败不弹窗，仅写日志。
        - from_auto: True 表示自动保存触发，成功时不刷日志，避免日志刷屏。
        """
        try:
            self.config_path.write_text(
                json.dumps(self._collect_config(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            self._refresh_config_watch_snapshot()
            self._last_watch_error_signature = None
            if not from_auto:
                self._append_log(f"参数已保存：{self.config_path}")
        except Exception as exc:
            if silent:
                self._append_log(f"自动保存失败：{exc}")
                return
            QMessageBox.critical(self, "保存失败", f"保存参数失败：{exc}")

    def _config_file_signature(self, path: Path) -> Optional[tuple[int, int]]:
        """获取配置文件签名。

        返回值说明：
        - None: 文件不存在或无法访问。
        - (mtime_ns, size): 用于判断文件是否发生变化。
        """
        try:
            stat = path.stat()
        except OSError:
            return None
        return (stat.st_mtime_ns, stat.st_size)

    def _refresh_config_watch_snapshot(self) -> None:
        """刷新配置监视快照，避免把本 GUI 的保存误判为外部改动。"""
        self._config_signature = self._config_file_signature(self.config_path)

    def _load_config(
        self,
        source_path: Optional[Path] = None,
        *,
        silent: bool = False,
        from_watch: bool = False,
    ) -> bool:
        """从本地文件加载参数并回填界面。

        参数说明：
        - source_path: 指定读取路径；为空时按 config.json -> 旧版隐藏文件顺序查找。
        - silent: True 时不弹窗/不刷失败日志，适合自动轮询重试。
        - from_watch: True 表示由文件监视器触发，用于区分日志文案。
        """
        if source_path is None:
            if self.config_path.exists():
                source_path = self.config_path
            elif self.legacy_config_path.exists():
                source_path = self.legacy_config_path
            else:
                return False

        try:
            data = json.loads(source_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                self._config_loading = True
                try:
                    self._apply_config_data(data)
                finally:
                    self._config_loading = False
                self._auto_save_pending = False
                self._auto_save_timer.stop()
                # 兼容旧版隐藏文件，自动迁移到 config.json。
                if source_path == self.legacy_config_path and not self.config_path.exists():
                    self.config_path.write_text(
                        json.dumps(data, ensure_ascii=False, indent=2),
                        encoding="utf-8",
                    )
                    self._append_log(f"已迁移配置到：{self.config_path}")
                self._refresh_config_watch_snapshot()
                self._last_watch_error_signature = None
                if from_watch:
                    self._append_log(f"检测到配置变更，已自动应用：{self.config_path}")
                else:
                    self._append_log(f"已读取参数：{source_path}")
                return True
            if not silent:
                self._append_log(f"读取参数失败：{source_path} 不是 JSON 对象。")
        except Exception as exc:
            self._config_loading = False
            if not silent:
                self._append_log(f"读取参数失败：{exc}")
        return False

    def _check_external_config_change(self, force_apply: bool = False) -> None:
        """轮询检测 config.json 外部变化，并自动回填到 GUI。

        参数说明：
        - force_apply: True 时忽略“打印中延后应用”策略，立即尝试加载。
        """
        signature = self._config_file_signature(self.config_path)
        if signature is None:
            return

        if self._config_signature is None:
            self._config_signature = signature
            return

        if not force_apply and signature == self._config_signature:
            return

        if self._is_process_running() and not force_apply:
            self._pending_config_reload = True
            if not self._config_watch_defer_logged:
                self._append_log("检测到 config.json 变更：当前打印中，任务结束后自动应用。")
                self._config_watch_defer_logged = True
            return

        if self._load_config(self.config_path, silent=True, from_watch=True):
            self._pending_config_reload = False
            self._config_watch_defer_logged = False
            return

        # 外部写入可能是“先截断再写入”，解析失败时等待下次轮询重试，避免日志刷屏。
        if self._last_watch_error_signature != signature:
            self._append_log(
                f"检测到配置文件变化，但暂时无法解析：{self.config_path}。将自动重试。"
            )
            self._last_watch_error_signature = signature

    def _apply_pending_config_reload(self) -> None:
        """打印结束后应用“打印中积压”的外部配置更新。"""
        if not self._pending_config_reload:
            return
        self._append_log("打印任务已结束，开始应用外部配置更新。")
        self._pending_config_reload = False
        self._config_watch_defer_logged = False
        self._check_external_config_change(force_apply=True)

    # ========================= 串口与预览 =========================
    def _refresh_ports(self) -> None:
        """扫描系统串口并刷新下拉框。"""
        current = self.port_combo.currentText().strip()
        ports: list[str] = []
        if serial_list_ports is not None:
            try:
                ports = sorted([p.device for p in serial_list_ports.comports()])
            except Exception as exc:
                self._append_log(f"扫描串口失败：{exc}")

        self.port_combo.blockSignals(True)
        self.port_combo.clear()
        self.port_combo.addItems(ports)
        if current:
            self.port_combo.setCurrentText(current)
        elif ports:
            self.port_combo.setCurrentIndex(0)
        else:
            self.port_combo.setCurrentText("/dev/cu.usbserial-0001")
        self.port_combo.blockSignals(False)
        self._refresh_cmd_preview()

    def _choose_image(self) -> None:
        """选择图片文件。"""
        fp, _ = QFileDialog.getOpenFileName(
            self,
            "选择待打印图片",
            str(Path.cwd()),
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;所有文件 (*)",
        )
        if fp:
            self.image_edit.setText(fp)

    def _refresh_preview(self) -> None:
        """刷新图片预览。"""
        path = self.image_edit.text().strip()
        if not path:
            self._last_pixmap = None
            self.preview_label.setText("未选择图片")
            self.preview_label.setPixmap(QPixmap())
            return
        pix = QPixmap(path)
        if pix.isNull():
            self._last_pixmap = None
            self.preview_label.setText("图片加载失败")
            self.preview_label.setPixmap(QPixmap())
            return
        self._last_pixmap = pix
        self._show_scaled_preview()

    def _show_scaled_preview(self) -> None:
        """按当前显示区域缩放预览图。"""
        if self._last_pixmap is None:
            return
        scaled = self._last_pixmap.scaled(
            self.preview_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.preview_label.setPixmap(scaled)

    # ========================= 命令拼接与执行 =========================
    def _format_float(self, value: float, digits: int = 3) -> str:
        """把浮点数格式化成较短字符串。"""
        txt = f"{value:.{digits}f}"
        return txt.rstrip("0").rstrip(".") if "." in txt else txt

    def _build_command(self, dry_run: bool, self_test: bool = False) -> list[str]:
        """根据当前界面参数构造命令行参数。

        参数说明：
        - dry_run: True 时仅预处理/预演，不实际发送串口。
        - self_test: True 时走“打印自检页”模式（发送 ESC @ + DC2 T）。
        """
        cmd = [
            sys.executable,
            str(self.script_path),
            "--port",
            self.port_combo.currentText().strip(),
            "--baudrate",
            str(self.baud_spin.value()),
            "--backend",
            ("raw" if self_test else self.backend_combo.currentText()),
            "--speed-mode",
            self.speed_mode_combo.currentText(),
            "--chunk-size",
            str(self.chunk_size_spin.value()),
            "--target-bps",
            str(self.target_bps_spin.value()),
            "--inter-band-gap-ms",
            self._format_float(self.inter_band_gap_spin.value(), 2),
            "--send-mode",
            ("paced" if self.smooth_send_check.isChecked() else "burst"),
        ]

        if self_test:
            cmd.append("--self-test")
        else:
            cmd.extend(
                [
                    "--image",
                    self.image_edit.text().strip(),
                    "--width",
                    str(self.width_spin.value()),
                    "--gray-depth",
                    self.gray_depth_combo.currentText(),
                    "--gamma",
                    self._format_float(self.gamma_spin.value()),
                    "--contrast",
                    self._format_float(self.contrast_spin.value()),
                    "--threshold",
                    str(self.threshold_spin.value()),
                    "--dither",
                    self.dither_combo.currentText(),
                    "--feed",
                    str(self.feed_spin.value()),
                    "--feed-mode",
                    self.feed_mode_combo.currentText(),
                    "--band-height",
                    str(self.band_height_spin.value()),
                    "--tail-bands",
                    str(self.tail_bands_spin.value()),
                    "--tail-delay-ms",
                    self._format_float(self.tail_delay_spin.value(), 1),
                    "--min-tail-rows",
                    str(self.min_tail_rows_spin.value()),
                    "--impl",
                    self.impl_combo.currentText(),
                    "--fragment-height",
                    str(self.fragment_height_spin.value()),
                ]
            )

            if self.upscale_check.isChecked():
                cmd.append("--upscale")
            if self.invert_check.isChecked():
                cmd.append("--invert")

            cmd.append("--auto-band-height" if self.auto_band_height_check.isChecked() else "--no-auto-band-height")
            cmd.append("--pad-last-band" if self.pad_last_band_check.isChecked() else "--no-pad-last-band")

            if self.low_density_v_check.isChecked():
                cmd.append("--low-density-vertical")
            if self.low_density_h_check.isChecked():
                cmd.append("--low-density-horizontal")

            if self.enable_heat_check.isChecked():
                cmd.extend(
                    [
                        "--heat-n1",
                        str(self.heat_n1_spin.value()),
                        "--heat-n2",
                        str(self.heat_n2_spin.value()),
                        "--heat-n3",
                        str(self.heat_n3_spin.value()),
                    ]
                )

        # 通用串口行为参数：自检和正常打印都生效。
        cmd.append("--read-reply" if self.read_reply_check.isChecked() else "--no-read-reply")
        cmd.append("--status-check" if self.status_check_check.isChecked() else "--no-status-check")
        cmd.append("--diagnostic" if self.diagnostic_check.isChecked() else "--no-diagnostic")
        cmd.append("--diag-passive-rx" if self.diag_passive_rx_check.isChecked() else "--no-diag-passive-rx")
        cmd.append(
            "--diag-active-status"
            if self.diag_active_status_check.isChecked()
            else "--no-diag-active-status"
        )

        cmd.extend(
            [
                "--diag-snapshot-every-band",
                str(self.diag_every_spin.value()),
                "--diag-rx-wait-ms",
                self._format_float(self.diag_rx_wait_spin.value(), 1),
                "--diag-rx-quiet-ms",
                self._format_float(self.diag_rx_quiet_spin.value(), 1),
                "--diag-status-timeout-ms",
                self._format_float(self.diag_status_timeout_spin.value(), 1),
            ]
        )

        diag_file = self.diag_file_edit.text().strip()
        if diag_file:
            cmd.extend(["--diag-file", diag_file])

        if self.manual_delay_check.isChecked():
            cmd.extend(["--chunk-delay-ms", self._format_float(self.chunk_delay_spin.value(), 1)])

        if dry_run:
            cmd.append("--dry-run")
        return cmd

    def _refresh_cmd_preview(self) -> None:
        """刷新命令预览文本。"""
        cmd = self._build_command(dry_run=False)
        self.cmd_preview.setPlainText(shlex.join(cmd))

    def _validate_before_run(self, need_image: bool = True) -> bool:
        """执行前做必要校验。

        参数说明：
        - need_image: True 表示必须校验图片路径；自检模式可传 False。
        """
        if self._process is not None and self._process.state() != QProcess.ProcessState.NotRunning:
            QMessageBox.warning(self, "提示", "已有任务在运行，请先停止。")
            return False
        if not self.script_path.exists():
            QMessageBox.critical(self, "错误", f"未找到脚本：{self.script_path}")
            return False
        if need_image:
            image_path = Path(self.image_edit.text().strip())
            if not image_path.exists():
                QMessageBox.warning(self, "提示", "图片路径无效，请先选择图片。")
                return False
        if not self.port_combo.currentText().strip():
            QMessageBox.warning(self, "提示", "串口不能为空。")
            return False
        return True

    def _start_print(self) -> None:
        """开始正常打印。"""
        self._start_process(dry_run=False, self_test=False)

    def _start_dry_run(self) -> None:
        """开始 dry-run（仅预处理，不发送串口）。"""
        self._start_process(dry_run=True, self_test=False)

    def _start_self_test(self) -> None:
        """开始打印自检页（DC2 T）。"""
        self._start_process(dry_run=False, self_test=True)

    def _start_process(self, dry_run: bool, self_test: bool) -> None:
        """启动 print_pic.py 子进程。"""
        if not self._validate_before_run(need_image=not self_test):
            return
        cmd = self._build_command(dry_run=dry_run, self_test=self_test)
        self._append_log("==========")
        self._append_log("执行命令：")
        self._append_log(shlex.join(cmd))

        self._process = QProcess(self)
        self._process.setProgram(cmd[0])
        self._process.setArguments(cmd[1:])
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._on_process_output)
        self._process.finished.connect(self._on_process_finished)
        self._process.errorOccurred.connect(self._on_process_error)
        self._process.start()

        if not self._process.waitForStarted(2000):
            QMessageBox.critical(self, "启动失败", "子进程未能启动。")
            self._set_running_state(False)
            return
        self._set_running_state(True)
        self.status_label.setText("状态：自检中" if self_test else "状态：打印中")

    def _stop_print(self) -> None:
        """停止打印：优先发送 SIGINT，超时后强制 kill。"""
        if self._process is None:
            return
        if self._process.state() == QProcess.ProcessState.NotRunning:
            return

        pid = int(self._process.processId())
        self._append_log("收到停止请求：尝试发送 Ctrl+C（SIGINT）...")
        try:
            if pid > 0:
                os.kill(pid, signal.SIGINT)
            else:
                self._process.terminate()
        except Exception as exc:
            self._append_log(f"发送 SIGINT 失败，改用 terminate：{exc}")
            self._process.terminate()

        # 若 1.2s 还未退出，进行 kill，避免卡住。
        QTimer.singleShot(1200, self._force_kill_if_needed)

    def _is_process_running(self) -> bool:
        """判断子进程是否处于运行状态。"""
        return (
            self._process is not None
            and self._process.state() != QProcess.ProcessState.NotRunning
        )

    def _handle_terminal_sigint(self) -> None:
        """处理终端 Ctrl+C。

        - 若正在打印：先停打印，待子进程结束后退出 GUI。
        - 若未打印：直接退出 GUI。
        """
        if self._sigint_handling:
            return
        self._sigint_handling = True

        if self._is_process_running():
            self._quit_when_process_stops = True
            self._append_log("收到终端 Ctrl+C：正在停止打印并退出 GUI...")
            self.status_label.setText("状态：停止中")
            self._stop_print()
            return

        self._append_log("收到终端 Ctrl+C：正在退出 GUI...")
        QApplication.quit()

    def _force_kill_if_needed(self) -> None:
        """兜底强制结束进程。"""
        if self._process is None:
            return
        if self._process.state() != QProcess.ProcessState.NotRunning:
            self._append_log("进程未及时退出，执行 kill。")
            self._process.kill()

    def _on_process_output(self) -> None:
        """读取并显示子进程输出。"""
        if self._process is None:
            return
        data = bytes(self._process.readAllStandardOutput()).decode("utf-8", errors="replace")
        if data:
            self._append_log(data.rstrip("\n"))

    def _on_process_error(self, err: QProcess.ProcessError) -> None:
        """处理子进程错误事件。"""
        self._append_log(f"进程错误：{err}")

    def _on_process_finished(self, exit_code: int, _exit_status) -> None:
        """处理子进程结束事件。"""
        if exit_code == 0:
            self.status_label.setText("状态：完成")
            self._append_log("任务结束：成功。")
        elif exit_code == 130:
            self.status_label.setText("状态：已中断")
            self._append_log("任务结束：用户中断（Ctrl+C）。")
        else:
            self.status_label.setText(f"状态：失败（code={exit_code}）")
            self._append_log(f"任务结束：失败，退出码 {exit_code}。")
        self._set_running_state(False)
        self._apply_pending_config_reload()
        if self._quit_when_process_stops:
            self._append_log("打印进程已停止，正在退出 GUI。")
            QApplication.quit()

    def _set_running_state(self, running: bool) -> None:
        """更新运行态按钮状态。"""
        self.start_btn.setEnabled(not running)
        self.dry_run_btn.setEnabled(not running)
        self.self_test_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)

    def _append_log(self, text: str) -> None:
        """向日志框追加文本。"""
        if not text:
            return
        self.log_edit.appendPlainText(text)
        sb = self.log_edit.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _on_heat_toggle(self, checked: bool) -> None:
        """热敏参数开关联动。"""
        self.heat_n1_spin.setEnabled(checked)
        self.heat_n2_spin.setEnabled(checked)
        self.heat_n3_spin.setEnabled(checked)
        self._refresh_cmd_preview()

    def _on_manual_delay_toggle(self, checked: bool) -> None:
        """手动 chunk-delay 开关联动。"""
        self.chunk_delay_spin.setEnabled(checked)
        self._refresh_cmd_preview()

    def _on_smooth_send_toggle(self, checked: bool) -> None:
        """发送模式开关联动：checked=True 代表 paced。"""
        self.target_bps_spin.setEnabled(checked)
        self.inter_band_gap_spin.setEnabled(checked)
        self._refresh_cmd_preview()

    def _on_diag_toggle(self, checked: bool) -> None:
        """诊断模式开关联动。"""
        self.diag_passive_rx_check.setEnabled(checked)
        self.diag_active_status_check.setEnabled(checked)
        self.diag_every_spin.setEnabled(checked)
        self.diag_rx_wait_spin.setEnabled(checked)
        self.diag_rx_quiet_spin.setEnabled(checked)
        self.diag_status_timeout_spin.setEnabled(checked)
        self.diag_file_edit.setEnabled(checked)
        self._refresh_cmd_preview()

    def resizeEvent(self, event) -> None:
        """窗口缩放时同步刷新预览图。"""
        super().resizeEvent(event)
        self._show_scaled_preview()


def main() -> int:
    """GUI 程序入口。"""
    global _GUI_SIGINT_REQUESTED
    _GUI_SIGINT_REQUESTED = False

    app = QApplication(sys.argv)
    win = PrinterGui()
    win.show()

    def _sigint_handler(_signum, _frame) -> None:
        """SIGINT 信号处理器：只打标记，不直接操作 Qt UI。"""
        global _GUI_SIGINT_REQUESTED
        _GUI_SIGINT_REQUESTED = True

    prev_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, _sigint_handler)

    poll_timer = QTimer()
    poll_timer.setInterval(100)

    def _poll_sigint() -> None:
        global _GUI_SIGINT_REQUESTED
        if not _GUI_SIGINT_REQUESTED:
            return
        _GUI_SIGINT_REQUESTED = False
        win._handle_terminal_sigint()

    poll_timer.timeout.connect(_poll_sigint)
    poll_timer.start()
    try:
        return app.exec()
    finally:
        signal.signal(signal.SIGINT, prev_sigint)


if __name__ == "__main__":
    raise SystemExit(main())
