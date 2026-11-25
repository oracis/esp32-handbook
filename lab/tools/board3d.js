/* ESP32 DevKitC-1 真 3D 交互模型（three.js）
   构建：esbuild 打成 IIFE 内联进 lab/index.html，运行时无外部请求。
   设计：保留原 SVG 作为状态锚点/降级视图，本模块在其上叠加 WebGL。 */
import {
  Scene, WebGLRenderer, PerspectiveCamera, Group, Mesh, BoxGeometry, CylinderGeometry,
  SphereGeometry, PlaneGeometry, MeshStandardMaterial, MeshBasicMaterial, CanvasTexture,
  AmbientLight, HemisphereLight, DirectionalLight, GridHelper, Raycaster, Vector2,
  Color, SRGBColorSpace, ACESFilmicToneMapping, MathUtils
} from 'three';

const SVG_CX = 380, SVG_CY = 230, SCALE = 100;
const P = (sx, sy) => [(sx - SVG_CX) / SCALE, (sy - SVG_CY) / SCALE];

const TEAL = 0x2fc4b2, BLUE = 0x4da6ff, RED = 0xff5a4e;
const BOARD_Y = 0.08;                 // PCB 顶面高度
const PARTS = ['pcb', 'usb', 'module', 'usbchip', 'vreg', 'xtal', 'en', 'boot',
               'pwrled', 'led', 'pinsL', 'pinsR'];

let renderer, scene, camera, box, canvas, grid;
let yaw = 0.26, pitch = 0.60, distance = 11.4, baseDistance = 11.4;
let drag = null, moved = false, pickables = [], groups = {}, materials = {};
let glows = {}, raycaster = new Raycaster(), ndc = new Vector2();
let cbPick = null, pwmLevel = -1, ready = false, fail = '';
let ro = null;

function tex(text, opt){
  opt = opt || {};
  const c = document.createElement('canvas');
  c.width = opt.w || 512; c.height = opt.h || 128;
  const g = c.getContext('2d');
  if (opt.bg){ g.fillStyle = opt.bg; g.fillRect(0, 0, c.width, c.height); }
  g.clearRect && opt.clear && g.clearRect(0, 0, c.width, c.height);
  g.fillStyle = opt.color || '#d7e3dc';
  g.textAlign = 'center'; g.textBaseline = 'middle';
  g.font = (opt.bold === false ? '' : 'bold ') + (opt.size || 44) + 'px ' +
           (opt.mono === false ? 'sans-serif' : 'ui-monospace,Consolas,monospace');
  g.fillText(text, c.width / 2, c.height / 2);
  const t = new CanvasTexture(c);
  t.colorSpace = SRGBColorSpace;
  t.anisotropy = 4;
  return t;
}

function silk(text, x, z, w, h, opt){
  const m = new Mesh(
    new PlaneGeometry(w, h),
    new MeshBasicMaterial({ map: tex(text, opt), transparent: true, depthWrite: false,
                            opacity: (opt && opt.opacity) || 0.9 })
  );
  m.rotation.x = -Math.PI / 2;
  m.position.set(x, BOARD_Y + 0.006, z);
  return m;
}

function partMesh(geo, mat, part, x, y, z){
  const m = new Mesh(geo, mat);
  m.position.set(x, y, z);
  m.castShadow = true; m.receiveShadow = true;
  m.userData.part = part;
  pickables.push(m);
  return m;
}

function group(name){
  const g = new Group();
  g.name = name;
  groups[name] = g;
  scene.add(g);
  return g;
}

function std(color, opt){
  return new MeshStandardMaterial(Object.assign({
    color: color, metalness: 0.25, roughness: 0.62
  }, opt || {}));
}

function antennaTexture(){
  const c = document.createElement('canvas');
  c.width = 256; c.height = 512;
  const g = c.getContext('2d');
  g.fillStyle = '#7d858d'; g.fillRect(0, 0, 256, 512);
  g.strokeStyle = '#4d555d'; g.lineWidth = 3;
  for (let i = 0; i < 9; i++){
    const y = 32 + i * 54;
    g.beginPath(); g.moveTo(20, y); g.lineTo(236, y); g.stroke();
  }
  g.strokeStyle = '#5a626a'; g.lineWidth = 4;
  for (let x = 36; x <= 220; x += 26){
    g.beginPath(); g.moveTo(x, 20); g.lineTo(x, 492); g.stroke();
  }
  const t = new CanvasTexture(c);
  t.colorSpace = SRGBColorSpace;
  return t;
}

