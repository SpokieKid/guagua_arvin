#include "serial_printer_tool.h"

#include <freertos/FreeRTOS.h>

#include <algorithm>
#include <cctype>
#include <cstdio>
#include <stdexcept>
#include <vector>

#include <esp_log.h>
#include <mbedtls/base64.h>

namespace {
constexpr size_t kUartTxBufferSize = 4096;
constexpr size_t kUartWriteChunkSize = 128;
constexpr TickType_t kUartChunkDrainTimeout = pdMS_TO_TICKS(1500);
constexpr TickType_t kUartInterChunkDelay = pdMS_TO_TICKS(4);
constexpr TickType_t kUartFlushTimeout = pdMS_TO_TICKS(5000);
constexpr size_t kBase64PreviewLength = 32;
constexpr size_t kBase64ContextRadius = 12;

const char* kTag = "SerialPrinter";

bool IsWhitespace(char c) {
    return std::isspace(static_cast<unsigned char>(c)) != 0;
}

bool IsBase64Char(char c) {
    unsigned char uc = static_cast<unsigned char>(c);
    return std::isalnum(uc) != 0 || c == '+' || c == '/' || c == '=';
}

std::string HexByte(unsigned char byte) {
    char buffer[5] = {};
    std::snprintf(buffer, sizeof(buffer), "0x%02X", byte);
    return std::string(buffer);
}

std::string LogPreview(const std::string& value, size_t start, size_t length) {
    std::string preview;
    if (start >= value.size()) {
        return preview;
    }

    size_t end = std::min(value.size(), start + length);
    for (size_t i = start; i < end; ++i) {
        unsigned char byte = static_cast<unsigned char>(value[i]);
        if (std::isprint(byte) != 0) {
            preview.push_back(static_cast<char>(byte));
        } else {
            preview += "\\x";
            preview += HexByte(byte).substr(2);
        }
    }
    return preview;
}

void LogBase64Preview(const std::string& label, const std::string& value) {
    size_t suffix_start = value.size() > kBase64PreviewLength ? value.size() - kBase64PreviewLength : 0;
    ESP_LOGI(kTag, "%s: len=%u prefix=%s suffix=%s",
             label.c_str(),
             static_cast<unsigned>(value.size()),
             LogPreview(value, 0, kBase64PreviewLength).c_str(),
             LogPreview(value, suffix_start, kBase64PreviewLength).c_str());
}

void ValidateBase64Characters(const std::string& value) {
    for (size_t i = 0; i < value.size(); ++i) {
        if (!IsBase64Char(value[i])) {
            size_t context_start = i > kBase64ContextRadius ? i - kBase64ContextRadius : 0;
            size_t context_len = std::min(value.size() - context_start, kBase64ContextRadius * 2 + 1);
            unsigned char byte = static_cast<unsigned char>(value[i]);
            ESP_LOGE(kTag, "base64 非法字符: pos=%u byte=%u hex=%s context=%s",
                     static_cast<unsigned>(i),
                     static_cast<unsigned>(byte),
                     HexByte(byte).c_str(),
                     LogPreview(value, context_start, context_len).c_str());
            throw std::runtime_error("base64 含非法字符: pos=" + std::to_string(i) +
                                     " byte=" + std::to_string(static_cast<unsigned>(byte)));
        }
    }

    size_t padding_pos = value.find('=');
    if (padding_pos == std::string::npos) {
        return;
    }

    size_t padding_count = value.size() - padding_pos;
    for (size_t i = padding_pos; i < value.size(); ++i) {
        if (value[i] != '=') {
            ESP_LOGE(kTag, "base64 padding 位置不合法: first_padding=%u bad_pos=%u context=%s",
                     static_cast<unsigned>(padding_pos),
                     static_cast<unsigned>(i),
                     LogPreview(value, padding_pos, std::min(value.size() - padding_pos, kBase64PreviewLength)).c_str());
            throw std::runtime_error("base64 padding 位置不合法");
        }
    }
    if (padding_count > 2) {
        ESP_LOGE(kTag, "base64 padding 数量不合法: count=%u", static_cast<unsigned>(padding_count));
        throw std::runtime_error("base64 padding 数量不合法");
    }
}

size_t ValidateEscposRasterPayload(const unsigned char* data, size_t len) {
    size_t raster_count = 0;
    for (size_t i = 0; i + 8 <= len; ++i) {
        if (data[i] != 0x1D || data[i + 1] != 0x76 || data[i + 2] != 0x30) {
            continue;
        }

        size_t width_bytes = static_cast<size_t>(data[i + 4]) | (static_cast<size_t>(data[i + 5]) << 8);
        size_t height = static_cast<size_t>(data[i + 6]) | (static_cast<size_t>(data[i + 7]) << 8);
        size_t raster_bytes = width_bytes * height;
        size_t raster_start = i + 8;
        size_t raster_end = raster_start + raster_bytes;
        ESP_LOGI(kTag,
                 "ESC/POS 光栅图: offset=%u width_bytes=%u height=%u raster_bytes=%u payload_len=%u",
                 static_cast<unsigned>(i),
                 static_cast<unsigned>(width_bytes),
                 static_cast<unsigned>(height),
                 static_cast<unsigned>(raster_bytes),
                 static_cast<unsigned>(len));

        if (width_bytes == 0 || height == 0) {
            throw std::runtime_error("ESC/POS 光栅图尺寸不合法");
        }
        if (raster_end > len) {
            ESP_LOGE(kTag,
                     "ESC/POS 光栅图数据不完整: need=%u have=%u",
                     static_cast<unsigned>(raster_end),
                     static_cast<unsigned>(len));
            throw std::runtime_error("ESC/POS 光栅图数据不完整");
        }

        raster_count++;
        i = raster_end - 1;
    }

    ESP_LOGI(kTag, "ESC/POS 光栅图校验完成: count=%u", static_cast<unsigned>(raster_count));
    return raster_count;
}

} // namespace

