# 呱呱盒子固件 · 预编译烧录包 (ai-vox3 / ESP32-S3 / 16MB)

最后一次刷入设备的固件二进制。关键版本特征：打印串口波特率 **9600**（匹配 638 打印机出厂设置）。

## 分区烧录地址
| 地址 | 文件 |
|---|---|
| `0x0` | bootloader.bin |
| `0x8000` | partition-table.bin |
| `0xd000` | ota_data_initial.bin |
| `0x20000` | xiaozhi.bin（主程序） |
| `0x800000` | generated_assets.bin（唤醒词/表情/打印资源） |

## esptool 命令（进下载模式：按住 BOOT → 插 USB → 松开 BOOT）
```bash
python -m esptool --chip esp32s3 -p <PORT> -b 460800 \
  --before default_reset --after hard_reset write_flash \
  0x0 bootloader.bin 0x8000 partition-table.bin 0xd000 ota_data_initial.bin \
  0x20000 xiaozhi.bin 0x800000 generated_assets.bin
```
目标设备 MAC：`10:20:ba:40:04:60`。刷完在 192.168.4.1 配网。