function buildBoard(){
  /* ---- PCB ---- */
  const g = group('pcb');
  const pcb = new Mesh(new BoxGeometry(6.4, 0.16, 3.68), std(0x12301f, { roughness: 0.84 }));
  pcb.userData.part = 'pcb'; pickables.push(pcb);
  g.add(pcb);
  // 板边高光 + 四角定位孔
  const edge = new Mesh(new BoxGeometry(6.42, 0.025, 3.70),
    new MeshBasicMaterial({ color: 0x1d4a31, wireframe: true, transparent: true, opacity: 0.55 }));
  edge.position.y = 0.085; g.add(edge);
  [[-2.93, -1.55], [2.93, -1.55], [-2.93, 1.55], [2.93, 1.55]].forEach(([x, z]) => {
    const h = new Mesh(new CylinderGeometry(0.075, 0.075, 0.2, 16),
      std(0xa9a684, { metalness: 0.7, roughness: 0.4 }));
    h.position.set(x, 0, z); g.add(h);
  });
  g.add(silk('ESP32 DevKitC-1', -2.35, -1.55, 2.1, 0.24,
             { size: 42, color: '#e6f4ec', opacity: 0.9 }));
  g.add(silk('5V  3.3V  GND  I2C  SPI  UART', -1.55, 1.66, 3.4, 0.18,
             { size: 34, color: '#9fc4ab', opacity: 0.72 }));
  g.add(silk('USB-UART   TX/RX', -2.08, 1.33, 1.8, 0.16,
             { size: 32, color: '#86a893', opacity: 0.6 }));

  /* ---- USB Type-C ---- */
  const u = group('usb');
  const [ux, uz] = P(47, 234);
  u.add(partMesh(new BoxGeometry(0.62, 0.36, 0.96),
    std(0x8a939d, { metalness: 0.9, roughness: 0.24 }), 'usb', ux, 0.05, uz));
  u.add(partMesh(new BoxGeometry(0.42, 0.18, 0.66),
    std(0x2b333b, { metalness: 0.5, roughness: 0.6 }), 'usb', ux - 0.26, 0.05, uz));
  const usbTip = partMesh(new BoxGeometry(0.08, 0.20, 0.54),
    std(0x3a4149, { metalness: 0.6 }), 'usb', ux - 0.38, 0.05, uz);
  u.add(usbTip);
  u.add(silk('USB-C', ux, uz + 0.68, 0.7, 0.16,
             { size: 40, color: '#c9d6cf' }));

  /* ---- ESP32-WROOM 模组 ---- */
  const mo = group('module');
  const [mx, mz] = P(254, 200);
  mo.add(partMesh(new BoxGeometry(2.08, 0.05, 1.80),
    std(0x1b2520, { roughness: 0.8 }), 'module', mx, 0.105, mz));
  const shieldMat = std(0xb9c0c8, { metalness: 0.78, roughness: 0.34 });
  materials.module = shieldMat;
  mo.add(partMesh(new BoxGeometry(1.22, 0.16, 1.64), shieldMat,
    'module', mx - 0.42, 0.19, mz));
  const antMat = new MeshStandardMaterial({ map: antennaTexture(), metalness: 0.55,
    roughness: 0.42, emissive: new Color(TEAL), emissiveIntensity: 0 });
  materials.antenna = antMat;
  mo.add(partMesh(new BoxGeometry(0.60, 0.10, 1.64), antMat, 'module', mx + 0.58, 0.16, mz));
  const label = new Mesh(new PlaneGeometry(1.05, 0.20),
    new MeshBasicMaterial({ map: tex('ESP32-WROOM', { size: 46, color: '#485059' }),
                            transparent: true }));
  label.rotation.x = -Math.PI / 2;
  label.position.set(mx - 0.42, 0.274, mz - 0.52);
  mo.add(label);
  for (let i = 0; i < 15; i++){
    const pin = new Mesh(new BoxGeometry(0.035, 0.045, 0.035),
      std(0xd8cfa0, { metalness: 0.85, roughness: 0.28 }));
    pin.position.set(mx - 0.98, 0.10, mz - 0.78 + i * 0.112);
    mo.add(pin);
  }

  /* ---- USB 转串口芯片 ---- */
  const c = group('usbchip');
  const [cx, cz] = P(198, 343);
  const chipMat = std(0x223044, { roughness: 0.66 });
  materials.usbchip = chipMat;
  c.add(partMesh(new BoxGeometry(0.96, 0.10, 0.62), chipMat, 'usbchip', cx, 0.13, cz));
  c.add(silk('CH340 / CP210x', cx, cz - 0.13, 0.86, 0.15,
             { size: 34, color: '#9fb0c4' }));
  c.add(silk('USB-UART', cx, cz + 0.15, 0.76, 0.13,
             { size: 28, color: '#7890a8' }));

  /* ---- LDO 稳压 ---- */
  const v = group('vreg');
  const [vx, vz] = P(305, 343);
  v.add(partMesh(new BoxGeometry(0.78, 0.11, 0.62),
    std(0x223044, { roughness: 0.66 }), 'vreg', vx, 0.135, vz));
  v.add(silk('LDO 5V>3V3', vx, vz, 0.72, 0.14,
             { size: 32, color: '#9fb0c4' }));

  /* ---- 晶振 ---- */
  const x = group('xtal');
  const [xx, xz] = P(393, 343);
  x.add(partMesh(new CylinderGeometry(0.29, 0.29, 0.12, 28),
    std(0xb7c1ca, { metalness: 0.87, roughness: 0.25 }), 'xtal', xx, 0.14, xz));
  x.add(partMesh(new CylinderGeometry(0.20, 0.20, 0.126, 28),
    std(0x929ca6, { metalness: 0.85, roughness: 0.3 }), 'xtal', xx, 0.143, xz));
  x.add(silk('26MHz', xx, xz + 0.46, 0.72, 0.14,
             { size: 30, color: '#9fc4ab' }));

  /* ---- EN / BOOT 按键 ---- */
  function button(name, sx, sy, caption){
    const gg = group(name);
    const [bx, bz] = P(sx, sy);
    gg.add(partMesh(new BoxGeometry(0.56, 0.10, 0.56),
      std(0x2a3340, { metalness: 0.3, roughness: 0.6 }), name, bx, 0.13, bz));
    const capMat = std(0x1d2732, { metalness: 0.4, roughness: 0.5 });
    materials[name] = capMat;
    const cap = partMesh(new CylinderGeometry(0.13, 0.13, 0.10, 20), capMat,
      name, bx, 0.22, bz);
    gg.userData.cap = cap;
    gg.userData.capY = 0.22;
    gg.add(cap);
    gg.add(silk(caption, bx, bz + 0.47, 0.68, 0.15,
               { size: 34, color: '#c8d8cd' }));
  }
  button('en', 484, 340, 'EN');
  button('boot', 568, 340, 'BOOT');

  /* ---- LED ---- */
  function led(name, sx, sy, color, caption){
    const gg = group(name);
    const [lx, lz] = P(sx, sy);
    gg.add(partMesh(new CylinderGeometry(0.115, 0.115, 0.045, 18),
      std(0x111d27, { roughness: 0.7 }), name, lx, 0.103, lz));
    const mat = new MeshStandardMaterial({
      color: color, emissive: new Color(color), emissiveIntensity: name === 'pwrled' ? 1.5 : 0.04,
      metalness: 0.1, roughness: 0.35
    });
    materials[name] = mat;
    gg.add(partMesh(new SphereGeometry(0.075, 16, 12), mat, name, lx, 0.155, lz));
    const glowMat = new MeshBasicMaterial({ color: color, transparent: true,
      opacity: name === 'pwrled' ? 0.28 : 0, depthWrite: false });
    const glow = new Mesh(new SphereGeometry(0.19, 16, 12), glowMat);
    glow.position.set(lx, 0.16, lz); gg.add(glow);
    glows[name] = glowMat;
    gg.add(silk(caption, lx, lz + 0.36, 0.72, 0.15,
               { size: 32, color: name === 'pwrled' ? '#e4a49f' : '#9ecbea' }));
  }
  led('pwrled', 462, 136, RED, 'PWR');
  led('led', 546, 136, BLUE, 'GPIO2');

  /* ---- 双侧排针 ---- */
  function pins(name, sx, label){
    const gg = group(name);
    const [px, pz] = P(sx, 230);
    gg.add(partMesh(new BoxGeometry(0.22, 0.10, 3.30),
      std(0x1a222a, { roughness: 0.72 }), name, px, 0.13, pz));
    for (let i = 0; i < 15; i++){
      const z = pz - 1.54 + i * 0.22;
      const pin = partMesh(new CylinderGeometry(0.052, 0.052, 0.28, 8),
        std(0xd8cfa0, { metalness: 0.86, roughness: 0.3 }), name, px, 0.30, z);
      gg.add(pin);
    }
    gg.add(silk(label, px, pz - 1.83, 0.46, 0.16,
               { size: 36, color: '#c9d6cf' }));
  }
  pins('pinsL', 95, 'J1');
  pins('pinsR', 665, 'J3');

  /* ---- 地面网格 ---- */
  grid = new GridHelper(18, 18, 0x1f5138, 0x163a28);
  grid.position.y = -0.46;
  grid.material.transparent = true;
  grid.material.opacity = 0.42;
  scene.add(grid);
}

