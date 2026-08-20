#include "websocket_protocol.h"
#include "board.h"
#include "system_info.h"
#include "application.h"
#include "settings.h"

#include <cstring>
#include <cJSON.h>
#include <esp_log.h>
#include <arpa/inet.h>
#include "assets/lang_config.h"

#define TAG "WS"
#define WEBSOCKET_RECONNECT_INTERVAL_MS 10000
#define WEBSOCKET_PING_INTERVAL_MS 30000

WebsocketProtocol::WebsocketProtocol() {
    event_group_handle_ = xEventGroupCreate();

    esp_timer_create_args_t reconnect_timer_args = {
        .callback = [](void* arg) {
            auto* protocol = static_cast<WebsocketProtocol*>(arg);
            auto& app = Application::GetInstance();
            auto alive = protocol->alive_;
            app.Schedule([protocol, alive]() {
                if (*alive) {
                    protocol->ConnectWebSocket(false);
                }
            });
        },
        .arg = this,
    };
    esp_timer_create(&reconnect_timer_args, &reconnect_timer_);

    esp_timer_create_args_t ping_timer_args = {
        .callback = [](void* arg) {
            auto* protocol = static_cast<WebsocketProtocol*>(arg);
            auto alive = protocol->alive_;
            if (!*alive || protocol->websocket_ == nullptr || !protocol->websocket_->IsConnected()) {
                return;
            }
            protocol->websocket_->Ping();
        },
        .arg = this,
    };
    esp_timer_create(&ping_timer_args, &ping_timer_);
}

WebsocketProtocol::~WebsocketProtocol() {
    *alive_ = false;
    StopReconnectTimer();
    StopPingTimer();
    if (reconnect_timer_ != nullptr) {
        esp_timer_delete(reconnect_timer_);
    }
    if (ping_timer_ != nullptr) {
        esp_timer_delete(ping_timer_);
    }
    websocket_.reset();
    vEventGroupDelete(event_group_handle_);
}

bool WebsocketProtocol::Start() {
    return ConnectWebSocket(false);
}

bool WebsocketProtocol::SendAudio(std::unique_ptr<AudioStreamPacket> packet) {
    if (!IsAudioChannelOpened()) {
        return false;
    }

    if (version_ == 2) {
        std::string serialized;
        serialized.resize(sizeof(BinaryProtocol2) + packet->payload.size());
        auto bp2 = (BinaryProtocol2*)serialized.data();
        bp2->version = htons(version_);
        bp2->type = 0;
        bp2->reserved = 0;
        bp2->timestamp = htonl(packet->timestamp);
        bp2->payload_size = htonl(packet->payload.size());
        memcpy(bp2->payload, packet->payload.data(), packet->payload.size());

        return websocket_->Send(serialized.data(), serialized.size(), true);
    } else if (version_ == 3) {
        std::string serialized;
        serialized.resize(sizeof(BinaryProtocol3) + packet->payload.size());
        auto bp3 = (BinaryProtocol3*)serialized.data();
        bp3->type = 0;
        bp3->reserved = 0;
        bp3->payload_size = htons(packet->payload.size());
        memcpy(bp3->payload, packet->payload.data(), packet->payload.size());

        return websocket_->Send(serialized.data(), serialized.size(), true);
    } else {
        return websocket_->Send(packet->payload.data(), packet->payload.size(), true);
    }
}

bool WebsocketProtocol::SendText(const std::string& text) {
    if (websocket_ == nullptr || !websocket_->IsConnected()) {
        return false;
    }

    if (!websocket_->Send(text)) {
        ESP_LOGE(TAG, "Failed to send text: %s", text.c_str());
        SetError(Lang::Strings::SERVER_ERROR);
        return false;
    }

    return true;
}

bool WebsocketProtocol::IsAudioChannelOpened() const {
    return websocket_ != nullptr && websocket_->IsConnected() && connection_ready_ && !error_occurred_;
}

void WebsocketProtocol::CloseAudioChannel() {
    bool notify_audio_closed = audio_channel_opened_;
    manual_disconnect_ = true;
    connection_ready_ = false;
    audio_channel_opened_ = false;
    StopReconnectTimer();
    StopPingTimer();
    websocket_.reset();
    if (on_disconnected_ != nullptr) {
        on_disconnected_();
    }
    if (notify_audio_closed && on_audio_channel_closed_ != nullptr) {
        on_audio_channel_closed_();
    }
}

bool WebsocketProtocol::OpenAudioChannel() {
    if (!IsAudioChannelOpened() && !ConnectWebSocket(true)) {
        return false;
    }

    // 常连模式下，这里只负责开启语音会话
    error_occurred_ = false;
    if (!audio_channel_opened_) {
        audio_channel_opened_ = true;
        if (on_audio_channel_opened_ != nullptr) {
            on_audio_channel_opened_();
        }
    }
    return true;
}

