#include <driver/rtc_io.h>
#include <esp_http_client.h>
#include <esp_lcd_panel_vendor.h>
#include <esp_log.h>
#include <esp_sleep.h>
#include <wifi_station.h>

#include <stdexcept>
#include <vector>
#include "application.h"
#include "assets/lang_config.h"
#include "button.h"
#include "config.h"
#include "display/lcd_display.h"
#include "dual_network_board.h"
#include "led/single_led.h"
#include "mcp_server.h"
#include "serial_printer_tool.h"

#include "ai_vox3_audio_codec.h"
#include "power_manager.h"

#define TAG "AIVOX3"

class AIVOX3 : public DualNetworkBoard {
  private:
    Button boot_button_;
    Button volume_up_button_;
    Button volume_down_button_;
    PowerManager *power_manager_;
    i2c_master_bus_handle_t codec_i2c_bus_;
    LcdDisplay *display_;
    SerialPrinterTool *printer_tool_ = nullptr;

    uint8_t GetAsciiFontCommandValue(int font_size) {
        if (font_size <= 1) {
            return 0x00;
        }
        if (font_size == 2) {
            return 0x11;
        }
        return 0x22;
    }

    uint8_t GetUtf8FontCommandValue(int font_size) {
        if (font_size <= 1) {
            return 0x00;
        }
        // 汉字模式先统一按倍宽倍高处理
        return 0x0C;
    }

    std::string BuildPrintPayload(const std::string &body, bool utf8_text_mode = false,
                                  int font_size = PRINTER_TEXT_FONT_SIZE_DEFAULT) {
        std::string payload;
        // 预留初始化、字号和编码切换命令空间
        payload.reserve(24 + body.size());
        // ESC @ 初始化
        payload.append("\x1B\x40", 2);
        if (utf8_text_mode) {
            // FS & 进入汉字模式
            payload.append("\x1C\x26", 2);
            // ESC 9 1 切换到 UTF-8 双字节编码
            payload.append("\x1B\x39\x01", 3);
            // FS ! n 设置汉字字号
            payload.append("\x1C\x21", 2);
            payload.push_back(static_cast<char>(GetUtf8FontCommandValue(font_size)));
        } else {
            // GS ! n 设置西文字号
            payload.append("\x1D\x21", 2);
            payload.push_back(static_cast<char>(GetAsciiFontCommandValue(font_size)));
        }

        payload.append(body);
        payload.push_back('\n');

        if (utf8_text_mode) {
            // FS . 退出汉字模式
            payload.append("\x1C\x2E", 2);
        }
        return payload;
    }

    static esp_err_t HandlePrintUrlHttpEvent(esp_http_client_event_t *evt) {
        if (evt->event_id != HTTP_EVENT_ON_DATA || evt->data == nullptr || evt->data_len <= 0) {
            return ESP_OK;
        }

        auto payload = static_cast<std::vector<unsigned char> *>(evt->user_data);
        if (payload == nullptr) {
            return ESP_FAIL;
        }

        // HTTP 返回的是 ESC/POS 原始字节流，逐块拼到内存后再统一校验发送
        const auto *data = static_cast<const unsigned char *>(evt->data);
        payload->insert(payload->end(), data, data + evt->data_len);
        return ESP_OK;
    }

    std::vector<unsigned char> DownloadPrintPayload(const std::string &url) {
        if (url.rfind("http://", 0) != 0 && url.rfind("https://", 0) != 0) {
            throw std::runtime_error("print_url 仅支持 http/https");
        }

        std::vector<unsigned char> payload;
        payload.reserve(64 * 1024);

        esp_http_client_config_t config = {};
        config.url = url.c_str();
        config.event_handler = HandlePrintUrlHttpEvent;
        config.user_data = &payload;
        config.timeout_ms = 20000;
        config.buffer_size = 1024;

        ESP_LOGI(TAG, "开始下载打印数据: url=%s", url.c_str());
        esp_http_client_handle_t client = esp_http_client_init(&config);
        if (client == nullptr) {
            throw std::runtime_error("HTTP 客户端初始化失败");
        }

        esp_err_t err = esp_http_client_perform(client);
        int status_code = esp_http_client_get_status_code(client);
        int64_t content_length = esp_http_client_get_content_length(client);
        esp_http_client_cleanup(client);

        if (err != ESP_OK) {
            throw std::runtime_error("下载打印数据失败: " + std::to_string(static_cast<int>(err)));
        }
        if (status_code < 200 || status_code >= 300) {
            throw std::runtime_error("下载打印数据 HTTP 状态异常: " + std::to_string(status_code));
        }
        if (payload.empty()) {
            throw std::runtime_error("下载打印数据为空");
        }
        if (content_length > 0 && static_cast<int64_t>(payload.size()) != content_length) {
            throw std::runtime_error("下载打印数据长度不完整");
        }
        if (payload.size() > PRINTER_BASE64_MAX_CHARS) {
            throw std::runtime_error("下载打印数据过大，已超过设备限制");
        }

        ESP_LOGI(TAG,
                 "打印数据下载完成: bytes=%u content_length=%lld status=%d",
                 static_cast<unsigned>(payload.size()),
                 static_cast<long long>(content_length),
                 status_code);
        return payload;
    }