function updateCamera(){
  const cp = Math.cos(pitch);
  camera.position.set(distance * Math.sin(yaw) * cp,
                      distance * Math.sin(pitch),
                      distance * Math.cos(yaw) * cp);
  camera.lookAt(0, 0, 0);
}

function resize(){
  if (!ready || !box) return;
  const w = Math.max(box.clientWidth, 1), h = Math.max(box.clientHeight, 1);
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}

function hit(ev){
  const r = canvas.getBoundingClientRect();
  ndc.set(((ev.clientX - r.left) / r.width) * 2 - 1,
          -((ev.clientY - r.top) / r.height) * 2 + 1);
  raycaster.setFromCamera(ndc, camera);
  const arr = raycaster.intersectObjects(pickables, false);
  return arr.length ? arr[0].object.userData.part : null;
}

function bindInput(){
  canvas.addEventListener('pointerdown', ev => {
    drag = { x: ev.clientX, y: ev.clientY, yaw: yaw, pitch: pitch };
    moved = false;
    try { canvas.setPointerCapture(ev.pointerId); } catch (e) { /* 合成事件无 pointerId */ }
    canvas.style.cursor = 'grabbing';
  });
  canvas.addEventListener('pointermove', ev => {
    if (drag){
      const dx = ev.clientX - drag.x, dy = ev.clientY - drag.y;
      if (Math.abs(dx) + Math.abs(dy) > 4) moved = true;
      yaw = drag.yaw + dx * 0.007;
      pitch = MathUtils.clamp(drag.pitch + dy * 0.005, 0.12, 1.42);
      updateCamera();
    } else canvas.style.cursor = hit(ev) ? 'pointer' : 'grab';
  });
  canvas.addEventListener('pointerup', ev => {
    canvas.style.cursor = 'grab';
    if (drag && !moved){
      const part = hit(ev);
      if (part && cbPick) cbPick(part, ev);
    }
    drag = null;
  });
  canvas.addEventListener('pointercancel', () => { drag = null; canvas.style.cursor = 'grab'; });
  // 不要让点击冒泡到 #svgBox 的「关闭说明」处理器
  canvas.addEventListener('click', ev => ev.stopPropagation());
  canvas.addEventListener('wheel', ev => {
    ev.preventDefault();
    // 复用页面原有缩放通道：SVG 的 handler 会同步 3D 相机
    document.getElementById('board').dispatchEvent(new WheelEvent('wheel', {
      deltaY: ev.deltaY, clientX: ev.clientX, clientY: ev.clientY,
      bubbles: true, cancelable: true
    }));
  }, { passive: false });
  canvas.addEventListener('dblclick', () => {
    document.getElementById('board').dispatchEvent(new MouseEvent('dblclick', { bubbles: true }));
  });
  ro = new ResizeObserver(resize);
  ro.observe(box);
}