SerialPrinterTool::SerialPrinterTool(uart_port_t uart_port,
                                     gpio_num_t tx_pin,
                                     gpio_num_t rx_pin,
                                     int baud_rate,
                                     size_t max_base64_chars,
                                     uint8_t feed_lines_after_print)
    : uart_port_(uart_port),
      tx_pin_(tx_pin),
      rx_pin_(rx_pin),
      baud_rate_(baud_rate),
      max_base64_chars_(max_base64_chars),
      feed_lines_after_print_(feed_lines_after_print) {
}

SerialPrinterTool::~SerialPrinterTool() {
    std::lock_guard<std::mutex> lock(mutex_);
    if (!initialized_) {
        return;
    }
    uart_driver_delete(uart_port_);
    initialized_ = false;
}

bool SerialPrinterTool::Initialize(std::string* error) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (initialized_) {
        return true;
    }

    // 固定 8N1，无流控
    uart_config_t uart_config = {
        .baud_rate = baud_rate_,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };

    esp_err_t err = uart_driver_install(uart_port_, kUartTxBufferSize, 0, 0, nullptr, 0);
    if (err != ESP_OK) {
        init_error_ = "uart_driver_install 失败: " + std::to_string(static_cast<int>(err));
    } else {
        err = uart_param_config(uart_port_, &uart_config);
        if (err != ESP_OK) {
            init_error_ = "uart_param_config 失败: " + std::to_string(static_cast<int>(err));
        } else {
            err = uart_set_pin(uart_port_, tx_pin_, rx_pin_, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE);
            if (err != ESP_OK) {
                init_error_ = "uart_set_pin 失败: " + std::to_string(static_cast<int>(err));
            } else {
                initialized_ = true;
                init_error_.clear();
                ESP_LOGI(kTag, "打印串口初始化成功: uart=%d tx=%d rx=%d baud=%d",
                         static_cast<int>(uart_port_),
                         static_cast<int>(tx_pin_),
                         static_cast<int>(rx_pin_),
                         baud_rate_);
                return true;
            }
        }
    }

    ESP_LOGE(kTag, "%s", init_error_.c_str());
    if (error != nullptr) {
        *error = init_error_;
    }
    return false;
}

bool SerialPrinterTool::IsReady() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return initialized_;
}

std::string SerialPrinterTool::GetInitError() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return init_error_;
}

int SerialPrinterTool::SendRawLocked(const unsigned char* data, size_t len) {
    if (len == 0) {
        throw std::runtime_error("打印数据为空");
    }

    // 分块写串口，避免一次写入过大
    size_t offset = 0;
    while (offset < len) {
        size_t write_len = std::min(kUartWriteChunkSize, len - offset);
        int wrote = uart_write_bytes(
            uart_port_,
            reinterpret_cast<const char*>(data + offset),
            static_cast<size_t>(write_len));
        if (wrote <= 0) {
            throw std::runtime_error("串口发送失败");
        }
        offset += static_cast<size_t>(wrote);
        if (offset < len) {
            esp_err_t chunk_err = uart_wait_tx_done(uart_port_, kUartChunkDrainTimeout);
            if (chunk_err != ESP_OK) {
                throw std::runtime_error("等待串口分块发送完成失败: " + std::to_string(static_cast<int>(chunk_err)));
            }
            if (kUartInterChunkDelay > 0) {
                vTaskDelay(kUartInterChunkDelay);
            }
        }
    }

    esp_err_t err = uart_wait_tx_done(uart_port_, kUartFlushTimeout);
    if (err != ESP_OK) {
        throw std::runtime_error("等待串口发送完成失败: " + std::to_string(static_cast<int>(err)));
    }

    return static_cast<int>(len);
}

int SerialPrinterTool::SendFeedCommandLocked() {
    if (feed_lines_after_print_ == 0) {
        return 0;
    }

    // 统一在打印任务尾部补一条走纸命令
    const unsigned char feed_command[] = {'\n', '\x1B', 'd', feed_lines_after_print_};
    return SendRawLocked(feed_command, sizeof(feed_command));
}

