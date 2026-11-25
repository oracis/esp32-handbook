/* ESP32 工作台：浏览器内运行的 Arduino C 子集解释器（零外部依赖）
   目标不是完整 C++，而是让学习者写的 sketch 真正在浏览器里“跑”起来：
   setup()/loop()、变量、if/else、for/while、函数、算术与比较、注释，
   以及 ESP32 常用 API（digitalWrite/analogWrite/digitalRead/Serial/delay/millis）。

   构建：esbuild 打成 IIFE 内联进 lab/index.html。
   对外 API：window.Workbench = { tokenize, parse, compile, VM }
*/
'use strict';

/* ============ 1. 词法分析 ============ */
const KEYWORDS = new Set(['int','long','float','double','bool','boolean','char','byte','unsigned',
  'void','const','if','else','for','while','return','break','continue','true','false','HIGH','LOW',
  'INPUT','OUTPUT','INPUT_PULLUP','setup','loop']);
const TYPES = new Set(['int','long','float','double','bool','boolean','char','byte','unsigned']);

function tokenize(src){
  const out = [];
  let i = 0;
  const n = src.length;
  const isIdStart = c => /[A-Za-z_]/.test(c);
  const isId = c => /[A-Za-z0-9_]/.test(c);
  const isNum = c => /[0-9.]/.test(c);
  while (i < n){
    const c = src[i];
    if (/\s/.test(c)){ i++; continue; }
    if (c === '/' && src[i+1] === '/'){ i += 2; while (i < n && src[i] !== '\n') i++; continue; }
    if (c === '/' && src[i+1] === '*'){ i += 2; while (i < n && !(src[i] === '*' && src[i+1] === '/')) i++; i += 2; continue; }
    if (c === '#'){ while (i < n && src[i] !== '\n') i++; continue; }              // #include / #define
    if (c === '"' || c === "'"){
      const q = c; let s = ''; i++;
      while (i < n && src[i] !== q){
        if (src[i] === '\\' && i + 1 < n){ s += src[i+1]; i += 2; }
        else { s += src[i]; i++; }
      }
      i++; out.push({ t:'str', v:s }); continue;
    }
    if (isNum(c) || (c === '.' && isNum(src[i+1]))){
      let s = '';
      if (c === '0' && (src[i+1] === 'x' || src[i+1] === 'X')){
        s += '0x'; i += 2;
        while (i < n && /[0-9a-fA-F]/.test(src[i])) s += src[i++];
      } else {
        while (i < n && isNum(src[i])) s += src[i++];
      }
      out.push({ t:'num', v:s }); continue;
    }
    if (isIdStart(c)){
      let s = '';
      while (i < n && isId(src[i])) s += src[i++];
      out.push({ t: KEYWORDS.has(s) ? 'kw' : 'id', v:s }); continue;
    }
    const two = src.substr(i, 2);
    if (['==','!=','<=','>=','&&','||','++','--','+=','-=','*=','/=','<<','>>'].indexOf(two) >= 0){
      out.push({ t:'op', v:two }); i += 2; continue;
    }
    out.push({ t:'op', v:c }); i++;
  }
  out.push({ t:'eof', v:'' });
  return out;
}

