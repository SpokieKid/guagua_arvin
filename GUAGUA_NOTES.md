# guagua_arvin · 呱呱盒子固件（ai-vox3 fork）

基于 xiaozhi-esp32 的 **ai-vox3（呱呱盒子）** 固件，带 **638 热敏打印机** 支持。
本仓库是最后一次刷入设备的源码快照（2026-07）。

## 关键改动
- `main/boards/ai-vox3/config.h`：`PRINTER_UART_BAUD_RATE = 9600`（匹配 638 打印机出厂波特率，原为 115200）
- 打印机 MCP 工具：`self.printer.{test_hello, print_text, print_utf8_text, send_base64, print_url, get_profile}`（UART2，TX=IO5 / RX=IO6）

## 预编译固件
`firmware-prebuilt/` 下是最后刷入的二进制 + 烧录说明（`FLASH.md`）。

## 构建
```bash
source ~/esp/esp-idf/export.sh
idf.py set-target esp32s3 && idf.py build
# 或： python ./scripts/release.py ai-vox3 --name ai-vox3-aec
```
注意：ESP-IDF 项目路径不能有空格；组件仓库 components.espressif.com 需直连。
