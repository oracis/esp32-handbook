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
    "SP11": "Tipping isn't open yet; when it is, it will live here. Until then a star or one "
            "specific question is worth more.",
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
    "SP11": "打賞通道還沒開，開了會掛在這裡。在那之前，一個 Star 或一條具體的問題，比打賞更有用。",
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
    "SP11": "投げ銭の窓口はまだ開いていません。開いたらここに載せます。それまでは Star ひとつ、具体的な質問ひとつのほうが役に立ちます。",
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
    "SP11": "후원 창구는 아직 열지 않았습니다. 열리면 여기에 올립니다. 그때까지는 Star 하나, 구체적인 질문 하나가 더 도움이 됩니다.",
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
    "SP2": "Este manual no tiene anuncios, ni muro de inicio de sesión, ni lecciones bloqueadas; lo mantiene una sola persona. Si te ahorró unas cuantas noches de prueba y error, cualquiera de las dos cosas de abajo cuenta.",
    "SP3": "Dale una Star al repositorio",
    "SP4": "No cuesta nada, pero decide si la próxima persona que busque ESP32 encuentra esta página. Con tu Star, cada revisión también aparece en tu inicio de GitHub.",
    "SP5": "Ir a GitHub",
    "SP6": "Preguntas, errores, peticiones",
    "SP7": "Un dato equivocado, un enlace roto o un resultado que no coincide con tu placa: dilo. Cada aviso se convierte en la próxima revisión.",
    "SP8": "Ir a Discussions",
    "SP9": "<b>Más contenido</b> — más escenarios de ESP32 convertidos en experimentos que se pueden recorrer y saltar.",
    "SP10": "<b>El sitio sigue en línea</b> — dominio, alojamiento y un peso que abre incluso con mala red.",
    "SP11": "Las donaciones aún no están abiertas; cuando lo estén, se publicarán aquí. Mientras tanto, una Star o una pregunta concreta sirve más.",
    "FT1": "Volver arriba",
    "FT2": "Zona de prácticas",
    "FT3": "Apoyo",
    "FT4": "Comentarios",
    "FT5": "Manual ESP32 Panorama",
    "FT6": "página estática única, sin dependencias externas",
    "FT7": "Proyecto personal no oficial, sin relación con Espressif. Las especificaciones eléctricas y los nombres de modelo siguen el datasheet oficial.",
    "FT8": "La placa cambia, el criterio no: primero qué hay que conectar, después a qué velocidad.",
}

PT = {
    "SP1": "Apoie este projeto",
    "SP2": "Este manual não tem anúncios, nem tela de login, nem aulas bloqueadas; é mantido por uma só pessoa. Se economizou algumas noites de tentativa e erro, qualquer uma das duas opções abaixo conta.",
    "SP3": "Dê uma Star ao repositório",
    "SP4": "Não custa nada, mas decide se a próxima pessoa que procurar ESP32 encontra esta página. Com a Star, cada revisão também aparece no seu início do GitHub.",
    "SP5": "Ir para o GitHub",
    "SP6": "Perguntas, erros, pedidos",
    "SP7": "Um dado errado, um link quebrado ou um resultado que não bate com a sua placa: diga. Cada aviso vira a próxima revisão.",
    "SP8": "Ir para Discussions",
    "SP9": "<b>Mais conteúdo</b> — mais cenários de ESP32 transformados em experimentos que dá para percorrer e pular.",
    "SP10": "<b>O site continua no ar</b> — domínio, hospedagem e um peso que abre até em rede fraca.",
    "SP11": "As doações ainda não estão abertas; quando estiverem, ficarão aqui. Até lá, uma Star ou uma pergunta concreta ajuda mais.",
    "FT1": "Voltar ao topo",
    "FT2": "Área de prática",
    "FT3": "Apoio",
    "FT4": "Feedback",
    "FT5": "Manual Panorama ESP32",
    "FT6": "página estática única, sem dependências externas",
    "FT7": "Projeto pessoal não oficial, sem vínculo com a Espressif. As especificações elétricas e os nomes de modelo seguem o datasheet oficial.",
    "FT8": "A placa muda, o critério não: primeiro o que precisa ser conectado, depois a que velocidade.",
}