/* ============ 2. 语法分析（递归下降 → AST） ============ */
function parse(src){
  const toks = tokenize(src);
  let p = 0;
  const peek = (k=0) => toks[p + k] || { t:'eof', v:'' };
  const next = () => toks[p++];
  const eat = v => { if (peek().v === v){ p++; return true; } return false; };
  const expect = v => { if (!eat(v)) throw new Error('期待 ' + v + '，实际遇到 ' + JSON.stringify(peek().v)); };

  function program(){
    const body = [];
    while (peek().t !== 'eof') body.push(statement());
    return { k:'prog', body };
  }
  function declaration(){
    // const/unsigned 修饰 + 类型 + 变量名 [= expr]，支持 int a=1,b=2;
    let isConst = false;
    while (peek().v === 'const' || peek().v === 'unsigned' || MODIFIERS.has(peek().v)){
      if (peek().v === 'const') isConst = true;
      next();
    }
    if (!TYPES.has(peek().v)) throw new Error('未知类型 ' + JSON.stringify(peek().v));
    next();
    const decls = [];
    do {
      const name = next();
      if (name.t !== 'id') throw new Error('变量名非法 ' + JSON.stringify(name.v));
      let init = null;
      if (eat('=')) init = expression();
      decls.push({ name:name.v, init });
    } while (eat(','));
    expect(';');
    return { k:'decl', isConst, decls };
  }
  const MODIFIERS = new Set(['static','volatile','register','extern']);
  const isTypeStart = () => ['const','unsigned','void'].indexOf(peek().v) >= 0 ||
                            TYPES.has(peek().v) || MODIFIERS.has(peek().v);
  function skipModifiers(){
    while (peek().v === 'const' || peek().v === 'unsigned' || MODIFIERS.has(peek().v)) next();
  }
  function statement(){
    if (peek().v === '{') return block();
    if (peek().v === 'if') return ifStmt();
    if (peek().v === 'for') return forStmt();
    if (peek().v === 'while') return whileStmt();
    if (peek().v === 'return'){
      next(); const e = peek().v === ';' ? null : expression(); expect(';');
      return { k:'return', e };
    }
    if (peek().v === 'break'){ next(); expect(';'); return { k:'break' }; }
    if (peek().v === 'continue'){ next(); expect(';'); return { k:'continue' }; }
    // 函数定义优先：void setup() / int add(int a,int b)。名字可能是 id 或 kw(setup/loop)。
    {
      let q = 0;
      while (['const','unsigned','void'].indexOf(toks[p+q] && toks[p+q].v) >= 0 ||
             TYPES.has(toks[p+q] && toks[p+q].v) || MODIFIERS.has(toks[p+q] && toks[p+q].v)) q++;
      const nm = toks[p+q], op = toks[p+q+1];
      // q>0 表示确实吃掉了类型/修饰符关键字；否则 foo() 只是普通调用表达式
      if (q > 0 && nm && (nm.t === 'id' || nm.t === 'kw') && op && op.v === '(') return funcDef();
    }
    if (isTypeStart()) return declaration();
    // 表达式语句
    const e = expression();
    expect(';');
    return { k:'expr', e };
  }
  function funcDef(){
    skipModifiers();
    if (!eat('void')) next();                     // 返回类型（已由 skipModifiers 去掉 const/unsigned）
    const name = next().v;
    expect('(');
    const params = [];
    if (peek().v !== ')'){
      do {
        while (peek().v === 'const' || peek().v === 'unsigned' || TYPES.has(peek().v) || MODIFIERS.has(peek().v)) next();
        params.push(next().v);
      } while (eat(','));
    }
    expect(')');
    const body = block();
    return { k:'func', name, params, body };
  }
  function block(){
    expect('{');
    const body = [];
    while (peek().v !== '}'){
      if (peek().t === 'eof') throw new Error('缺少右花括号 }');
      body.push(statement());
    }
    expect('}');
    return { k:'block', body };
  }
  function ifStmt(){
    next(); expect('(');
    const cond = expression(); expect(')');
    const then = statement();
    let alt = null;
    if (eat('else')) alt = statement();
    return { k:'if', cond, then, alt };
  }
  function forStmt(){
    next(); expect('(');
    let init;
    if (peek().v === ';'){ next(); init = null; }
    else if (peek().v === 'const' || TYPES.has(peek().v) || peek().v === 'unsigned'){
      init = declaration();
    } else { init = { k:'expr', e:expression() }; expect(';'); }
    const test = peek().v === ';' ? null : expression(); expect(';');
    const update = peek().v === ')' ? null : expression(); expect(')');
    const body = statement();
    return { k:'for', init, test, update, body };
  }
  function whileStmt(){
    next(); expect('(');
    const test = expression(); expect(')');
    return { k:'while', test, body:statement() };
  }
  /* 优先级：赋值 < 或 || < && < 比较 < 加减 < 乘除 < 一元 < 后缀 < 主 */
  function expression(){ return assignment(); }
  function assignment(){
    const l = orExpr();
    if (['=','+=','-=','*=','/='].indexOf(peek().v) >= 0){
      const op = next().v;
      const r = assignment();
      if (l.k !== 'var') throw new Error('赋值目标必须是变量');
      return { k:'assign', name:l.name, op, e:r };
    }
    return l;
  }
  function orExpr(){
    let l = andExpr();
    while (eat('||')) l = { k:'bin', op:'||', a:l, b:andExpr() };
    return l;
  }
  function andExpr(){
    let l = cmpExpr();
    while (eat('&&')) l = { k:'bin', op:'&&', a:l, b:cmpExpr() };
    return l;
  }
  function cmpExpr(){
    let l = addExpr();
    while (['==','!=','<=','>=','<','>'].indexOf(peek().v) >= 0){
      const op = next().v;
      l = { k:'bin', op, a:l, b:addExpr() };
    }
    return l;
  }
  function addExpr(){
    let l = mulExpr();
    while (peek().v === '+' || peek().v === '-'){
      const op = next().v;
      l = { k:'bin', op, a:l, b:mulExpr() };
    }
    return l;
  }
  function mulExpr(){
    let l = unary();
    while (['*','/','%'].indexOf(peek().v) >= 0){
      const op = next().v;
      l = { k:'bin', op, a:l, b:unary() };
    }
    return l;
  }
  function unary(){
    if (peek().v === '-' || peek().v === '!' || peek().v === '+'){
      const op = next().v;
      return { k:'un', op, e:unary() };
    }
    return postfix();
  }
  function postfix(){
    let e = primary();
    for (;;){
      if (eat('++')){ e = { k:'post', op:'++', e }; continue; }
      if (eat('--')){ e = { k:'post', op:'--', e }; continue; }
      break;
    }
    return e;
  }
  function primary(){
    const t = next();
    if (t.v === '('){ const e = expression(); expect(')'); return e; }
    if (t.t === 'num') return { k:'lit', v: t.v.indexOf('0x') === 0 ? parseInt(t.v, 16) : parseFloat(t.v) };
    if (t.t === 'str') return { k:'lit', v:t.v };
    if (t.v === 'true' || t.v === 'HIGH') return { k:'lit', v:1 };
    if (t.v === 'false' || t.v === 'LOW') return { k:'lit', v:0 };
    if (t.v === 'INPUT' || t.v === 'OUTPUT' || t.v === 'INPUT_PULLUP') return { k:'lit', v:t.v };
    if (t.t === 'id' || t.v === 'setup' || t.v === 'loop'){
      let name = t.v;
      while (eat('.')) name += '.' + next().v;   // Serial.println 等成员调用
      if (eat('(')){
        const args = [];
        if (peek().v !== ')'){
          do { args.push(expression()); } while (eat(','));
        }
        expect(')');
        return { k:'call', name:name, args };
      }
      return { k:'var', name:name };
    }
    throw new Error('无法解析的符号 ' + JSON.stringify(t.v));
  }
  return program();
}