    void InitializePowerManager() { power_manager_ = new PowerManager(BATTERY_LEVEL_PIN, BATTERY_CHARGING_PIN); }

    void InitializeI2c() {
        i2c_master_bus_config_t i2c_bus_cfg = {
            .i2c_port = I2C_NUM_0,
            .sda_io_num = AUDIO_CODEC_I2C_SDA_PIN,
            .scl_io_num = AUDIO_CODEC_I2C_SCL_PIN,
            .clk_source = I2C_CLK_SRC_DEFAULT,
            .glitch_ignore_cnt = 7,
            .intr_priority = 0,
            .trans_queue_depth = 0,
            .flags =
                {
                    .enable_internal_pullup = 1,
                },
        };
        ESP_ERROR_CHECK(i2c_new_master_bus(&i2c_bus_cfg, &codec_i2c_bus_));
    }

    void InitializeSpi() {
        spi_bus_config_t buscfg = {};
        buscfg.mosi_io_num = DISPLAY_MOSI_PIN;
        buscfg.miso_io_num = GPIO_NUM_NC;
        buscfg.sclk_io_num = DISPLAY_CLK_PIN;
        buscfg.quadwp_io_num = GPIO_NUM_NC;
        buscfg.quadhd_io_num = GPIO_NUM_NC;
        buscfg.max_transfer_sz = DISPLAY_WIDTH * DISPLAY_HEIGHT * sizeof(uint16_t);
        ESP_ERROR_CHECK(spi_bus_initialize(SPI3_HOST, &buscfg, SPI_DMA_CH_AUTO));
    }

    void InitializeLcdDisplay() {
        esp_lcd_panel_io_handle_t panel_io = nullptr;
        esp_lcd_panel_handle_t panel = nullptr;

        // 液晶屏控制IO初始化
        ESP_LOGD(TAG, "Install panel IO");
        esp_lcd_panel_io_spi_config_t io_config = {};
        io_config.cs_gpio_num = DISPLAY_CS_PIN;
        io_config.dc_gpio_num = DISPLAY_DC_PIN;
        io_config.spi_mode = DISPLAY_SPI_MODE;
        io_config.pclk_hz = 40 * 1000 * 1000;
        io_config.trans_queue_depth = 10;
        io_config.lcd_cmd_bits = 8;
        io_config.lcd_param_bits = 8;
        ESP_ERROR_CHECK(esp_lcd_new_panel_io_spi(SPI3_HOST, &io_config, &panel_io));

        // 初始化液晶屏驱动芯片
        ESP_LOGD(TAG, "Install LCD driver");
        esp_lcd_panel_dev_config_t panel_config = {};
        panel_config.reset_gpio_num = DISPLAY_RST_PIN;
        panel_config.rgb_ele_order = DISPLAY_RGB_ORDER;
        panel_config.bits_per_pixel = 16;
        ESP_ERROR_CHECK(esp_lcd_new_panel_st7789(panel_io, &panel_config, &panel));

        esp_lcd_panel_reset(panel);

        esp_lcd_panel_init(panel);
        esp_lcd_panel_invert_color(panel, DISPLAY_INVERT_COLOR);
        esp_lcd_panel_swap_xy(panel, DISPLAY_SWAP_XY);
        esp_lcd_panel_mirror(panel, DISPLAY_MIRROR_X, DISPLAY_MIRROR_Y);

        display_ = new SpiLcdDisplay(panel_io, panel, DISPLAY_WIDTH, DISPLAY_HEIGHT, DISPLAY_OFFSET_X, DISPLAY_OFFSET_Y,
                                     DISPLAY_MIRROR_X, DISPLAY_MIRROR_Y, DISPLAY_SWAP_XY);
    }