FR = {
    "SP1": "Soutenez ce projet",
    "SP2": "Ce manuel n'a ni publicité, ni mur de connexion, ni leçons verrouillées ; une seule personne le tient à jour. S'il vous a épargné quelques soirées d'essais, l'une ou l'autre des deux options ci-dessous compte.",
    "SP3": "Mettre une Star au dépôt",
    "SP4": "Ça ne coûte rien, mais cela décide si la prochaine personne qui cherche ESP32 trouve cette page. Avec une Star, chaque révision apparaît aussi sur votre accueil GitHub.",
    "SP5": "Aller sur GitHub",
    "SP6": "Questions, erreurs, demandes",
    "SP7": "Une valeur fausse, un lien mort, ou un résultat qui ne correspond pas à votre carte : dites-le. Chaque retour devient la révision suivante.",
    "SP8": "Aller sur Discussions",
    "SP9": "<b>Plus de contenu</b> — plus de scénarios ESP32 transformés en expériences qu'on peut parcourir et passer.",
    "SP10": "<b>Le site reste en ligne</b> — domaine, hébergement et un poids qui s'ouvre même en réseau faible.",
    "SP11": "Les dons ne sont pas encore ouverts ; quand ils le seront, ils apparaîtront ici. D'ici là, une Star ou une question précise aide davantage.",
    "FT1": "Retour en haut",
    "FT2": "Zone d'essais",
    "FT3": "Soutien",
    "FT4": "Retour",
    "FT5": "Manuel Panorama ESP32",
    "FT6": "page statique unique, sans dépendance externe",
    "FT7": "Projet personnel non officiel, sans lien avec Espressif. Les caractéristiques électriques et les noms de modèle suivent le datasheet officiel.",
    "FT8": "La carte change, le critère non : d'abord ce qu'il faut connecter, ensuite à quelle vitesse.",
}

RU = {
    "SP1": "Поддержать проект",
    "SP2": "В этом руководстве нет рекламы, нет стены входа и нет закрытых уроков — его ведёт один человек. Если оно сэкономило вам пару вечеров проб и ошибок, подойдёт любой из двух способов ниже.",
    "SP3": "Поставить Star репозиторию",
    "SP4": "Это ничего не стоит, но решает, найдёт ли эту страницу следующий, кто ищет ESP32. После Star новые версии тоже появятся в вашей ленте GitHub.",
    "SP5": "Открыть GitHub",
    "SP6": "Вопросы, ошибки, пожелания",
    "SP7": "Неверное значение в таблице, битая ссылка или результат, который не совпал с вашей платой, — просто напишите. Каждое замечание становится следующей правкой.",
    "SP8": "Открыть Discussions",
    "SP9": "<b>Больше материалов</b> — больше сценариев ESP32, превращённых в эксперименты, которые можно пройти и пропустить.",
    "SP10": "<b>Сайт остаётся онлайн</b> — домен, хостинг и вес, который открывается даже на слабой сети.",
    "SP11": "Донаты пока не открыты; когда откроются, будут здесь. До тех пор один Star или конкретный вопрос полезнее.",
    "FT1": "Наверх",
    "FT2": "Практикум",
    "FT3": "Поддержка",
    "FT4": "Обратная связь",
    "FT5": "Руководство по ESP32 Panorama",
    "FT6": "одна статическая страница, без внешних зависимостей",
    "FT7": "Неофициальный личный проект, не связан с Espressif. Электрические параметры и названия моделей — по официальному datasheet.",
    "FT8": "Плата меняется, критерий — нет: сначала что нужно подключить, потом как быстро.",
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
