#ifndef SERIAL_PRINTER_TOOL_H
#define SERIAL_PRINTER_TOOL_H

#include <driver/gpio.h>
#include <driver/uart.h>

#include <mutex>
#include <string>
#include <vector>

class SerialPrinterTool {
public:
    SerialPrinterTool(uart_port_t uart_port,
                      gpio_num_t tx_pin,
                      gpio_num_t rx_pin,
                      int baud_rate,
                      size_t max_base64_chars,
                      uint8_t feed_lines_after_print);
    ~SerialPrinterTool();

    // 初始化打印串口驱动
    bool Initialize(std::string* error = nullptr);
    // 返回串口是否初始化完成
    bool IsReady() const;
    // 返回最近一次初始化错误
    std::string GetInitError() const;
    // 直接发送原始打印字节流
    int SendRaw(const std::string& raw_payload);
    // 接收 base64 打印流并经串口发送原始字节
    int SendBase64(const std::string& base64_payload);
    // 发送已生成好的 ESC/POS 打印字节流
    int SendEscposBytes(const std::vector<unsigned char>& payload);

private:
    void EnsureInitializedLocked() const;
    int SendRawLocked(const unsigned char* data, size_t len);
    int SendFeedCommandLocked();
    std::string NormalizeBase64(const std::string& input) const;

    uart_port_t uart_port_;
    gpio_num_t tx_pin_;
    gpio_num_t rx_pin_;
    int baud_rate_;
    size_t max_base64_chars_;
    uint8_t feed_lines_after_print_;
    bool initialized_ = false;
    std::string init_error_;
    mutable std::mutex mutex_;
};

#endif // SERIAL_PRINTER_TOOL_H