    void InitializeButtons() {
        boot_button_.OnClick([this]() {
            auto &app = Application::GetInstance();
            if (GetNetworkType() == NetworkType::WIFI) {
                if (app.GetDeviceState() == kDeviceStateStarting ||
                    app.GetDeviceState() == kDeviceStateWifiConfiguring) {
                    // cast to WifiBoard
                    auto &wifi_board = static_cast<WifiBoard &>(GetCurrentBoard());
                    wifi_board.EnterWifiConfigMode();
                }
            }
            app.ToggleChatState();
        });

        boot_button_.OnLongPress([this]() {
            auto &app = Application::GetInstance();
            if (app.GetDeviceState() == kDeviceStateStarting || app.GetDeviceState() == kDeviceStateWifiConfiguring) {
                SwitchNetworkType();
            }
        });

#if CONFIG_USE_DEVICE_AEC
        boot_button_.OnDoubleClick([this]() {
            auto &app = Application::GetInstance();
            if (app.GetDeviceState() == kDeviceStateIdle) {
                app.SetAecMode(app.GetAecMode() == kAecOff ? kAecOnDeviceSide : kAecOff);
            }
        });
#endif

        volume_up_button_.OnClick([this]() {
            auto codec = GetAudioCodec();
            auto volume = codec->output_volume() + 10;
            if (volume > 100) {
                volume = 100;
            }
            codec->SetOutputVolume(volume);
            GetDisplay()->ShowNotification(Lang::Strings::VOLUME + std::to_string(volume));
        });

        volume_up_button_.OnLongPress([this]() {
            GetAudioCodec()->SetOutputVolume(100);
            GetDisplay()->ShowNotification(Lang::Strings::MAX_VOLUME);
        });

        volume_down_button_.OnClick([this]() {
            auto codec = GetAudioCodec();
            auto volume = codec->output_volume() - 10;
            if (volume < 0) {
                volume = 0;
            }
            codec->SetOutputVolume(volume);
            GetDisplay()->ShowNotification(Lang::Strings::VOLUME + std::to_string(volume));
        });

        volume_down_button_.OnLongPress([this]() {
            GetAudioCodec()->SetOutputVolume(0);
            GetDisplay()->ShowNotification(Lang::Strings::MUTED);
        });
    }

