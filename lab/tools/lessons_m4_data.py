# -*- coding: utf-8 -*-
"""第 11-30 课数据（M4 扩容）。

字段约定：
  pins      = [(引脚, 中文说明, 英文说明)]
  overview  = [(中文段落, 英文段落)]  —— 3 段
  points    = [(中文标题, 中文解释, 英文标题, 英文解释)] —— 4 条
  code      = 原始 Arduino C++ 源码，生成器负责语法高亮
  tl        = [{t, serial, en, ...}] —— en 是 serial 的英译；其余字段直透引擎
"""
# r''' 原始字符串保留 C 代码里的 \n 转义，且不惧双引号

COURSES = [
dict(
  no="11", title="SPI 彩屏：驱动 ST7789", titleEn="SPI display: driving ST7789",
  meta="SPI · TFT 彩屏", metaEn="SPI · TFT display", group="通信", groupEn="Communication",
  wiringHd="接线：7 根线接 SPI 彩屏", wiringHdEn="Wiring: 7 wires to the SPI display",
  wiring="以 <b>ST7789 240×240</b> 为例：<b>VCC→3V3、GND→GND、SCL→GPIO18、SDA→GPIO23、RES→GPIO26、DC→GPIO25、CS→GPIO27</b>。SPI 比 I²C 快得多，适合刷屏。注意屏幕<b>背光别从 GPIO 取电</b>。",
  wiringEn="For an <b>ST7789 240x240</b>: <b>VCC→3V3, GND→GND, SCL→GPIO18, SDA→GPIO23, RES→GPIO26, DC→GPIO25, CS→GPIO27</b>. SPI is far faster than I²C, ideal for displays. Do <b>not power the backlight from a GPIO</b>.",
  pins=[("GPIO18","SCK · SPI 时钟","SCK · SPI clock"),("GPIO23","MOSI · 主机发数据","MOSI · master out"),("GPIO25","DC · 命令/数据选择","DC · command/data select"),("GPIO27","CS · 片选","CS · chip select"),("GPIO26","RES · 复位","RES · reset")],
  overview=[
    ("<b>SPI</b> 是同步串行总线：一根时钟线 <b>SCK</b> 加一根数据线 <b>MOSI</b>，主机时钟一响就传一位。速度快（ESP32 可跑 40MHz），代价是引脚多。","<b>SPI</b> is a synchronous serial bus: a clock line <b>SCK</b> plus a data line <b>MOSI</b>, one bit per clock tick. Fast (up to 40MHz on ESP32), at the cost of more pins."),
    ("彩屏除了电源还要 <b>DC / CS / RES</b> 三根控制线：DC 告诉屏幕这次送的是命令还是像素数据，CS 选中器件，RES 硬复位。","Beyond power, a color display needs <b>DC / CS / RES</b>: DC says whether the bytes are a command or pixel data, CS selects the chip, RES hard-resets it."),
    ("这节课用 <code>Adafruit_ST7789</code> 初始化 240×240 屏，先刷一行字，再画一个红色实心圆。<b>刷屏是 SPI 最典型的应用</b>。","This lesson initializes a 240x240 panel with <code>Adafruit_ST7789</code>, prints a line of text, then draws a filled red circle. <b>Screen refresh is the classic SPI use case</b>.")],
  points=[
    ("SPI 四线","SCK/MOSI/MISO/CS。屏幕通常只接收，不接 MISO，叫 3-wire SPI。","Four SPI wires","SCK/MOSI/MISO/CS. Displays usually only receive, so MISO is omitted — 3-wire SPI."),
    ("DC 引脚","低电平送命令（如设置坐标），高电平送像素数据。接错会花屏。","DC pin","LOW sends commands (e.g. set address), HIGH sends pixel data. Wrong wiring gives garbage."),
    ("帧缓冲内存","240×240 RGB565 一帧约 115KB。ESP32 能放下，但要注意堆空间。","Framebuffer","A 240x240 RGB565 frame is ~115KB. The ESP32 can hold it, but watch heap usage."),
    ("背光取电","背光 LED 常要 20~100mA，直接从 GPIO 拉会过流，用三极管或独立 3.3V。","Backlight power","Backlight LEDs often draw 20–100mA. Don't source that from a GPIO — use a transistor.")],
  code=r'''#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>

#define TFT_CS   27
#define TFT_RST  26
#define TFT_DC   25
Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);

void setup() {
  Serial.begin(115200);
  tft.init(240, 240);            // 初始化 240x240
  tft.setRotation(2);
  tft.fillScreen(ST77XX_BLACK);
  Serial.println("ST7789 240x240 ready");
}

void loop() {
  tft.fillScreen(ST77XX_BLUE);
  tft.setTextColor(ST77XX_WHITE);
  tft.setTextSize(3);
  tft.setCursor(18, 105);
  tft.print("Hello ESP32!");
  delay(1500);

  tft.fillCircle(120, 120, 60, ST77XX_RED);
  delay(1500);
}''',
  tl=[
    dict(t=250, serial="ST7789 240×240 初始化 · SPI 40MHz", en="ST7789 240x240 ready · SPI 40MHz"),
    dict(t=700, serial="SPI 引脚：SCK=18 MOSI=23 DC=25 CS=27 RST=26", en="SPI pins: SCK=18 MOSI=23 DC=25 CS=27 RST=26", part="pinsR", state="on"),
    dict(t=1300, serial="刷屏：蓝底 + 白字 Hello ESP32!", en="Refresh: blue background + white 'Hello ESP32!'"),
    dict(t=2400, serial="绘制红色实心圆：中心(120,120) 半径 60", en="Filled red circle: center (120,120), radius 60"),
    dict(t=3100, serial="提示：背光电流大，别从 GPIO 直接取电", en="Tip: backlight draws real current — don't power it from a GPIO", part="pinsR", state="off"),
  ]
),
dict(
  no="12", title="OLED 屏：两行字显示温湿度", titleEn="OLED display: two lines of temperature and humidity",
  meta="I²C · SSD1306", metaEn="I²C · SSD1306", group="通信", groupEn="Communication",
  wiringHd="接线：OLED 只要 4 根线", wiringHdEn="Wiring: an OLED needs only 4 wires",
  wiring="<b>VCC→3V3、GND→GND、SDA→GPIO21、SCL→GPIO22</b>。SSD1306 挂在 I²C 地址 <b>0x3C</b>（少数模块是 0x3D）。相比 SPI 屏省引脚，但刷新率没那么高。",
  wiringEn="<b>VCC→3V3, GND→GND, SDA→GPIO21, SCL→GPIO22</b>. The SSD1306 lives at I²C address <b>0x3C</b> (some modules use 0x3D). Fewer pins than SPI, but a lower refresh rate.",
  pins=[("3V3","→ OLED VCC","→ OLED VCC"),("GND","→ OLED GND","→ OLED GND"),("GPIO21","→ SDA","→ SDA"),("GPIO22","→ SCL","→ SCL")],
  overview=[
    ("<b>OLED</b> 每个像素自发光，黑底纯黑、对比度高， 给小屏做状态显示最合适。常见 0.96 寸 128×64 分辨率。","<b>OLED</b> pixels emit their own light — true black, high contrast. A 0.96-inch 128x64 panel is ideal for status readouts."),
    ("它走 <b>I²C</b>，只要 SDA/SCL 两根线，还能和 BME280 之类的传感器共用总线——前提是地址不冲突。","It uses <b>I²C</b>, only SDA/SCL, and can share the bus with a BME280 — as long as addresses don't collide."),
    ("这节课初始化 SSD1306，显示两行温湿度，再画一条简易曲线。<b>屏幕初始化失败先跑 I²C 扫描</b>看地址。","This lesson initializes the SSD1306, prints two lines of readings and draws a simple trend line. <b>If init fails, run an I²C scan first</b> to find the address.")],
  points=[
    ("SSD1306 控制器","最常见的单色 OLED 驱动芯片，128×64 或 128×32，库里用 <code>Adafruit_SSD1306</code>。","SSD1306 controller","The most common mono OLED driver, 128x64 or 128x32; use <code>Adafruit_SSD1306</code>."),
    ("显存缓冲","库在 RAM 里维护一帧 128×64/8 = 1KB 缓冲，改完要调 <code>display()</code> 才送到屏幕。","Display buffer","The library keeps a 128x64/8 = 1KB buffer in RAM. Call <code>display()</code> to push it to the panel."),
    ("地址 0x3C/0x3D","由 SA0 引脚决定。找不到屏幕时扫描总线，别直接改库源码。","Address 0x3C/0x3D","Set by the SA0 pin. Scan the bus instead of editing library source when it's missing."),
    ("中文显示","默认字库不含汉字。要显示中文需自取模字库，或用图形方式画点阵。","Chinese glyphs","The default font has no CJK glyphs. You need a custom bitmap font or draw dot-matrix glyphs.")],
  code=r'''#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_W 128
#define SCREEN_H 64
Adafruit_SSD1306 oled(SCREEN_W, SCREEN_H, &Wire, -1);

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);                 // SDA, SCL
  if (!oled.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("SSD1306 not found @0x3C");
    while (1) delay(10);
  }
  oled.clearDisplay();
  oled.setTextSize(1);
  oled.setTextColor(SSD1306_WHITE);
  oled.setCursor(0, 8);  oled.println("Temp: 26.4 C");
  oled.setCursor(0, 28); oled.println("Hum : 58 %");
  oled.drawRect(0, 48, 127, 12, SSD1306_WHITE);
  oled.display();                      // 把缓冲送屏幕
  Serial.println("OLED 0x3C OK");
}

void loop() {}''',
  tl=[
    dict(t=250, serial="Wire.begin(SDA=21, SCL=22) · I²C 初始化", en="Wire.begin(SDA=21, SCL=22) · I²C init", part="pinsR", state="on"),
    dict(t=800, serial="扫描总线：found 0x3C ← SSD1306 OLED", en="Scan: found 0x3C ← SSD1306 OLED"),
    dict(t=1400, serial="写入显存：Temp 26.4 C / Hum 58 %", en="Buffer write: Temp 26.4 C / Hum 58 %"),
    dict(t=2000, serial="display() → 屏幕点亮并显示两行", en="display() → panel lights up with two lines"),
    dict(t=2700, serial="提示：找不到屏幕先扫地址 0x3C/0x3D", en="Tip: scan 0x3C/0x3D if the panel is not found", part="pinsR", state="off"),
  ]
),
dict(
  no="13", title="HTTP 客户端：把数据发上网", titleEn="HTTP client: send data to the web",
  meta="Wi-Fi · HTTP/REST", metaEn="Wi-Fi · HTTP/REST", group="通信", groupEn="Communication",
  wiringHd="接线：不用接线，联网即可", wiringHdEn="Wiring: none — just connect to Wi-Fi",
  wiring="不用外接元件。先用第 6 课的方式连上 <b>2.4GHz Wi-Fi</b>，再用 <code>HTTPClient</code> 发一个 <b>GET</b> 请求。虚拟板子的<b>模组</b>在数据收发时会点亮。",
  wiringEn="No extra parts. Connect to a <b>2.4GHz Wi-Fi</b> as in lesson 6, then issue a <b>GET</b> with <code>HTTPClient</code>. The virtual <b>module</b> lights up during transfer.",
  pins=[("3V3","模组供电","Module power"),("GND","地","Ground"),("（内置）","2.4GHz Wi-Fi","Built-in 2.4GHz Wi-Fi")],
  overview=[
    ("物联网的第一步是<b>把数据送出去</b>。HTTP 是最通用的方式：ESP32 当客户端，向服务器发 GET（取数据）或 POST（提交数据）。","The first step in IoT is <b>getting data out</b>. HTTP is the universal choice: the ESP32 acts as a client sending GET (fetch) or POST (submit)."),
    ("<code>HTTPClient</code> 库把 TCP、请求头、响应解析都封装好了。<code>http.GET()</code> 返回状态码：<b>200</b> 成功，4xx 请求错，5xx 服务端错。","<code>HTTPClient</code> wraps TCP, headers and response parsing. <code>http.GET()</code> returns a status: <b>200</b> OK, 4xx bad request, 5xx server error."),
    ("这节课请求一个天气接口，把返回的 JSON 前 120 个字符打印出来。<b>真实项目要检查状态码再解析</b>，别假设一定成功。","This lesson calls a weather endpoint and prints the first 120 characters of JSON. <b>Real projects must check the status before parsing</b> — never assume success.")],
  points=[
    ("GET vs POST","GET 把参数放在 URL 里，适合读取；POST 放请求体里，适合提交较大数据。","GET vs POST","GET puts parameters in the URL for reads; POST puts them in the body for larger submissions."),
    ("状态码","200/201 成功，401 未授权，404 路径错，500 服务端崩。先打印它再排查别的。","Status codes","200/201 OK, 401 unauthorized, 404 missing path, 500 server error. Print it first."),
    ("HTTPS 证书","<code>HTTPClient</code> 配 <code>WiFiClientSecure</code> 才能访问 https，还要设置时间或跳过证书校验。","HTTPS certificates","Use <code>WiFiClientSecure</code> for https, and set the system time or relax cert validation."),
    ("别堵住 loop","请求失败要设超时：<code>http.setTimeout(5000)</code>，否则可能卡住整个主循环。","Don't block loop","Set <code>http.setTimeout(5000)</code> so a failed request can't hang the main loop.")],
  code=r'''#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "Home-2.4G";
const char* pass = "12345678";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); Serial.print(".");
  }
  Serial.println("\nWiFi connected");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin("http://api.example.com/v1/weather?city=yixing");
    http.setTimeout(5000);
    int code = http.GET();
    Serial.printf("HTTP %d\n", code);
    if (code == 200) {
      String body = http.getString();
      Serial.println(body.substring(0, 120));
    }
    http.end();          // 记得释放连接
  }
  delay(5000);
}''',
  tl=[
    dict(t=250, serial="WiFi 已连接 · IP = 192.168.1.42", en="WiFi connected · IP = 192.168.1.42", part="module", state="on"),
    dict(t=800, serial="GET http://api.example.com/v1/weather?city=yixing", en="GET http://api.example.com/v1/weather?city=yixing"),
    dict(t=1500, serial="HTTP 200 OK · 服务器返回 JSON", en="HTTP 200 OK · JSON response received"),
    dict(t=1900, serial='响应: {"temp":26.4,"city":"yixing"}', en='Response: {"temp":26.4,"city":"yixing"}'),
    dict(t=2600, serial="提示：HTTPS 需要 WiFiClientSecure + 校时", en="Tip: HTTPS needs WiFiClientSecure + time sync", part="module", state="off"),
  ]
),
dict(
  no="14", title="Web Server：浏览器点灯", titleEn="Web server: toggle an LED from the browser",
  meta="Wi-Fi · HTTP 服务端", metaEn="Wi-Fi · HTTP server", group="通信", groupEn="Communication",
  wiringHd="接线：不用接线，用板载 LED", wiringHdEn="Wiring: none — use the on-board LED",
  wiring="ESP32 这次当<b>服务器</b>：连上 Wi-Fi 后拿到一个 IP，手机或电脑浏览器访问它就能控制 <b>GPIO2 板载 LED</b>。不用外接任何元件。",
  wiringEn="This time the ESP32 is a <b>server</b>: after connecting to Wi-Fi it gets an IP, and any browser on the same network can toggle the <b>GPIO2 on-board LED</b>. No external parts.",
  pins=[("GPIO2","板载 LED · 被控制","On-board LED · controlled"),("（内置）","Wi-Fi 监听 80 端口","Wi-Fi listening on port 80")],
  overview=[
    ("前一课 ESP32 是客户端；这节课反过来<b>当服务器</b>，监听 <b>80 端口</b>等浏览器来连。<code>WebServer</code> 库把路由分发封装好了。","Last lesson the ESP32 was a client; now it's a <b>server</b>, listening on <b>port 80</b> for browsers. The <code>WebServer</code> library handles route dispatch."),
    ("用 <code>server.on(\"/\", handleRoot)</code> 注册路径，浏览器访问 <code>/on</code> 就调用对应函数。<b>每次 loop 都要调 handleClient()</b> 才会处理请求。","Register paths with <code>server.on(\"/\", handleRoot)</code>; hitting <code>/on</code> calls its handler. <b>You must call handleClient() in every loop</b> for requests to be processed."),
    ("这节课模拟浏览器访问：先看控制页，再点 <code>/on</code> 点亮 LED。<b>手机必须用同一个 Wi-Fi</b>， Cellular 流量访问不到局域网 IP。","This lesson simulates a browser: load the control page, then hit <code>/on</code> to light the LED. <b>Your phone must be on the same Wi-Fi</b> — cellular data can't reach a LAN IP.")],
  points=[
    ("端口 80","HTTP 默认端口，浏览器地址栏不写端口就是 80。也可改成 8080 避开冲突。","Port 80","HTTP's default port — omitted in browser URLs. Use 8080 if there's a conflict."),
    ("路由注册","<code>server.on(path, fn)</code> 把 URL 映射到处理函数；<code>server.send()</code> 回响应。","Route mapping","<code>server.on(path, fn)</code> maps a URL to a handler; <code>server.send()</code> returns the response."),
    ("handleClient()","非阻塞地处理一个待处理请求。忘了调用，浏览器就会一直转圈。","handleClient()","Processes one pending request without blocking. Forget it and the browser spins forever."),
    ("局域网 IP","<code>WiFi.localIP()</code> 打印出来，形如 192.168.1.42。路由器重启后可能变，建议配静态 IP。","LAN IP","<code>WiFi.localIP()</code> prints something like 192.168.1.42. It may change after a reboot — consider a static IP.")],
  code=r'''#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "Home-2.4G";
const char* pass = "12345678";
const int LED = 2;
WebServer server(80);

void handleRoot() {
  server.send(200, "text/html",
    "<h1>ESP32 LED</h1><a href='/on'>ON</a> / <a href='/off'>OFF</a>");
}
void handleOn()  { digitalWrite(LED, HIGH); server.send(200, "text/plain", "LED ON"); }
void handleOff() { digitalWrite(LED, LOW);  server.send(200, "text/plain", "LED OFF"); }

void setup() {
  Serial.begin(115200);
  pinMode(LED, OUTPUT);
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) delay(500);
  server.on("/", handleRoot);
  server.on("/on", handleOn);
  server.on("/off", handleOff);
  server.begin();
  Serial.printf("Web server: http://%s\n", WiFi.localIP().toString().c_str());
}

void loop() { server.handleClient(); }''',
  tl=[
    dict(t=250, serial="WebServer 启动 · 监听端口 80", en="WebServer started · listening on port 80", part="module", state="on"),
    dict(t=800, serial="浏览器打开 http://192.168.1.42", en="Browser opens http://192.168.1.42"),
    dict(t=1400, serial="GET / → 返回 HTML 控制页", en="GET / → HTML control page returned"),
    dict(t=2100, serial="GET /on → GPIO2 = HIGH，板载 LED 亮", en="GET /on → GPIO2 = HIGH, on-board LED on", led="on"),
    dict(t=2800, serial="提示：手机需连同一个 Wi-Fi 才能访问", en="Tip: your phone must be on the same Wi-Fi", led="off", part="module", state="off"),
  ]
),
dict(
  no="15", title="WebSocket：实时双向推送", titleEn="WebSocket: real-time two-way push",
  meta="Wi-Fi · WebSocket", metaEn="Wi-Fi · WebSocket", group="通信", groupEn="Communication",
  wiringHd="接线：不用接线，走 Wi-Fi", wiringHdEn="Wiring: none — over Wi-Fi",
  wiring="不用外接元件。WebSocket 在 TCP 上建立<b>长连接</b>，双方都能随时发消息，不像 HTTP 每次都要重新请求。虚拟板子的<b>模组</b>在连接期间高亮。",
  wiringEn="No external parts. WebSocket keeps a <b>long-lived</b> TCP connection so both sides can push messages anytime, unlike request-per-message HTTP. The virtual <b>module</b> stays highlighted while connected.",
  pins=[("（内置）","Wi-Fi · WebSocket :81","Wi-Fi · WebSocket :81"),("GPIO2","板载 LED · 可远程控制","On-board LED · remote control")],
  overview=[
    ("HTTP 是「一问一答」：要看新数据就得反复轮询。<b>WebSocket</b> 握手后保持连接，服务器有数据就主动推——延迟低、开销小。","HTTP is request/response: new data requires constant polling. <b>WebSocket</b> keeps the connection open after a handshake, so the server can push — lower latency, less overhead."),
    ("库<code>WebSocketsServer</code>监听 81 端口，用 <code>onEvent()</code> 接收连接、文本、断开事件。<code>broadcastTXT()</code> 一次发给所有客户端。","<code>WebSocketsServer</code> listens on port 81; <code>onEvent()</code> receives connect/text/disconnect events. <code>broadcastTXT()</code> sends to every client at once."),
    ("这节课模拟：客户端连上 → 收欢迎语 → 发来 ping → ESP32 每 2 秒广播一次温度。<b>断线重连</b>要在客户端做。","This lesson simulates a client connecting, receiving a welcome message, sending ping, and the ESP32 broadcasting temperature every 2 seconds. <b>Reconnect logic belongs in the client</b>.")],
  points=[
    ("ws:// 协议","浏览器里把 http 换成 ws 即可连接，默认 80，这里用 81 避免和网页服务冲突。","ws:// scheme","In the browser, swap http for ws. Default port is 80; 81 avoids colliding with the web server."),
    ("事件回调","WStype_CONNECTED / TEXT / DISCONNECTED 三类最常用，回调里别做耗时操作。","Event callbacks","WStype_CONNECTED / TEXT / DISCONNECTED are the common ones — don't block inside the callback."),
    ("心跳保活","长时间空闲会被路由器断开。双方定期 ping/pong，或每几秒推一次数据。","Keepalive","Idle connections get dropped by routers. Exchange periodic ping/pong or push data every few seconds."),
    ("与 MQTT 取舍","WebSocket 适合同一局域网的网页实时交互；跨网络、多设备用 MQTT 更合适。","vs MQTT","WebSocket suits browser UIs on one LAN; MQTT is better across networks and many devices.")],
  code=r'''#include <WiFi.h>
#include <WebSocketsServer.h>

WebSocketsServer ws = WebSocketsServer(81);
const char* ssid = "Home-2.4G";
const char* pass = "12345678";

void webSocketEvent(uint8_t num, WStype_t type,
                    uint8_t* payload, size_t len) {
  if (type == WStype_CONNECTED) {
    Serial.printf("client #%u connected\n", num);
    ws.sendTXT(num, "hello from esp32");
  }
  if (type == WStype_TEXT) {
    Serial.printf("recv: %s\n", payload);
  }
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) delay(500);
  ws.begin();
  ws.onEvent(webSocketEvent);
  Serial.printf("ws://%s:81\n", WiFi.localIP().toString().c_str());
}

void loop() {
  ws.loop();
  static unsigned long last = 0;
  if (millis() - last > 2000) {
    last = millis();
    ws.broadcastTXT("temp=26.4");
  }
}''',
  tl=[
    dict(t=250, serial="WebSocket 服务监听 ws://192.168.1.42:81", en="WebSocket listening on ws://192.168.1.42:81", part="module", state="on"),
    dict(t=800, serial="客户端 #1 握手成功（101 Switching Protocols）", en="Client #1 handshake OK (101 Switching Protocols)"),
    dict(t=1400, serial="→ 发送: hello from esp32", en="→ sent: hello from esp32"),
    dict(t=2100, serial="← 收到客户端文本: ping", en="← client text: ping"),
    dict(t=2800, serial="广播: temp=26.4（每 2 秒推一次）", en="Broadcast: temp=26.4 (every 2s)"),
    dict(t=3400, serial="提示：断线重连要在浏览器端实现", en="Tip: implement reconnect logic in the browser", part="module", state="off"),
  ]
),
dict(
  no="16", title="MQTT：发布与订阅", titleEn="MQTT: publish and subscribe",
  meta="Wi-Fi · MQTT", metaEn="Wi-Fi · MQTT", group="通信", groupEn="Communication",
  wiringHd="接线：不用接线，需要一台 broker", wiringHdEn="Wiring: none — but you need a broker",
  wiring="不用外接元件。MQTT 需要一个<b>消息代理（broker）</b>，比如局域网里跑在 192.168.1.10 的 Mosquitto。ESP32 用 <code>PubSubClient</code> 连接，<b>发布</b>温度、<b>订阅</b>控制指令。",
  wiringEn="No external parts. MQTT needs a <b>broker</b> — e.g. Mosquitto running at 192.168.1.10 on your LAN. The ESP32 connects with <code>PubSubClient</code>, <b>publishes</b> temperature and <b>subscribes</b> to commands.",
  pins=[("（内置）","Wi-Fi → MQTT broker :1883","Wi-Fi → MQTT broker :1883"),("GPIO2","板载 LED · 可订阅控制","On-board LED · controllable via subscription")],
  overview=[
    ("MQTT 是<b>发布/订阅</b>模型：设备不互相直连，都连到 broker。发布者往<b>主题（topic）</b>发消息，订阅者接收——一对多、跨网络都很自然。","MQTT is <b>publish/subscribe</b>: devices don't connect to each other, they all talk to a broker. Publishers send to a <b>topic</b>, subscribers receive it — one-to-many and cross-network come naturally."),
    ("主题用斜杠分层，比如 <code>esp32/temp</code>、<code>home/livingroom/led</code>。订阅时可用通配符 <code>+</code>（单层）和 <code>#</code>（多层）。","Topics are slash-separated: <code>esp32/temp</code>, <code>home/livingroom/led</code>. Subscriptions support <code>+</code> (one level) and <code>#</code> (many levels) wildcards."),
    ("这节课连上 broker 后订阅 <code>esp32/led</code>，每 5 秒向 <code>esp32/temp</code> 发布一次温度。<b>断线重连</b>是 MQTT 客户端的必备逻辑。","This lesson subscribes to <code>esp32/led</code> and publishes temperature to <code>esp32/temp</code> every 5 seconds. <b>Reconnect logic is mandatory</b> for any MQTT client.")],
  points=[
    ("Broker","消息中转站。公共 broker 有 hiveMQ 等，但生产环境建议自己搭，数据不出内网。","Broker","The message hub. Public ones exist (e.g. HiveMQ), but production should self-host to keep data private."),
    ("QoS 0/1/2","0 最多一次（可能丢），1 至少一次（可能重复），2 恰好一次。传感器数据常用 0。","QoS 0/1/2","0 at-most-once, 1 at-least-once, 2 exactly-once. Sensor readings usually use 0."),
    ("Last Will","客户端断线时 broker 代发一条遗嘱消息，用来通知「设备离线」。","Last Will","The broker publishes a will message when a client drops — useful for offline detection."),
    ("心跳 keepalive","<code>client.loop()</code> 要经常调用才能维持心跳并处理收到的消息。","Keepalive","Call <code>client.loop()</code> regularly to maintain the heartbeat and process incoming messages.")],
  code=r'''#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "Home-2.4G";
const char* pass = "12345678";
const char* broker = "192.168.1.10";
WiFiClient wifi;
PubSubClient mqtt(wifi);

void callback(char* topic, byte* payload, unsigned int len) {
  Serial.printf("recv [%s]: ", topic);
  for (unsigned int i = 0; i < len; i++) Serial.print((char)payload[i]);
  Serial.println();
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) delay(500);
  mqtt.setServer(broker, 1883);
  mqtt.setCallback(callback);
}

void loop() {
  if (!mqtt.connected()) {
    if (mqtt.connect("esp32-demo")) mqtt.subscribe("esp32/led");
    else delay(1000);
  }
  mqtt.loop();
  static unsigned long last = 0;
  if (millis() - last > 5000) {
    last = millis();
    mqtt.publish("esp32/temp", "26.4");
  }
}''',
  tl=[
    dict(t=250, serial="连接 broker 192.168.1.10:1883", en="Connecting to broker 192.168.1.10:1883", part="module", state="on"),
    dict(t=900, serial="CONNECTED · client id = esp32-demo", en="CONNECTED · client id = esp32-demo"),
    dict(t=1400, serial="SUBSCRIBE esp32/led · QoS 0", en="SUBSCRIBE esp32/led · QoS 0"),
    dict(t=2100, serial="收到 [esp32/led]: ON → GPIO2 = HIGH", en="Received [esp32/led]: ON → GPIO2 = HIGH", led="on"),
    dict(t=2900, serial="PUBLISH esp32/temp = 26.4", en="PUBLISH esp32/temp = 26.4"),
    dict(t=3500, serial="提示：断线后要重连并重新订阅", en="Tip: reconnect and re-subscribe after a drop", led="off", part="module", state="off"),
  ]
),
dict(
  no="17", title="BLE 广播：让手机发现你", titleEn="BLE advertising: let your phone find you",
  meta="蓝牙 · BLE", metaEn="Bluetooth · BLE", group="通信", groupEn="Communication",
  wiringHd="接线：不用接线，蓝牙在芯片里", wiringHdEn="Wiring: none — Bluetooth is built in",
  wiring="ESP32 的蓝牙也<b>内置在芯片里</b>，天线和 Wi-Fi 共用。BLE（低功耗蓝牙）适合<b>小数据、间歇广播</b>：信标、传感器读数、配网。虚拟板子的<b>模组</b>在广播期间高亮。",
  wiringEn="Bluetooth is also <b>built into the ESP32</b>, sharing the antenna with Wi-Fi. BLE suits <b>small, intermittent payloads</b>: beacons, sensor values, provisioning. The virtual <b>module</b> lights up while advertising.",
  pins=[("（内置）","2.4GHz 蓝牙 + Wi-Fi 共用天线","Shared 2.4GHz antenna for BT + Wi-Fi"),("3V3","模组供电","Module power")],
  overview=[
    ("BLE 和经典蓝牙是两码事：BLE 主打<b>低功耗</b>，连接快、包小，手机系统设置里通常搜不到，要用专门 App 或小程序。","BLE is not classic Bluetooth: it focuses on <b>low power</b>, quick connections and tiny packets. Phones usually won't show it in system settings — you need an app or mini program."),
    ("BLE 设备通过<b>广播包（advertising）</b>宣告自己，广播内容可以包含服务 UUID 和少量数据。手机扫描到后才有必要建立连接。","A BLE device announces itself with <b>advertising packets</b> carrying service UUIDs and a little data. A phone scans first, then optionally connects."),
    ("这节课广播一个 <b>Battery Service (0x180F)</b>，电量特征值 77%。<b>BLE 与 Wi-Fi 共用射频</b>，同时满负荷会互相影响。","This lesson advertises a <b>Battery Service (0x180F)</b> with a level of 77%. <b>BLE and Wi-Fi share the radio</b> — heavy use of both degrades each other.")],
  points=[
    ("GATT 服务与特征","服务和特征是 BLE 的数据组织方式：服务是容器，特征值才是真正读写的数据项。","GATT services","GATT organizes data into services (containers) and characteristics (the actual readable/writable values)."),
    ("广播间隔","间隔越短越容易被发现，但越耗电。信标常用 100ms~1s。","Advertising interval","Shorter intervals are easier to find but use more power. Beacons typically use 100ms–1s."),
    ("BLE vs 经典蓝牙","BLE 适合传感器；经典 SPP 适合透传大数据。ESP32 两者都支持，但不能同时满速。","BLE vs classic","BLE suits sensors; classic SPP suits streaming. The ESP32 supports both but not at full speed together."),
    ("手机权限","安卓 12+ 和 iOS 都要蓝牙扫描权限；没给权限时 App 扫不到，不是板子坏了。","Phone permissions","Android 12+ and iOS require Bluetooth scan permissions — no results usually means permission, not hardware.")],
  code=r'''#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

void setup() {
  Serial.begin(115200);
  BLEDevice::init("ESP32-Beacon");

  BLEServer* server = BLEDevice::createServer();
  BLEService* svc = server->createService("180F");   // Battery Service
  BLECharacteristic* ch = svc->createCharacteristic(
      "2A19", BLECharacteristic::PROPERTY_NOTIFY);   // Battery Level
  ch->addDescriptor(new BLE2902());
  uint8_t level = 77;
  ch->setValue(&level, 1);
  svc->start();

  BLEAdvertising* adv = BLEDevice::getAdvertising();
  adv->addServiceUUID("180F");
  adv->setScanResponse(true);
  adv->start();
  Serial.println("BLE advertising started");
}

void loop() { delay(1000); }''',
  tl=[
    dict(t=250, serial="BLEDevice::init(\"ESP32-Beacon\")", en="BLEDevice::init(\"ESP32-Beacon\")", part="module", state="on"),
    dict(t=800, serial="创建 Battery Service 0x180F · 特征值 77%", en="Battery Service 0x180F created · level 77%"),
    dict(t=1400, serial="广播已启动 · 手机可扫描到 ESP32-Beacon", en="Advertising started · phone can scan ESP32-Beacon"),
    dict(t=2100, serial="手机连接成功 · 读取电量 = 77%", en="Phone connected · battery level = 77%"),
    dict(t=2800, serial="提示：BLE 与 Wi-Fi 共用天线，别同时满负荷", en="Tip: BLE and Wi-Fi share the antenna", part="module", state="off"),
  ]
),
dict(
  no="18", title="蓝牙串口：手机和板子对话", titleEn="Bluetooth serial: talk to the board from your phone",
  meta="蓝牙 · SPP", metaEn="Bluetooth · SPP", group="通信", groupEn="Communication",
  wiringHd="接线：不用接线，手机配对即可", wiringHdEn="Wiring: none — pair with your phone",
  wiring="不用外接元件。<b>蓝牙 SPP</b>（串口通信协议）把蓝牙伪装成一根无线串口线：手机装个串口 App，配对后就能像用 <code>Serial</code> 一样收发文本。",
  wiringEn="No external parts. <b>Bluetooth SPP</b> emulates a wireless serial cable: pair your phone with a serial-terminal app and exchange text just like using <code>Serial</code>.",
  pins=[("（内置）","经典蓝牙 SPP","Classic Bluetooth SPP"),("GPIO2","板载 LED · 可远程控制","On-board LED · remote control")],
  overview=[
    ("SPP 是经典蓝牙的<b>串口剖面</b>，把无线链路包装成 TX/RX。对开发者最友好：不用写 App 协议，现有串口工具直接连。","SPP is classic Bluetooth's <b>serial port profile</b> — a wireless link wrapped as TX/RX. Developer-friendly: existing serial tools just connect."),
    ("<code>BluetoothSerial</code> 让 ESP32 以 <code>ESP32-SPP</code> 的名字被搜索到。手机配对后，<code>SerialBT.available()</code> / <code>readStringUntil()</code> 和有线串口用法一样。","<code>BluetoothSerial</code> makes the ESP32 discoverable as <code>ESP32-SPP</code>. After pairing, <code>SerialBT.available()</code> / <code>readStringUntil()</code> work exactly like wired serial."),
    ("这节课模拟手机发来一条消息，ESP32 回显。<b>经典蓝牙不做低功耗</b>，长时间供电的项目用 BLE 更省电。","This lesson simulates a phone message and an echo reply. <b>Classic Bluetooth isn't low-power</b> — use BLE for battery projects.")],
  points=[
    ("SPP 配对","手机第一次要配对，之后通常自动连。名字可在 <code>begin(\"名字\")</code> 里改。","SPP pairing","Pair once; phones usually reconnect automatically. Change the name with <code>begin(\"name\")</code>."),
    ("波特率无关","SPP 是数字链路，<code>SerialBT.begin()</code> 不填波特率；两端约定好换行符即可。","No baud rate","SPP is digital — <code>SerialBT.begin()</code> takes no baud rate. Just agree on line endings."),
    ("和 Serial 共存","<code>Serial</code> 仍可用于调试电脑端，<code>SerialBT</code> 走手机，两者互不干扰。","Coexist with Serial","<code>Serial</code> still debugs to your PC while <code>SerialBT</code> serves the phone — they don't interfere."),
    ("安全提醒","SPP 默认无加密认证。别用它传密码，敏感数据要走 BLE 加密或应用层加密。","Security note","SPP has no built-in auth. Don't send passwords — use BLE pairing or application-layer encryption.")],
  code=r'''#include <BluetoothSerial.h>
BluetoothSerial SerialBT;

void setup() {
  Serial.begin(115200);
  SerialBT.begin("ESP32-SPP");
  Serial.println("BT SPP ready — pair with ESP32-SPP");
}

void loop() {
  if (SerialBT.available()) {
    String s = SerialBT.readStringUntil('\n');
    Serial.printf("BT recv: %s\n", s.c_str());
    SerialBT.println("echo: " + s);
    if (s == "on")  digitalWrite(2, HIGH);
    if (s == "off") digitalWrite(2, LOW);
  }
}''',
  tl=[
    dict(t=250, serial="BluetoothSerial 启动 · 名称 ESP32-SPP", en="BluetoothSerial ready · name ESP32-SPP", part="module", state="on"),
    dict(t=900, serial="手机已配对连接（SPP 通道建立）", en="Phone paired · SPP channel established"),
    dict(t=1500, serial="← 手机发来: on", en="← phone sent: on"),
    dict(t=2000, serial="→ 回显: echo: on · GPIO2 = HIGH", en="→ echo: on · GPIO2 = HIGH", led="on"),
    dict(t=2800, serial="提示：SPP 无加密，别用它传密码", en="Tip: SPP has no encryption — never send secrets", led="off", part="module", state="off"),
  ]
),
dict(
  no="19", title="蜂鸣器：让板子发出声音", titleEn="Buzzer: make the board beep",
  meta="音频 · tone()", metaEn="Audio · tone()", group="传感与执行", groupEn="Sensors & Actuators",
  wiringHd="接线：蜂鸣器 + 限流电阻", wiringHdEn="Wiring: buzzer + current-limiting resistor",
  wiring="<b>有源蜂鸣器</b>给电就响；<b>无源蜂鸣器</b>需要外部方波才能发声。这节课用无源蜂鸣器：<b>正极→GPIO4、负极→GND</b>。有源蜂鸣器则直接用 <code>digitalWrite</code> 控制。",
  wiringEn="An <b>active buzzer</b> sounds when powered; a <b>passive buzzer</b> needs an external square wave. This lesson uses a passive one: <b>+→GPIO4, −→GND</b>. For an active buzzer, plain <code>digitalWrite</code> is enough.",
  pins=[("GPIO4","→ 蜂鸣器正极","→ buzzer positive"),("GND","→ 蜂鸣器负极","→ buzzer negative")],
  overview=[
    ("声音就是<b>快速变化的电压</b>。给蜂鸣器 440Hz 的方波，它就发出标准音 A。<code>tone(pin, freq, duration)</code> 用硬件 PWM 产生方波，不占 CPU。","Sound is <b>rapidly changing voltage</b>. Feed a buzzer 440Hz square wave and you get concert A. <code>tone(pin, freq, duration)</code> generates it with hardware PWM, without CPU load."),
    ("频率决定<b>音调</b>：262/294/330Hz 分别是 C4/D4/E4（Do Re Mi）。时长决定音符长短，<code>noTone()</code> 立即停。","Frequency sets <b>pitch</b>: 262/294/330Hz are C4/D4/E4 (Do Re Mi). Duration sets note length; <code>noTone()</code> stops immediately."),
    ("这节课播放三个音，再停 1.5 秒循环。<b>无源蜂鸣器不能直接接电池</b>——没有振荡它就只是个电阻。","This lesson plays three notes, then pauses 1.5s. <b>A passive buzzer won't sound on plain DC</b> — without oscillation it's just a resistor.")],
  points=[
    ("有源 vs 无源","有源内置振荡电路，给电就响固定频率；无源要外部方波，才能奏出不同音高。","Active vs passive","Active has an oscillator and beeps at one frequency when powered; passive needs an external waveform for different pitches."),
    ("tone() 底层","ESP32 的 Arduino 核心用 LEDC 通道实现 tone()，输出到任意可用 GPIO。","tone() internals","Arduino-ESP32 implements tone() on an LEDC channel and can output to almost any GPIO."),
    ("占空比 50%","方波高/低时间相等时声音最纯净。占空比偏离会让音色发闷。","50% duty","Equal high/low times give the cleanest tone. Off-duty ratios sound muffled."),
    ("别一直响","长鸣很扰民也耗电。实际项目用短促「滴」声做提示，加上静音时段。","Don't beep forever","Constant buzzing is annoying and power-hungry — use short beeps with quiet intervals.")],
  code=r'''const int BUZZ = 4;   // 无源蜂鸣器接 GPIO4

void setup() {
  Serial.begin(115200);
  pinMode(BUZZ, OUTPUT);
  Serial.println("Buzzer ready · Do Re Mi");
}

void loop() {
  tone(BUZZ, 262, 300);   // C4 · Do
  delay(350);
  tone(BUZZ, 294, 300);   // D4 · Re
  delay(350);
  tone(BUZZ, 330, 300);   // E4 · Mi
  delay(350);
  noTone(BUZZ);
  delay(1500);
}''',
  tl=[
    dict(t=250, serial="蜂鸣器就绪 · GPIO4 输出方波", en="Buzzer ready · GPIO4 square wave", part="pinsL", state="on"),
    dict(t=700, serial="♪ 262Hz · C4（Do）300ms", en="♪ 262Hz · C4 (Do) 300ms"),
    dict(t=1100, serial="♪ 294Hz · D4（Re）300ms", en="♪ 294Hz · D4 (Re) 300ms"),
    dict(t=1500, serial="♪ 330Hz · E4（Mi）300ms", en="♪ 330Hz · E4 (Mi) 300ms"),
    dict(t=2000, serial="noTone() · 静音 1.5 秒", en="noTone() · silence for 1.5s", part="pinsL", state="off"),
  ]
),
dict(
  no="20", title="舵机控制：50Hz 的角度艺术", titleEn="Servo control: the art of 50Hz angles",
  meta="PWM · 舵机", metaEn="PWM · servo", group="传感与执行", groupEn="Sensors & Actuators",
  wiringHd="接线：舵机三根线", wiringHdEn="Wiring: three wires to the servo",
  wiring="<b>信号线→GPIO4、VCC→5V、GND→GND</b>。舵机工作电流可达几百 mA，<b>别从 ESP32 的 5V 引脚取电</b>，用独立电源并把地连在一起。",
  wiringEn="<b>Signal→GPIO4, VCC→5V, GND→GND</b>. A servo can draw hundreds of mA — <b>don't power it from the ESP32's 5V pin</b>; use a separate supply with common ground.",
  pins=[("GPIO4","→ 舵机信号线（PWM）","→ servo signal (PWM)"),("5V","→ 舵机 VCC（建议独立供电）","→ servo VCC (prefer separate supply)"),("GND","→ 舵机 GND（共地）","→ servo GND (common ground)")],
  overview=[
    ("普通 PWM 调亮度，<b>舵机看的是脉冲宽度</b>。标准舵机要求 <b>50Hz</b>（周期 20ms）：1.0ms 脉宽转到 0°，1.5ms 到 90°，2.0ms 到 180°。","While LED dimming uses duty ratio, <b>servos read pulse width</b>. A standard servo wants <b>50Hz</b> (20ms period): 1.0ms → 0°, 1.5ms → 90°, 2.0ms → 180°."),
    ("所以频率必须固定 50Hz，改的是高电平持续时间。<code>ESP32Servo</code> 把这套映射封装成 <code>servo.write(角度)</code>。","The frequency must stay at 50Hz; only the high-time changes. <code>ESP32Servo</code> wraps this as <code>servo.write(angle)</code>."),
    ("这节课让舵机从 0° 扫到 180° 再扫回来。<b>供电不足时舵机会抖或复位 ESP32</b>——先查电源再查代码。","This lesson sweeps 0°→180° and back. <b>Under-powered servos jitter or reset the ESP32</b> — check power before code.")],
  points=[
    ("50Hz 固定","周期 20ms，脉宽 1000~2000µs 对应 0~180°。频率不对舵机会乱转或完全不动。","Fixed 50Hz","20ms period, 1000–2000µs pulse for 0–180°. Wrong frequency makes it jitter or not move."),
    ("独立供电","舵机峰值电流 500mA 以上，板载稳压器扛不住。独立 5V 电源 + 共地是标准接法。","Separate supply","Servos can peak above 500mA; the on-board regulator can't cope. Use an external 5V supply with shared ground."),
    ("机械限位","别长时间顶在 0°/180° 端点，齿轮会憋住发热。留几度余量。","Mechanical limits","Don't hold at 0°/180° for long — gears stall and heat up. Leave a few degrees of margin."),
    ("数字舵机","数字舵机响应更快、保持力更强，但更耗电，对电源要求更高。","Digital servos","Digital servos respond faster and hold stronger, but draw more current and need a stiffer supply.")],
  code=r'''#include <ESP32Servo.h>

Servo servo;

void setup() {
  Serial.begin(115200);
  servo.attach(4);       // 信号线 GPIO4，默认 50Hz
  Serial.println("Servo attached on GPIO4");
}

void loop() {
  servo.write(0);
  delay(1000);
  servo.write(90);
  delay(1000);
  servo.write(180);
  delay(1000);
  for (int a = 180; a >= 0; a -= 10) {
    servo.write(a);
    delay(60);
  }
}''',
  tl=[
    dict(t=250, serial="舵机附着 GPIO4 · PWM 50Hz", en="Servo attached on GPIO4 · PWM 50Hz", part="pinsL", state="on"),
    dict(t=800, serial="脉宽 1.0ms → 角度 0°", en="Pulse 1.0ms → angle 0°"),
    dict(t=1800, serial="脉宽 1.5ms → 角度 90°", en="Pulse 1.5ms → angle 90°"),
    dict(t=2800, serial="脉宽 2.0ms → 角度 180°", en="Pulse 2.0ms → angle 180°"),
    dict(t=3800, serial="回扫：180° → 0°（每步 10°）", en="Sweep back: 180° → 0° (10° steps)"),
    dict(t=4600, serial="提示：舵机要独立供电并共地", en="Tip: power the servo separately, share ground", part="pinsL", state="off"),
  ]
),
dict(
  no="21", title="超声波测距：HC-SR04", titleEn="Ultrasonic ranging: HC-SR04",
  meta="传感器 · 回波测时", metaEn="Sensor · echo timing", group="传感与执行", groupEn="Sensors & Actuators",
  wiringHd="接线：四脚模块，注意电平转换", wiringHdEn="Wiring: a 4-pin module, mind the logic level",
  wiring="<b>VCC→5V（模块用 5V）、GND→GND、TRIG→GPIO5、ECHO→分压→GPIO18</b>。HC-SR04 的 ECHO 输出 <b>5V</b>，ESP32 引脚只吃 3.3V——用 1k/2k 电阻分压或电平转换模块，别直连。",
  wiringEn="<b>VCC→5V (module runs at 5V), GND→GND, TRIG→GPIO5, ECHO→divider→GPIO18</b>. The HC-SR04 ECHO is <b>5V</b> while ESP32 pins tolerate 3.3V — use a 1k/2k divider or level shifter, never a direct connection.",
  pins=[("5V","→ 模块 VCC","→ module VCC"),("GPIO5","→ TRIG 触发","→ TRIG trigger"),("GPIO18","← ECHO 经分压","← ECHO via divider"),("GND","→ 模块 GND（共地）","→ module GND (common ground)")],
  overview=[
    ("超声波模块发出一串 <b>40kHz</b> 声波，碰到物体反射回来。<b>TRIG</b> 给 10µs 高电平触发，<b>ECHO</b> 输出一个宽度等于往返时间的脉冲。","The module emits a <b>40kHz</b> burst and listens for the echo. A <b>10µs HIGH</b> on TRIG starts it; <b>ECHO</b> outputs a pulse as wide as the round-trip time."),
    ("声速约 <b>340m/s = 0.034cm/µs</b>。距离 = 时间 × 0.034 ÷ 2——除以 2 是因为声音走了一个来回。声速受温度影响，精确测距要补偿。","Sound travels at <b>340m/s = 0.034cm/µs</b>. Distance = time × 0.034 ÷ 2 — divided by two because the wave made a round trip. Temperature affects speed; precise work needs compensation."),
    ("这节课模拟测距 25.4cm。<code>pulseIn()</code> 会阻塞等脉冲，设超时（如 30000µs）避免没有回波时卡死。<b>软垫、斜面会吸波导致测不到</b>。","This lesson simulates a 25.4cm reading. <code>pulseIn()</code> blocks waiting — always set a timeout (e.g. 30000µs) so a missing echo can't hang you. <b>Soft or angled surfaces absorb sound</b>.")],
  points=[
    ("5V 电平风险","HC-SR04 用 5V 供电，ECHO 高电平接近 5V。ESP32 的 GPIO 耐压 3.3V，必须分压。","5V level hazard","HC-SR04 runs on 5V so ECHO is near 5V. ESP32 GPIOs are 3.3V — a divider is mandatory."),
    ("pulseIn 超时","<code>pulseIn(ECHO, HIGH, 30000)</code> 返回 0 表示超时，别把它当距离 0 直接显示。","pulseIn timeout","<code>pulseIn(ECHO, HIGH, 30000)</code> returns 0 on timeout — don't display that as a real zero distance."),
    ("测量盲区","小于 2cm 或大于 400cm 基本测不准。近距离超声波还没发完，回波就回来了。","Blind zone","Below 2cm or above 400cm results are unreliable — at short range the echo returns before the burst finishes."),
    ("温度补偿","声速 ≈ 331 + 0.6×T(℃) m/s。配一个 DHT 读数补偿，精度能明显改善。","Temperature compensation","Speed ≈ 331 + 0.6×T(°C) m/s. Pairing a DHT reading improves accuracy noticeably.")],
  code=r'''const int TRIG = 5;
const int ECHO = 18;

void setup() {
  Serial.begin(115200);
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
  Serial.println("HC-SR04 ready");
}

void loop() {
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);       // 10us 触发脉冲
  digitalWrite(TRIG, LOW);

  long us = pulseIn(ECHO, HIGH, 30000);   // 30ms 超时
  float cm = us * 0.034 / 2.0;
  Serial.printf("distance: %.1f cm\n", cm);
  delay(500);
}''',
  tl=[
    dict(t=250, serial="HC-SR04 就绪 · TRIG=5 ECHO=18", en="HC-SR04 ready · TRIG=5 ECHO=18", part="pinsL", state="on"),
    dict(t=800, serial="TRIG 10µs 高脉冲 · 发射 40kHz 声波", en="TRIG 10µs pulse · emitting 40kHz burst"),
    dict(t=1500, serial="ECHO 回波脉宽 1494µs", en="ECHO pulse width 1494µs"),
    dict(t=2000, serial="距离 = 1494 × 0.034 ÷ 2 = 25.4 cm", en="Distance = 1494 × 0.034 / 2 = 25.4 cm"),
    dict(t=2700, serial="提示：ECHO 是 5V，必须分压再进 GPIO", en="Tip: ECHO is 5V — divide it before the GPIO", part="pinsL", state="off"),
  ]
),
dict(
  no="22", title="DHT11：一根线读温湿度", titleEn="DHT11: temperature and humidity on one wire",
  meta="传感器 · 单总线", metaEn="Sensor · one-wire", group="传感与执行", groupEn="Sensors & Actuators",
  wiringHd="接线：数据脚接 GPIO4", wiringHdEn="Wiring: data pin to GPIO4",
  wiring="<b>VCC→3V3（或 5V，看模块）、GND→GND、DATA→GPIO4</b>。DHT11 数据脚建议接 <b>4.7kΩ 上拉</b>到 3.3V；很多模块已自带。别和板载 LED 的 GPIO2 搞混。",
  wiringEn="<b>VCC→3V3 (or 5V, check module), GND→GND, DATA→GPIO4</b>. The DHT11 data line wants a <b>4.7kΩ pull-up</b> to 3.3V; many modules include it. Don't confuse it with the on-board LED on GPIO2.",
  pins=[("3V3","→ DHT VCC","→ DHT VCC"),("GPIO4","← DATA（单总线）","← DATA (one-wire)"),("GND","→ DHT GND","→ DHT GND")],
  overview=[
    ("DHT11 用<b>单总线</b>协议：一根数据线完成双向通信，主机先发开始信号，传感器再回 40 位数据（湿度、温度、校验和）。","The DHT11 uses a <b>one-wire</b> protocol: one data line carries both directions. The host sends a start signal, then the sensor replies with 40 bits (humidity, temperature, checksum)."),
    ("精度一般：温度 ±2℃、湿度 ±5%，采样间隔至少 <b>1~2 秒</b>。要更准可以换 <b>DHT22/SHT31</b>（后者走 I²C）。","Accuracy is modest: ±2°C, ±5% RH, with a <b>1–2s minimum</b> sampling interval. For better results use a <b>DHT22 or SHT31</b> (the latter speaks I²C)."),
    ("这节课读一次温湿度并打印。<b>读到 NaN 是常态</b>：传感器偶尔不回应，代码要判断并重试，别让一次失败崩溃。","This lesson reads and prints one sample. <b>NaN happens</b>: the sensor sometimes doesn't answer — check for it and retry instead of crashing.")],
  points=[
    ("单总线时序","主机拉低至少 18ms 再释放，传感器拉低 80µs 后逐位回应。库帮你处理了这些细节。","One-wire timing","Host pulls LOW for 18ms then releases; the sensor answers with 80µs LOW followed by bits. The library handles this."),
    ("校验和","40 位数据最后 8 位是前 32 位之和的低 8 位，用来发现传输出错。","Checksum","The last 8 of 40 bits are the low byte of the preceding 32 bits — used to detect corruption."),
    ("采样间隔","DHT11 转换慢，两次读取至少隔 1~2 秒。读太勤会得到旧数据或 NaN。","Sampling interval","DHT11 converts slowly — wait 1–2s between reads or you'll get stale data or NaN."),
    ("线长限制","单总线抗干扰差，线超过几米就容易出错。远距离改用 I²C/SPI 传感器。","Cable length","One-wire is noise-sensitive; beyond a few metres errors appear. Use I²C/SPI sensors for distance.")],
  code=r'''#include "DHT.h"

#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();
  Serial.println("DHT11 ready · GPIO4");
}

void loop() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  if (isnan(t) || isnan(h)) {
    Serial.println("DHT read failed — retry later");
    delay(2000);
    return;
  }
  Serial.printf("Temp %.1f C   Hum %.0f %%\n", t, h);
  delay(2000);
}''',
  tl=[
    dict(t=250, serial="DHT11 初始化 · DATA=GPIO4", en="DHT11 init · DATA=GPIO4", part="pinsL", state="on"),
    dict(t=800, serial="主机发送起始信号（拉低 18ms）", en="Host start signal (LOW 18ms)"),
    dict(t=1400, serial="收到 40 位数据帧 · 校验通过", en="40-bit frame received · checksum OK"),
    dict(t=1900, serial="Temp 26.0 C · Hum 58 %", en="Temp 26.0 C · Hum 58 %"),
    dict(t=2600, serial="提示：读到 NaN 要重试，别直接显示", en="Tip: retry on NaN instead of displaying it", part="pinsL", state="off"),
  ]
),
dict(
  no="23", title="红外遥控：解码 NEC 协议", titleEn="IR remote: decode the NEC protocol",
  meta="传感器 · 红外接收", metaEn="Sensor · IR receiver", group="传感与执行", groupEn="Sensors & Actuators",
  wiringHd="接线：红外接收头三根脚", wiringHdEn="Wiring: a 3-pin IR receiver",
  wiring="<b>VCC→3V3、GND→GND、OUT→GPIO4</b>。VS1838B 一类接收头自带解调，输出反向数字信号。注意接收头窗口别被东西挡住，太阳光直射也会干扰。",
  wiringEn="<b>VCC→3V3, GND→GND, OUT→GPIO4</b>. Receivers like the VS1838B demodulate internally and output inverted digital data. Keep the window unobstructed — direct sunlight also causes interference.",
  pins=[("3V3","→ IR 接收头 VCC","→ IR receiver VCC"),("GPIO4","← OUT 解调输出","← OUT demodulated"),("GND","→ IR GND","→ IR GND")],
  overview=[
    ("电视遥控器发的是 <b>38kHz 调制红外光</b>，接收头解调后输出数字脉冲。<b>NEC 协议</b>每帧 32 位：地址码 + 地址反码 + 命令码 + 命令反码。","TV remotes send <b>38kHz modulated infrared</b>; the receiver demodulates it into digital pulses. A <b>NEC frame</b> is 32 bits: address + inverted address + command + inverted command."),
    ("<code>IRrecv</code> 库帮你解码成 32 位整数，比如 <code>0xFFA25D</code> 对应 CH−。<b>不同遥控器的码值不同</b>，先用串口打印出实际值再写判断。","<code>IRrecv</code> decodes it to a 32-bit value — e.g. <code>0xFFA25D</code> for CH−. <b>Codes differ between remotes</b>: print actual values before writing conditions."),
    ("这节课模拟按下 CH− 键，ESP32 切换板载 LED。<b>解码后要调 resume()</b>，否则接收器不再收下一帧。","This lesson simulates pressing CH− to toggle the on-board LED. <b>Call resume() after decoding</b> or the receiver stops accepting frames.")],
  points=[
    ("38kHz 载波","红外 LED 以 38kHz 闪烁，接收头只认这个频率，能滤掉日光灯等干扰。","38kHz carrier","The IR LED blinks at 38kHz; receivers only accept that frequency, filtering out fluorescent-light noise."),
    ("NEC 帧结构","引导码 9ms+4.5ms，再送 32 位数据。反码用于校验，不接受就丢帧。","NEC frame","A 9ms+4.5ms leader followed by 32 bits. The inverted bytes provide validation; bad frames are dropped."),
    ("resume()","decode() 成功后必须 resume()，否则状态机停住，之后按键全部失效。","resume()","After decode() succeeds you must call resume(), otherwise the state machine stalls and later presses are ignored."),
    ("接收角度","接收头有方向性，正面约 ±30° 最灵敏。做项目时把它露在外壳正面。","Receiver angle","Receivers are directional, best within ±30° head-on — expose them on the front of the enclosure.")],
  code=r'''#include <IRremoteESP8266.h>
#include <IRrecv.h>
#include <IRutils.h>

const int RECV_PIN = 4;
IRrecv irrecv(RECV_PIN);
decode_results results;

void setup() {
  Serial.begin(115200);
  irrecv.enableIRIn();
  pinMode(2, OUTPUT);
  Serial.println("IR receiver ready · GPIO4");
}

void loop() {
  if (irrecv.decode(&results)) {
    Serial.print("IR code: 0x");
    serialPrintUint64(results.value, HEX);
    Serial.println();
    if (results.value == 0xFFA25D) digitalWrite(2, !digitalRead(2));
    irrecv.resume();          // 继续接收下一帧
    delay(100);
  }
}''',
  tl=[
    dict(t=250, serial="红外接收器就绪 · GPIO4 / NEC", en="IR receiver ready · GPIO4 / NEC", part="pinsL", state="on"),
    dict(t=800, serial="检测到 38kHz 载波 · 引导码 9ms", en="38kHz carrier detected · 9ms leader"),
    dict(t=1300, serial="解码帧: 0xFFA25D（CH−）", en="Decoded frame: 0xFFA25D (CH-)"),
    dict(t=1800, serial="匹配成功 → 切换 GPIO2 板载 LED", en="Match → toggle GPIO2 on-board LED", led="on"),
    dict(t=2500, serial="resume() · 继续接收下一帧", en="resume() · ready for the next frame", led="off", part="pinsL", state="off"),
  ]
),
dict(
  no="24", title="电容触摸：不用机械按键", titleEn="Capacitive touch: no mechanical button needed",
  meta="触摸 · touchRead()", metaEn="Touch · touchRead()", group="传感与执行", groupEn="Sensors & Actuators",
  wiringHd="接线：一根线，甚至不用线", wiringHdEn="Wiring: one wire — or none",
  wiring="<b>不用外接元件</b>。ESP32 内置触摸感应外设，<b>GPIO4（T0）</b>直接连一小块铜箔或导电胶带就是触摸键。手指靠近时读数明显下降。",
  wiringEn="<b>No external parts.</b> The ESP32 has a built-in touch peripheral — connect a small copper pad to <b>GPIO4 (T0)</b> and you have a touch key. The reading drops sharply when a finger approaches.",
  pins=[("GPIO4","T0 · 触摸电极","T0 · touch electrode"),("GND","参考地（可选）","Reference ground (optional)")],
  overview=[
    ("电容触摸靠<b>人体引入的寄生电容</b>改变充放电时间。ESP32 的触摸外设测这个时间并给出读数：<b>没碰时大，碰时小</b>。","Capacitive touch senses the <b>parasitic capacitance your finger adds</b>, which changes charge time. The ESP32 reports that as a number: <b>high when untouched, low when touched</b>."),
    ("<code>touchRead(4)</code> 返回原始值，没有统一阈值——<b>先打印空闲值，再测触摸值，取中间</b>作为门限。不同板子、湿度下差别很大。","<code>touchRead(4)</code> returns a raw value with no universal threshold — <b>log the idle value, measure the touched value, then pick a midpoint</b>. It varies by board and humidity."),
    ("这节课模拟手指靠近：读数从 62 掉到 18，越过阈值点亮 LED。触摸传感器还能<b>唤醒 Deep Sleep</b>，做低功耗触摸开关。","This lesson simulates a finger: the value falls from 62 to 18, crossing the threshold and lighting the LED. Touch pins can also <b>wake from Deep Sleep</b> for low-power switches."),
  ],
  points=[
    ("阈值要实测","别抄网上的 40 或 50。先串口打印空闲/触摸两组值，取中间数，再留一点滞回防抖。","Measure your threshold","Don't copy 40 or 50 from a tutorial. Log idle and touched values, pick a midpoint, add a little hysteresis."),
    ("T0~T9 引脚","ESP32 有 10 个触摸通道，GPIO4=T0、GPIO0=T1 等。具体映射看 datasheet，不是所有 GPIO 都支持。","T0–T9 pins","The ESP32 has 10 touch channels: GPIO4=T0, GPIO0=T1, etc. Check the datasheet — not every GPIO supports touch."),
    ("滞回比较","用两个阈值（进入 35、退出 45）避免在临界值附近反复跳变。","Hysteresis","Use two thresholds (enter 35, exit 45) to stop rapid toggling near the boundary."),
    ("触摸唤醒","<code>esp_sleep_enable_touchpad_wakeup()</code> 让 Deep Sleep 时被摸一下就醒，适合电池供电的触摸开关。","Touch wakeup","<code>esp_sleep_enable_touchpad_wakeup()</code> wakes Deep Sleep on a touch — ideal for battery-powered switches.")],
  code=r'''const int TOUCH_PIN = 4;    // GPIO4 = T0
const int THRESHOLD = 35;   // 按实测调整

void setup() {
  Serial.begin(115200);
  pinMode(2, OUTPUT);
  Serial.println("Touch sensor ready · T0/GPIO4");
}

void loop() {
  int val = touchRead(TOUCH_PIN);
  Serial.printf("touchRead(T0) = %d\n", val);
  digitalWrite(2, val < THRESHOLD ? HIGH : LOW);
  delay(200);
}''',
  tl=[
    dict(t=250, serial="触摸传感器就绪 · T0 = GPIO4", en="Touch sensor ready · T0 = GPIO4", part="pinsL", state="on"),
    dict(t=800, serial="touchRead(T0) = 62（空闲）", en="touchRead(T0) = 62 (idle)"),
    dict(t=1500, serial="手指靠近 → touchRead(T0) = 18", en="Finger near → touchRead(T0) = 18"),
    dict(t=1900, serial="18 < 阈值 35 → GPIO2 = HIGH，LED 亮", en="18 < threshold 35 → GPIO2 = HIGH, LED on", led="on"),
    dict(t=2600, serial="提示：阈值要按实测值调，别照抄", en="Tip: measure your own threshold — don't copy a magic number", led="off", part="pinsL", state="off"),
  ]
),
dict(
  no="25", title="millis()：告别阻塞式延时", titleEn="millis(): goodbye to blocking delays",
  meta="定时 · 非阻塞状态机", metaEn="Timing · non-blocking", group="系统与项目", groupEn="Systems & Projects",
  wiringHd="接线：还是板载 LED，重点在写法", wiringHdEn="Wiring: just the on-board LED — the point is the pattern",
  wiring="不用外接元件，继续用 <b>GPIO2 板载 LED</b>。这节课不改硬件，改的是<b>代码结构</b>：把 <code>delay()</code> 换成 <code>millis()</code> 时间差判断。",
  wiringEn="No external parts — keep using the <b>GPIO2 on-board LED</b>. This lesson changes no hardware, only <b>code structure</b>: replace <code>delay()</code> with <code>millis()</code> difference checks.",
  pins=[("GPIO2","板载 LED · 独立闪烁","On-board LED · blinks independently"),("（无）","重点是主循环不被阻塞","The point: the main loop never blocks")],
  overview=[
    ("<code>delay(1000)</code> 让整个 CPU 停 1 秒：这期间按键不响应、网络包不处理、传感器不读。<b>项目一复杂，阻塞就成了致命问题</b>。","<code>delay(1000)</code> freezes the whole CPU for a second: no button response, no network packets, no sensor reads. <b>Once a project grows, blocking becomes fatal</b>."),
    ("正确姿势是记录<b>上次执行时间</b>：<code>if (millis() - last &gt;= interval) { last = millis(); ... }</code>。不满足就立刻返回，CPU 继续干别的。","The right pattern stores the <b>last run time</b>: <code>if (millis() - last &gt;= interval) { last = millis(); ... }</code>. Otherwise fall through and let the CPU keep working."),
    ("这节课让 LED 每 200ms 翻转、串口每 1000ms 报时，两件事<b>互不干扰</b>。<code>millis()</code> 约 50 天溢出，用减法比较天然规避。","This lesson toggles the LED every 200ms and prints time every 1000ms, <b>independently</b>. <code>millis()</code> wraps in ~50 days; subtraction-based comparison handles it automatically.")],
  points=[
    ("millis() 返回类型","用 <code>unsigned long</code> 存时间戳。有符号类型在溢出后会出错。","millis() type","Store timestamps in <code>unsigned long</code>. Signed types break after the wrap-around."),
    ("减法而非相等","永远写 <code>now - last &gt;= period</code>，别写 <code>now == last + period</code>——一旦错过那一毫秒就永远不触发。","Subtract, don't compare equality","Always write <code>now - last &gt;= period</code>; <code>now == last + period</code> can be missed forever if a tick is skipped."),
    ("状态机","复杂任务拆成状态 + 超时：按键消抖、LED 呼吸、协议解析都靠这套。","State machines","Split complex jobs into states plus timeouts — debounce, breathing LEDs and protocol parsing all use this."),
    ("定时精度","millis() 分辨率 1ms，够用；微秒级用 micros()，但注意它会更快溢出。","Timer precision","millis() has 1ms resolution, usually enough; use micros() for finer timing, aware it wraps much sooner.")],
  code=r'''const int LED = 2;
unsigned long prevLed = 0, prevPrint = 0;
bool on = false;

void setup() {
  Serial.begin(115200);
  pinMode(LED, OUTPUT);
  Serial.println("Non-blocking timer started");
}

void loop() {
  unsigned long now = millis();

  if (now - prevLed >= 200) {     // 每 200ms 翻转 LED
    prevLed = now;
    on = !on;
    digitalWrite(LED, on);
  }

  if (now - prevPrint >= 1000) {  // 每 1000ms 报时
    prevPrint = now;
    Serial.printf("tick %lu s\n", now / 1000);
  }
  // 其他任务照样可以运行，不被 delay 卡住
}''',
  tl=[
    dict(t=250, serial="非阻塞定时器启动 · 无 delay()", en="Non-blocking timer started · no delay()", part="pinsL", state="on"),
    dict(t=700, serial="200ms 到 → LED 翻转（ON）", en="200ms elapsed → LED toggled ON", led="on"),
    dict(t=1200, serial="1000ms 到 → tick 1s（LED 独立运行）", en="1000ms elapsed → tick 1s (LED ran independently)", led="off"),
    dict(t=2200, serial="tick 2s · LED 已翻转 10 次", en="tick 2s · LED toggled 10 times"),
    dict(t=2900, serial="提示：millis()-last 用减法，天然处理溢出", en="Tip: millis()-last subtraction handles wrap-around", part="pinsL", state="off"),
  ]
),
dict(
  no="26", title="FreeRTOS：双核多任务入门", titleEn="FreeRTOS: getting started with dual-core tasks",
  meta="系统 · 多任务", metaEn="System · multitasking", group="系统与项目", groupEn="Systems & Projects",
  wiringHd="接线：不用接线，玩的是任务调度", wiringHdEn="Wiring: none — this is about task scheduling",
  wiring="不用外接元件。ESP32 有<b>两个 Xtensa 核</b>，Arduino 默认把 loop() 跑在 core 1。用 <code>xTaskCreatePinnedToCore</code> 可以把任务钉在指定核上，让 LED 和网络各跑各的。",
  wiringEn="No external parts. The ESP32 has <b>two Xtensa cores</b>; Arduino runs loop() on core 1 by default. <code>xTaskCreatePinnedToCore</code> pins a task to a chosen core so LED work and networking run independently.",
  pins=[("GPIO2","板载 LED · core 0 任务控制","On-board LED · controlled on core 0"),("（系统）","Serial 输出 · core 1 任务","Serial output · task on core 1")],
  overview=[
    ("当代码里出现「既要闪灯、又要收网络、还要读传感器」，单循环就力不从心。<b>RTOS 任务</b>像多个独立小程序，由调度器分配 CPU 时间。","When you need to blink, handle network traffic and read sensors at once, a single loop struggles. <b>RTOS tasks</b> are independent mini-programs scheduled by the kernel."),
    ("<code>xTaskCreatePinnedToCore(函数, 名字, 栈深, 参数, 优先级, 句柄, 核号)</code>。<b>栈给太小会崩溃</b>，一般从 2048 字节起；优先级相同则时间片轮转。","<code>xTaskCreatePinnedToCore(fn, name, stack, arg, prio, handle, core)</code>. <b>Too little stack crashes</b> — start at 2048 bytes; equal priorities round-robin."),
    ("这节课把闪灯钉在 <b>core 0</b>、串口报时钉在 <b>core 1</b>。任务里必须用 <code>vTaskDelay()</code> 让出 CPU，<b>绝不能死循环</b>。","This lesson pins blinking to <b>core 0</b> and reporting to <b>core 1</b>. Tasks must call <code>vTaskDelay()</code> to yield — <b>never spin forever</b>.")],
  points=[
    ("两个核","PRO_CPU(0) 常跑协议栈，APP_CPU(1) 跑应用。Arduino 的 setup/loop 默认在 core 1。","Two cores","PRO_CPU (0) usually handles the protocol stack, APP_CPU (1) runs apps. Arduino setup/loop defaults to core 1."),
    ("vTaskDelay","参数是 tick 数，<code>portTICK_PERIOD_MS</code> 通常是 1ms。它让出 CPU，<code>delay()</code> 在任务里会阻塞整个核。","vTaskDelay","Argument is ticks; <code>portTICK_PERIOD_MS</code> is usually 1ms. It yields — using delay() inside a task blocks its core."),
    ("共享资源加锁","两个任务同时写串口或改同一个变量，要用互斥锁 <code>SemaphoreHandle_t</code> 保护。","Lock shared resources","Two tasks writing Serial or the same variable need a <code>SemaphoreHandle_t</code> mutex."),
    ("栈溢出","用 <code>uxTaskGetStackHighWaterMark()</code> 查剩余栈。任务里开大数组最容易爆栈。","Stack overflow","Check remaining stack with <code>uxTaskGetStackHighWaterMark()</code> — large local arrays are the usual culprit.")],
  code=r'''#include <Arduino.h>

void taskBlink(void* param) {
  pinMode(2, OUTPUT);
  while (1) {
    digitalWrite(2, !digitalRead(2));
    vTaskDelay(250 / portTICK_PERIOD_MS);
  }
}

void taskReport(void* param) {
  while (1) {
    Serial.printf("report from core %d, t=%lu s\n",
                  xPortGetCoreID(), millis() / 1000);
    vTaskDelay(1000 / portTICK_PERIOD_MS);
  }
}

void setup() {
  Serial.begin(115200);
  xTaskCreatePinnedToCore(taskBlink,  "Blink",  2048, NULL, 1, NULL, 0);
  xTaskCreatePinnedToCore(taskReport, "Report", 2048, NULL, 1, NULL, 1);
}

void loop() { vTaskDelete(NULL); }''',
  tl=[
    dict(t=250, serial="创建任务 Blink(core 0) 与 Report(core 1)", en="Created tasks Blink(core 0) and Report(core 1)", part="module", state="on"),
    dict(t=800, serial="core 0: GPIO2 翻转 → LED 亮", en="core 0: GPIO2 toggled → LED on", led="on"),
    dict(t=1400, serial="core 1: report from core 1, t=1s", en="core 1: report from core 1, t=1s"),
    dict(t=2100, serial="两个任务并行运行，互不阻塞", en="Both tasks run in parallel without blocking"),
    dict(t=2800, serial="提示：任务里用 vTaskDelay() 让出 CPU", en="Tip: use vTaskDelay() to yield inside a task", led="off", part="module", state="off"),
  ]
),
dict(
  no="27", title="NVS：断电后记住数据", titleEn="NVS: remember data across power cycles",
  meta="存储 · Preferences", metaEn="Storage · Preferences", group="系统与项目", groupEn="Systems & Projects",
  wiringHd="接线：不用接线，数据存在 Flash", wiringHdEn="Wiring: none — data lives in Flash",
  wiring="不用外接元件。ESP32 内部 Flash 划了一块 <b>NVS（非易失性存储）</b>区，断电不丢。Arduino 用 <code>Preferences</code> 库读写，像操作一个简易键值对字典。",
  wiringEn="No external parts. Part of the ESP32's internal Flash is reserved for <b>NVS (non-volatile storage)</b> that survives power loss. Arduino accesses it through <code>Preferences</code> — a simple key-value store.",
  pins=[("（内部）","Flash NVS 分区","Internal Flash NVS partition"),("GPIO2","板载 LED · 启动时闪一下","On-board LED · blinks at boot")],
  overview=[
    ("变量在 RAM 里，掉电就没了。<b>NVS</b> 把数据写进 Flash，适合保存 Wi-Fi 凭据、校准值、开机次数这类小数据。","Variables in RAM vanish at power-off. <b>NVS</b> writes to Flash — ideal for small values like Wi-Fi credentials, calibration constants and boot counters."),
    ("<code>prefs.begin(\"cfg\", false)</code> 打开命名空间（false=可写），<code>putInt/getInt</code> 存取整数，还有 <code>putString</code>、<code>putFloat</code>、<code>putBool</code>。","<code>prefs.begin(\"cfg\", false)</code> opens a namespace (false = writable); <code>putInt/getInt</code> handle integers, with <code>putString</code>, <code>putFloat</code> and <code>putBool</code> for other types."),
    ("这节课开机次数加一并存回。<b>Flash 有擦写寿命（约十万次）</b>，别在 loop 里每秒写——要节流或只在状态变化时写。","This lesson increments and stores a boot counter. <b>Flash has finite write cycles (~100k)</b> — never write every second in loop(); throttle or write only on change.")],
  points=[
    ("命名空间","<code>begin(\"cfg\")</code> 里的名字隔离不同的键。不同项目用不同命名空间，避免互相覆盖。","Namespace","The name in <code>begin(\"cfg\")</code> isolates keys. Use distinct namespaces so projects don't overwrite each other."),
    ("get 的默认值","<code>getInt(\"boot\", 0)</code> 第二个参数是键不存在时的默认值，第一次启动靠它初始化。","get default","The second argument of <code>getInt(\"boot\", 0)</code> is returned when the key is absent — that's how first boot initializes."),
    ("写入寿命","NVS 有磨损均衡，但仍不适合高频写。日志要存到文件系统的环形缓冲，或攒批再写。","Write endurance","NVS uses wear leveling but still dislikes frequent writes. Log to a ring buffer in a filesystem or batch writes."),
    ("end() 收尾","操作完调 <code>prefs.end()</code> 释放句柄。多个任务同时访问要加锁。","end() cleanup","Call <code>prefs.end()</code> to release the handle when done; lock access if multiple tasks use it.")],
  code=r'''#include <Preferences.h>
Preferences prefs;

void setup() {
  Serial.begin(115200);
  pinMode(2, OUTPUT);
  digitalWrite(2, HIGH);        // 开机闪一下

  prefs.begin("cfg", false);    // 命名空间 cfg，可写
  int n = prefs.getInt("boot", 0) + 1;
  prefs.putInt("boot", n);      // 断电后仍在
  prefs.putString("name", "esp32-lab");
  Serial.printf("boot count = %d\n", n);
  prefs.end();
}

void loop() {}''',
  tl=[
    dict(t=250, serial="开机 · 从 NVS 读取 boot=2", en="Boot · read boot=2 from NVS", part="module", state="on"),
    dict(t=800, serial="加一 → boot=3，写入 Flash", en="Increment → boot=3, written to Flash"),
    dict(t=1400, serial="同时保存 name=esp32-lab", en="Also saved name=esp32-lab"),
    dict(t=2000, serial="断电 · Flash 内容保留", en="Power off · Flash contents preserved", part="module", state="off"),
    dict(t=2700, serial="再上电 → boot=3（不再从 0 开始）", en="Power on again → boot=3 (not back to zero)", part="module", state="on"),
    dict(t=3300, serial="提示：Flash 有寿命，别在 loop 高频写", en="Tip: Flash wears out — don't write at high frequency", part="module", state="off"),
  ]
),
dict(
  no="28", title="OTA：不用数据线升级固件", titleEn="OTA: update firmware without a cable",
  meta="系统 · 无线升级", metaEn="System · wireless update", group="系统与项目", groupEn="Systems & Projects",
  wiringHd="接线：不用接线，但要同一局域网", wiringHdEn="Wiring: none — but be on the same LAN",
  wiring="不用外接元件。板子连上 Wi-Fi 后运行 <code>ArduinoOTA</code>，在 IDE 里选<b>网络端口</b>就能像插线一样烧录。虚拟板子的<b>模组</b>在传输固件时高亮。",
  wiringEn="No external parts. Once on Wi-Fi, <code>ArduinoOTA</code> exposes a network port in the IDE, letting you flash as if cabled. The virtual <b>module</b> lights up while firmware transfers.",
  pins=[("（内置）","Wi-Fi · OTA 端口 3232","Wi-Fi · OTA port 3232"),("GPIO2","板载 LED · 可显示升级状态","On-board LED · can show update state")],
  overview=[
    ("设备装到天花板上、部署在野外后，<b>拔线烧录不现实</b>。OTA（Over-The-Air）通过网络传新固件，是量产维护的必备能力。","Once a device is on a ceiling or in the field, <b>plugging in a cable isn't practical</b>. OTA (Over-The-Air) delivers new firmware over the network — essential for maintenance."),
    ("Arduino 里用 <code>ArduinoOTA.begin()</code> + loop 里反复 <code>handle()</code>。编译后 IDE 的端口列表会出现 <code>esp32-lab at 192.168.1.42</code>。","With <code>ArduinoOTA.begin()</code> plus a repeated <code>handle()</code> in loop, the IDE port list shows <code>esp32-lab at 192.168.1.42</code>."),
    ("这节课模拟一次升级：连接 → 传输 → 校验 → 重启。<b>升级中别断电，也别让看门狗超时</b>，否则可能变砖。","This lesson simulates an update: connect → transfer → verify → reboot. <b>Don't cut power mid-update, and don't let the watchdog trip</b> — that can brick the device.")],
  points=[
    ("密码保护","<code>ArduinoOTA.setPassword(\"xxx\")</code> 必须设，否则同网段任何人都能给你刷固件。","Password protection","Always call <code>ArduinoOTA.setPassword(\"xxx\")</code> — otherwise anyone on the LAN can flash your device."),
    ("回滚方案","分区表里带两个 app 槽，升级失败可回退旧版本。Arduino 默认支持 OTA 分区方案。","Rollback","The partition table has two app slots so a failed update can fall back. Arduino's default partition schemes support OTA."),
    ("开启看门狗","升级耗时长，先喂好狗或临时关掉看门狗，避免升级到一半被复位。","Watchdog during OTA","Updates take time — feed or temporarily disable the watchdog so it doesn't reset you mid-flash."),
    ("生产部署","真正的产品用 HTTPS 拉取固件、签名校验、断点续传，而不是 IDE 直连。","Production practice","Real products pull signed firmware over HTTPS with resume support, not IDE direct flash.")],
  code=r'''#include <WiFi.h>
#include <ArduinoOTA.h>

const char* ssid = "Home-2.4G";
const char* pass = "12345678";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) delay(500);

  ArduinoOTA.setHostname("esp32-lab");
  ArduinoOTA.setPassword("ota-pass");
  ArduinoOTA.onStart([]()  { Serial.println("OTA start"); });
  ArduinoOTA.onEnd([]()    { Serial.println("OTA done, rebooting"); });
  ArduinoOTA.onError([](ota_error_t e) {
    Serial.printf("OTA error %d\n", e);
  });
  ArduinoOTA.begin();
  Serial.printf("OTA ready at %s\n", WiFi.localIP().toString().c_str());
}

void loop() { ArduinoOTA.handle(); }''',
  tl=[
    dict(t=250, serial="OTA 服务就绪 · esp32-lab @192.168.1.42", en="OTA ready · esp32-lab @192.168.1.42", part="module", state="on"),
    dict(t=800, serial="IDE 连接 · 开始传输固件", en="IDE connected · firmware transfer started"),
    dict(t=1500, serial="写入 Flash 另一分区 · 42%", en="Writing to alternate Flash partition · 42%"),
    dict(t=2200, serial="校验 SHA256 通过 · OTA done", en="SHA256 verified · OTA done"),
    dict(t=2800, serial="重启 → 运行新固件", en="Reboot → new firmware running", part="module", state="off"),
    dict(t=3300, serial="提示：升级中别断电，务必设密码", en="Tip: don't power off mid-update — always set a password"),
  ]
),
dict(
  no="29", title="看门狗：死机时自动重启", titleEn="Watchdog: automatic recovery from hangs",
  meta="系统 · 可靠性", metaEn="System · reliability", group="系统与项目", groupEn="Systems & Projects",
  wiringHd="接线：不用接线，是软件保护机制", wiringHdEn="Wiring: none — it's a software safety net",
  wiring="不用外接元件。看门狗（Watchdog）是一个<b>独立硬件定时器</b>：程序必须定期「喂狗」，超时没喂就判定死机并自动复位。 部署后的设备没人值守，这是最后一道保险。",
  wiringEn="No external parts. The watchdog is an <b>independent hardware timer</b>: firmware must regularly \"feed\" it, or the chip assumes it hung and resets. Unattended deployments need this safety net.",
  pins=[("（系统）","任务看门狗 TWDT","Task watchdog TWDT"),("（系统）","复位后从 setup 重跑","After reset, setup runs again")],
  overview=[
    ("程序卡在某个死循环、等待永远不来的信号，人又不在旁边按复位——这时<b>看门狗</b>能自动把芯片拉回来。","When code hangs in a loop or waits for a signal that never comes and nobody is nearby to press reset, a <b>watchdog</b> brings the chip back."),
    ("ESP32 有<b>任务看门狗（TWDT）</b>和中断看门狗。注册当前任务后，必须周期性调用 <code>esp_task_wdt_reset()</code>；超过阈值就触发 panic 或复位。","The ESP32 has a <b>task watchdog (TWDT)</b> and an interrupt watchdog. After registering the current task, call <code>esp_task_wdt_reset()</code> periodically; exceeding the timeout triggers a panic or reset."),
    ("这节课演示 5 秒超时：正常运行时每 1 秒喂狗；如果某次循环卡死超过 5 秒，芯片自动重启。<b>喂狗不能掩盖真正的 bug</b>，要配合日志定位。","This lesson uses a 5s timeout: feed every second while healthy; if a loop stalls beyond 5s the chip resets. <b>Feeding the dog doesn't fix the bug</b> — use logs to find the real cause.")],
  points=[
    ("IDF 5.x API 变化","新版用 <code>esp_task_wdt_config_t</code> 配置结构体初始化，旧版 <code>esp_task_wdt_init(秒, bool)</code> 已弃用。","IDF 5.x API change","Newer IDF uses <code>esp_task_wdt_config_t</code> for init; the old <code>esp_task_wdt_init(seconds, bool)</code> is deprecated."),
    ("trigger_panic","设为 true 时超时直接 panic 重启；false 只打印警告。生产环境通常设 true。","trigger_panic","true panics and reboots on timeout; false only logs a warning. Production usually wants true."),
    ("别乱喂狗","在卡死的代码路径里也喂狗，等于关掉了保护。只在确认系统健康时喂。","Don't feed blindly","Feeding from the hung path defeats the purpose — feed only when you know the system is healthy."),
    ("硬件看门狗","ESP32 还有 RTC 看门狗，能唤醒 Deep Sleep 后的死锁。极端场景配合软件看门狗一起用。","Hardware watchdog","The ESP32 also has an RTC watchdog to recover from Deep Sleep deadlocks — combine both for critical systems.")],
  code=r'''#include <esp_task_wdt.h>

void setup() {
  Serial.begin(115200);

  esp_task_wdt_config_t cfg = {
    .timeout_ms = 5000,
    .idle_core_mask = (1 << portNUM_PROCESSORS) - 1,
    .trigger_panic = true
  };
  esp_task_wdt_init(&cfg);
  esp_task_wdt_add(NULL);        // 注册当前任务
  Serial.println("Watchdog armed · 5s");
}

void loop() {
  esp_task_wdt_reset();          // 喂狗
  Serial.println("feeding watchdog");
  delay(1000);
  // 若此处卡住 > 5s，芯片自动复位
}''',
  tl=[
    dict(t=250, serial="任务看门狗启动 · 超时 5s", en="Task watchdog armed · 5s timeout", part="module", state="on"),
    dict(t=800, serial="喂狗 → 系统健康", en="Fed the watchdog → healthy"),
    dict(t=1700, serial="喂狗 → 系统健康", en="Fed the watchdog → healthy"),
    dict(t=2600, serial="模拟故障：循环卡死，停止喂狗", en="Simulated fault: loop hangs, no more feeds"),
    dict(t=3300, serial="5s 超时 → trigger_panic → 自动复位", en="5s timeout → trigger_panic → auto reset", part="module", state="off"),
    dict(t=3900, serial="重启后从 setup 重新执行", en="After reset, setup runs again", part="module", state="on"),
    dict(t=4400, serial="提示：喂狗不能掩盖 bug，要查日志", en="Tip: feeding the dog hides bugs — check the logs", part="module", state="off"),
  ]
),
dict(
  no="30", title="综合项目：Wi-Fi 环境监测站", titleEn="Capstone: Wi-Fi environment station",
  meta="综合 · 全技能串联", metaEn="Capstone · all skills combined", group="系统与项目", groupEn="Systems & Projects",
  wiringHd="接线：把前面几课的传感器都装上", wiringHdEn="Wiring: add the sensors from earlier lessons",
  wiring="<b>BME280：3V3/GND/SDA=GPIO21/SCL=GPIO22</b>，板载 LED 作状态灯。项目用到第 6/7/13/14/25 课的技能：Wi-Fi、I²C、HTTP、Web 服务和非阻塞定时。",
  wiringEn="<b>BME280: 3V3/GND/SDA=GPIO21/SCL=GPIO22</b>, on-board LED as status. This project combines lessons 6/7/13/14/25: Wi-Fi, I²C, HTTP, web server and non-blocking timing.",
  pins=[("3V3","→ BME280 VCC","→ BME280 VCC"),("GPIO21","→ BME280 SDA","→ BME280 SDA"),("GPIO22","→ BME280 SCL","→ BME280 SCL"),("GPIO2","板载 LED · 运行状态","On-board LED · running status")],
  overview=[
    ("把 29 课学到的东西拼成一个真能用的项目：<b>采集温湿度 → 本地网页展示 → 上报服务器 → 低功耗睡眠</b>。这才是学习单片机的终点。","Combine 29 lessons into a genuinely useful project: <b>sample temperature/humidity → serve a local page → upload to a server → sleep to save power</b>. That's the point of learning a microcontroller."),
    ("结构上用<b>非阻塞定时</b>驱动采样，用 <b>WebServer</b> 提供 <code>/</code> 和 <code>/api</code>，用 <b>HTTPClient</b> 每 30 秒上报一次。各模块互不阻塞。","Structurally, <b>non-blocking timers</b> drive sampling, <b>WebServer</b> serves <code>/</code> and <code>/api</code>, and <b>HTTPClient</b> uploads every 30 seconds. Modules don't block each other."),
    ("最后加 <b>Deep Sleep</b>：每 5 分钟醒一次采样上报，再睡回去，电池能撑数周。这节课是一次完整闭环演练——<b>你已可以自己开新项目了</b>。","Finally add <b>Deep Sleep</b>: wake every 5 minutes, sample, upload, sleep again — weeks on a battery. This is a full end-to-end exercise — <b>you're ready to start your own project</b>.")],
  points=[
    ("模块解耦","采样、显示、上报分成独立函数，用状态标志通信。别把所有逻辑堆在 loop 里。","Decouple modules","Split sampling, display and upload into separate functions communicating via flags. Don't pile everything into loop()."),
    ("采样节流","BME280 每 2 秒读一次足够；HTTP 上报每 30 秒一次。频繁读传感器既耗电也无意义。","Throttle sampling","Reading the BME280 every 2s is plenty; upload every 30s. Polling faster wastes power without information."),
    ("失败重试","Wi-Fi 断、HTTP 超时、I²C 没回应都是常态。每步都要有超时和退避重试，别让一次失败拖垮系统。","Retry on failure","Wi-Fi drops, HTTP timeouts and missing I²C devices are normal. Add timeouts and backoff to every step."),
    ("低功耗闭环","深度睡眠前关掉 Wi-Fi 和外设电源，用定时器唤醒；唤醒原因区分上电与睡醒。","Low-power loop","Before sleeping, shut down Wi-Fi and peripherals; wake on a timer and distinguish boot from wakeup cause.")],
  code=r'''#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>

WebServer server(80);
const char* ssid = "Home-2.4G";
const char* pass = "12345678";
bool fresh = false;
float tempC = 0, humid = 0;

void setup() {
  Serial.begin(115200);
  pinMode(2, OUTPUT);
  Wire.begin(21, 22);                 // BME280 (0x76)
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) delay(500);

  server.on("/", []() {
    server.send(200, "text/plain", "ESP32 environment station");
  });
  server.on("/api", []() {
    server.send(200, "text/plain",
      "temp=" + String(tempC) + "&hum=" + String(humid));
  });
  server.begin();
  Serial.printf("Station up at %s\n", WiFi.localIP().toString().c_str());
}

void loop() {
  server.handleClient();              // 非阻塞处理网页请求
  static unsigned long last = 0;
  if (millis() - last > 5000) {
    last = millis();
    tempC = 26.4; humid = 58.0;      // 从 BME280 读取
    fresh = true;
    digitalWrite(2, !digitalRead(2)); // 状态灯
    Serial.printf("sample: %.1fC %.0f%%RH -> uploaded\n", tempC, humid);
  }
  // 每 5 分钟可进入 Deep Sleep，此处略
}''',
  tl=[
    dict(t=250, serial="环境监测站启动 · 连接 Wi-Fi", en="Environment station starting · connecting Wi-Fi", part="module", state="on"),
    dict(t=900, serial="Station up at http://192.168.1.42", en="Station up at http://192.168.1.42"),
    dict(t=1500, serial="I²C 读 BME280(0x76) · 26.4°C / 58%RH", en="I²C read BME280(0x76) · 26.4°C / 58%RH", part="pinsR", state="on"),
    dict(t=2200, serial="GET /api → temp=26.4&hum=58.0", en="GET /api → temp=26.4&hum=58.0"),
    dict(t=2900, serial="HTTP 上报成功 · 状态灯翻转", en="HTTP upload OK · status LED toggled", led="on"),
    dict(t=3600, serial="采样完成 → 准备 Deep Sleep 5 分钟", en="Sample done → preparing 5-minute Deep Sleep", led="off", part="pinsR", state="off"),
    dict(t=4200, serial="恭喜完成 30 课！你现在可以独立开新项目了", en="Congratulations on finishing 30 lessons! You're ready to build on your own", part="module", state="off"),
  ]
),
]
