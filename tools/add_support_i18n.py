# -*- coding: utf-8 -*-
"""支持区块 / 页脚的 9 语言文案（人工写定，不经机器翻译）。

机器翻译在这批文案上反复出问题：俄语混入汉字、西班牙语法律声明整条丢失
回退英文、把「名词性陈述」译成祈使句。对外门面文案改为手写，确定性强。

写回 window.I18N.b（en）与 window.I18N.MULTI[lang].b。
幂等：直接覆盖这些键，可反复执行。
用法：python tools/add_support_i18n.py [--dry]
"""
import io
import json
import re
import sys

SITE = "index.html"
LANGS = ["zh-TW", "ja", "ko", "es", "pt", "fr", "ru"]

EN = {
    "SP1": "Support this project",
    "SP2": "No ads, no login wall, no locked lessons — one person keeps this handbook going. "
           "If it saved you a few evenings of trial and error, either of the two things below counts.",
    "SP3": "Star the repo",
    "SP4": "It costs nothing, but it decides whether the next person searching for ESP32 finds "
           "this page. Star it and new revisions show up on your GitHub home feed too.",
    "SP5": "Open GitHub",
    "SP6": "Ask, report, request",
    "SP7": "A wrong figure, a dead link, or a result that doesn't match your bench — just say so. "
           "Every report becomes the next revision.",
    "SP8": "Open Discussions",
    "SP9": "<b>More content</b> — more ESP32 scenarios turned into experiments you can click "
           "through and skip.",
    "SP10": "<b>Keeping the site online</b> — domain, hosting, and a page light enough to open on "
            "a weak network.",
    "SP11": "Leave a tip",
    "SP12": "The handbook is free and ad-free. If it saved you one bad night of debugging, a tip is "
            "welcome — Ko-fi from abroad, or the QR code from inside China.",
    "SP13": "Open Ko-fi",
    "SP14": "WeChat QR · or long-press to scan",
    "SP15": "Tipping is entirely optional and changes nothing about what gets covered. On a phone "
            "you can long-press the code to scan it; readers outside China can use Ko-fi.",
    "FT1": "Back to top",
    "FT2": "Lab",
    "FT3": "Support",
    "FT4": "Feedback",
    "FT5": "ESP32 Field Guide",
    "FT6": "static single page, no external dependencies",
    "FT7": "An unofficial personal project, not affiliated with Espressif. Electrical specs and "
           "part numbers follow the official datasheet.",
    "FT8": "Boards change, the criterion does not: first ask what it has to connect to, then how fast.",
}

ZH_TW = {
    "SP1": "支持這個專案",
    "SP2": "這本手冊沒有廣告、沒有登入牆、也沒有課程鎖，由一個人整理和維護。如果它幫你省下了幾個晚上的試錯，下面兩件事都算支持。",
    "SP3": "給倉庫點一個 Star",
    "SP4": "不花錢，但決定下一個搜 ESP32 的人能不能找到這裡。點過 Star 之後，每次修訂也會出現在你的 GitHub 首頁。",
    "SP5": "去 GitHub",
    "SP6": "提問、回報錯誤、催更",
    "SP7": "表格裡的參數不對、連結失效，或者你的實測結果不一樣，直接說。每條回饋都會變成下一次修訂。",
    "SP8": "去 Discussions",
    "SP9": "<b>更多內容</b> —— 把更多 ESP32 場景做成可以點、可以跳過的實驗。",
    "SP10": "<b>站點一直線上</b> —— 網域、託管，以及弱網也能開啟的體積。",
    "SP11": "打賞支持",
    "SP12": "手冊免費、也沒有廣告。如果它幫你少踩了一個坑，可以打賞支持：海外走 Ko-fi，國內掃碼都行。",
    "SP13": "去 Ko-fi",
    "SP14": "微信掃碼 · 或長按識別",
    "SP15": "打賞完全自願，不影響內容的取捨。手機端可以長按二維碼識別，海外讀者用 Ko-fi。",
    "FT1": "回到頂部",
    "FT2": "實驗區",
    "FT3": "支持",
    "FT4": "回饋",
    "FT5": "ESP32 全景手冊",
    "FT6": "靜態單頁，無外部依賴",
    "FT7": "非官方個人專案，與 Espressif 無隸屬關係；電氣參數與型號命名以官方 datasheet 為準。",
    "FT8": "板子會換，判據不變：先問「要連什麼」，再問「要多快」。",
}