    // 物联网初始化，添加对 AI 可见设备
    void InitializeTools() {
        // 初始化打印串口：UART2 + IO5(TX)/IO6(RX)
        printer_tool_ = new SerialPrinterTool(PRINTER_UART_PORT,
                                              PRINTER_UART_TX_PIN,
                                              PRINTER_UART_RX_PIN,
                                              PRINTER_UART_BAUD_RATE,
                                              PRINTER_BASE64_MAX_CHARS,
                                              PRINTER_FEED_LINES_AFTER_PRINT);

        std::string init_error;
        if (!printer_tool_->Initialize(&init_error)) {
            ESP_LOGE(TAG, "打印串口初始化失败: %s", init_error.c_str());
        }

        auto &mcp_server = McpServer::GetInstance();
        // 先让服务端读取参数画像，确认型号/纸宽/波特率/板型
        mcp_server.AddTool(
            "self.printer.get_profile",
            "获取当前打印链路参数。服务端下发打印前先调用此工具，确认型号、纸宽、波特率和板型一致。",
            PropertyList(),
            [this](const PropertyList &) -> ReturnValue {
                cJSON *result = cJSON_CreateObject();
                cJSON_AddStringToObject(result, "board", BOARD_TYPE);
                cJSON_AddStringToObject(result, "printer_model", PRINTER_MODEL);
                cJSON_AddNumberToObject(result, "paper_width_mm", PRINTER_PAPER_WIDTH_MM);
                cJSON_AddNumberToObject(result, "baud_rate", PRINTER_UART_BAUD_RATE);
                cJSON_AddStringToObject(result, "encoding", "base64");
                cJSON_AddNumberToObject(result, "tx_pin", PRINTER_UART_TX_PIN);
                cJSON_AddNumberToObject(result, "rx_pin", PRINTER_UART_RX_PIN);
                cJSON_AddBoolToObject(result, "ready", printer_tool_ != nullptr && printer_tool_->IsReady());
                if (printer_tool_ != nullptr && !printer_tool_->IsReady()) {
                    cJSON_AddStringToObject(result, "error", printer_tool_->GetInitError().c_str());
                }
                return result;
            });

        // 仅接受匹配参数的打印任务，避免发错规格
        mcp_server.AddTool(
            "self.printer.send_base64",
            "向 638 热敏打印机发送 base64 打印流。仅允许 80mm、115200、ai-vox3 的任务，参数不匹配将拒绝执行。",
            PropertyList({
                Property("data", kPropertyTypeString),
                Property("printer_model", kPropertyTypeString),
                Property("paper_width_mm", kPropertyTypeInteger),
                Property("baud_rate", kPropertyTypeInteger),
                Property("target_board", kPropertyTypeString),
            }),
            [this](const PropertyList &properties) -> ReturnValue {
                if (printer_tool_ == nullptr) {
                    throw std::runtime_error("打印工具未初始化");
                }

                auto printer_model = properties["printer_model"].value<std::string>();
                auto paper_width_mm = properties["paper_width_mm"].value<int>();
                auto baud_rate = properties["baud_rate"].value<int>();
                auto target_board = properties["target_board"].value<std::string>();
                auto data = properties["data"].value<std::string>();
                ESP_LOGI(TAG,
                         "send_base64 参数: data_len=%u printer_model=%s paper_width_mm=%d baud_rate=%d target_board=%s",
                         static_cast<unsigned>(data.size()),
                         printer_model.c_str(),
                         paper_width_mm,
                         baud_rate,
                         target_board.c_str());
                // 严格校验服务端下发参数
                if (printer_model != PRINTER_MODEL) {
                    throw std::runtime_error("printer_model 不匹配");
                }
                if (paper_width_mm != PRINTER_PAPER_WIDTH_MM) {
                    throw std::runtime_error("paper_width_mm 不匹配");
                }
                if (baud_rate != PRINTER_UART_BAUD_RATE) {
                    throw std::runtime_error("baud_rate 不匹配");
                }
                if (target_board != BOARD_TYPE) {
                    throw std::runtime_error("target_board 不匹配");
                }

                int bytes = printer_tool_->SendBase64(data);
                cJSON *result = cJSON_CreateObject();
                cJSON_AddBoolToObject(result, "ok", true);
                cJSON_AddNumberToObject(result, "bytes", bytes);
                return result;
            });

        // 通过 URL 下载完整 ESC/POS 图片打印流，避免大 base64 被服务端改写
        mcp_server.AddTool(
            "self.printer.print_url",
            "从 URL 下载 638 热敏打印机 ESC/POS 原始打印流并发送。仅允许 80mm、115200、ai-vox3 的任务，URL 内容必须是 application/octet-stream 打印字节流。",
            PropertyList({
                Property("url", kPropertyTypeString),
                Property("printer_model", kPropertyTypeString),
                Property("paper_width_mm", kPropertyTypeInteger),
                Property("baud_rate", kPropertyTypeInteger),
                Property("target_board", kPropertyTypeString),
            }),
            [this](const PropertyList &properties) -> ReturnValue {
                if (printer_tool_ == nullptr) {
                    throw std::runtime_error("打印工具未初始化");
                }

                auto url = properties["url"].value<std::string>();
                auto printer_model = properties["printer_model"].value<std::string>();
                auto paper_width_mm = properties["paper_width_mm"].value<int>();
                auto baud_rate = properties["baud_rate"].value<int>();
                auto target_board = properties["target_board"].value<std::string>();
                ESP_LOGI(TAG,
                         "print_url 参数: url_len=%u printer_model=%s paper_width_mm=%d baud_rate=%d target_board=%s",
                         static_cast<unsigned>(url.size()),
                         printer_model.c_str(),
                         paper_width_mm,
                         baud_rate,
                         target_board.c_str());
                // 严格校验服务端下发参数
                if (printer_model != PRINTER_MODEL) {
                    throw std::runtime_error("printer_model 不匹配");
                }
                if (paper_width_mm != PRINTER_PAPER_WIDTH_MM) {
                    throw std::runtime_error("paper_width_mm 不匹配");
                }
                if (baud_rate != PRINTER_UART_BAUD_RATE) {
                    throw std::runtime_error("baud_rate 不匹配");
                }
                if (target_board != BOARD_TYPE) {
                    throw std::runtime_error("target_board 不匹配");
                }

                auto payload = DownloadPrintPayload(url);
                int bytes = printer_tool_->SendEscposBytes(payload);
                cJSON *result = cJSON_CreateObject();
                cJSON_AddBoolToObject(result, "ok", true);
                cJSON_AddNumberToObject(result, "bytes", bytes);
                cJSON_AddNumberToObject(result, "downloaded_bytes", static_cast<double>(payload.size()));
                return result;
            });

        // 本地打印自测：直接打印 hello
        mcp_server.AddTool(
            "self.printer.test_hello",
            "直接通过串口打印 hello，用于本地链路测试。",
            PropertyList(),
            [this](const PropertyList &) -> ReturnValue {
                if (printer_tool_ == nullptr) {
                    throw std::runtime_error("打印工具未初始化");
                }

                int bytes = printer_tool_->SendRaw(BuildPrintPayload("hello"));
                cJSON *result = cJSON_CreateObject();
                cJSON_AddBoolToObject(result, "ok", true);
                cJSON_AddNumberToObject(result, "bytes", bytes);
                return result;
            });

        // 直接打印纯文本，当前仅适合 ASCII 文本
        mcp_server.AddTool(
            "self.printer.print_text",
            "直接通过串口打印纯文本。当前仅适合英文、数字和 ASCII 标点。",
            PropertyList({
                Property("text", kPropertyTypeString),
                Property("font_size", kPropertyTypeInteger, PRINTER_TEXT_FONT_SIZE_DEFAULT, 1, 3),
            }),
            [this](const PropertyList &properties) -> ReturnValue {
                if (printer_tool_ == nullptr) {
                    throw std::runtime_error("打印工具未初始化");
                }

                auto text = properties["text"].value<std::string>();
                auto font_size = properties["font_size"].value<int>();
                int bytes = printer_tool_->SendRaw(BuildPrintPayload(text, false, font_size));
                cJSON *result = cJSON_CreateObject();
                cJSON_AddBoolToObject(result, "ok", true);
                cJSON_AddNumberToObject(result, "bytes", bytes);
                return result;
            });

        // 直接打印 UTF-8 文本，依赖打印机支持 UTF-8 双字节编码
        mcp_server.AddTool(
            "self.printer.print_utf8_text",
            "直接通过串口打印 UTF-8 文本。用于测试 638 内置中文打印能力。",
            PropertyList({
                Property("text", kPropertyTypeString),
                Property("font_size", kPropertyTypeInteger, PRINTER_TEXT_FONT_SIZE_DEFAULT, 1, 3),
            }),
            [this](const PropertyList &properties) -> ReturnValue {
                if (printer_tool_ == nullptr) {
                    throw std::runtime_error("打印工具未初始化");
                }

                auto text = properties["text"].value<std::string>();
                auto font_size = properties["font_size"].value<int>();
                int bytes = printer_tool_->SendRaw(BuildPrintPayload(text, true, font_size));
                cJSON *result = cJSON_CreateObject();
                cJSON_AddBoolToObject(result, "ok", true);
                cJSON_AddNumberToObject(result, "bytes", bytes);
                return result;
            });
    }

