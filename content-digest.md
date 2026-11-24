# 站点真实内容摘要（三方向共用，规格数据必须原样使用）

## 芯片选型表（11 行：型号 | 架构主频 | SRAM | WiFi | 蓝牙 | 15.4 | 存在理由）
- ESP32 初代 / WROOM-32 | Xtensa LX6 双核 240 MHz | 520 KB | Wi-Fi 4 | Classic + BLE 4.2 | — | 生态最厚：十年教程、答案和库都默认它。 跟老教程走、要做蓝牙音频（A2DP）时仍是唯一选择。
- ESP32-S2 单核 · 无蓝牙 | Xtensa LX7 单核 240 MHz | 320 KB | Wi-Fi 4 | 无 | — | 原生 USB OTG 是唯一卖点。 要模拟 HID 键鼠 / U 盘，又不需要蓝牙时才考虑。
- ESP32-S3 ★ 默认推荐 | Xtensa LX7 双核 240 MHz | 512 KB | Wi-Fi 4 | BLE 5.0 | — | 带向量指令，能做端侧 AI。摄像头 / 屏 / 语音项目的事实标准。 近两年几乎所有「好玩」的项目都跑在它上面。
- ESP32-C3 性价比连接节点 | RISC-V 单核 160 MHz | 400 KB | Wi-Fi 4 | BLE 5.0 | — | 只要「联网 + 几个 IO」时的最省解。RISC-V 入门首选。 无 PSRAM，别拿它跑大屏或语音。
- ESP32-C2 极致成本 | RISC-V 单核 120 MHz | 272 KB | Wi-Fi 4 | BLE 5.0 | — | 为走量而生，不是为折腾而生。 量产 BOM 敏感时选它；个人玩建议绕过。
- ESP32-C6 Matter 单芯片 | RISC-V 单核 160 MHz | 512 KB | Wi-Fi 6 | BLE 5.3 | ✓ Thread Zigbee | Wi-Fi 6 + Zigbee 3.0 + Thread 1.3 同 die。 做 Matter 设备几乎没得选，除非加第二颗射频。
- ESP32-C5 唯一 5 GHz | RISC-V 单核 240 MHz | 384 KB | Wi-Fi 6 2.4 + 5 GHz | BLE 5.0 | ✓ | 全家族唯一双频。 办公室/宿舍 2.4G 挤爆时，这一条就值回票价。
- ESP32-H2 无 Wi-Fi 是特性 | RISC-V 单核 96 MHz | 256 KB | 无 | BLE 5.0 | ✓ Thread Zigbee | 功耗全家族最低。 纽扣电池 + 已有 Thread/Zigbee 网关的传感器，只有它合适。
- ESP32-P4 HMI / 视觉主控 | RISC-V 双核 400 MHz | 768 KB | 无 | 无 | — | MIPI + H.264 硬编 + AI 扩展，跑大屏不卡。 无射频，做联网产品必须配 C6/C5/C61 当无线协处理器。
- ESP32-C61 Wi-Fi 6 降本款 新 | RISC-V 单核 160 MHz | — | Wi-Fi 6 | BLE 5.0 | — | C6 去掉 15.4 的成本优化版。 只要 Wi-Fi 6 不要 Thread 时，比 C6 便宜。
- ESP32-S31 多射频中枢 新 | RISC-V 双核 320 MHz | — | Wi-Fi 6 | Classic + 5.4 | ✓ | Wi-Fi 6 + BT 5.4 + 15.4 + 千兆 MAC 全塞一颗。 多协议中枢、音频、HMI 面板；但资料与生态仍在补齐。

## 大模型 Agent 区文本

    
01
大模型 Agent：
这块板子开始自己想了
    
2026 年最热的一条路。板上只负责听清、说清、执行，理解交给云。两条主线都已成熟：
小智 AI
 把语音入口和 MCP 控设备做成了标准件，
ESP-Claw
 干脆把 Agent Runtime 搬进了芯片。
    
      
        
小智 AI · xiaozhi-esp32
33.7K★ · MIT
        
离线唤醒
 ESP-SR 自带中文唤醒词，唤醒不上云，隐私和延迟都省。
链路
 Opus 编码 + 流式 ASR → LLM → TTS，WebSocket 或 MQTT+UDP 二选一。
MCP 双端
 设备端控制音量、灯、舵机、GPIO；云端 MCP 接智能家居、搜索、桌面操作。
硬件
 已适配 70+ 开源硬件（S3-BOX3、CoreS3、微雪 AMOLED 等），C3/S3/P4 都能跑。
上手
 官方服务器注册就送 Qwen 实时模型额度，烧完固件配网就能说话。
        
github.com/78/xiaozhi-esp32 ↗
      
      
        