/* ============ 3. 执行器 ============ */
const BUILTINS = new Set(['digitalWrite','digitalRead','analogWrite','analogRead','pinMode',
  'Serial','delay','millis','micros','map','constrain','min','max','abs','random','randomSeed',
  'print','println','tone','noTone','begin','write','read']);

function compile(src, host, opts){
  opts = opts || {};
  const ast = parse(src);
  const funcs = {};
  ast.body.forEach(n => { if (n.k === 'func') funcs[n.name] = n; });
  if (!funcs.setup && !funcs.loop) throw new Error('缺少 setup() 或 loop() 函数');

  let steps = 0;
  const maxSteps = opts.maxSteps || 200000;
  const scope = Object.create(null);          // 全局变量池：setup 与 loop 共享
  let aborted = false;
  const tick = () => {
    if (aborted) throw { __abort:true };
    if (++steps > maxSteps) throw new Error('执行步数超限（可能有死循环）');
  };
  const now = () => host.millis ? host.millis() : Date.now();

  function call(name, args){
    if (funcs[name]) return invoke(funcs[name], args);
    const fn = host.api && host.api[name];
    if (typeof fn === 'function') return fn.apply(null, args);
    if (BUILTINS.has(name)) return 0;             // 未接线的 API 静默返回
    throw new Error('未定义的函数 ' + name + '()');
  }

  function invoke(f, args){
    const env = scope;                           // 所有函数共享全局池，模拟 Arduino 全局量
    const saved = Object.create(null);
    f.params.forEach((pn, i) => { saved[pn] = env[pn]; env[pn] = args[i]; });

    // 控制流用异常传递：break / continue / return 都是可抛出的信号对象
    const exec = nodes => {
      for (const node of nodes){
        if (aborted) throw { __abort:true };
        switch (node.k){
          case 'decl':
            node.decls.forEach(d => { tick(); env[d.name] = d.init ? evalNode(d.init, env) : 0; });
            break;
          case 'expr': tick(); evalNode(node.e, env); break;
          case 'assign': {
            tick();
            const rv = evalNode(node.e, env);
            let nv = rv;
            const old = env[node.name] || 0;
            if (node.op === '+=') nv = old + rv;
            else if (node.op === '-=') nv = old - rv;
            else if (node.op === '*=') nv = old * rv;
            else if (node.op === '/=') nv = bdiv(old, rv);
            env[node.name] = nv;
            break;
          }
          case 'if':
            tick();
            if (evalNode(node.cond, env)) runStmt(node.then, env);
            else if (node.alt) runStmt(node.alt, env);
            break;
          case 'for': {
            tick();
            if (node.init){
              if (node.init.k === 'decl') node.init.decls.forEach(d => { env[d.name] = d.init ? evalNode(d.init, env) : 0; });
              else evalNode(node.init.e, env);
            }
            let guard = 0;
            while (!aborted && (!node.test || evalNode(node.test, env))){
              tick();
              try { runStmt(node.body, env); }
              catch (sig){ if (sig && sig.__break) break; if (!(sig && sig.__continue)) throw sig; }
              if (node.update) evalNode(node.update, env);
              if (++guard > 200000) throw new Error('for 循环次数超限');
            }
            break;
          }
          case 'while': {
            tick(); let guard = 0;
            while (!aborted && evalNode(node.test, env)){
              tick();
              try { runStmt(node.body, env); }
              catch (sig){ if (sig && sig.__break) break; if (!(sig && sig.__continue)) throw sig; }
              if (++guard > 200000) throw new Error('while 循环次数超限');
            }
            break;
          }
          case 'return': throw { __return:true, v: node.e ? evalNode(node.e, env) : undefined };
          case 'break': throw { __break:true };
          case 'continue': throw { __continue:true };
          case 'func': break;                      // 嵌套函数定义：忽略（顶层已收集）
          default: break;
        }
      }
    };
    const runStmt = (s, ev) => { if (s.k === 'block') exec(s.body); else exec([s]); };
    let result;
    try { exec(f.body.body); }
    catch (sig){ if (sig && sig.__return) result = sig.v; else throw sig; }
    finally { f.params.forEach(pn => { if (saved[pn] === undefined) delete env[pn]; else env[pn] = saved[pn]; }); }
    return result;
  }
  // 顶层全局变量初始化（如 int counter=0;），只执行一次
  (function initGlobals(){
    const initNodes = ast.body.filter(n => n.k === 'decl' || n.k === 'assign' || n.k === 'expr');
    try { execNodesAtTop(initNodes); } catch (e) { throw e; }
  })();
  function execNodesAtTop(nodes){
    // 复用 invoke 的执行体：造一个零参函数包住顶层语句
    const wrapper = { params: [], body: { k:'block', body: nodes } };
    invoke(wrapper, []);
  }
  const bdiv = (a, b) => b === 0 ? 0 : a / b;

  function evalNode(node, env){
    if (node === null || node === undefined) return 0;
    switch (node.k){
      case 'lit': return node.v;
      case 'var': {
        if (node.name in env) return env[node.name];
        if (node.name in scope) return scope[node.name];
        return 0;
      }
      case 'bin': {
        if (node.op === '&&'){ const a = evalNode(node.a, env); return a && evalNode(node.b, env) ? 1 : 0; }
        if (node.op === '||'){ const a = evalNode(node.a, env); return a || evalNode(node.b, env) ? 1 : 0; }
        const a = evalNode(node.a, env);
        const b = evalNode(node.b, env);
        switch (node.op){
          case '+': return (typeof a === 'string' || typeof b === 'string') ? String(a) + String(b) : a + b;
          case '-': return a - b; case '*': return a * b; case '/': return bdiv(a, b);
          case '%': return b === 0 ? 0 : a % b;
          case '==': return a == b ? 1 : 0; case '!=': return a != b ? 1 : 0;
          case '<': return a < b ? 1 : 0; case '>': return a > b ? 1 : 0;
          case '<=': return a <= b ? 1 : 0; case '>=': return a >= b ? 1 : 0;
          default: return 0;
        }
      }
      case 'un': {
        const v = evalNode(node.e, env);
        if (node.op === '-') return -v;
        if (node.op === '!') return v ? 0 : 1;
        return v;
      }
      case 'post': {
        const old = evalNode(node.e, env);
        if (node.e.k === 'var'){
          const cur = (node.e.name in env) ? env[node.e.name] : (scope[node.e.name] || 0);
          env[node.e.name] = old + (node.op === '++' ? 1 : -1);
          void cur;
        }
        return old;
      }
      case 'assign': {
        const rv = evalNode(node.e, env);
        let nv = rv;
        const old = env[node.name] || 0;
        if (node.op === '+=') nv = old + rv;
        else if (node.op === '-=') nv = old - rv;
        else if (node.op === '*=') nv = old * rv;
        else if (node.op === '/=') nv = bdiv(old, rv);
        env[node.name] = nv;
        return nv;
      }
      case 'call': {
        tick();
        const args = node.args.map(a => evalNode(a, env));
        if (node.name === 'map'){
          const [x, a1, a2, b1, b2] = args;
          return b1 + (x - a1) * (b2 - b1) / ((a2 - a1) || 1);
        }
        if (node.name === 'constrain') return Math.max(args[1], Math.min(args[2], args[0]));
        if (node.name === 'min') return Math.min(args[0], args[1]);
        if (node.name === 'max') return Math.max(args[0], args[1]);
        if (node.name === 'abs') return Math.abs(args[0]);
        if (node.name === 'millis' || node.name === 'micros') return node.name === 'micros' ? now() * 1000 : now();
        if (node.name === 'random'){
          if (args.length === 1) return Math.floor(Math.random() * args[0]);
          return Math.floor(args[0] + Math.random() * (args[1] - args[0]));
        }
        if (node.name === 'randomSeed') return 0;
        if (node.name === 'String' || node.name === 'String.') return String(args[0] === undefined ? '' : args[0]);
        if (node.name === 'delay'){
          if (aborted) throw { __abort:true };
          host.delay(Math.max(0, Math.min(3000, +args[0] || 0)));
          if (aborted) throw { __abort:true };
          return 0;
        }
        if (node.name.indexOf('Serial.') === 0){
          const m = node.name.split('.')[1];
          if (m === 'println') return host.api.Serial.println(args.length ? args[0] : '');
          if (m === 'print') return host.api.Serial.print(args.length ? args[0] : '');
          if (m === 'begin') return 0;
        }
        return call(node.name, args);
      }
      default: return 0;
    }
  }

  return {
    runSetup(){ if (funcs.setup) invoke(funcs.setup, []); },
    runLoopOnce(){ if (funcs.loop) invoke(funcs.loop, []); },
    abort(){ aborted = true; },
    isAborted(){ return aborted; },
    steps(){ return steps; },
    hasLoop(){ return !!funcs.loop; }
  };
}

window.Workbench = { tokenize, parse, compile };
