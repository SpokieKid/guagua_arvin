1. 使用idf的环境变量
```BASH
. ~/code/xiaozhi_guagua/esp-idf/export.sh
```
2. 通过配置文件main/boards/ai-vox3/config.json 编译:
```BASH
python3 ./scripts/release.py ai-vox3
```
3. 只编译main/boards/ai-vox3/config.json中的 ai-vox3:
```BASH
python3 ./scripts/release.py ai-vox3 --name ai-vox3
```
产物会在build文件夹和release文件夹中
4. 编译配置怎么修改
默认使用的是根目录的sdkconfig
config.json会追加配置进去来影响条件编译
5. 烧录
1. 烧录build文件夹中的产物
```BASH
idf.py flash
```
2. 烧录特定的bin，从0x0开始烧录，配网信息也会抹掉
```BASH
esptool.py --chip esp32s3 --port /dev/cu.usbmodem1101 --baud 921600 write_flash 0x0 releases/merged-binary.bin
```
6. 串口连接口
侧边有一个PH2.0接口可以使用，io5+io6接口可以使用, 并且刚好是5v的接口
从上到下依次是：
G
5v
io5
io6
7. 接入外设
https://dcnmu33qx4fc.feishu.cn/docx/EcXxdXiuJomKDyxjSoIc6af0nig
沉淀出的调用方法：
    1. 外设必须在 Engine::Start() 前完成初始化。
    2. 外设能力要封装成 MCP Tool（名称、描述、参数 schema）。
    3. 语音意图最终会映射为 McpToolCallEvent，在循环里按 tool name 分发执行。
    4. 执行前要做参数校验，执行后用 SendMcpCallResponse/Error 回传结果。
    5. 这套模式适合把灯、舵机、电机、串口设备都标准化成 self.xxx.yyy 工具。

    InitializeTools