bool WebsocketProtocol::ConnectWebSocket(bool report_error) {
    Settings settings("websocket", false);
    std::string url = settings.GetString("url");
    std::string token = settings.GetString("token");
    int version = settings.GetInt("version");
    if (version != 0) {
        version_ = version;
    }

    if (url.empty()) {
        ESP_LOGW(TAG, "Websocket url is not specified");
        if (report_error) {
            SetError(Lang::Strings::SERVER_NOT_FOUND);
        }
        return false;
    }

    if (websocket_ != nullptr && websocket_->IsConnected() && connection_ready_) {
        return true;
    }

    error_occurred_ = false;
    manual_disconnect_ = false;
    connection_ready_ = false;
    StopReconnectTimer();
    StopPingTimer();
    xEventGroupClearBits(event_group_handle_, WEBSOCKET_PROTOCOL_SERVER_HELLO_EVENT);

    auto network = Board::GetInstance().GetNetwork();
    websocket_ = network->CreateWebSocket(1);
    if (websocket_ == nullptr) {
        ESP_LOGE(TAG, "Failed to create websocket");
        return false;
    }

    if (!token.empty()) {
        // If token not has a space, add "Bearer " prefix
        if (token.find(" ") == std::string::npos) {
            token = "Bearer " + token;
        }
        websocket_->SetHeader("Authorization", token.c_str());
    }
    websocket_->SetHeader("Protocol-Version", std::to_string(version_).c_str());
    websocket_->SetHeader("Device-Id", SystemInfo::GetMacAddress().c_str());
    websocket_->SetHeader("Client-Id", Board::GetInstance().GetUuid().c_str());

    websocket_->OnData([this](const char* data, size_t len, bool binary) {
        if (binary) {
            if (on_incoming_audio_ != nullptr) {
                if (version_ == 2) {
                    BinaryProtocol2* bp2 = (BinaryProtocol2*)data;
                    bp2->version = ntohs(bp2->version);
                    bp2->type = ntohs(bp2->type);
                    bp2->timestamp = ntohl(bp2->timestamp);
                    bp2->payload_size = ntohl(bp2->payload_size);
                    auto payload = (uint8_t*)bp2->payload;
                    on_incoming_audio_(std::make_unique<AudioStreamPacket>(AudioStreamPacket{
                        .sample_rate = server_sample_rate_,
                        .frame_duration = server_frame_duration_,
                        .timestamp = bp2->timestamp,
                        .payload = std::vector<uint8_t>(payload, payload + bp2->payload_size)
                    }));
                } else if (version_ == 3) {
                    BinaryProtocol3* bp3 = (BinaryProtocol3*)data;
                    bp3->type = bp3->type;
                    bp3->payload_size = ntohs(bp3->payload_size);
                    auto payload = (uint8_t*)bp3->payload;
                    on_incoming_audio_(std::make_unique<AudioStreamPacket>(AudioStreamPacket{
                        .sample_rate = server_sample_rate_,
                        .frame_duration = server_frame_duration_,
                        .timestamp = 0,
                        .payload = std::vector<uint8_t>(payload, payload + bp3->payload_size)
                    }));
                } else {
                    on_incoming_audio_(std::make_unique<AudioStreamPacket>(AudioStreamPacket{
                        .sample_rate = server_sample_rate_,
                        .frame_duration = server_frame_duration_,
                        .timestamp = 0,
                        .payload = std::vector<uint8_t>((uint8_t*)data, (uint8_t*)data + len)
                    }));
                }
            }
        } else {
            // Parse JSON data
            auto root = cJSON_Parse(data);
            auto type = cJSON_GetObjectItem(root, "type");
            if (cJSON_IsString(type)) {
                if (strcmp(type->valuestring, "hello") == 0) {
                    ParseServerHello(root);
                } else {
                    if (on_incoming_json_ != nullptr) {
                        on_incoming_json_(root);
                    }
                }
            } else {
                ESP_LOGE(TAG, "Missing message type, data: %s", data);
            }
            cJSON_Delete(root);
        }
        last_incoming_time_ = std::chrono::steady_clock::now();
    });

    websocket_->OnDisconnected([this]() {
        ESP_LOGI(TAG, "Websocket disconnected");
        HandleDisconnected();
    });

    ESP_LOGI(TAG, "Connecting to websocket server: %s with version: %d", url.c_str(), version_);
    if (!websocket_->Connect(url.c_str())) {
        ESP_LOGE(TAG, "Failed to connect to websocket server, code=%d", websocket_->GetLastError());
        websocket_.reset();
        if (report_error) {
            SetError(Lang::Strings::SERVER_NOT_CONNECTED);
        }
        ScheduleReconnect();
        return false;
    }

    // Send hello message to describe the client
    auto message = GetHelloMessage();
    if (!SendText(message)) {
        websocket_.reset();
        if (report_error) {
            SetError(Lang::Strings::SERVER_ERROR);
        }
        ScheduleReconnect();
        return false;
    }

    // Wait for server hello
    EventBits_t bits = xEventGroupWaitBits(event_group_handle_, WEBSOCKET_PROTOCOL_SERVER_HELLO_EVENT, pdTRUE, pdFALSE, pdMS_TO_TICKS(10000));
    if (!(bits & WEBSOCKET_PROTOCOL_SERVER_HELLO_EVENT)) {
        ESP_LOGE(TAG, "Failed to receive server hello");
        websocket_.reset();
        if (report_error) {
            SetError(Lang::Strings::SERVER_TIMEOUT);
        }
        ScheduleReconnect();
        return false;
    }

    connection_ready_ = true;
    last_incoming_time_ = std::chrono::steady_clock::now();
    // 用协议层 ping 维持空闲连接
    StartPingTimer();
    if (on_connected_ != nullptr) {
        on_connected_();
    }
    return true;
}

