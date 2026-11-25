# -*- coding: utf-8 -*-
"""第 31-46 课：RFID/NFC（31-38）与声音（39-46）。

字段与 lessons_m4_data.py 完全一致：
  no/title/titleEn/meta/metaEn/group/groupEn
  wiringHd/wiringHdEn/wiring/wiringEn
  pins [[pin, zh, en], ...]
  overview [[zh, en], ...]
  points [[kzh, vzh, ken, ven], ...]
  code 原始 Arduino 源码（生成器负责高亮）
  tl [{t, serial, en, part?, state?}, ...]
"""

RFID = "RFID 与 NFC"
RFID_EN = "RFID & NFC"
SND = "声音与音频"
SND_EN = "Sound & audio"

COURSES = [
dict(
  no="31", title="RFID 入门：13.56 MHz 与 MFRC522",
  titleEn="RFID basics: 13.56 MHz and the MFRC522",
  meta="RFID · SPI 六线", metaEn="RFID · six-wire SPI",
  group=RFID, groupEn=RFID_EN,
  wiringHd="接线：MFRC522 六根线，只能 3.3V",
  wiringHdEn="Wiring: six wires to the MFRC522, 3.3V only",
  wiring="<b>3V3→3.3V、GND→GND、SDA(SS)→GPIO5、SCK→GPIO18、MOSI→GPIO23、MISO→GPIO19、RST→GPIO22</b>。模块丝印上的 <b>SDA 就是 SPI 的片选 SS</b>，不是 I²C 的 SDA。供电一定接 3.3V——读卡芯片和卡片都靠它。",
  wiringEn="<b>3V3→3.3V, GND→GND, SDA(SS)→GPIO5, SCK→GPIO18, MOSI→GPIO23, MISO→GPIO19, RST→GPIO22</b>. The silkscreen <b>SDA is the SPI chip-select SS</b>, not I2C SDA. Power it from 3.3V only — both the reader chip and the card depend on it.",
  pins=[["3V3","供电 · 只能 3.3V","3.3V supply only"],
        ["GPIO5","SDA/SS · 片选","SDA/SS · chip select"],
        ["GPIO18","SCK · SPI 时钟","SCK · SPI clock"],
        ["GPIO23","MOSI · 主板发命令","MOSI · commands out"],
        ["GPIO19","MISO · 卡片回数据","MISO · card data in"],
        ["GPIO22","RST · 硬复位","RST · hard reset"]],
  overview=[
    ["<b>RFID 不是「扫描」，是磁场耦合。</b>读卡器天线产生 13.56 MHz 的交变磁场，卡片里的线圈从这个场里<b>感应取电</b>——所以卡片没有电池也能工作。",
     "RFID is not optical scanning — it is magnetic coupling. The reader antenna radiates a 13.56 MHz alternating field, and the coil inside the card harvests power from it, which is why the card needs no battery."],
    ["卡片回话靠<b>负载调制</b>：它按数据快速改变自己线圈的负载，读卡器端就能测到载波幅度的微小抖动，从而解出 0 和 1。整条链路只有读卡器一端在主动供电。",
     "The card answers by load modulation: it toggles the load on its own coil, and the reader sees tiny amplitude changes in the carrier and decodes them as bits. Only the reader actively supplies power."],
    ["<b>MFRC522</b> 是常见的 13.56 MHz 读卡芯片，支持 ISO14443A（MIFARE Classic、Ultralight、NTAG 系列）。本课目标：让串口打印出一张卡片的 <b>UID</b>，先确认硬件通了。",
     "The <b>MFRC522</b> is a common 13.56 MHz reader chip supporting ISO14443A (MIFARE Classic, Ultralight, NTAG). Goal of this lesson: print a card's <b>UID</b> on the serial port to prove the hardware works."]],
  points=[
    ["只能 3.3V","模块上标 5V 也不要用 5V。逻辑电平 3.3V，5V 供电容易烧芯片或让读卡距离骤降。",
     "3.3V only","Do not use 5V even if the module claims tolerance. Logic is 3.3V; 5V can kill the chip or shrink read range."],
    ["天线别贴金属","线圈正下方和周围 1 cm 内不要有金属、导线、电池，否则磁场被短路，读不到卡。",
     "Keep metal away","No metal, wires or batteries within ~1 cm of the coil, or the field is shorted and nothing reads."],
    ["先读版本寄存器","<code>VersionReg</code> 正常返回 <b>0x91/0x92</b>；读回 0x00 或 0xFF 说明 SPI 线序、片选或供电有问题。",
     "Read the version register","<code>VersionReg</code> returns <b>0x91/0x92</b> when healthy; 0x00 or 0xFF means wrong SPI wiring, chip select, or power."],
    ["读完要 HaltA","同一张卡不 <code>PICC_HaltA()</code> 就会一直被当成「新卡」，串口刷屏。",
     "Halt after reading","Without <code>PICC_HaltA()</code> the same card keeps being reported as new and floods the log."]],
  code=r'''// 第 31 课：读一张卡片的 UID
#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN   5
#define RST_PIN  22

MFRC522 rfid(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(115200);
  SPI.begin(18, 19, 23, SS_PIN);      // SCK, MISO, MOSI, SS
  rfid.PCD_Init();
  delay(50);

  byte v = rfid.PCD_ReadRegister(MFRC522::VersionReg);
  Serial.print("MFRC522 version: 0x");
  Serial.println(v, HEX);             // 0x91 / 0x92 正常
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent()) return;
  if (!rfid.PICC_ReadCardSerial())   return;

  Serial.print("UID:");
  for (byte i = 0; i < rfid.uid.size; i++) {
    Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
    Serial.print(rfid.uid.uidByte[i], HEX);
  }
  Serial.println();

  rfid.PICC_HaltA();                  // 让这张卡先退场
  delay(300);
}
''',
  tl=[
    dict(t=300,  serial="上电自检 · 3.3V 供电正常", en="Power-on check · 3.3V rail OK", part="pwrled", state="on"),
    dict(t=800,  serial="SPI 初始化：SCK=18 MISO=19 MOSI=23 SS=5", en="SPI init: SCK=18 MISO=19 MOSI=23 SS=5", part="pinsR", state="on"),
    dict(t=1300, serial="MFRC522 版本 0x92 · 读卡芯片在线", en="MFRC522 version 0x92 · reader online"),
    dict(t=1900, serial="天线场开启 · 13.56 MHz 载波", en="Field on · 13.56 MHz carrier", part="pinsR", state="on"),
    dict(t=2450, serial="发现卡片 · ATQA=0x0004 SAK=0x08", en="Card present · ATQA=0x0004 SAK=0x08"),
    dict(t=2900, serial="UID: 4A 2F 91 7C", en="UID: 4A 2F 91 7C"),
    dict(t=3300, serial="PICC_HaltA · 卡片休眠，等下一张", en="PICC_HaltA · card halted, waiting", part="pinsR", state="off"),
  ]),

dict(
  no="32", title="读卡：卡片没有电池，怎么回话",
  titleEn="Reading a card: how a batteryless tag answers",
  meta="RFID · 感应取电与负载调制", metaEn="RFID · harvesting and load modulation",
  group=RFID, groupEn=RFID_EN,
  wiringHd="接线：沿用第 31 课的六根线", wiringHdEn="Wiring: same six wires as lesson 31",
  wiring="和上一课完全一样：<b>3V3、GND、SDA(SS)=5、SCK=18、MOSI=23、MISO=19、RST=22</b>。这一课不换线，只把「卡片怎么答话」拆开看，顺便把卡型认出来。",
  wiringEn="Identical to the previous lesson: <b>3V3, GND, SDA(SS)=5, SCK=18, MOSI=23, MISO=19, RST=22</b>. No rewiring — we only open up how the card replies and identify the card type.",
  pins=[["3V3","给读卡器和场供电","Powers reader and field"],
        ["GPIO5","SS · 选择读卡芯片","SS · selects the reader"],
        ["GPIO19","MISO · 接收卡片位流","MISO · incoming bit stream"],
        ["GPIO22","RST · 重启读卡芯片","RST · restart the reader"]],
  overview=[
    ["读卡器一直在发 <b>REQA</b>（请求）或 <b>WUPA</b>（唤醒）短帧。卡片进场后先靠磁场给自己充电，充到工作电压才开始应答 <b>ATQA</b>——这就是「刷卡要贴一下」的物理原因。",
     "The reader keeps sending short <b>REQA</b> (request) or <b>WUPA</b> (wake-up) frames. A card charges up from the field, and only when it reaches operating voltage does it answer with <b>ATQA</b> — that is why you must hold the card close for a moment."],
    ["应答数据不是「发射」，而是<b>改变自己线圈的负载</b>。读卡器测载波幅度的微小起伏，就能还原出曼彻斯特编码的位流。所以卡片越远，信号越弱，误码越多。",
     "The card does not transmit; it <b>changes the load on its coil</b>. The reader detects tiny carrier amplitude dips and recovers the Manchester-coded bit stream. The farther the card, the weaker the signal and the more errors."],
    ["每张卡出厂有一个 <b>UID</b>：常见 4 字节（MIFARE Classic 1K 多为 4 字节），也有 7 字节与 10 字节的（NTAG、DESFire）。<code>uid.size</code> 直接告诉你长度。",
     "Every card ships with a <b>UID</b>: usually 4 bytes for MIFARE Classic 1K, but 7 or 10 bytes for NTAG and DESFire. <code>uid.size</code> tells you the length."]],
  points=[
    ["先看 ATQA 再看 SAK","ATQA 说明卡支持哪种防冲突，SAK 说明卡型。<code>PICC_GetType()</code> 把两者映射成可读字符串，比猜 UID 长度可靠。",
     "ATQA first, then SAK","ATQA describes the anti-collision scheme, SAK the card family. <code>PICC_GetType()</code> maps both to a readable name."],
    ["UID 不是密钥","UID 谁都能读，也常被克隆卡改写。<b>只靠 UID 做门禁等于没有门禁</b>，后面第 35 课会讲真正的密钥认证。",
     "UID is not a secret","Anyone can read a UID and clone cards can fake it. <b>UID-only access control is no access control</b>; lesson 35 covers real key authentication."],
    ["7 字节 UID 有级联","长 UID 分多级读出（CTU 级联标记）。自己拼 UID 时别假设固定 4 字节，按 <code>uid.size</code> 循环。",
     "7-byte UIDs cascade","Long UIDs are read in cascade levels. Never assume 4 bytes — loop over <code>uid.size</code>."],
    ["距离与角度都影响","读卡距离取决于天线尺寸、卡片朝向和供电。平行贴近最稳，斜着放会明显变短。",
     "Range depends on angle","Range depends on antenna size, card orientation and supply. Face-to-face parallel is best; tilting it drops range fast."]],
  code=r'''// 第 32 课：读 UID + 认出卡型
#include <SPI.h>
#include <MFRC522.h>

MFRC522 rfid(5, 22);

void setup() {
  Serial.begin(115200);
  SPI.begin(18, 19, 23, 5);
  rfid.PCD_Init();
  Serial.println("Hold a card near the antenna...");
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent()) return;
  if (!rfid.PICC_ReadCardSerial())   return;

  MFRC522::PICC_Type type = rfid.PICC_GetType(rfid.uid.sak);
  Serial.print("Type: ");
  Serial.println(rfid.PICC_GetTypeName(type));

  Serial.print("UID (");
  Serial.print(rfid.uid.size);
  Serial.print(" bytes): ");
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) Serial.print("0");
    Serial.print(rfid.uid.uidByte[i], HEX);
    if (i + 1 < rfid.uid.size) Serial.print(":");
  }
  Serial.println();

  rfid.PICC_HaltA();
  delay(500);
}
''',
  tl=[
    dict(t=300,  serial="读卡器发 REQA · 等待场内有卡", en="Reader sends REQA · waiting for a card", part="pinsR", state="on"),
    dict(t=900,  serial="卡片感应取电 · 电压爬升到 2.5V", en="Card harvesting · rail rising to 2.5V", part="pwrled", state="on"),
    dict(t=1500, serial="ATQA=0x0004 · 1 KB 卡，支持防冲突", en="ATQA=0x0004 · 1 KB card with anti-collision"),
    dict(t=2000, serial="SAK=0x08 · MIFARE Classic 1K", en="SAK=0x08 · MIFARE Classic 1K"),
    dict(t=2450, serial="UID (4 bytes): 4A:2F:91:7C", en="UID (4 bytes): 4A:2F:91:7C"),
    dict(t=2900, serial="负载调制解码完成 · 误码 0", en="Load modulation decoded · 0 bit errors"),
    dict(t=3300, serial="卡片休眠 · 场仍在，可读下一张", en="Card halted · field stays on for the next tag"),
  ]),

dict(
  no="33", title="防冲突：多张卡同时在场上",
  titleEn="Anti-collision: several cards in the field",
  meta="RFID · 逐位仲裁", metaEn="RFID · bit-wise arbitration",
  group=RFID, groupEn=RFID_EN,
  wiringHd="接线：不变，多拿几张卡过来", wiringHdEn="Wiring: unchanged, just bring several cards",
  wiring="线路和上一课一致。区别在「场里有几张卡」：把 2–3 张卡叠在一起放到天线上，观察读卡器怎么做到<b>一次只认一张</b>。",
  wiringEn="Same wiring as before. The variable is how many cards share the field: stack two or three on the antenna and watch the reader pick <b>one at a time</b>.",
  pins=[["3V3","场功率决定能带几张卡","Field power limits card count"],
        ["GPIO5","SS · 片选","SS · chip select"],
        ["GPIO19","MISO · 冲突位也在这","MISO · collisions show here"],
        ["GPIO18","SCK · 时钟","SCK · clock"]],
  overview=[
    ["多张卡同时应答会撞在一起，这叫<b>冲突</b>。ISO14443A 用<b>逐位仲裁</b>解决：读卡器广播一个 UID 前缀，卡片只在「自己的 UID 以这个前缀开头」时才继续应答，逐位收窄，最终只剩一张。",
     "When several cards answer at once the bits collide. ISO14443A solves it with <b>bit-wise arbitration</b>: the reader broadcasts a UID prefix, cards keep answering only if their UID starts with it, narrowing one bit at a time until exactly one remains."],
    ["被选中的那张完成读取后会收到 <b>HALT</b>，退出本轮；剩下的卡继续参与下一轮。所以「一次读一张、循环读全部」是标准做法，而不是去并行读。",
     "The selected card gets <b>HALT</b> and leaves the round; the rest stay. So the standard pattern is read-one-then-halt in a loop, not parallel reads."],
    ["冲突不只发生在 UID 上：卡片数量多、距离近、场功率不足时，误码率会上升，表现为<b>读不到、读一半、串口刷同一张卡</b>。这三类现象要分开排查。",
     "Collisions are not only in the UID: many cards, short range or weak field raise the bit error rate, showing up as missed reads, half reads, or the same card repeating. Debug these three separately."]],
  points=[
    ["循环里别死等","<code>PICC_IsNewCardPresent()</code> 返回 false 就立刻返回，让 <code>loop()</code> 继续跑；在里面 <code>delay</code> 长等会拖慢整轮扫描。",
     "Never block the loop","Return immediately when <code>PICC_IsNewCardPresent()</code> is false so <code>loop()</code> keeps spinning; long delays inside stall the whole scan."],
    ["每读一张就 HaltA","不休眠会导致同一张卡反复被读到，多卡场景下永远轮不到第二张。",
     "Halt after each read","Without HALT the same card repeats forever and the second card never gets a turn."],
    ["用计数去重","工程上按 UID 做一张「最近读过」的短表（比如 8 条），避免同卡在 1 秒内被打印十几次。",
     "De-duplicate by UID","Keep a small recent-UID table (say 8 entries) so one card is not printed ten times per second."],
    ["场功率有上限","读卡器天线由 3.3V 供电，同时带太多卡会互相抢电，表现为「越读越慢」。真实门禁一般一次只让一张卡靠近。",
     "Field power is finite","The antenna runs off 3.3V; too many cards draw power from the same field and reads slow down. Real readers assume one card at a time."]],
  code=r'''// 第 33 课：一轮一张，循环读完整场
#include <SPI.h>
#include <MFRC522.h>

MFRC522 rfid(5, 22);

byte last[8][4];          // 最近读过的 8 张卡
byte lastCount = 0;

bool seenBefore(byte *uid) {
  for (byte i = 0; i < lastCount; i++)
    if (memcmp(last[i], uid, 4) == 0) return true;
  return false;
}

void remember(byte *uid) {
  byte slot = lastCount < 8 ? lastCount++ : 7;
  memcpy(last[slot], uid, 4);
}

void setup() {
  Serial.begin(115200);
  SPI.begin(18, 19, 23, 5);
  rfid.PCD_Init();
  Serial.println("Scanning field...");
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent()) return;   // 立刻返回，不阻塞
  if (!rfid.PICC_ReadCardSerial())   return;

  if (!seenBefore(rfid.uid.uidByte)) {
    remember(rfid.uid.uidByte);
    Serial.print("card ");
    for (byte i = 0; i < 4; i++) {
      if (rfid.uid.uidByte[i] < 0x10) Serial.print("0");
      Serial.print(rfid.uid.uidByte[i], HEX);
    }
    Serial.println(" picked");
  }

  rfid.PICC_HaltA();      // 这张退场，下一轮读别的
  delay(120);
}
''',
  tl=[
    dict(t=300,  serial="场内有 3 张卡 · 同时应答产生冲突", en="3 cards in the field · simultaneous answers collide", part="pinsR", state="on"),
    dict(t=900,  serial="逐位仲裁 · 前缀 0x4A 收窄", en="Bit-wise arbitration · prefix narrowed to 0x4A"),
    dict(t=1400, serial="选中 1 张 · 其余等待下一轮", en="One card selected · others wait for the next round"),
    dict(t=1900, serial="card 4A2F917C picked", en="card 4A2F917C picked"),
    dict(t=2350, serial="HALT 该卡 · 回到场中扫描", en="Card halted · rescanning the field"),
    dict(t=2800, serial="card 8B01D3E5 picked", en="card 8B01D3E5 picked"),
    dict(t=3250, serial="card 1C77A0B2 picked", en="card 1C77A0B2 picked"),
    dict(t=3700, serial="3 张全部读完 · 无重复输出", en="All 3 cards read · no duplicates"),
  ]),

dict(
  no="34", title="卡片内部：MIFARE Classic 1K 的 16 个扇区",
  titleEn="Inside the card: 16 sectors of MIFARE Classic 1K",
  meta="RFID · 存储器结构与认证", metaEn="RFID · memory layout and auth",
  group=RFID, groupEn=RFID_EN,
  wiringHd="接线：不变，卡要一直放着", wiringHdEn="Wiring: unchanged, keep the card on the antenna",
  wiring="接线不变。这一课开始<b>读卡片存储区</b>：卡必须一直贴着天线，因为每次认证和读块都要重新走一遍寻卡流程。",
  wiringEn="Same wiring. Now we <b>read card memory</b>: keep the card on the antenna, because every authenticate-and-read cycle repeats the discovery handshake.",
  pins=[["3V3","认证过程电流会抖动","Current dips during auth"],
        ["GPIO5","SS · 片选","SS · chip select"],
        ["GPIO23","MOSI · 发认证命令","MOSI · auth commands"],
        ["GPIO19","MISO · 块数据回传","MISO · block data in"]],
  overview=[
    ["MIFARE Classic 1K 的「1K」指 <b>1024 字节</b>：16 个扇区 × 4 块 × 16 字节。每块 16 字节，每个扇区最后一块（块 3）是<b>控制块</b>，存两把密钥和存取权限。",
     "The 1K in MIFARE Classic 1K means <b>1024 bytes</b>: 16 sectors x 4 blocks x 16 bytes. Every block is 16 bytes, and the last block of each sector (block 3) is the <b>trailer</b> holding two keys and the access bits."],
    ["扇区 0 的块 0 是<b>厂家块</b>，存 UID 和厂商数据，正常只读。往这里写等于把卡变砖，任何教程让你「写块 0」都要先警惕。",
     "Block 0 of sector 0 is the <b>manufacturer block</b> holding UID and vendor data; it is read-only in practice. Writing it bricks the card — be suspicious of any tutorial that tells you to write block 0."],
    ["访问一个扇区要先 <b>认证</b>：用 Key A 或 Key B 加存取位允许的操作。出厂默认密钥常常是 <code>FF FF FF FF FF FF</code>，不改等于把卡敞开。",
     "Accessing a sector requires <b>authentication</b> with Key A or Key B plus the permissions in the access bits. Factory default is often <code>FF FF FF FF FF FF</code>; leaving it means the card is wide open."]],
  points=[
    ["块 3 千万别乱写","控制块写错会永久锁死该扇区（甚至整卡）。改密钥要在同一块里同时写 Key A、存取位、Key B，格式错一位就废。",
     "Never write block 3 casually","A wrong trailer can permanently lock the sector or the card. Changing keys means writing Key A, access bits and Key B together; one wrong nibble bricks it."],
    ["认证是按扇区","<code>PCD_Authenticate()</code> 只对目标扇区生效，换扇区要重新认证。读多扇区时别只认证一次。",
     "Auth is per sector","<code>PCD_Authenticate()</code> unlocks one sector; switch sectors and you must authenticate again."],
    ["读 18 字节是规矩","<code>MIFARE_Read()</code> 的缓冲要 18 字节：16 字节数据 + 2 字节 CRC。给 16 会越界，这是新手最常见的崩溃点。",
     "Read buffer is 18 bytes","<code>MIFARE_Read()</code> needs an 18-byte buffer: 16 data bytes plus 2 CRC bytes. Passing 16 overflows — the classic newbie crash."],
    ["默认密钥等于没锁","<code>FFFFFFFFFFFF</code> 是公开默认值。真做门禁必须换成自己生成的密钥，并且别把 Key B 设成可读。",
     "Default keys are no lock","<code>FFFFFFFFFFFF</code> is public. Real access control needs generated keys, and Key B must not be readable."]],
  code=r'''// 第 34 课：认证扇区 1，读块 4
#include <SPI.h>
#include <MFRC522.h>

MFRC522 rfid(5, 22);
MFRC522::MIFARE_Key key;          // 默认 FF FF FF FF FF FF

void setup() {
  Serial.begin(115200);
  SPI.begin(18, 19, 23, 5);
  rfid.PCD_Init();
  for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;
  Serial.println("Tap a MIFARE Classic card...");
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent()) return;
  if (!rfid.PICC_ReadCardSerial())   return;

  MFRC522::StatusCode st;
  st = rfid.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, 4, &key, &rfid.uid);
  if (st != MFRC522::STATUS_OK) {
    Serial.print("auth failed: ");
    Serial.println(rfid.GetStatusCodeName(st));
    rfid.PICC_HaltA();
    return;
  }

  byte buf[18];                   // 16 数据 + 2 CRC
  byte len = sizeof(buf);
  st = rfid.MIFARE_Read(4, buf, &len);
  if (st == MFRC522::STATUS_OK) {
    Serial.print("block 4:");
    for (byte i = 0; i < 16; i++) {
      Serial.print(" ");
      if (buf[i] < 0x10) Serial.print("0");
      Serial.print(buf[i], HEX);
    }
    Serial.println();
  }

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();         // 释放认证状态
  delay(500);
}
''',
  tl=[
    dict(t=300,  serial="寻卡成功 · SAK=0x08（1K 卡）", en="Card found · SAK=0x08 (1K card)", part="pinsR", state="on"),
    dict(t=850,  serial="认证扇区 1 · Key A = FFFFFFFFFFFF", en="Authenticating sector 1 · Key A = FFFFFFFFFFFF"),
    dict(t=1400, serial="认证通过 · Crypto1 流加密已建立", en="Auth OK · Crypto1 stream established"),
    dict(t=1850, serial="读块 4（16 字节数据 + 2 字节 CRC）", en="Reading block 4 (16 data bytes + 2 CRC)"),
    dict(t=2300, serial="block 4: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00", en="block 4: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"),
    dict(t=2750, serial="扇区 1 共 4 块 · 块 7 是控制块，别写", en="Sector 1 has 4 blocks · block 7 is the trailer, do not write"),
    dict(t=3200, serial="PCD_StopCrypto1 · 认证状态释放", en="PCD_StopCrypto1 · crypto state released", part="pinsR", state="off"),
  ]),

dict(
  no="35", title="写卡与钱包：块写入与值块加减",
  titleEn="Writing: data blocks and the value-block wallet",
  meta="RFID · 写入与校验", metaEn="RFID · write and verify",
  group=RFID, groupEn=RFID_EN,
  wiringHd="接线：不变，卡必须一直贴着", wiringHdEn="Wiring: unchanged, keep the card in the field",
  wiring="接线不变。写卡比读卡更怕<b>中途离开场</b>：写到一半卡被拿开，块内容可能只剩一半。写的时候把卡压稳。",
  wiringEn="Same wiring. Writes are far more sensitive to the card leaving the field: a half-written block is possible. Keep the card steady while writing.",
  pins=[["3V3","写操作电流更大","Writes draw more current"],
        ["GPIO5","SS · 片选","SS · chip select"],
        ["GPIO23","MOSI · 写入数据","MOSI · data out"],
        ["GPIO19","MISO · 状态回传","MISO · status back"]],
  overview=[
    ["数据块就是 <b>16 字节的格子</b>，可以当字符、数字、结构体随便用。常见做法：块 4 存卡号，块 5 存用户名，块 6 存余额或计数器。",
     "A data block is just a <b>16-byte cell</b> you can use as text, numbers or a struct. Common layout: block 4 the card ID, block 5 the holder name, block 6 the balance or counter."],
    ["MIFARE 还有一种特殊格式 <b>值块</b>：同一数值存三份（原值、反码、原值）加一个地址字节，并用冗余校验防写坏。它支持 <b>加、减、恢复</b> 三种原子操作，适合做不联网的钱包。",
     "MIFARE also has a <b>value block</b>: the number stored three times (value, complement, value) plus an address byte with redundancy checks. It supports atomic <b>increment, decrement and restore</b> — good for an offline wallet."],
    ["最关键的一条：<b>写完一定要读回校验</b>。写命令返回 OK 只代表通信成功，不代表块内容对。生产代码里「写-读-比对」是硬规矩。",
     "The golden rule: <b>always read back after writing</b>. An OK status only means the command was acknowledged, not that the bytes are right. Write-read-compare is mandatory in production code."]],
  points=[
    ["先读出原值备份","任何写操作前先读一遍并打印，写坏了至少知道原来是什么。别对着「看起来是空的」块直接写。",
     "Back up before writing","Read and print the block first. Never write into a block just because it looks empty."],
    ["只能写同扇区地址","值块的地址字节必须等于该块所在块号，否则部分卡片会拒绝或损坏数据。跨扇区搬运要「读旧块→写新块」。",
     "Address must match the block","A value block's address byte must equal its own block number, or cards may reject or corrupt it. To move data across sectors, read then write."],
    ["写控制块会锁死","块 3 / 7 / 11 是控制块，写错一次该扇区可能永久不可读。教程里「改密钥」的代码要先在废卡上练。",
     "Trailers lock you out","Blocks 3, 7, 11 are trailers; one bad write can lock the sector forever. Practise key changes on a throwaway card."],
    ["写入寿命有限","MIFARE Classic 的写寿命常标 10 万次量级。做计数器要算频率：每秒写一次，几天就到寿命。",
     "Limited write endurance","MIFARE Classic is rated around 100k writes. Counting once per second wears a card out in days."]],
  code=r'''// 第 35 课：写 16 字节 + 读回校验
#include <SPI.h>
#include <MFRC522.h>

MFRC522 rfid(5, 22);
MFRC522::MIFARE_Key key;
byte BLOCK = 5;

void setup() {
  Serial.begin(115200);
  SPI.begin(18, 19, 23, 5);
  rfid.PCD_Init();
  for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;
  Serial.println("Tap a card to write...");
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent()) return;
  if (!rfid.PICC_ReadCardSerial())   return;

  byte sector = BLOCK / 4;
  if (rfid.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A,
                            BLOCK, &key, &rfid.uid) != MFRC522::STATUS_OK) {
    Serial.println("auth failed");
    rfid.PICC_HaltA();
    return;
  }

  byte data[16];
  memset(data, 0, 16);
  memcpy(data, "ESP32-LAB-OK", 12);        // 写 12 字节，剩下补 0

  MFRC522::StatusCode st = rfid.MIFARE_Write(BLOCK, data, 16);
  Serial.print("write: ");
  Serial.println(rfid.GetStatusCodeName(st));

  byte back[18];                            // 16 + 2 CRC
  byte len = sizeof(back);
  if (rfid.MIFARE_Read(BLOCK, back, &len) == MFRC522::STATUS_OK) {
    Serial.print("read back: ");
    Serial.println((char *)back);
    if (memcmp(back, data, 16) == 0) Serial.println("verify OK");
    else                             Serial.println("verify FAILED");
  }

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
  delay(1000);
}
''',
  tl=[
    dict(t=300,  serial="寻卡 · 扇区 1 / 块 5 目标", en="Card found · target sector 1 / block 5", part="pinsR", state="on"),
    dict(t=800,  serial="认证扇区 1 · Key A 通过", en="Sector 1 authenticated with Key A"),
    dict(t=1300, serial="写块 5：ESP32-LAB-OK + 4 字节填充", en="Writing block 5: ESP32-LAB-OK plus padding"),
    dict(t=1800, serial="write: STATUS_OK", en="write: STATUS_OK"),
    dict(t=2300, serial="read back: ESP32-LAB-OK", en="read back: ESP32-LAB-OK"),
    dict(t=2750, serial="verify OK · 16 字节逐字节一致", en="verify OK · all 16 bytes match"),
    dict(t=3200, serial="提示：值块可用 Increment/Decrement 做离线钱包", en="Tip: value blocks support Increment/Decrement for offline wallets"),
  ]),

dict(
  no="36", title="极限实验：把参数推到出问题为止",
  titleEn="Limit tests: push each setting until it breaks",
  meta="RFID · 时钟、增益、距离", metaEn="RFID · clock, gain, range",
  group=RFID, groupEn=RFID_EN,
  wiringHd="接线：不变，电源换质量更好的那根线", wiringHdEn="Wiring: unchanged, swap in a better USB cable",
  wiring="接线不变，但要<b>换一根更短更粗的 USB 线</b>再测一遍：供电纹波直接影响读卡距离，这一项差异比改代码明显得多。",
  wiringEn="Same wiring, but retest with a <b>shorter, thicker USB cable</b>: supply ripple affects read range more than any code change here.",
  pins=[["3V3","纹波直接决定读距","Ripple decides read range"],
        ["GPIO18","SCK · 频率可调 1–10 MHz","SCK · 1–10 MHz tunable"],
        ["GPIO5","SS · 片选","SS · chip select"],
        ["GPIO19","MISO · 用于统计误码","MISO · used to count errors"]],
  overview=[
    ["这一课不写新功能，而是做<b>参数扫描</b>：SPI 时钟、接收增益、读卡距离、卡片类型，每次只改一项，记录成功率。工程能力往往就体现在这种「知道边界在哪」上。",
     "No new feature here — this is a <b>parameter sweep</b>: SPI clock, receiver gain, distance, card type. Change one thing at a time and record the success rate. Knowing where the limits are is real engineering."],
    ["MFRC522 的 SPI 上限约 <b>10 MHz</b>，超了会丢位。接收增益在 <code>RFCfgReg</code> 里，调高能多读几毫米，但也会把噪声一起放大，误码率反而上升。",
     "The MFRC522 tops out around <b>10 MHz</b> SPI; beyond that bits drop. Receiver gain lives in <code>RFCfgReg</code> — a higher gain buys a few millimetres but amplifies noise and can raise the error rate."],
    ["把同一张卡从「贴着天线」一点点移远，每档读 20 次，记录成功次数。你会发现曲线不是线性下降，而是在某个距离上<b>突然全部失败</b>——那是场强低于卡片启动电压的临界点。",
     "Move one card away from the antenna step by step, 20 tries per step, and count successes. The curve does not fall linearly; it <b>collapses</b> at one point — the threshold where the field drops below the card's start-up voltage."]],
  points=[
    ["一次只改一个变量","同时改时钟和增益，出问题就不知道是谁的锅。扫描表要比代码更有价值。",
     "One variable at a time","Change clock and gain together and you cannot blame either. The sweep table is worth more than the code."],
    ["供电比代码更关键","USB 线细、延长线长、共用大功率外设，都会让 3.3V 掉压，表现为「代码没改却突然读不到」。",
     "Power beats code","Thin cables, long extensions or a hungry peripheral sag the 3.3V rail and cause phantom read failures."],
    ["卡片之间也有差异","不同厂家的卡天线匝数、芯片灵敏度不同，同一距离下一张能读、另一张不能。做产品要拿目标卡型实测。",
     "Cards differ","Antenna turns and chip sensitivity vary by vendor; at the same distance one card reads and another does not. Test with the exact card you will ship."],
    ["失败要有分类","记录「没回应」「UID 冲突」「CRC 错」三类，分别对应场强、多卡、时钟问题，比一个「失败」有用得多。",
     "Classify failures","Log no-response, UID collision and CRC error separately — they point at field strength, multiple cards and clock issues."]],
  code=r'''// 第 36 课：参数扫描，统计读卡成功率
#include <SPI.h>
#include <MFRC522.h>

MFRC522 rfid(5, 22);

struct Trial { const char *name; uint32_t hz; byte gain; };
Trial trials[] = {
  { "1 MHz  / gain 18dB", 1000000,  0x40 },
  { "4 MHz  / gain 18dB", 4000000,  0x40 },
  { "8 MHz  / gain 18dB", 8000000,  0x40 },
  { "8 MHz  / gain 33dB", 8000000,  0x70 },
  { "10 MHz / gain 33dB",10000000,  0x70 },
};

void setup() {
  Serial.begin(115200);
  for (auto &t : trials) {
    SPI.begin(18, 19, 23, 5);
    SPI.setFrequency(t.hz);
    rfid.PCD_Init();
    rfid.PCD_SetRegisterBitMask(MFRC522::RFCfgReg, t.gain);

    byte ok = 0;
    for (byte i = 0; i < 20; i++) {
      if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
        ok++;
        rfid.PICC_HaltA();
      }
      delay(40);
    }
    Serial.print(t.name);
    Serial.print(" -> ");
    Serial.print(ok);
    Serial.println("/20");
    SPI.end();
    delay(200);
  }
  Serial.println("sweep done");
}

void loop() {}
''',
  tl=[
    dict(t=300,  serial="扫描开始 · 5 组参数 × 20 次", en="Sweep start · 5 settings x 20 tries", part="pinsR", state="on"),
    dict(t=900,  serial="1 MHz  / gain 18dB -> 20/20", en="1 MHz  / gain 18dB -> 20/20"),
    dict(t=1400, serial="4 MHz  / gain 18dB -> 20/20", en="4 MHz  / gain 18dB -> 20/20"),
    dict(t=1900, serial="8 MHz  / gain 18dB -> 19/20", en="8 MHz  / gain 18dB -> 19/20"),
    dict(t=2400, serial="8 MHz  / gain 33dB -> 20/20", en="8 MHz  / gain 33dB -> 20/20"),
    dict(t=2900, serial="10 MHz / gain 33dB -> 11/20", en="10 MHz / gain 33dB -> 11/20"),
    dict(t=3350, serial="结论：时钟 8 MHz + 高增益是这块板的最优点", en="Result: 8 MHz with high gain is the sweet spot here"),
    dict(t=3750, serial="提醒：换一根劣质 USB 线，全部档位都会掉", en="Reminder: a poor USB cable drops every row", part="usb", state="on"),
  ]),

dict(
  no="37", title="卡片管理器：浏览器里管名单",
  titleEn="Card manager: a web console for the whitelist",
  meta="RFID · Web Server + 存储", metaEn="RFID · web server and storage",
  group=RFID, groupEn=RFID_EN,
  wiringHd="接线：读卡器 + 一根 USB 供电", wiringHdEn="Wiring: reader plus USB power",
  wiring="接线不变。手机连上同一 Wi-Fi 后打开串口打印的 IP，就能看到名单页面：刷卡即登记，点删除即移除。<b>不需要装 App</b>。",
  wiringEn="Same wiring. Join the same Wi-Fi from your phone, open the IP printed on serial, and you get the roster page: tap a card to enrol, tap delete to remove. <b>No app needed</b>.",
  pins=[["3V3","读卡器供电","Reader supply"],
        ["GPIO5","SS · 片选","SS · chip select"],
        ["GPIO2","板载 LED · 授权指示","On-board LED · grant hint"],
        ["GPIO0","BOOT · 长按清空名单","BOOT · hold to clear roster"]],
  overview=[
    ["把「读卡」升级成「管理」：ESP32 起一个 HTTP 服务，<code>/api/cards</code> 返回 JSON 名单，<code>/api/grant</code> 把当前卡加进去，<code>/api/revoke</code> 删掉。前端就是一个静态页面。",
     "Move from reading to managing: the ESP32 serves HTTP, <code>/api/cards</code> returns the roster as JSON, <code>/api/grant</code> enrols the current card and <code>/api/revoke</code> removes it. The UI is one static page."],
    ["名单要断电不丢，所以落在 <b>NVS</b> 或 LittleFS 里。NVS 适合小键值（几十条 UID），LittleFS 适合放网页文件和长列表。",
     "The roster must survive power loss, so store it in <b>NVS</b> or LittleFS. NVS suits small key-value sets (dozens of UIDs), LittleFS suits web assets and long lists."],
    ["这一课也是安全课：<b>只认 UID 的名单可以被克隆卡绕过</b>。真实系统要加「密钥认证 + 时间窗 + 审计日志」，本站第 35 课的密钥和这里的名单要一起用。",
     "This is also a security lesson: <b>a UID-only roster falls to cloned cards</b>. Real systems add key authentication, time windows and an audit log; combine lesson 35's keys with this roster."]],
  points=[
    ["接口先定 JSON","<code>{\"cards\":[\"4A2F917C\"],\"log\":[...]}</code> 这种形状，前端和固件都简单。别用自定义二进制协议折腾自己。",
     "Agree on JSON first","A shape like <code>{\"cards\":[\"4A2F917C\"],\"log\":[...]}</code> keeps both ends simple. Do not invent a binary protocol for this."],
    ["写名单要加锁","HTTP 任务和读卡任务在不同核上，同时改名单会破坏数据。用一个互斥量或统一走队列。",
     "Lock the roster","HTTP and reader tasks may run on different cores; concurrent writes corrupt it. Use a mutex or a single queue."],
    ["日志比名单更重要","谁在几点刷了卡，比「名单里有谁」更能定位问题。日志用环形缓冲，别无限增长。",
     "Logs beat rosters","Who tapped at what time explains failures better than the roster itself. Use a ring buffer, not unbounded growth."],
    ["别把接口暴露到公网","这类页面没有账号体系，仅限内网。要远程访问就套一层认证或走 VPN。",
     "Never expose it publicly","These endpoints have no auth. Keep them on the LAN; use a VPN for remote access."]],
  code=r'''// 第 37 课：Web 名单管理（内网使用）
#include <WiFi.h>
#include <WebServer.h>
#include <Preferences.h>
#include <SPI.h>
#include <MFRC522.h>

WebServer server(80);
Preferences prefs;
MFRC522 rfid(5, 22);

String roster = "";             // 逗号分隔的 UID
String lastCard = "";
SemaphoreHandle_t lock;

void saveRoster() {
  prefs.begin("rfid", false);
  prefs.putString("cards", roster);
  prefs.end();
}

void setup() {
  Serial.begin(115200);
  SPI.begin(18, 19, 23, 5);
  rfid.PCD_Init();
  lock = xSemaphoreCreateMutex();

  prefs.begin("rfid", true);
  roster = prefs.getString("cards", "");
  prefs.end();

  WiFi.begin("YOUR_SSID", "YOUR_PASS");
  while (WiFi.status() != WL_CONNECTED) delay(300);
  Serial.print("open http://");
  Serial.println(WiFi.localIP());

  server.on("/api/cards", []() {
    server.send(200, "application/json",
                "{\"cards\":\"" + roster + "\",\"last\":\"" + lastCard + "\"}");
  });

  server.on("/api/grant", []() {
    if (lastCard.length() == 0) return server.send(409, "text/plain", "no card");
    if (xSemaphoreTake(lock, portMAX_DELAY) == pdTRUE) {
      if (roster.indexOf(lastCard) < 0) roster += (roster.length() ? "," : "") + lastCard;
      xSemaphoreGive(lock);
    }
    saveRoster();
    server.send(200, "text/plain", "granted " + lastCard);
  });

  server.begin();
}

void loop() {
  server.handleClient();

  if (!rfid.PICC_IsNewCardPresent()) return;
  if (!rfid.PICC_ReadCardSerial())   return;

  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(rfid.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();
  lastCard = uid;

  bool ok = roster.indexOf(uid) >= 0;
  digitalWrite(2, ok ? HIGH : LOW);
  Serial.println(ok ? "ACCESS OK  " + uid : "DENIED     " + uid);

  rfid.PICC_HaltA();
  delay(300);
}
''',
  tl=[
    dict(t=300,  serial="Wi-Fi 连接中 · 等待分配 IP", en="Joining Wi-Fi · waiting for an IP", part="module", state="on"),
    dict(t=900,  serial="本机地址 192.168.1.42 · 页面已就绪", en="Local IP 192.168.1.42 · page ready"),
    dict(t=1400, serial="GET /api/cards · 返回 3 张授权卡", en="GET /api/cards · 3 authorised cards"),
    dict(t=1900, serial="刷卡 4A2F917C · 名单命中", en="Card 4A2F917C · in roster"),
    dict(t=2300, serial="ACCESS OK  4A2F917C", en="ACCESS OK  4A2F917C", part="led", state="on"),
    dict(t=2750, serial="刷卡 1C77A0B2 · 不在名单", en="Card 1C77A0B2 · not in roster"),
    dict(t=3150, serial="DENIED     1C77A0B2", en="DENIED     1C77A0B2"),
    dict(t=3550, serial="POST /api/grant · 新卡写入 NVS", en="POST /api/grant · new card written to NVS"),
  ]),

dict(
  no="38", title="卡片小伙伴：给孩子的门禁玩具",
  titleEn="Card buddy: an access-control toy for kids",
  meta="RFID · 状态机综合项目", metaEn="RFID · state-machine project",
  group=RFID, groupEn=RFID_EN,
  wiringHd="接线：读卡器 + 舵机 + 蜂鸣器 + LED",
  wiringHdEn="Wiring: reader + servo + buzzer + LED",
  wiring="读卡器六线照旧；<b>舵机信号→GPIO13</b>，<b>蜂鸣器→GPIO4</b>，<b>绿灯→GPIO2（板载）</b>。<b>舵机必须独立 5V 供电并共地</b>——从板子 3.3V 取电会复位。",
  wiringEn="Reader wiring as before; <b>servo signal→GPIO13</b>, <b>buzzer→GPIO4</b>, <b>green LED→GPIO2 (on-board)</b>. <b>Power the servo from a separate 5V rail with a shared ground</b> — pulling it from 3.3V resets the board.",
  pins=[["GPIO5","读卡器 SS","Reader SS"],
        ["GPIO13","舵机 PWM · 0° / 90°","Servo PWM · 0 / 90 deg"],
        ["GPIO4","蜂鸣器 · 成功/失败音","Buzzer · ok / deny tones"],
        ["GPIO2","板载 LED · 状态","On-board LED · status"]],
  overview=[
    ["把前七课拼成一个真东西：刷对卡→舵机开门→绿灯+上扬提示音→2 秒后自动关上；刷错卡→红灯闪+低沉音+3 秒冷却。这就是一台门禁。",
     "Assemble the previous seven lessons into a real object: valid card opens the servo, green LED and rising tone, auto-close after 2 s; invalid card flashes red, plays a low tone and locks out for 3 s. That is an access controller."],
    ["关键是用<b>状态机</b>而不是 <code>delay</code> 串起来：<code>IDLE → CHECK → OPEN → COOLDOWN</code>。每个状态只做一件小事，读卡在状态机外面持续跑，刷卡永远不会被「正在等待」卡住。",
     "The key is a <b>state machine</b> instead of chained <code>delay</code>s: <code>IDLE → CHECK → OPEN → COOLDOWN</code>. Each state does one small thing and card polling runs outside the machine, so a tap is never blocked by a pending wait."],
    ["给孩子玩的话，反馈比安全更重要：<b>声音要不一样</b>（成功两个上扬音、失败一个低音），<b>灯要明显</b>，门要开得慢一点让他看清。做到这三点，他就知道「为什么这次没开」。",
     "For kids, feedback matters more than security: <b>distinct sounds</b> (two rising notes for ok, one low for deny), <b>obvious lights</b>, and a slow door so he sees it move. Those three teach him why it did not open."]],
  points=[
    ["状态机优于 delay","<code>delay(2000)</code> 期间不读卡、不响应按键。用 <code>millis()</code> 记时间戳，主循环永不阻塞。",
     "State machine over delay","A <code>delay(2000)</code> blocks card reads and buttons. Stamp times with <code>millis()</code> and keep the loop non-blocking."],
    ["冷却时间防连刷","刷卡成功后的 2–3 秒内不再响应，避免孩子连续刷十次把舵机抖坏。",
     "Cooldown stops spamming","Ignore taps for 2–3 s after success so a kid cannot hammer the servo ten times."],
    ["舵机单独供电","SG90 堵转电流能到 700 mA，USB 3.3V 供不起。共地是必须的，否则 PWM 信号没有参考电平。",
     "Separate servo power","An SG90 can pull 700 mA in stall; USB 3.3V cannot. A shared ground is mandatory or the PWM has no reference."],
    ["失败也要有记录","串口打印时间 + UID + 结果，回头能看出「是这张卡没登记」还是「读卡器根本没读到」。",
     "Log the denials","Print time, UID and result so you can tell a missing enrolment from a reader that never saw the card."]],
  code=r'''// 第 38 课：刷卡开门（状态机版）
#include <SPI.h>
#include <MFRC522.h>
#include <ESP32Servo.h>

MFRC522 rfid(5, 22);
Servo door;

const char *WHITELIST[] = { "4A2F917C", "8B01D3E5" };
enum State { IDLE, OPEN, COOLDOWN };
State state = IDLE;
uint32_t since = 0;

bool allowed(const String &uid) {
  for (auto &w : WHITELIST) if (uid == w) return true;
  return false;
}

void tone2(int f1, int f2) {
  tone(4, f1, 120); delay(140);
  tone(4, f2, 160); delay(180);
  noTone(4);
}

void setup() {
  Serial.begin(115200);
  SPI.begin(18, 19, 23, 5);
  rfid.PCD_Init();
  pinMode(2, OUTPUT);
  door.attach(13);
  door.write(0);                 // 关
  Serial.println("tap your card");
}

void loop() {
  uint32_t now = millis();

  if (state == OPEN && now - since > 2000) {
    door.write(0); digitalWrite(2, LOW);
    state = COOLDOWN; since = now;
    Serial.println("door closed");
  }
  if (state == COOLDOWN && now - since > 3000) state = IDLE;

  if (state != IDLE) return;                       // 开门期间不读卡

  if (!rfid.PICC_IsNewCardPresent()) return;
  if (!rfid.PICC_ReadCardSerial())   return;

  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(rfid.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();

  if (allowed(uid)) {
    Serial.println("welcome " + uid);
    door.write(90); digitalWrite(2, HIGH);
    tone2(880, 1320);
    state = OPEN; since = now;
  } else {
    Serial.println("denied " + uid);
    tone2(220, 180);
    delay(120);
  }
  rfid.PICC_HaltA();
  delay(200);
}
''',
  tl=[
    dict(t=300,  serial="上电 · 舵机归零，门关闭", en="Boot · servo to 0, door closed", part="pwrled", state="on"),
    dict(t=900,  serial="刷白名单卡 4A2F917C", en="Whitelisted card 4A2F917C tapped", part="pinsR", state="on"),
    dict(t=1400, serial="welcome 4A2F917C · 上扬提示音", en="welcome 4A2F917C · rising tone"),
    dict(t=1800, serial="舵机转到 90° · 门打开", en="Servo to 90 deg · door open", part="led", state="on"),
    dict(t=2400, serial="2 秒后自动关门 · 进入冷却", en="Auto-close after 2 s · entering cooldown"),
    dict(t=2900, serial="刷陌生卡 1C77A0B2", en="Unknown card 1C77A0B2 tapped"),
    dict(t=3350, serial="denied 1C77A0B2 · 低沉音 + 3 秒冷却", en="denied 1C77A0B2 · low tone plus 3 s cooldown"),
    dict(t=3750, serial="状态机回到 IDLE · 等待下一次刷卡", en="Back to IDLE · waiting for the next tap", part="led", state="off"),
  ]),

dict(
  no="39", title="聆听：INMP441 I2S 数字麦克风",
  titleEn="Listening: the INMP441 I2S microphone",
  meta="声音 · I2S 输入", metaEn="Audio · I2S input",
  group=SND, groupEn=SND_EN,
  wiringHd="接线：I2S 三线 + 电源", wiringHdEn="Wiring: three I2S wires plus power",
  wiring="<b>VDD→3V3、GND→GND、L/R→GND、WS→GPIO25、SCK→GPIO26、SD→GPIO33</b>。<b>L/R 接地选左声道</b>，接 3V3 选右声道——接错只会读到静音，不会烧。",
  wiringEn="<b>VDD→3.3V, GND→GND, L/R→GND, WS→GPIO25, SCK→GPIO26, SD→GPIO33</b>. <b>Tie L/R to GND for the left channel</b>, to 3.3V for right — a wrong choice gives silence, not damage.",
  pins=[["GPIO25","WS · 左右声道时钟","WS · word select"],
        ["GPIO26","SCK · 位时钟","SCK · bit clock"],
        ["GPIO33","SD · 数据输入","SD · data in"],
        ["3V3","麦克风供电（1.8–3.3V）","Mic supply (1.8–3.3V)"]],
  overview=[
    ["模拟麦克风要先放大、再送进 ADC，一路都在捡噪声。<b>INMP441 直接把声音变成数字位流</b>：内部有 MEMS 振膜、ADC 和 I2S 接口，输出就是采样值，省掉了整个模拟链路。",
     "An analog mic needs amplification and an ADC, and picks up noise all the way. <b>The INMP441 digitises inside the package</b>: MEMS diaphragm, ADC and I2S interface, so you get sample values and skip the analog chain."],
    ["I2S 只要三根信号：<b>SCK</b>（位时钟）、<b>WS</b>（左右声道选择）、<b>SD</b>（数据）。它和 I²C/SPI 最大的不同是<b>连续流</b>——时钟不停，数据就一直在来，你必须持续读走，否则 DMA 缓冲溢出。",
     "I2S needs three signals: <b>SCK</b> (bit clock), <b>WS</b> (word select) and <b>SD</b> (data). Unlike I2C or SPI it is a <b>continuous stream</b>: the clock never stops, so you must keep draining the DMA buffers or they overflow."],
    ["INMP441 输出 <b>24 位</b>数据，但装在 32 位帧里。读到 <code>int32_t</code> 后要右移对齐，否则数值大得离谱、音量算出来全错——这是新手第一个大坑。",
     "The INMP441 emits <b>24-bit</b> samples inside 32-bit frames. Shift the <code>int32_t</code> into range, or the values look enormous and every loudness calculation is wrong — the first classic trap."]],
  points=[
    ["右移对齐 24 位","常见写法是 <code>v >> 14</code>（或 <code>>> 8</code> 取 24 位再截）。先打印几个值看量级，正常说话大约在 ±10 万到 ±100 万之间。",
     "Align the 24 bits","Usually <code>v >> 14</code> (or <code>>> 8</code> then scale). Print a few samples first: normal speech lands in the ±100k to ±1M range."],
    ["DMA 必须持续读","<code>i2s_read()</code> 要放在 <code>loop()</code> 里不停调用。中间做 <code>delay(1000)</code> 会让缓冲溢出、数据错位。",
     "Keep draining DMA","Call <code>i2s_read()</code> continuously. A <code>delay(1000)</code> in between overflows the buffers and shifts the data."],
    ["L/R 决定声道","悬空是最糟的选择：电平不确定，可能两个声道都拿不到。明确接 GND 或 3V3。",
     "Never leave L/R floating","A floating L/R is the worst case: undefined level and possibly no channel at all. Tie it to GND or 3.3V."],
    ["麦克风怕风和震动","MEMS 麦克风对气流敏感，装在盒子里要留声孔，别直接对着喇叭，否则会啸叫。",
     "Airflow and vibration","MEMS mics hate drafts. Leave a port in the enclosure and keep it away from the speaker to avoid feedback."]],
  code=r'''// 第 39 课：读 I2S 麦克风，串口打印波形值
#include <driver/i2s.h>

#define I2S_WS   25
#define I2S_SCK  26
#define I2S_SD   33

void setup() {
  Serial.begin(115200);

  i2s_config_t cfg = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = 16000,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,   // 24 bit 装在 32 bit 帧
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 4,
    .dma_buf_len = 256,
    .use_apll = false,
  };
  i2s_driver_install(I2S_NUM_0, &cfg, 0, NULL);

  i2s_pin_config_t pins = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = -1,
    .data_in_num = I2S_SD,
  };
  i2s_set_pin(I2S_NUM_0, &pins);
  Serial.println("listening at 16 kHz");
}

void loop() {
  int32_t raw[256];
  size_t got = 0;
  i2s_read(I2S_NUM_0, raw, sizeof(raw), &got, portMAX_DELAY);

  int n = got / sizeof(int32_t);
  for (int i = 0; i < n; i += 16) {
    Serial.println(raw[i] >> 14);        // 对齐到可用量级
  }
}
''',
  tl=[
    dict(t=300,  serial="I2S0 初始化 · 16 kHz / 32 bit 帧", en="I2S0 init · 16 kHz / 32-bit frames", part="pinsR", state="on"),
    dict(t=800,  serial="WS=25 SCK=26 SD=33 · L/R 接地选左声道", en="WS=25 SCK=26 SD=33 · L/R tied low, left channel"),
    dict(t=1300, serial="DMA 双缓冲运行 · 4 × 256 帧", en="DMA buffers running · 4 x 256 frames"),
    dict(t=1800, serial="sample: -12480", en="sample: -12480"),
    dict(t=2200, serial="sample: 33152", en="sample: 33152"),
    dict(t=2600, serial="sample: 180224 · 有人说话", en="sample: 180224 · speech detected"),
    dict(t=3050, serial="提示：24 位数据在 32 位帧里，记得右移对齐", en="Tip: 24-bit data in 32-bit frames needs an arithmetic shift"),
  ]),

dict(
  no="40", title="响度：从采样值算分贝",
  titleEn="Loudness: turning samples into decibels",
  meta="声音 · RMS 与 dBFS", metaEn="Audio · RMS and dBFS",
  group=SND, groupEn=SND_EN,
  wiringHd="接线：沿用第 39 课", wiringHdEn="Wiring: same as lesson 39",
  wiring="线路不变。<b>板载 LED 亮度</b>会跟着响度走：说话时亮、安静时暗，这样你不用看串口也能判断麦克风在工作。",
  wiringEn="No rewiring. <b>The on-board LED brightness</b> follows loudness — bright when you speak, dim when quiet — so you can tell the mic works without watching serial.",
  pins=[["GPIO25","WS · 声道选择","WS · word select"],
        ["GPIO26","SCK · 位时钟","SCK · bit clock"],
        ["GPIO33","SD · 采样数据","SD · sample data"],
        ["GPIO2","板载 LED · 响度指示","On-board LED · level meter"]],
  overview=[
    ["「多响」不能看单个采样值——波形每秒上下几千次，取哪个点都是随机的。正确做法是算<b>一段窗口内的 RMS</b>（均方根），它对应声音的能量。",
     "Loudness cannot come from one sample: the waveform crosses zero thousands of times a second. Compute the <b>RMS over a window</b> instead; that tracks acoustic energy."],
    ["RMS 再取对数变成 <b>dBFS</b>：<code>20 * log10(rms / fullScale)</code>。满量程是 0 dBFS，安静房间大约 −60 dBFS，正常说话 −25 到 −15 dBFS。用对数是因为人耳本身就是对数感知的。",
     "Take the log to get <b>dBFS</b>: <code>20 * log10(rms / fullScale)</code>. Full scale is 0 dBFS, a quiet room sits near −60, normal speech −25 to −15. The log matches how hearing works."],
    ["窗口长度决定反应速度：<b>50 ms</b> 左右既不闪烁也不迟钝。再用一个一阶低通做平滑（新值占 20%），读数就不会数字乱跳。",
     "Window length sets responsiveness: about <b>50 ms</b> is neither jittery nor sluggish. Smooth with a one-pole filter (20% new value) so the number stops flickering."],
  ],
  points=[
    ["别用平均值","声音是正负交替的，直接求平均会互相抵消，安静时读数反而最大。必须平方后平均，再开方。",
     "Never average raw samples","Samples alternate sign and cancel out; a raw average even peaks when silent. Square, average, then take the root."],
    ["0 dBFS 是数字上限","超过就削顶（clipping），波形变成方波，听起来破。看到读数贴 0 要立刻降增益或离远点。",
     "0 dBFS is the ceiling","Beyond it you clip into a square wave and it sounds torn. If readings hug 0, lower the gain or back off."],
    ["dBFS 不是 dB SPL","dBFS 是相对数字满量程，dB SPL 是相对声压。要读「多少分贝」必须用声级计做一次参考校准，加一个固定偏移。",
     "dBFS is not dB SPL","dBFS is relative to digital full scale; dB SPL is relative to sound pressure. Real decibels need a one-time calibration against a sound level meter."],
    ["LED 用 gamma 才线性","<code>analogWrite</code> 的占空比和视觉亮度不是线性关系，把 dB 映射到 0–255 后开个方（或查表）看起来才顺。",
     "Gamma-correct the LED","<code>analogWrite</code> duty is not perceptually linear; square the 0–255 value (or use a table) for a smooth meter."]],
  code=r'''// 第 40 课：RMS -> dBFS，并驱动 LED 亮度
#include <driver/i2s.h>
#include <math.h>

#define I2S_WS 25
#define I2S_SCK 26
#define I2S_SD 33
#define WINDOW 1024                       // 16 kHz 下约 64 ms

float smoothDb = -60;

void setup() {
  Serial.begin(115200);
  i2s_config_t cfg = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = 16000,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 4, .dma_buf_len = 256, .use_apll = false,
  };
  i2s_driver_install(I2S_NUM_0, &cfg, 0, NULL);
  i2s_pin_config_t pins = { I2S_SCK, I2S_WS, -1, I2S_SD };
  i2s_set_pin(I2S_NUM_0, &pins);
  pinMode(2, OUTPUT);
}

void loop() {
  int32_t raw[WINDOW];
  size_t got = 0;
  i2s_read(I2S_NUM_0, raw, sizeof(raw), &got, portMAX_DELAY);
  int n = got / sizeof(int32_t);
  if (n < 16) return;

  double sum = 0;
  for (int i = 0; i < n; i++) {
    double v = (double)(raw[i] >> 14) / 131072.0;   // 归一到 -1..1
    sum += v * v;
  }
  double rms = sqrt(sum / n);
  double db  = 20.0 * log10(rms + 1e-9);

  smoothDb = 0.8 * smoothDb + 0.2 * db;             // 一阶平滑

  Serial.print("rms=");
  Serial.print(rms, 4);
  Serial.print("  dBFS=");
  Serial.println(smoothDb, 1);

  int led = (int)constrain((smoothDb + 60) * 255 / 60, 0, 255);
  analogWrite(2, (led * led) / 255);                // 视觉线性
}
''',
  tl=[
    dict(t=300,  serial="麦克风就绪 · 窗口 1024 帧（约 64 ms）", en="Mic ready · 1024-frame window (~64 ms)", part="pinsR", state="on"),
    dict(t=900,  serial="rms=0.0009  dBFS=-60.9 · 安静房间", en="rms=0.0009  dBFS=-60.9 · quiet room"),
    dict(t=1500, serial="rms=0.0182  dBFS=-34.8 · 空调底噪", en="rms=0.0182  dBFS=-34.8 · HVAC noise"),
    dict(t=2100, serial="rms=0.1630  dBFS=-15.8 · 正常说话", en="rms=0.1630  dBFS=-15.8 · normal speech", part="led", state="on"),
    dict(t=2600, serial="rms=0.0041  dBFS=-47.7 · 停顿", en="rms=0.0041  dBFS=-47.7 · pause"),
    dict(t=3050, serial="LED 亮度跟随 dBFS · gamma 校正后线性", en="LED follows dBFS · gamma-corrected"),
  ]),

dict(
  no="41", title="拍手控制：阈值、去抖与误触发",
  titleEn="Clap control: thresholds, debounce, false triggers",
  meta="声音 · 事件检测", metaEn="Audio · event detection",
  group=SND, groupEn=SND_EN,
  wiringHd="接线：麦克风 + 板载 LED", wiringHdEn="Wiring: mic plus on-board LED",
  wiring="接线不变。拍一下手，板载 LED 亮 1 秒——这就是「用声音当按钮」。难点不在亮灯，在<b>让空调噪声和说话都不触发</b>。",
  wiringEn="Same wiring. One clap lights the on-board LED for a second — a sound-triggered button. The hard part is <b>rejecting HVAC noise and speech</b>.",
  pins=[["GPIO33","SD · 采样数据","SD · sample data"],
        ["GPIO26","SCK · 位时钟","SCK · bit clock"],
        ["GPIO2","板载 LED · 触发指示","On-board LED · trigger hint"],
        ["GPIO4","蜂鸣器 · 可选反馈","Buzzer · optional feedback"]],
  overview=[
    ["拍手是<b>短促的宽带脉冲</b>：几百毫秒内能量猛涨又猛落，且高频成分多。说话是持续的低频起伏，空调是平稳噪声。三者可以用「超阈值 + 快速回落 + 高频占比」区分开。",
     "A clap is a <b>short broadband burst</b>: energy spikes for a few hundred milliseconds, then falls, with plenty of high-frequency content. Speech is sustained with low-frequency swings; HVAC is steady noise. Rise time plus high-frequency share separates them."],
    ["最省事的可靠做法是<b>双阈值滞回</b>：能量冲过 <code>TH_HIGH</code> 才算触发，之后必须跌回 <code>TH_LOW</code> 才能再次触发。单阈值会在边界反复触发，串口刷一片。",
     "The cheapest reliable trick is a <b>hysteresis pair</b>: only count a trigger when energy crosses <code>TH_HIGH</code>, and require a fall back under <code>TH_LOW</code> before re-arming. A single threshold re-triggers endlessly at the boundary."],
    ["再加两道保险：<b>最小间隔</b>（比如 250 ms 内不重复触发）和<b>最短持续时间</b>（能量必须保持 30 ms 以上，排除电火花这种单点毛刺）。",
     "Two more guards: a <b>minimum interval</b> (no re-trigger within 250 ms) and a <b>minimum duration</b> (energy must hold for 30 ms, rejecting single-sample spikes)."],
  ],
  points=[
    ["阈值要自动化","别写死 0.3。开机先采 2 秒算底噪，把阈值设成底噪 RMS 的 6–10 倍，换房间也不用改代码。",
     "Derive the threshold","Do not hardcode 0.3. Sample two seconds at boot, then set the threshold at 6–10x the noise RMS — no code change when you move rooms."],
    ["用包络不用瞬时值","每 10 ms 算一次窗口 RMS 形成包络，再在包络上做判断。直接比单个采样点会被一个毛刺骗到。",
     "Judge the envelope","Compute a 10 ms RMS envelope and decide on that. Comparing single samples lets one spike fool you."],
    ["低频要滤掉","加一个一阶高通（或直接用「相邻采样差分的能量」）能压掉风扇和空调的隆隆声，拍手的高频部分保留。",
     "High-pass first","A one-pole high-pass (or energy of the sample difference) kills fan rumble while keeping the clap's highs."],
    ["反馈要即时","触发后立刻给声音或灯光反馈，延迟超过 150 ms 用户就会怀疑「没成功」而再拍一次。",
     "Give instant feedback","Respond within 150 ms or users clap again, convinced it failed."]],
  code=r'''// 第 41 课：拍手触发 LED（滞回 + 去抖）
#include <driver/i2s.h>
#include <math.h>

#define I2S_WS 25
#define I2S_SCK 26
#define I2S_SD 33

float TH_HIGH = 0.10;         // 开机自适应
float TH_LOW  = 0.04;
uint32_t lastHit = 0, riseAt = 0;
bool armed = true;

float windowRms() {
  int32_t raw[256];
  size_t got = 0;
  i2s_read(I2S_NUM_0, raw, sizeof(raw), &got, portMAX_DELAY);
  int n = got / sizeof(int32_t);
  double sum = 0;
  for (int i = 0; i < n; i++) {
    double v = (double)(raw[i] >> 14) / 131072.0;
    sum += v * v;
  }
  return n ? sqrt(sum / n) : 0;
}

void setup() {
  Serial.begin(115200);
  i2s_config_t cfg = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = 16000,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 4, .dma_buf_len = 256, .use_apll = false,
  };
  i2s_driver_install(I2S_NUM_0, &cfg, 0, NULL);
  i2s_pin_config_t pins = { I2S_SCK, I2S_WS, -1, I2S_SD };
  i2s_set_pin(I2S_NUM_0, &pins);
  pinMode(2, OUTPUT);

  double acc = 0;                       // 2 秒底噪
  for (int i = 0; i < 100; i++) acc += windowRms();
  double floorRms = acc / 100;
  TH_HIGH = max(0.03, (float)floorRms * 8);
  TH_LOW  = TH_HIGH * 0.4;
  Serial.printf("noise=%.4f  TH_HIGH=%.3f\n", floorRms, TH_HIGH);
}

void loop() {
  float rms = windowRms();
  uint32_t now = millis();

  if (rms > TH_HIGH) {
    if (riseAt == 0) riseAt = now;                 // 开始上升
  } else {
    if (riseAt && now - riseAt > 30 && armed && now - lastHit > 250) {
      lastHit = now; armed = false;
      digitalWrite(2, HIGH);
      Serial.printf("clap! rms=%.3f\n", rms);
      delay(120);
      digitalWrite(2, LOW);
    }
    riseAt = 0;
  }

  if (rms < TH_LOW) armed = true;                  // 回落到低阈值才重新武装
  delay(10);
}
''',
  tl=[
    dict(t=300,  serial="采集 2 秒底噪 · noise=0.0122", en="Sampling 2 s of noise · noise=0.0122", part="pinsR", state="on"),
    dict(t=900,  serial="阈值自适应 · TH_HIGH=0.098 TH_LOW=0.039", en="Adaptive thresholds · TH_HIGH=0.098 TH_LOW=0.039"),
    dict(t=1500, serial="包络 0.02 · 空调底噪，不触发", en="Envelope 0.02 · HVAC noise, no trigger"),
    dict(t=2000, serial="包络 0.34 · 冲过高阈值", en="Envelope 0.34 · crosses the high threshold"),
    dict(t=2450, serial="clap! rms=0.331 · LED 亮 120 ms", en="clap! rms=0.331 · LED on for 120 ms", part="led", state="on"),
    dict(t=2900, serial="回落到 0.03 · 重新武装，250 ms 冷却", en="Back to 0.03 · re-armed, 250 ms cooldown"),
    dict(t=3350, serial="说话不会触发：持续时间超过 300 ms 被排除", en="Speech rejected: bursts longer than 300 ms are ignored"),
  ]),

dict(
  no="42", title="录音机：把 I2S 采样打包成 WAV",
  titleEn="Recorder: packaging I2S samples into WAV",
  meta="声音 · WAV 与缓冲", metaEn="Audio · WAV and buffering",
  group=SND, groupEn=SND_EN,
  wiringHd="接线：麦克风；要下载就开 Wi-Fi", wiringHdEn="Wiring: mic; enable Wi-Fi to download",
  wiring="接线不变。录 3 秒进内存，再通过 <b>http://板子IP/rec.wav</b> 下载到手机——整条链路都在板子上，不需要 SD 卡。",
  wiringEn="Same wiring. Record three seconds into RAM and download it from <b>http://board-ip/rec.wav</b> — the whole chain lives on the board, no SD card needed.",
  pins=[["GPIO33","SD · 采样数据","SD · sample data"],
        ["GPIO26","SCK · 位时钟","SCK · bit clock"],
        ["GPIO25","WS · 声道选择","WS · word select"],
        ["GPIO2","板载 LED · 录音中","On-board LED · recording"]],
  overview=[
    ["WAV 其实很简单：<b>44 字节文件头 + 裸 PCM 数据</b>。头里写清采样率、位深、声道数、数据长度，播放器就能直接放。很多「录音失败」其实是头里的长度字段填错了。",
     "A WAV file is trivial: <b>a 44-byte header plus raw PCM</b>. The header declares sample rate, bit depth, channel count and data length; get any length field wrong and the file plays as silence or noise."],
    ["数据量要先算：<b>16 kHz × 16 位 × 单声道 = 32 KB/s</b>，3 秒约 96 KB。ESP32 内部 RAM 放得下几秒，长录音必须用 PSRAM 或边录边写 Flash。",
     "Do the arithmetic first: <b>16 kHz x 16 bit x mono = 32 KB/s</b>, so three seconds is ~96 KB. Internal RAM holds a few seconds; longer needs PSRAM or streaming to flash."],
    ["边录边写不能阻塞：I2S DMA 一直在来数据，写 Flash 的几百毫秒里必须有个缓冲接住，否则丢帧、录音出现「咔」的断裂。",
     "Recording must not block: DMA keeps delivering while flash writes take hundreds of milliseconds, so you need a buffer in between or you drop frames and hear clicks."]],
  points=[
    ["头里四个长度要对","RIFF chunk 长度、data 长度、byte rate、block align 互相自洽。先写头再填数据长度是唯一稳妥顺序。",
     "Four header fields must agree","RIFF chunk size, data size, byte rate and block align are interlinked. Write the header first and patch the data size at the end."],
    ["采样率决定音色","16 kHz 够语音，音乐要 44.1 kHz。降采样前先低通，否则高频折叠成刺耳的噪声。",
     "Sample rate sets quality","16 kHz is fine for speech, 44.1 kHz for music. Low-pass before downsampling or highs fold back as harsh aliasing."],
    ["PSRAM 要显式开启","8 MB PSRAM 是 octal 模式，不开启只剩内部 RAM。录音前先确认 <code>ESP.getPsramSize()</code> 不是 0。",
     "Enable PSRAM explicitly","8 MB PSRAM is octal mode and stays off unless enabled. Check <code>ESP.getPsramSize()</code> before recording."],
    ["别在中断里写 Flash","Flash 写入会关中断，和 Wi-Fi、I2S 冲突。用独立任务 + 队列，把写盘放到低优先级任务里。",
     "Never write flash in an ISR","Flash writes disable interrupts and fight Wi-Fi and I2S. Use a task plus a queue at low priority."]],
  code=r'''// 第 42 课：录 3 秒 WAV，用浏览器下载
#include <WiFi.h>
#include <WebServer.h>
#include <driver/i2s.h>

#define RATE 16000
#define SECONDS 3
#define SAMPLES (RATE * SECONDS)

WebServer server(80);
int16_t *pcm;
size_t pcmBytes;
uint8_t header[44];

void writeHeader(uint8_t *h, uint32_t dataLen) {
  uint32_t fileLen = dataLen + 36, rate = RATE;
  uint16_t bits = 16, ch = 1;
  memcpy(h,      "RIFF", 4);
  memcpy(h + 4,  &fileLen, 4);
  memcpy(h + 8,  "WAVEfmt ", 8);
  uint32_t fmtLen = 16;  uint16_t fmt = 1;
  memcpy(h + 16, &fmtLen, 4);
  memcpy(h + 20, &fmt, 2);
  memcpy(h + 22, &ch, 2);
  memcpy(h + 24, &rate, 4);
  uint32_t byteRate = rate * ch * bits / 8;
  memcpy(h + 28, &byteRate, 4);
  uint16_t align = ch * bits / 8;
  memcpy(h + 32, &align, 2);
  memcpy(h + 34, &bits, 2);
  memcpy(h + 36, "data", 4);
  memcpy(h + 40, &dataLen, 4);
}

void setup() {
  Serial.begin(115200);
  i2s_config_t cfg = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8, .dma_buf_len = 256, .use_apll = false,
  };
  i2s_driver_install(I2S_NUM_0, &cfg, 0, NULL);
  i2s_pin_config_t pins = { 26, 25, -1, 33 };
  i2s_set_pin(I2S_NUM_0, &pins);

  pcmBytes = SAMPLES * sizeof(int16_t);
  pcm = (int16_t *)ps_malloc(pcmBytes);          // 大块必须走 PSRAM
  if (!pcm) { Serial.println("no PSRAM"); return; }

  WiFi.begin("YOUR_SSID", "YOUR_PASS");
  while (WiFi.status() != WL_CONNECTED) delay(300);
  Serial.println(WiFi.localIP());

  server.on("/rec.wav", []() {                   // 录完再给，简单可靠
    writeHeader(header, pcmBytes);
    server.setContentLength(sizeof(header) + pcmBytes);
    server.send(200, "audio/wav", "");
    server.sendContent((const char *)header, sizeof(header));
    server.sendContent((const char *)pcm, pcmBytes);
  });
  server.begin();
}

void loop() {
  server.handleClient();

  Serial.println("recording 3s...");
  digitalWrite(2, HIGH);
  size_t done = 0;
  while (done < pcmBytes) {
    size_t got = 0;
    i2s_read(I2S_NUM_0, (uint8_t *)pcm + done, pcmBytes - done, &got, portMAX_DELAY);
    done += got;
  }
  digitalWrite(2, LOW);
  Serial.println("done, open /rec.wav");
  delay(2000);
}
''',
  tl=[
    dict(t=300,  serial="PSRAM 检测 · 8388608 字节可用", en="PSRAM found · 8388608 bytes available", part="module", state="on"),
    dict(t=900,  serial="Wi-Fi 已连接 · http://192.168.1.42", en="Wi-Fi up · http://192.168.1.42"),
    dict(t=1400, serial="开始录音 3 秒 · 16 kHz / 16 bit / 单声道", en="Recording 3 s · 16 kHz / 16 bit / mono", part="led", state="on"),
    dict(t=1900, serial="DMA 持续读入 · 已写 49152 字节", en="DMA streaming · 49152 bytes written"),
    dict(t=2400, serial="录音完成 · 96000 字节 PCM", en="Recording done · 96000 bytes of PCM"),
    dict(t=2850, serial="补写 WAV 头 44 字节 · data 长度 96000", en="WAV header written · data size 96000"),
    dict(t=3300, serial="GET /rec.wav · 浏览器开始下载", en="GET /rec.wav · browser starts the download"),
  ]),

dict(
  no="43", title="频谱：FFT 把声音拆成柱子",
  titleEn="Spectrum: FFT turns sound into bars",
  meta="声音 · FFT 与频段", metaEn="Audio · FFT and bands",
  group=SND, groupEn=SND_EN,
  wiringHd="接线：麦克风；有灯带就接 GPIO15", wiringHdEn="Wiring: mic; add an LED strip on GPIO15",
  wiring="接线不变。没有灯带也能看效果：<b>串口里用字符画频谱</b>，16 个频段从低到高排开，低音在左、高音在右。",
  wiringEn="Same wiring. No strip needed: <b>draw the spectrum with characters on serial</b>, 16 bands from low to high, bass on the left.",
  pins=[["GPIO33","SD · 采样数据","SD · sample data"],
        ["GPIO26","SCK · 位时钟","SCK · bit clock"],
        ["GPIO15","WS2812 灯带 · 可选","WS2812 strip · optional"],
        ["GPIO2","板载 LED · 峰值溢出","On-board LED · clipping hint"]],
  overview=[
    ["波形的横轴是时间，<b>频谱的横轴是频率</b>。FFT 把「一段采样」变成「每个频率上有多少能量」，于是你能看出这是男声、女声、拍手还是 440 Hz 的音叉。",
     "A waveform plots amplitude against time; <b>a spectrum plots it against frequency</b>. The FFT turns a block of samples into energy per frequency, revealing voice pitch, claps, or a 440 Hz fork."],
    ["频率分辨率 = <b>采样率 ÷ 点数</b>。16 kHz 采 1024 点，每格 15.6 Hz；采 4096 点分辨率更高，但延迟从 64 ms 涨到 256 ms。做实时效果要在这两者间取舍。",
     "Resolution is <b>sample rate / FFT size</b>. 16 kHz with 1024 points gives 15.6 Hz per bin; 4096 bins is finer but latency grows from 64 ms to 256 ms. Real-time work trades one for the other."],
    ["人耳对频率是对数感知的，所以显示不能线性分箱，否则 16 个柱子里 15 个都挤在低频。常见做法是按<b>倍频程</b>（1/3 或 1/1）合并频点。",
     "Hearing is logarithmic in frequency, so linear binning wastes the display: 15 of 16 bars crowd the bass. Merge bins by <b>octave</b> (1/3 or full) instead."]],
  points=[
    ["必须加窗","直接截一段做 FFT 会在两端产生突变，频谱泄漏成一片。加 <b>Hann 窗</b>（余弦窗）能压掉旁瓣。",
     "Window before FFT","Cutting a block abruptly leaks energy everywhere. Apply a <b>Hann window</b> to tame the side lobes."],
    ["先去掉直流分量","麦克风的采样有一个固定的中点偏移，不去掉的话 0 Hz 那根柱子永远是满的，掩盖真正的低频。",
     "Remove the DC offset","Mic samples carry a fixed offset; leave it in and the 0 Hz bin saturates and hides real bass."],
    ["用对数幅度","能量跨几个数量级，直接画只有最响的那根看得见。取 <code>20*log10</code> 再映射到高度才对。",
     "Use log magnitude","Energy spans orders of magnitude; linear bars show only the loudest bin. Map <code>20*log10</code> to height."],
    ["别在 loop 里 new","每帧 <code>malloc</code> 会碎片化堆内存，跑几小时就崩。缓冲在 <code>setup()</code> 里一次分配好。",
     "No malloc in loop","Allocating per frame fragments the heap and crashes after hours. Allocate buffers once in <code>setup()</code>."]],
  code=r'''// 第 43 课：16 段频谱，串口字符画
#include <driver/i2s.h>
#include <arduinoFFT.h>

#define N 1024
#define BANDS 16

double vReal[N], vImag[N];
arduinoFFT fft(vReal, vImag, N, 16000);
int bandBin[BANDS + 1];

void setup() {
  Serial.begin(115200);
  i2s_config_t cfg = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = 16000,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8, .dma_buf_len = 256, .use_apll = false,
  };
  i2s_driver_install(I2S_NUM_0, &cfg, 0, NULL);
  i2s_pin_config_t pins = { 26, 25, -1, 33 };
  i2s_set_pin(I2S_NUM_0, &pins);

  // 对数分箱：31 Hz 起，每段 ×1.5
  double f = 31.0;
  for (int b = 0; b <= BANDS; b++) {
    bandBin[b] = (int)(f * N / 16000);
    f *= 1.5;
  }
}

void loop() {
  int32_t raw[N];
  size_t got = 0;
  i2s_read(I2S_NUM_0, raw, sizeof(raw), &got, portMAX_DELAY);
  int n = got / sizeof(int32_t);
  if (n < N) return;

  double mean = 0;
  for (int i = 0; i < N; i++) mean += (double)(raw[i] >> 14);
  mean /= N;

  for (int i = 0; i < N; i++) {
    double hann = 0.5 * (1 - cos(2 * M_PI * i / (N - 1)));
    vReal[i] = ((double)(raw[i] >> 14) - mean) * hann;
    vImag[i] = 0;
  }

  fft.Windowing(FFTWindow::Hann, FFTDirection::Forward);
  fft.Compute(FFTDirection::Forward);
  fft.ComplexToMagnitude();

  for (int b = 0; b < BANDS; b++) {
    double peak = 0;
    for (int k = bandBin[b]; k < bandBin[b + 1] && k < N / 2; k++)
      peak = max(peak, vReal[k]);
    int h = (int)constrain((20 * log10(peak + 1e-6) + 40) * 2, 0, 32);
    for (int i = 0; i < h; i++) Serial.print('#');
    Serial.print(' ');
  }
  Serial.println();
}
''',
  tl=[
    dict(t=300,  serial="FFT 1024 点 · 分辨率 15.6 Hz", en="FFT 1024 points · 15.6 Hz per bin", part="pinsR", state="on"),
    dict(t=900,  serial="去直流 + Hann 窗 · 抑制频谱泄漏", en="DC removed, Hann window applied"),
    dict(t=1400, serial="低频段满格 · 空调隆隆声集中在 60–120 Hz", en="Bass bars full · HVAC rumble at 60–120 Hz"),
    dict(t=1900, serial="中频抬起 · 有人在说话", en="Mid bars rise · speech detected"),
    dict(t=2400, serial="4.1 kHz 处单峰 · 拍手的高频能量", en="Single peak at 4.1 kHz · clap energy"),
    dict(t=2900, serial="峰值 0.42 满量程 · 未削顶", en="Peak at 0.42 full scale · no clipping"),
    dict(t=3350, serial="提示：线性分箱会让 15 根柱子挤在低频", en="Tip: linear binning crams 15 bars into the bass"),
  ]),

dict(
  no="44", title="声音游戏：音高与反应速度",
  titleEn="Sound game: pitch and reaction time",
  meta="声音 · 音高检测", metaEn="Audio · pitch detection",
  group=SND, groupEn=SND_EN,
  wiringHd="接线：麦克风 + 蜂鸣器（可选）", wiringHdEn="Wiring: mic plus optional buzzer",
  wiring="接线不变。玩法：屏幕/串口给出一个目标音（如 440 Hz），你对着麦克风哼，接近目标就亮绿灯，差得远就亮红灯。<b>纯软件，不加硬件也能玩</b>。",
  wiringEn="Same wiring. The game names a target pitch (440 Hz); hum into the mic and the LED turns green when you are close, red when you are off. <b>Software only</b>.",
  pins=[["GPIO33","SD · 采样数据","SD · sample data"],
        ["GPIO26","SCK · 位时钟","SCK · bit clock"],
        ["GPIO2","板载 LED · 命中/偏离","On-board LED · hit or miss"],
        ["GPIO4","蜂鸣器 · 目标音提示","Buzzer · target tone"]],
  overview=[
    ["让板子「听出音高」有两条路：<b>过零率</b>（数一秒内波形穿零的次数，简单但对噪声敏感）和 <b>FFT 峰值</b>（更稳，但需要更长的窗口）。人声哼唱用 FFT 更靠谱。",
     "Two ways to hear pitch: <b>zero-crossing rate</b> (count sign changes per second — simple, noise-sensitive) or the <b>FFT peak</b> (steadier, needs a longer window). For humming, the FFT wins."],
    ["游戏的关键不是测量精度，而是<b>判定手感</b>：允许 ±3% 的容差（约半个半音），并要求连续保持 300 ms 才算命中，否则手抖一下就过关，没有成就感。",
     "What matters is not precision but <b>feel</b>: allow about ±3% (half a semitone) and require it to hold for 300 ms, or a wobble passes instantly and the game feels empty."],
    ["反应速度那部分用状态机：<b>等待 → 出题 → 计时 → 判定</b>。出题时随机目标音，玩家哼对了记录用时，错了扣一次机会，三轮结算。",
     "The reaction part is a state machine: <b>idle → prompt → timing → judge</b>. Random targets, record the time on a hit, lose a life on a miss, score after three rounds."]],
  points=[
    ["过零率只适合单音","一有人说话或背景有音乐，过零率就乱跳。要么加能量门限（只有足够响才判定），要么换 FFT。",
     "Zero-crossing needs a single tone","Speech or music makes ZCR jump. Add an energy gate (judge only when loud enough) or switch to FFT."],
    ["容差用半音","音乐里相邻半音是 5.9%，所以判定容差取 3%（半个半音）刚好：太严唱不准，太松没难度。",
     "Tolerance in semitones","Adjacent semitones differ by 5.9%, so ±3% is the sweet spot: tighter is unplayable, looser is trivial."],
    ["噪声门限必须有","安静时 FFT 峰值随机，会判成各种音高。先要求 RMS 超过底噪 6 倍再开始测音高。",
     "Always gate on energy","In silence the FFT peak is random and reads as arbitrary pitches. Require RMS above 6x noise before measuring."],
    ["反馈要分三层","对了亮绿+上扬音，接近亮黄，完全错亮红。只有对/错两态，玩家不知道自己在靠近还是远离。",
     "Three feedback levels","Green plus rising tone when right, amber when close, red when far. Binary feedback gives no sense of approach."]],
  code=r'''// 第 44 课：哼唱命中目标音（FFT 峰值 + 容差）
#include <driver/i2s.h>
#include <arduinoFFT.h>

#define N 2048
#define RATE 16000.0

double vReal[N], vImag[N];
arduinoFFT fft(vReal, vImag, N, RATE);

float targetHz = 440;
uint32_t holdStart = 0;
bool hit = false;

float dominantHz() {
  int32_t raw[N];
  size_t got = 0;
  i2s_read(I2S_NUM_0, raw, sizeof(raw), &got, portMAX_DELAY);
  if (got < sizeof(int32_t) * N) return 0;

  double rms = 0, mean = 0;
  for (int i = 0; i < N; i++) mean += (raw[i] >> 14);
  mean /= N;
  for (int i = 0; i < N; i++) {
    vReal[i] = (raw[i] >> 14) - mean;
    rms += vReal[i] * vReal[i];
    vImag[i] = 0;
  }
  if (sqrt(rms / N) < 800) return 0;              // 能量门限，太轻不判定

  fft.Windowing(FFTWindow::Blackman, FFTDirection::Forward);
  fft.Compute(FFTDirection::Forward);
  fft.ComplexToMagnitude();

  int best = 0;
  double bestV = 0;
  for (int k = 3; k < N / 2; k++) {               // 跳过直流与极低频
    if (vReal[k] > bestV) { bestV = vReal[k]; best = k; }
  }
  return best * RATE / N;
}

void setup() {
  Serial.begin(115200);
  i2s_config_t cfg = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = (int)RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8, .dma_buf_len = 256, .use_apll = false,
  };
  i2s_driver_install(I2S_NUM_0, &cfg, 0, NULL);
  i2s_pin_config_t pins = { 26, 25, -1, 33 };
  i2s_set_pin(I2S_NUM_0, &pins);
  pinMode(2, OUTPUT);
  Serial.printf("hum %.0f Hz\n", targetHz);
}

void loop() {
  float hz = dominantHz();
  if (hz <= 0) { holdStart = 0; return; }

  float err = fabs(hz - targetHz) / targetHz;
  Serial.printf("heard %.0f Hz  err %.1f%%\n", hz, err * 100);

  if (err < 0.03) {
    if (holdStart == 0) holdStart = millis();
    if (millis() - holdStart > 300 && !hit) {
      hit = true;
      digitalWrite(2, HIGH);
      Serial.println("HIT!");
      delay(400);
      digitalWrite(2, LOW);
      targetHz = 330 + random(0, 6) * 55;         // 换下一题
      Serial.printf("next %.0f Hz\n", targetHz);
      hit = false;
    }
  } else {
    holdStart = 0;
    digitalWrite(2, LOW);
  }
}
''',
  tl=[
    dict(t=300,  serial="目标音 440 Hz · 开始哼唱", en="Target 440 Hz · start humming", part="led", state="on"),
    dict(t=900,  serial="heard 402 Hz  err 8.6% · 偏低", en="heard 402 Hz  err 8.6% · too low"),
    dict(t=1400, serial="heard 431 Hz  err 2.0% · 进入容差", en="heard 431 Hz  err 2.0% · inside tolerance"),
    dict(t=1900, serial="保持 300 ms · 判定命中", en="Held for 300 ms · hit confirmed"),
    dict(t=2350, serial="HIT! · 得分 +1，用时 1.9 s", en="HIT! · score +1, time 1.9 s", part="led", state="on"),
    dict(t=2800, serial="下一题 550 Hz", en="Next target 550 Hz"),
    dict(t=3250, serial="能量低于门限 · 暂停判定（避免静音误判）", en="Below energy gate · judging paused"),
  ]),

dict(
  no="45", title="扬声器：MAX98357A 播放音调",
  titleEn="Speaker: tones from a MAX98357A",
  meta="声音 · I2S 输出", metaEn="Audio · I2S output",
  group=SND, groupEn=SND_EN,
  wiringHd="接线：I2S 功放 + 喇叭", wiringHdEn="Wiring: I2S amp plus speaker",
  wiring="<b>VIN→5V、GND→GND、LRC→GPIO25、BCLK→GPIO26、DIN→GPIO22</b>，喇叭接 <b>+ / −</b> 两端（8Ω 2W 带腔体最好）。功放吃 5V，电流峰值接近 1A，别从 3.3V 取电。",
  wiringEn="<b>VIN→5V, GND→GND, LRC→GPIO25, BCLK→GPIO26, DIN→GPIO22</b>; speaker across <b>+ / −</b> (8 ohm 2 W in an enclosure is ideal). The amp runs on 5V and peaks near 1 A — do not feed it 3.3V.",
  pins=[["GPIO25","LRC · 声道时钟","LRC · frame clock"],
        ["GPIO26","BCLK · 位时钟","BCLK · bit clock"],
        ["GPIO22","DIN · 音频数据","DIN · audio data"],
        ["5V","功放供电（峰值 1A）","Amp supply (1 A peak)"]],
  overview=[
    ["MAX98357A 是<b>数字功放</b>：I2S 进来的是采样值，它内部做 D 类调制直接推喇叭，不需要外部 DAC，也不需要滤波电路。三根信号线，比模拟功放干净得多。",
     "The MAX98357A is a <b>digital amp</b>: I2S samples go in, class-D modulation drives the speaker directly. No external DAC or filter network — three signals and far less noise than analog amps."],
    ["声音是怎么来的？按采样率不断送出<b>正弦波的采样点</b>，频率决定音高，幅度决定音量。440 Hz 的「啦」就是每秒 440 个完整周期，16 kHz 采样率下每个周期约 36 个点。",
     "Sound comes from streaming <b>samples of a sine wave</b> at the sample rate: frequency sets pitch, amplitude sets volume. A 440 Hz tone is 440 cycles per second — about 36 samples per cycle at 16 kHz."],
    ["功放板上的 <b>SD 引脚</b>用电阻分压决定声道与增益：悬空是单声道平均，接 GND 是左声道，接 VDD 是右声道。增益靠 SD 上的电阻档位选，接错会「没声」或「爆音」。",
     "The <b>SD pin</b> on the breakout selects channel and gain via a resistor divider: floating averages both channels, GND is left, VDD is right. Gain comes from the resistor value; the wrong one gives silence or clipping."]],
  points=[
    ["喇叭阻抗要对","8Ω 最稳，4Ω 更响但电流翻倍。2W 喇叭配 5V 供电刚好，别用 0.5W 小喇叭开到最大。",
     "Match speaker impedance","8 ohm is safest; 4 ohm is louder but doubles current. A 2 W speaker with 5 V is the sweet spot; do not max out a tiny 0.5 W one."],
    ["音量靠幅度不靠采样率","减少采样点的数值就是调小音量，改采样率只会变调（像快进的磁带）。",
     "Volume is amplitude, not rate","Scaling sample values changes loudness; changing the sample rate changes pitch, like a tape sped up."],
    ["静音要送 0 不能停时钟","I2S 一旦停时钟，功放会进入 idle 并可能「啪」一声。持续送 0 才是干净静音。",
     "Send zeros to mute","Stopping the clock puts the amp in idle and often causes a pop. Keep streaming zeros instead."],
    ["共地且别和麦克风同一条线","功放电流大，和麦克风共用地线会引入嗡声。电源线分开走，地只在一点汇合。",
     "Separate amp and mic power","The amp draws big current; sharing a ground wire with the mic injects hum. Run separate power leads and join grounds at one point."]],
  code=r'''// 第 45 课：正弦波音阶（do re mi fa sol）
#include <driver/i2s.h>
#include <math.h>

#define RATE 16000
#define I2S_BCLK 26
#define I2S_LRC  25
#define I2S_DIN  22

float notes[] = { 262, 294, 330, 349, 392 };   // C4 D4 E4 F4 G4

void writeTone(float hz, int ms, float amp) {
  const int chunk = 256;
  int16_t buf[chunk];
  uint32_t total = (uint32_t)RATE * ms / 1000;
  uint32_t phase = 0, step = (uint32_t)(hz * 4294967296.0 / RATE);

  for (uint32_t done = 0; done < total; done += chunk) {
    for (int i = 0; i < chunk; i++) {
      phase += step;
      buf[i] = (int16_t)(sinf(phase * 6.2831853f / 4294967296.0f) * amp);
    }
    size_t written = 0;
    i2s_write(I2S_NUM_0, buf, sizeof(buf), &written, portMAX_DELAY);
  }
}

void setup() {
  Serial.begin(115200);
  i2s_config_t cfg = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
    .sample_rate = RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 6, .dma_buf_len = 256, .use_apll = false,
  };
  i2s_driver_install(I2S_NUM_0, &cfg, 0, NULL);
  i2s_pin_config_t pins = {
    .bck_io_num = I2S_BCLK,
    .ws_io_num = I2S_LRC,
    .data_out_num = I2S_DIN,
    .data_in_num = -1,
  };
  i2s_set_pin(I2S_NUM_0, &pins);
  Serial.println("playing scale");
}

void loop() {
  for (float hz : notes) {
    Serial.printf("%.0f Hz\n", hz);
    writeTone(hz, 350, 6000);
    writeTone(0, 60, 0);              // 音符之间留一点静音
  }
  delay(800);
}
''',
  tl=[
    dict(t=300,  serial="I2S 输出初始化 · 16 kHz / 16 bit", en="I2S TX init · 16 kHz / 16-bit", part="pinsR", state="on"),
    dict(t=800,  serial="262 Hz · do（C4）", en="262 Hz · do (C4)"),
    dict(t=1400, serial="294 Hz · re（D4）", en="294 Hz · re (D4)"),
    dict(t=2000, serial="330 Hz · mi（E4）", en="330 Hz · mi (E4)"),
    dict(t=2600, serial="349 Hz · fa（F4）", en="349 Hz · fa (F4)"),
    dict(t=3200, serial="392 Hz · sol（G4）", en="392 Hz · sol (G4)"),
    dict(t=3700, serial="功放静音送 0 · 停时钟会「啪」一声", en="Amp muted with zeros · stopping the clock pops", part="pinsR", state="off"),
  ]),

dict(
  no="46", title="语音特效：实时变声与回声",
  titleEn="Voice effects: real-time pitch and echo",
  meta="声音 · 全双工 I2S", metaEn="Audio · full-duplex I2S",
  group=SND, groupEn=SND_EN,
  wiringHd="接线：麦克风 + 功放同时接", wiringHdEn="Wiring: mic and amp together",
  wiring="麦克风照第 39 课接（<b>WS=25 SCK=26 SD=33</b>），功放照第 45 课接但把时钟换成 <b>LRC=27 BCLK=32 DIN=22</b>——两套 I2S 各用一组引脚，互不干扰。喇叭别正对麦克风。",
  wiringEn="Mic as in lesson 39 (<b>WS=25 SCK=26 SD=33</b>); amp as in lesson 45 but on <b>LRC=27 BCLK=32 DIN=22</b> so the two I2S buses do not collide. Keep the speaker away from the mic.",
  pins=[["GPIO33","麦克风 SD","Mic data in"],
        ["GPIO25","麦克风 WS","Mic word select"],
        ["GPIO27","功放 LRC","Amp frame clock"],
        ["GPIO22","功放 DIN","Amp data out"]],
  overview=[
    ["把输入和输出接在同一条链路上，就是<b>实时环回</b>：读到一块采样，处理完立刻送出去要保证延迟低于 30 ms，否则你听到自己的声音会明显滞后，说话就结巴了。",
     "Wiring input to output gives a <b>real-time loopback</b>: read a block, process it, send it — with latency under about 30 ms, or you hear yourself late and start stuttering."],
    ["回声最简单：开一个<b>环形缓冲</b>，把当前采样加上「N 毫秒前的采样 × 衰减系数」。延迟长度就是缓冲大小，衰减决定回声几次后消失。",
     "Echo is easy: keep a <b>ring buffer</b> and add the sample from N milliseconds ago scaled by a decay factor. Buffer length sets the delay, the factor sets how fast it fades."],
    ["变声听起来复杂，本质是<b>重采样</b>：把读指针走得比写指针快，就变尖（升调），走得慢就变低沉。代价是音长会变——真正的「变调不变速」需要相位声码器，MCU 上很少做。",
     "Pitch shifting is really <b>resampling</b>: advance the read pointer faster than the write pointer to sound higher and slower to sound lower. Duration changes too; true pitch-shift-without-tempo needs a phase vocoder, rare on an MCU."]],
  points=[
    ["块大小定延迟","256 点 @16 kHz = 16 ms，加上 DMA 缓冲约 30 ms。要更低就用 128 点，但处理时间也更紧。",
     "Block size sets latency","256 samples at 16 kHz is 16 ms; with DMA you land near 30 ms. Use 128 for lower, but processing time gets tight."],
    ["别做浮点重运算","<code>sin</code> 每个采样都算会跑不动。查表 + 线性插值，或直接用整数移位的重采样。",
     "Avoid per-sample floats","A <code>sin</code> per sample will not keep up. Use a lookup table with interpolation, or integer resampling."],
    ["回声要限幅","电流+回声叠加会超过 ±32767 直接削顶，听起来像破音。混完做一次 <code>constrain</code> 或软限幅。",
     "Limit after mixing","Direct plus echo easily exceeds ±32767 and clips audibly. Constrain or soft-limit after mixing."],
    ["防啸叫是物理问题","喇叭对着麦克风，任何增益都会啸叫。先解决摆位和外壳，再调代码。",
     "Feedback is physical","A speaker facing the mic howls at any gain. Fix placement and enclosure before touching code."]],
  code=r'''// 第 46 课：环回 + 回声 + 变调
#include <driver/i2s.h>

#define RATE 16000
#define BLOCK 256
#define MAX_DELAY (RATE / 2)          // 最多 500 ms 回声

int16_t ring[MAX_DELAY];
uint32_t wpos = 0;

// 0.0 = 原调, 1.5 = 升五度, 0.7 = 变低沉
float pitchRatio = 1.5;
float echoMix = 0.45;
int   echoMs  = 220;

void setupBus(i2s_port_t port, bool tx, int bck, int ws, int data) {
  i2s_config_t cfg = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | (tx ? I2S_MODE_TX : I2S_MODE_RX)),
    .sample_rate = RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 4, .dma_buf_len = 128, .use_apll = false,
  };
  i2s_driver_install(port, &cfg, 0, NULL);
  i2s_pin_config_t pins = {
    .bck_io_num = bck,
    .ws_io_num = ws,
    .data_out_num = tx ? data : -1,
    .data_in_num = tx ? -1 : data,
  };
  i2s_set_pin(port, &pins);
}

void setup() {
  Serial.begin(115200);
  setupBus(I2S_NUM_0, false, 26, 25, 33);   // 麦克风
  setupBus(I2S_NUM_1, true,  32, 27, 22);   // 功放
  Serial.printf("ratio %.2f  echo %d ms\n", pitchRatio, echoMs);
}

void loop() {
  int16_t in[BLOCK], out[BLOCK];
  size_t got = 0;
  i2s_read(I2S_NUM_0, in, sizeof(in), &got, portMAX_DELAY);
  int n = got / sizeof(int16_t);
  if (n == 0) return;

  int echoSamples = (int)(echoMs * RATE / 1000.0);

  for (int i = 0; i < n; i++) {
    // 变调：读指针按比例前进（最近的历史样本）
    int back = (int)(i * (pitchRatio - 1.0f));
    int idx  = (wpos + MAX_DELAY - back) % MAX_DELAY;
    int16_t shifted = ring[idx];

    ring[wpos] = in[i];
    wpos = (wpos + 1) % MAX_DELAY;

    int eIdx = (wpos + MAX_DELAY - echoSamples) % MAX_DELAY;
    int32_t mixed = shifted + (int32_t)(ring[eIdx] * echoMix);
    out[i] = (int16_t)constrain(mixed, -32768, 32767);
  }

  size_t written = 0;
  i2s_write(I2S_NUM_1, out, n * sizeof(int16_t), &written, portMAX_DELAY);
}
''',
  tl=[
    dict(t=300,  serial="麦克风 I2S0 + 功放 I2S1 · 双总线就绪", en="Mic on I2S0, amp on I2S1 · both ready", part="pinsR", state="on"),
    dict(t=900,  serial="环回延迟约 28 ms · 低于人耳察觉阈值", en="Loopback latency about 28 ms · below perception"),
    dict(t=1400, serial="ratio 1.50 · 变调升高五度", en="ratio 1.50 · shifted up a fifth"),
    dict(t=1900, serial="echo 220 ms · mix 0.45", en="echo 220 ms · mix 0.45"),
    dict(t=2400, serial="输出峰值 0.82 满量程 · 未削顶", en="Output peak 0.82 full scale · no clipping"),
    dict(t=2900, serial="ratio 0.70 · 低沉效果", en="ratio 0.70 · lower voice"),
    dict(t=3350, serial="提醒：喇叭正对麦克风会啸叫", en="Reminder: speaker facing the mic will howl"),
  ]),
]