ESP-Claw · espressif/esp-claw
2.4K★ · Apache-2.0
        
聊天造物
 在飞书/QQ/微信/Telegram 里说一句需求，模型生成 Lua 脚本下发到板子执行。
三级路由
 Lua 确定性规则走毫秒级；需要理解意图才升级到 LLM；更复杂的转云端模型。
MCP 双身份
 既能当 Server 把传感器/执行器暴露给别的 Agent，也能当 Client 调外部工具。
记忆本地
 结构化记忆存板上（标签 + JSONL），隐私不上云，跨会话还记得你。
门槛
 要 
Flash ≥ 8MB + PSRAM ≥ 8MB
；S3 / P4 / C5 / S31 可用，网页一键烧录。
        
github.com/espressif/esp-claw ↗
      
    
    
      
一句话说完的数据流
      
麦克风
I2S / PDM
→
唤醒
ESP-SR · 离线
→
编码
Opus 16k
→
上行
WS / MQTT
→
ASR
流式识别
→
LLM
+ MCP 工具
→
TTS
流式合成
→
喇叭
I2S 功放
      
时延预算：端到端 1.2–2.5 秒，钱和体验都花在这
      
唤醒词检测（板上）
0.2–0.3 s
静音判定 VAD
0.3–0.5 s
上行 + 流式 ASR 首字
0.3–0.5 s
LLM 首 token
0.3–0.8 s
TTS 首包
0.2–0.4 s
合计（用户体感的「它怎么还没说话」）
1.2–2.5 s
    
    
      
板上真正能干的，和别指望的
      
        
能跑在板上
离线唤醒词（中文自带）、VAD、回声消除（S3/P4 双麦）
Opus 编解码 + TLS + WebSocket，8MB PSRAM 够用
MCP 工具执行：GPIO、PWM、舵机、WS2812、继电器
S3 上的摄像头 JPEG 抓帧、LVGL 表情屏
本地 Lua 规则：断网也能守住的硬约束
        
别指望
板上跑 7B 级模型 —— 显存单位是 MB，不是 GB
本地 Whisper 级 ASR —— 大模型塞不进 8MB PSRAM
多轮长上下文 —— 40 轮之后必须截断，否则 token 账单失控
高质量端侧 TTS —— 能跑，但一听就是机器
完全离线对话 —— 断网只剩唤醒和本地规则
      
    
    
      
      
        
A
先听个响
        
十分钟 · 零代码
        
买一块 S3 N16R8（N16R8 是硬门槛，C3 无 PSRAM 跑不动）
网页一键烧录官方固件（无需装 ESP-IDF）
配网 → 注册 xiaozhi.me → 绑定设备
直接说话，先用官方送的 Qwen 实时额度
        
验证「这东西到底能不能用」，只在十分钟内回答。
      
      
        
B
自己当运营商
        
半天 · 一台服务器
        
部署 xinnan-tech/xiaozhi-esp32-server（11.4K★，Python）
填自己的 ASR/LLM/TTS key，换成自己的音色
接私有知识库，让回答带上你家/你公司的语料
数据不出门，成本按 token 实报实销
        
适合要把设备给别人用、或数据不能出内网的人。
      
      
        
C
让它自己长本事
        
一天 · Agent 化
        
烧 ESP-Claw 到 S3 或 P4（网页烧录，8+8MB 起步）
在设备网页里填 LLM key + 绑 IM（飞书/QQ/微信/Telegram）
发一句话：「每天 8 点温度超 28 就开风扇并发消息给我」
模型生成 Lua → 下发 → 板上本地执行，毫秒级响应
        
从「对话」升级到「替我做事」，这是今年真正的变化。
      
    
    
      
成本：语音是按分钟烧的钱（按每天 20 分钟、每轮 30 秒、回 60 字估算）
      
        
方案
单价
≈ 月账单
        
豆包 Seed-Realtime 端到端
语音进语音出，延迟最低，按分钟计费最省心
0.2 元/分钟
¥120
分离式：ASR + 文本 LLM + TTS
拼装麻烦，但便宜 4 倍，可换任意模型
ASR 1 元/小时 · TTS 3 元/万字符
¥30–35
OpenAI gpt-realtime-2.1
≈ 0.06 美元/分钟

## Hero 标题
一块芯片， 从闪烁 LED 到量产 HMI。
         ESP32 家族已有 11 款在售 SoC、4 条主流开发路线，现在还能接大模型 Agent。 这个站点把它们理成一张能直接用的地图。
## Hero 副题
不讲「Hello World 之后呢」。这里回答三个真问题：
         我该买哪块板 、 我该用哪套框架 、 别人已经用它做成了什么 。
        每一节都带官方出处与可复制的命令。

## 采购清单 board 组样例