void SerialPrinterTool::EnsureInitializedLocked() const {
    if (initialized_) {
        return;
    }
    if (!init_error_.empty()) {
        throw std::runtime_error("打印串口未初始化: " + init_error_);
    }
    throw std::runtime_error("打印串口未初始化");
}

std::string SerialPrinterTool::NormalizeBase64(const std::string& input) const {
    ESP_LOGI(kTag, "base64 接收长度: raw_len=%u max_len=%u",
             static_cast<unsigned>(input.size()),
             static_cast<unsigned>(max_base64_chars_));

    std::string normalized;
    normalized.reserve(input.size());
    // 去掉空白，兼容带换行的 base64
    for (char c : input) {
        if (!IsWhitespace(c)) {
            normalized.push_back(c);
        }
    }

    if (normalized.empty()) {
        throw std::runtime_error("base64 数据为空");
    }

    if (normalized.rfind("data:", 0) == 0) {
        // 兼容 data URL
        size_t comma_pos = normalized.find(',');
        if (comma_pos == std::string::npos || comma_pos + 1 >= normalized.size()) {
            throw std::runtime_error("data URL 格式错误");
        }
        normalized = normalized.substr(comma_pos + 1);
        ESP_LOGI(kTag, "base64 data URL 已剥离: comma_pos=%u payload_len=%u",
                 static_cast<unsigned>(comma_pos),
                 static_cast<unsigned>(normalized.size()));
    }

    LogBase64Preview("base64 归一化预览", normalized);

    if (normalized.size() > max_base64_chars_) {
        throw std::runtime_error("base64 数据过大，已超过设备限制");
    }

    ValidateBase64Characters(normalized);

    size_t mod = normalized.size() % 4;
    if (mod == 1) {
        throw std::runtime_error("base64 数据长度不合法");
    }
    if (mod == 2) {
        normalized.append("==");
    } else if (mod == 3) {
        normalized.push_back('=');
    }

    ESP_LOGI(kTag, "base64 归一化完成: normalized_len=%u mod=%u",
             static_cast<unsigned>(normalized.size()),
             static_cast<unsigned>(normalized.size() % 4));
    return normalized;
}

int SerialPrinterTool::SendRaw(const std::string& raw_payload) {
    std::lock_guard<std::mutex> lock(mutex_);
    EnsureInitializedLocked();
    int bytes = SendRawLocked(reinterpret_cast<const unsigned char*>(raw_payload.data()), raw_payload.size());
    return bytes + SendFeedCommandLocked();
}

int SerialPrinterTool::SendBase64(const std::string& base64_payload) {
    std::lock_guard<std::mutex> lock(mutex_);
    EnsureInitializedLocked();

    std::string normalized = NormalizeBase64(base64_payload);

    // 先计算解码后长度，避免重复扩容
    size_t output_len = 0;
    int ret = mbedtls_base64_decode(nullptr, 0, &output_len,
                                    reinterpret_cast<const unsigned char*>(normalized.data()),
                                    normalized.size());
    if (ret != 0 && ret != MBEDTLS_ERR_BASE64_BUFFER_TOO_SMALL) {
        LogBase64Preview("base64 预解码失败数据", normalized);
        throw std::runtime_error("base64 预解码失败: " + std::to_string(ret));
    }
    if (output_len == 0) {
        throw std::runtime_error("base64 解码结果为空");
    }

    std::vector<unsigned char> decoded(output_len);
    ret = mbedtls_base64_decode(decoded.data(), decoded.size(), &output_len,
                                reinterpret_cast<const unsigned char*>(normalized.data()),
                                normalized.size());
    if (ret != 0) {
        throw std::runtime_error("base64 解码失败: " + std::to_string(ret));
    }

    size_t raster_count = ValidateEscposRasterPayload(decoded.data(), output_len);

    int bytes = SendRawLocked(decoded.data(), output_len);
    if (raster_count > 0) {
        // 图片分段由 payload 自己控制最后走纸，避免每段之间被拉开
        ESP_LOGI(kTag, "检测到 ESC/POS 光栅图，跳过统一尾部走纸");
        return bytes;
    }
    return bytes + SendFeedCommandLocked();
}

int SerialPrinterTool::SendEscposBytes(const std::vector<unsigned char>& payload) {
    std::lock_guard<std::mutex> lock(mutex_);
    EnsureInitializedLocked();

    if (payload.empty()) {
        throw std::runtime_error("ESC/POS 打印数据为空");
    }

    // URL 下载的图片任务必须包含完整光栅图，避免把错误页面发给打印机
    size_t raster_count = ValidateEscposRasterPayload(payload.data(), payload.size());
    if (raster_count == 0) {
        throw std::runtime_error("ESC/POS 光栅图缺失");
    }

    int bytes = SendRawLocked(payload.data(), payload.size());
    ESP_LOGI(kTag, "ESC/POS 原始打印流已发送: bytes=%d raster_count=%u",
             bytes,
             static_cast<unsigned>(raster_count));
    return bytes;
}