JA = {
    "SP1": "このプロジェクトを支援する",
    "SP2": "このマニュアルには広告もログイン画面も講義のロックもありません。ひとりで整理し、更新しています。何晩分かの試行錯誤が減ったなら、下のどちらでも支援になります。",
    "SP3": "リポジトリに Star を付ける",
    "SP4": "お金はかかりませんが、次に ESP32 を検索した人がここに辿り着けるかが変わります。Star を付けると、更新もあなたの GitHub ホームに表示されます。",
    "SP5": "GitHub へ",
    "SP6": "質問・誤りの報告・更新のリクエスト",
    "SP7": "表の数値が違う、リンクが切れている、手元の実測と合わない——どれも直接知らせてください。フィードバックは次の改訂に入ります。",
    "SP8": "Discussions へ",
    "SP9": "<b>コンテンツの追加</b> —— より多くの ESP32 シナリオを、クリックして飛ばせる実験にします。",
    "SP10": "<b>サイトを開いたままに</b> —— ドメイン、ホスティング、そして弱い回線でも開ける軽さ。",
    "SP11": "投げ銭で支援",
    "SP12": "このマニュアルは無料で、広告もありません。遠回りをひとつ減らせたなら、投げ銭で支援していただけると助かります。海外からは Ko-fi、中国国内からは QR コードでどうぞ。",
    "SP13": "Ko-fi へ",
    "SP14": "WeChat QR ・ 長押しで読み取り",
    "SP15": "投げ銭はまったく任意で、内容の取捨には影響しません。スマートフォンでは QR コードを長押しして読み取れます。中国国外の方は Ko-fi をご利用ください。",
    "FT1": "ページ先頭へ",
    "FT2": "実験エリア",
    "FT3": "サポート",
    "FT4": "フィードバック",
    "FT5": "ESP32 Panorama マニュアル",
    "FT6": "静的単一ページ、外部依存なし",
    "FT7": "個人による非公式プロジェクトです。Espressif とは関係ありません。電気的仕様と型番は公式 datasheet に従ってください。",
    "FT8": "ボードは変わっても、判断の基準は変わりません。まず「何をつなぐか」、次に「どれだけ速く」。",
}

KO = {
    "SP1": "이 프로젝트 후원하기",
    "SP2": "이 매뉴얼에는 광고도, 로그인 장벽도, 강의 잠금도 없습니다. 한 사람이 정리하고 관리합니다. 며칠 밤의 시행착오를 줄여 주었다면, 아래 두 가지 모두 후원입니다.",
    "SP3": "저장소에 Star 남기기",
    "SP4": "비용은 없지만, 다음에 ESP32를 검색하는 사람이 이 페이지를 찾을 수 있는지가 여기서 갈립니다. Star를 남기면 새 개정판도 GitHub 홈에 표시됩니다.",
    "SP5": "GitHub 열기",
    "SP6": "질문, 오류 신고, 강의 요청",
    "SP7": "표의 수치가 틀렸거나, 링크가 죽었거나, 직접 측정한 값이 다르면 그냥 알려 주세요. 모든 피드백은 다음 개정판에 반영됩니다.",
    "SP8": "Discussions 열기",
    "SP9": "<b>콘텐츠 추가</b> —— 더 많은 ESP32 상황을 클릭하고 건너뛸 수 있는 실험으로 만듭니다.",
    "SP10": "<b>사이트 계속 열어 두기</b> —— 도메인, 호스팅, 그리고 약한 네트워크에서도 열리는 가벼움.",
    "SP11": "후원으로 응원하기",
    "SP12": "이 매뉴얼은 무료이고 광고도 없습니다. 시행착오를 하나라도 줄였다면 후원으로 응원해 주세요. 해외에서는 Ko-fi, 중국 내에서는 QR 코드로 하시면 됩니다.",
    "SP13": "Ko-fi 열기",
    "SP14": "위챗 QR · 길게 눌러 인식",
    "SP15": "후원은 전적으로 자발적이며 콘텐츠 선택에는 영향을 주지 않습니다. 휴대폰에서는 QR을 길게 눌러 인식할 수 있고, 해외 독자는 Ko-fi를 이용하면 됩니다.",
    "FT1": "맨 위로",
    "FT2": "실습 구역",
    "FT3": "후원",
    "FT4": "피드백",
    "FT5": "ESP32 파노라마 매뉴얼",
    "FT6": "정적 단일 페이지, 외부 의존성 없음",
    "FT7": "개인이 만든 비공식 프로젝트이며 Espressif와 무관합니다. 전기 사양과 모델명은 공식 datasheet를 따릅니다.",
    "FT8": "보드는 바뀌어도 판단 기준은 그대로입니다. 먼저 무엇을 연결할지, 다음에 얼마나 빠를지를 묻습니다.",
}