std::string WebsocketProtocol::GetHelloMessage() {
    // keys: message type, version, audio_params (format, sample_rate, channels)
    cJSON* root = cJSON_CreateObject();
    cJSON_AddStringToObject(root, "type", "hello");
    cJSON_AddNumberToObject(root, "version", version_);
    cJSON* features = cJSON_CreateObject();
#if CONFIG_USE_SERVER_AEC
    cJSON_AddBoolToObject(features, "aec", true);
#endif
    cJSON_AddBoolToObject(features, "mcp", true);
    cJSON_AddItemToObject(root, "features", features);
    cJSON_AddStringToObject(root, "transport", "websocket");
    cJSON* audio_params = cJSON_CreateObject();
    cJSON_AddStringToObject(audio_params, "format", "opus");
    cJSON_AddNumberToObject(audio_params, "sample_rate", 16000);
    cJSON_AddNumberToObject(audio_params, "channels", 1);
    cJSON_AddNumberToObject(audio_params, "frame_duration", OPUS_FRAME_DURATION_MS);
    cJSON_AddItemToObject(root, "audio_params", audio_params);
    auto json_str = cJSON_PrintUnformatted(root);
    std::string message(json_str);
    cJSON_free(json_str);
    cJSON_Delete(root);
    return message;
}

void WebsocketProtocol::ParseServerHello(const cJSON* root) {
    auto transport = cJSON_GetObjectItem(root, "transport");
    if (transport == nullptr || strcmp(transport->valuestring, "websocket") != 0) {
        ESP_LOGE(TAG, "Unsupported transport: %s", transport->valuestring);
        return;
    }

    auto session_id = cJSON_GetObjectItem(root, "session_id");
    if (cJSON_IsString(session_id)) {
        session_id_ = session_id->valuestring;
        ESP_LOGI(TAG, "Session ID: %s", session_id_.c_str());
    }

    auto audio_params = cJSON_GetObjectItem(root, "audio_params");
    if (cJSON_IsObject(audio_params)) {
        auto sample_rate = cJSON_GetObjectItem(audio_params, "sample_rate");
        if (cJSON_IsNumber(sample_rate)) {
            server_sample_rate_ = sample_rate->valueint;
        }
        auto frame_duration = cJSON_GetObjectItem(audio_params, "frame_duration");
        if (cJSON_IsNumber(frame_duration)) {
            server_frame_duration_ = frame_duration->valueint;
        }
    }

    xEventGroupSetBits(event_group_handle_, WEBSOCKET_PROTOCOL_SERVER_HELLO_EVENT);
}

void WebsocketProtocol::ScheduleReconnect() {
    if (manual_disconnect_ || reconnect_timer_ == nullptr) {
        return;
    }
    if (esp_timer_is_active(reconnect_timer_)) {
        return;
    }
    // 避免断网时在回调里反复抢连
    esp_timer_start_once(reconnect_timer_, WEBSOCKET_RECONNECT_INTERVAL_MS * 1000);
}

void WebsocketProtocol::StopReconnectTimer() {
    if (reconnect_timer_ != nullptr && esp_timer_is_active(reconnect_timer_)) {
        esp_timer_stop(reconnect_timer_);
    }
}

void WebsocketProtocol::StopPingTimer() {
    if (ping_timer_ != nullptr && esp_timer_is_active(ping_timer_)) {
        esp_timer_stop(ping_timer_);
    }
}

void WebsocketProtocol::StartPingTimer() {
    if (ping_timer_ == nullptr) {
        return;
    }
    StopPingTimer();
    esp_timer_start_periodic(ping_timer_, WEBSOCKET_PING_INTERVAL_MS * 1000);
}

void WebsocketProtocol::HandleDisconnected() {
    bool notify_audio_closed = audio_channel_opened_;
    connection_ready_ = false;
    audio_channel_opened_ = false;
    StopPingTimer();
    if (on_disconnected_ != nullptr) {
        on_disconnected_();
    }
    if (notify_audio_closed && on_audio_channel_closed_ != nullptr) {
        on_audio_channel_closed_();
    }
    ScheduleReconnect();
}
