# 标签串口打印工具（Python）

脚本：`printer_tool.py`

默认串口：`/dev/cu.usbserial-0001`  
默认波特率：`9600`（8N1，无流控）
默认模式：`pos`（适配 80mm 的 638）

## 1. 安装依赖

```bash
python3 -m pip install -r requirements.txt
```

## 2. 文本打印（POS，默认）

```bash
python3 printer_tool.py print-text \
  --text "Hello"
```

中文建议（POS）：
- 默认 `--encoding gbk`
- 如固件支持 UTF8 可改 `--encoding utf8`

## 3. 图片打印（POS，默认）

```bash
python3 printer_tool.py print-image \
  --image gua3.png \
  --image-width 384 \
  --pos-image-cmd gs_v0 \
  --dither \
  --threshold 170 \
  --darken-passes 1 \
  --pos-strip-height 96
```

可调参数（POS）：
- `--threshold 128` 二值化阈值
- `--darken-passes 1` 打印加深（推荐 1~2）
- `--dither` 启用抖动
- `--invert` 黑白反相
- `--lsb-first` 切换位序（某些机型图像乱时可尝试）
- `--pos-image-cmd gs_v0|esc_star24` 图片协议（638 建议先用 `gs_v0`）
- `--pos-strip-height 96` 将大图按条带发送（降低乱码概率）
- `--chunk-size 64 --chunk-delay-ms 12 --write-timeout 30 --write-retry 1` 稳定发送参数
- `--flush-each-chunk` 仅在设备特别挑剔时再开（会显著变慢）
- `--flush-after-write` 发送完成后强制 flush（默认关，避免大图卡住）

## 4. 标签模式（仅当设备支持 1A 标签指令）

文本（Label）：

```bash
python3 printer_tool.py print-text \
  --mode label \
  --text "测试文本" \
  --x 40 --y 30 \
  --page-width 384 --page-height 240
```

图片（Label）：

```bash
python3 printer_tool.py print-image \
  --mode label \
  --image gua3.png \
  --x 0 --y 0 \
  --image-width 384 \
  --page-width 384 --page-height 320
```

## 5. 直接打印厂商位图样例（Label）

脚本内置了厂商文档中的 `24x24` 位图数据（`1A 21 01` 示例）：

```bash
python3 printer_tool.py print-vendor-bitmap \
  --x 0 --y 0 \
  --page-width 384 --page-height 320 \
  --show-type 0x2200
```

## 6. 调试（不发串口）

```bash
python3 printer_tool.py print-image --image gua3.png --dry-run
```

可同时导出 hex：

```bash
python3 printer_tool.py print-vendor-bitmap --dry-run --save-hex out.hex
```

## 7. 发送后回显与状态判断

脚本默认会在发送后做两件事：
1. 读取串口回显字节（reply）
2. 发送 `10 04 01~04` 查询实时状态并解析

可选参数：
- `--show-reply-hex` 打印回显的十六进制
- `--no-read-reply` 关闭回显读取
- `--no-status-check` 关闭状态查询
- `--status-timeout 0.5` 设置单次状态查询超时（秒）

## 8. 指令拼接顺序

POS（默认）：
1. `1B 40` 初始化
2. 文本直接发送，或位图使用 `1D 76 30 m xL xH yL yH d...`
3. 走纸与可选切刀

Label（`--mode label`）：
1. `1B 40` 初始化
2. `1C 26` + `1B 39 n`（文本编码）
3. `1A 5B 01 ...` 页开始
4. `1A 54 ...` 文本 或 `1A 21 ...` 位图
5. `1A 5D 00` 页结束
6. `1A 4F 00` 或 `1A 4F 01 PrintNum` 打印
7. 可选切刀