ES = {
    "SP1": "Apoya este proyecto",
    "SP2": "Este manual no tiene anuncios, ni muro de inicio de sesión, ni cursos bloqueados; lo recopila y mantiene una sola persona. Si te ha ahorrado unas cuantas noches de prueba y error, cualquiera de las dos cosas de abajo cuenta como apoyo.",
    "SP3": "Dale una Star al repositorio",
    "SP4": "No cuesta dinero, pero decide si la próxima persona que busque ESP32 podrá encontrar este sitio. Después de pulsar Star, cada revisión también aparecerá en tu página de inicio de GitHub.",
    "SP5": "Ir a GitHub",
    "SP6": "Preguntas, errores, peticiones",
    "SP7": "Un dato equivocado, un enlace roto o un resultado que no coincide con tu placa: dilo. Cada aviso se convierte en la próxima revisión.",
    "SP8": "Ir a Discussions",
    "SP9": "<b>Más contenido</b> — convertir más escenarios de ESP32 en experimentos en los que se puede hacer clic y que se pueden omitir.",
    "SP10": "<b>El sitio siempre está en línea</b> — el dominio, el alojamiento y un peso que carga incluso con mala conexión.",
    "SP11": "Dejar una propina",
    "SP12": "El manual es gratis y no tiene anuncios. Si te ahorró una noche de depuración, puedes dejar una propina: Ko-fi desde el extranjero, o el código QR desde China.",
    "SP13": "Ir a Ko-fi",
    "SP14": "QR de WeChat · mantén pulsado para escanear",
    "SP15": "Las donaciones son totalmente voluntarias y no cambian lo que se publica. En el móvil puedes mantener pulsado el código para escanearlo; fuera de China, usa Ko-fi.",
    "FT1": "Volver arriba",
    "FT2": "Zona de prácticas",
    "FT3": "Apoyo",
    "FT4": "Comentarios",
    "FT5": "Manual ESP32 Panorama",
    "FT6": "página estática única, sin dependencias externas",
    "FT7": "Proyecto personal no oficial, sin afiliación con Espressif; los parámetros eléctricos y la denominación de los modelos se rigen por el datasheet oficial.",
    "FT8": "Las placas cambian, el criterio no: primero qué hay que conectar, después a qué velocidad.",
}

PT = {
    "SP1": "Apoie este projeto",
    "SP2": "Este manual não tem anúncios, nem tela de login, nem aulas bloqueadas; é mantido por uma só pessoa. Se economizou algumas noites de tentativa e erro, qualquer uma das duas opções abaixo conta.",
    "SP3": "Dê uma Star ao repositório",
    "SP4": "Não custa nada, mas decide se a próxima pessoa que pesquisar por ESP32 conseguirá encontrar este lugar. Depois de clicar em Star, cada revisão também aparecerá na sua página inicial do GitHub.",
    "SP5": "Ir para o GitHub",
    "SP6": "Perguntas, erros, pedidos",
    "SP7": "Um dado errado, um link quebrado ou um resultado que não bate com a sua placa: diga. Cada aviso vira a próxima revisão.",
    "SP8": "Ir para Discussions",
    "SP9": "<b>Mais conteúdo</b> — transformar mais cenários de ESP32 em experimentos clicáveis e que podem ser pulados.",
    "SP10": "<b>O site está sempre online</b> — domínio, hospedagem e um tamanho que abre mesmo com internet fraca.",
    "SP11": "Deixar uma gorjeta",
    "SP12": "O manual é gratuito e sem anúncios. Se ele poupou uma noite de depuração, você pode deixar uma gorjeta: Ko-fi de fora do país, ou o código QR de dentro da China.",
    "SP13": "Ir para o Ko-fi",
    "SP14": "QR do WeChat · toque e segure para escanear",
    "SP15": "As doações são totalmente voluntárias e não mudam o que é publicado. No celular, toque e segure o código para escaneá-lo; fora da China, use o Ko-fi.",
    "FT1": "Voltar ao topo",
    "FT2": "Área de prática",
    "FT3": "Apoio",
    "FT4": "Feedback",
    "FT5": "Manual Panorama ESP32",
    "FT6": "página estática única, sem dependências externas",
    "FT7": "Projeto pessoal não oficial, sem afiliação com a Espressif; para parâmetros elétricos e nomenclatura de modelos, prevalece o datasheet oficial.",
    "FT8": "As placas mudam, o critério não: primeiro o que precisa ser conectado, depois a que velocidade.",
}