function animate(){
  if (!ready) return;
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

function init(container){
  try{
    box = container;
    canvas = document.createElement('canvas');
    canvas.id = 'board3d';
    canvas.setAttribute('aria-label', 'ESP32 DevKitC-1 3D model');
    box.appendChild(canvas);
    renderer = new WebGLRenderer({ canvas: canvas, antialias: true, alpha: false,
                                   powerPreference: 'high-performance' });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.outputColorSpace = SRGBColorSpace;
    renderer.toneMapping = ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.15;
    scene = new Scene();
    scene.background = new Color(0x0a1c15);
    camera = new PerspectiveCamera(35, 1, 0.1, 100);
    scene.add(new AmbientLight(0xffffff, 0.45));
    scene.add(new HemisphereLight(0xa9d8ff, 0x0a1a12, 1.35));
    const key = new DirectionalLight(0xffffff, 2.0); key.position.set(4, 8, 5); scene.add(key);
    const fill = new DirectionalLight(0x66c0ff, 0.85); fill.position.set(-5, 3, -4); scene.add(fill);
    buildBoard();
    updateCamera();
    bindInput();
    resize();
    ready = true;
    animate();
  } catch (e){
    fail = (e && e.message) || String(e);
    document.body.classList.add('no3d');
    if (canvas) canvas.remove();
  }
  return ready;
}

function setPart(part, on){
  if (!ready) return;
  const m = materials[part];
  if (m && m.emissive) m.emissiveIntensity = on ? (part === 'led' ? 2.4 : 0.38) : (part === 'led' ? 0.04 : 0);
  if (part === 'led' && pwmLevel < 0 && glows.led) glows.led.opacity = on ? 0.55 : 0;
  if (m && (part === 'usbchip' || part === 'module') && m.emissive)
    m.emissiveIntensity = on ? 0.42 : 0;
  if (part === 'module' && materials.antenna)
    materials.antenna.emissiveIntensity = on ? 0.35 : 0;
}

function setPwm(level){
  if (!ready) return;
  pwmLevel = level;
  if (level < 0){ setPart('led', false); return; }
  const v = MathUtils.clamp(level, 0, 1);
  materials.led.emissiveIntensity = 0.04 + 2.35 * v;
  glows.led.opacity = 0.04 + 0.52 * v;
}

function pulse(part){
  if (!ready) return;
  const m = materials[part];
  if (!m || !m.emissive) return;
  m.emissiveIntensity = 0.75;
  clearTimeout(m._pulse);
  m._pulse = setTimeout(() => { m.emissiveIntensity = 0; }, 180);
}

function pressBoot(){
  if (!ready) return;
  const g = groups.boot, cap = g && g.userData.cap;
  if (!cap) return;
  cap.position.y = g.userData.capY - 0.055;
  if (materials.boot) materials.boot.emissiveIntensity = 0.55;
  clearTimeout(cap._up);
  cap._up = setTimeout(() => {
    cap.position.y = g.userData.capY;
    if (materials.boot) materials.boot.emissiveIntensity = 0;
  }, 200);
}

function clearAll(){
  if (!ready) return;
  pwmLevel = -1;
  PARTS.forEach(p => { if (p !== 'pwrled') setPart(p, false); });
  if (materials.antenna) materials.antenna.emissiveIntensity = 0;
}

function zoom(k){
  if (!ready) return;
  distance = MathUtils.clamp(baseDistance / Math.max(k, 0.01), 3.6, 17);
  updateCamera();
}

function resetView(){
  if (!ready) return;
  yaw = 0.26; pitch = 0.60; distance = baseDistance;
  updateCamera();
}

function stats(){
  return { ready: ready, fail: fail, renderer: !!renderer,
           webgl2: !!(renderer && renderer.capabilities && renderer.capabilities.isWebGL2),
           meshes: pickables.length, parts: PARTS.length,
           distance: +distance.toFixed(3), yaw: +yaw.toFixed(3), pitch: +pitch.toFixed(3),
           ledLevel: ready ? +materials.led.emissiveIntensity.toFixed(3) : 0,
           pwmLevel: pwmLevel };
}

window.Board3D = {
  init: init,
  ready: () => ready,
  setPart: setPart,
  setPwm: setPwm,
  pulse: pulse,
  pressBoot: pressBoot,
  clearAll: clearAll,
  zoom: zoom,
  resetView: resetView,
  onPick: function (cb){ cbPick = cb; },
  pickPart: function (part){ if (cbPick) cbPick(part, null); },
  stats: stats
};