  public:
    AIVOX3()
        : DualNetworkBoard(ML307_TX_PIN, ML307_RX_PIN, GPIO_NUM_NC, 0), boot_button_(BOOT_BUTTON_GPIO),
          volume_up_button_(VOLUME_UP_BUTTON_GPIO), volume_down_button_(VOLUME_DOWN_BUTTON_GPIO) {
        InitializeI2c();
        InitializeSpi();
        InitializeLcdDisplay();
        InitializePowerManager();
        InitializeButtons();
        InitializeTools();
        GetBacklight()->RestoreBrightness();
    }

    virtual Led *GetLed() override {
        static SingleLed led(BUILTIN_LED_GPIO);
        return &led;
    }

    virtual AudioCodec *GetAudioCodec() override {
        static AIVOX3AudioCodec audio_codec(codec_i2c_bus_, I2C_NUM_0, AUDIO_INPUT_SAMPLE_RATE,
                                            AUDIO_OUTPUT_SAMPLE_RATE, AUDIO_I2S_GPIO_MCLK, AUDIO_I2S_GPIO_BCLK,
                                            AUDIO_I2S_GPIO_WS, AUDIO_I2S_GPIO_DOUT, AUDIO_I2S_GPIO_DIN,
                                            AUDIO_CODEC_ES8311_ADDR, AUDIO_INPUT_REFERENCE);
        return &audio_codec;
    }

    virtual Display *GetDisplay() override { return display_; }

    virtual Backlight *GetBacklight() override {
        static PwmBacklight backlight(DISPLAY_BACKLIGHT_PIN, DISPLAY_BACKLIGHT_OUTPUT_INVERT);
        return &backlight;
    }

    virtual bool GetBatteryLevel(int &level, bool &charging, bool &discharging) override {
        charging = power_manager_->IsCharging();
        discharging = power_manager_->IsDischarging();
        level = power_manager_->GetBatteryLevel();
        return true;
    }
};

DECLARE_BOARD(AIVOX3);