FR = {
    "SP1": "Soutenez ce projet",
    "SP2": "Ce manuel n'a ni publicité, ni mur de connexion, ni cours verrouillés ; il est compilé et maintenu par une seule personne. S'il vous a épargné quelques soirées d'essais et d'erreurs, les deux gestes ci-dessous comptent comme un soutien.",
    "SP3": "Mettre une Star au dépôt",
    "SP4": "C'est gratuit, mais cela détermine si la prochaine personne qui cherchera ESP32 pourra trouver ce site. Après avoir cliqué sur Star, chaque révision apparaîtra aussi sur votre page d'accueil GitHub.",
    "SP5": "Aller sur GitHub",
    "SP6": "Questions, erreurs, demandes",
    "SP7": "Une valeur fausse, un lien mort, ou un résultat qui ne correspond pas à votre carte : dites-le. Chaque retour devient la révision suivante.",
    "SP8": "Aller sur Discussions",
    "SP9": "<b>Plus de contenu</b> — transformer davantage de scénarios ESP32 en expériences cliquables et que l'on peut passer.",
    "SP10": "<b>Le site reste en ligne</b> — domaine, hébergement et un poids qui s'ouvre même en réseau faible.",
    "SP11": "Laisser un pourboire",
    "SP12": "Le manuel est gratuit et sans publicité. S'il vous a épargné une soirée de débogage, un pourboire est le bienvenu : Ko-fi depuis l'étranger, ou le code QR depuis la Chine.",
    "SP13": "Aller sur Ko-fi",
    "SP14": "QR WeChat · appui long pour scanner",
    "SP15": "Les dons sont entièrement facultatifs et ne changent rien à ce qui est publié. Sur mobile, un appui long sur le code permet de le scanner ; hors de Chine, utilisez Ko-fi.",
    "FT1": "Retour en haut",
    "FT2": "Zone d'essais",
    "FT3": "Soutien",
    "FT4": "Retour",
    "FT5": "Manuel Panorama ESP32",
    "FT6": "page statique unique, sans dépendance externe",
    "FT7": "Projet personnel non officiel, sans affiliation avec Espressif ; pour les paramètres électriques et la nomenclature des modèles, seul le datasheet officiel fait foi.",
    "FT8": "Les cartes changent, le critère non : d'abord ce qu'il faut connecter, ensuite à quelle vitesse.",
}

RU = {
    "SP1": "Поддержать проект",
    "SP2": "В этом руководстве нет рекламы, нет обязательной регистрации и нет закрытых курсов — оно собрано и поддерживается одним человеком. Если оно сэкономило вам несколько вечеров проб и ошибок, то любое из двух действий ниже станет поддержкой.",
    "SP3": "Поставить Star репозиторию",
    "SP4": "Это бесплатно, но от этого зависит, сможет ли следующий человек, который ищет ESP32, найти этот сайт. После того как вы поставите Star, каждое обновление будет появляться и на вашей главной странице GitHub.",
    "SP5": "Открыть GitHub",
    "SP6": "Вопросы, ошибки, пожелания",
    "SP7": "Неверное значение в таблице, битая ссылка или результат, который не совпал с вашей платой, — просто напишите. Каждое замечание становится следующей правкой.",
    "SP8": "Открыть Discussions",
    "SP9": "<b>Больше материалов</b> — превращаем больше сценариев с ESP32 в эксперименты, которые можно запустить кликом и пропустить.",
    "SP10": "<b>Сайт всегда онлайн</b> — домен, хостинг и размер, позволяющий открывать его даже при слабом интернете.",
    "SP11": "Оставить донат",
    "SP12": "Руководство бесплатное и без рекламы. Если оно избавило вас от вечера отладки, можно оставить донат: из-за границы — через Ko-fi, из Китая — по QR-коду.",
    "SP13": "Перейти на Ko-fi",
    "SP14": "QR-код WeChat · удерживайте для сканирования",
    "SP15": "Донат полностью добровольный и не влияет на то, что попадает в руководство. На телефоне код можно отсканировать долгим нажатием; из-за пределов Китая используйте Ko-fi.",
    "FT1": "Наверх",
    "FT2": "Практикум",
    "FT3": "Поддержка",
    "FT4": "Обратная связь",
    "FT5": "Руководство по ESP32 Panorama",
    "FT6": "одна статическая страница, без внешних зависимостей",
    "FT7": "Неофициальный личный проект, не связан с Espressif. Электрические параметры и названия моделей — по официальному datasheet.",
    "FT8": "Платы меняются, критерий — нет: сначала что нужно подключить, потом как быстро.",
}

BY_LANG = {"zh-TW": ZH_TW, "ja": JA, "ko": KO, "es": ES, "pt": PT, "fr": FR, "ru": RU}

# 旧页脚整行被替换后残留的 t 键：它已不在任何文本节点里，留着只会让自测永远红
STALE_T = [
    "ESP32 全景手册 · 静态单页，无外部依赖 · 整理于 2026-11",
]

CJK = re.compile(r"[\u4e00-\u9fff]")
KANA = re.compile(r"[\u3040-\u30ff]")
HANGUL = re.compile(r"[\uac00-\ud7af]")
KEEP = ("ESP32", "GitHub", "oracis", "Espressif", "datasheet", "Discussions", "Star")


def load_blocks(src):
    dec = json.JSONDecoder()
    i = src.index("window.I18N = ") + len("window.I18N = ")
    obj, e1 = dec.raw_decode(src, i)
    k = src.index("window.I18N.MULTI = ") + len("window.I18N.MULTI = ")
    mobj, e2 = dec.raw_decode(src, k)
    return obj, e1, mobj, e2, i, k


def dump(o):
    return json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def pick_zh(src):
    out = {}
    for m in re.finditer(
            r'<([a-z0-9]+)([^>]*?)data-l10n="((?:SP|FT)\d+)"([^>]*)>([\s\S]*?)</\1>', src):
        out[m.group(3)] = m.group(5)
    return out


def check(zh):
    """写入前自检：键齐全、标签数一致、专有名词保留、目标语言字形正确。"""
    errs = []
    keys = sorted(EN, key=lambda x: (x[:2], int(x[2:])))
    miss = [k for k in keys if k not in zh]
    if miss:
        errs.append("HTML 缺键: %s" % miss)
    for L, d in BY_LANG.items():
        if set(d) != set(keys):
            errs.append("%s 键集不符: %s" % (L, sorted(set(keys) ^ set(d))))
            continue
        for k in keys:
            v, src = d[k], zh.get(k, "")
            if v.count("<b>") != src.count("<b>"):
                errs.append("%s %s 标签数不符" % (L, k))
            for w in KEEP:
                if w in src and w not in v:
                    errs.append("%s %s 丢了 %s" % (L, k, w))
            if L == "ja" and not KANA.search(v):
                errs.append("%s %s 无假名" % (L, k))
            if L == "ko" and (CJK.search(v) or not HANGUL.search(v)):
                errs.append("%s %s 韩语字形异常" % (L, k))
            if L in ("es", "pt", "fr", "ru") and CJK.search(v):
                errs.append("%s %s 残留汉字" % (L, k))
    return errs


def main():
    dry = "--dry" in sys.argv
    src = io.open(SITE, encoding="utf-8").read()
    zh = pick_zh(src)
    errs = check(zh)
    if errs:
        print("!! 自检未通过，未写入：")
        for e in errs:
            print("   -", e)
        return 1

    i18n, end1, multi, end2, pos_i, pos_m = load_blocks(src)
    i18n.setdefault("b", {}).update(EN)
    for k in STALE_T:
        i18n.get("t", {}).pop(k, None)
        for L in LANGS:
            multi.get(L, {}).get("t", {}).pop(k, None)
    for L, d in BY_LANG.items():
        multi.setdefault(L, {}).setdefault("b", {}).update(d)

    if dry:
        print("自检通过；%d 键 × %d 语言（含英文）" % (len(EN), len(LANGS) + 1))
        return 0

    new = src[:pos_i] + dump(i18n) + src[end1:]
    shift = len(dump(i18n)) - (end1 - pos_i)
    new = new[:pos_m + shift] + dump(multi) + new[end2 + shift:]
    io.open(SITE, "w", encoding="utf-8", newline="\n").write(new)
    print("自检通过并写入：%d → %d 字节" % (len(src.encode()), len(new.encode())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
