# 支持区文案机翻对照（8 条长句 × 4 语言）

现译 = 当前线上的人工译文；glm / sage = 两个免费模型的机翻结果。
标 ⚠ 的是自动校验没过（标签数、汉字残留、长度偏离、Star 被译走）。

## 西班牙语 `es`

**SP2** · 这本手册没有广告、没有登录墙、也没有课程锁，由一个人整理和维护。如果它帮你省下了几个晚上的试错，下面两件事都算支持。

- 现译：Este manual no tiene anuncios, ni muro de inicio de sesión, ni lecciones bloqueadas; lo mantiene una sola persona. Si te ahorró unas cuantas noches de prueba y error, cualquiera de las dos cosas de abajo cuenta.
- glm：Este manual no contiene publicidad, no tiene barreras de registro ni bloqueos de cursos, y es organizado y mantenido por una persona. Si te ha ahorrado algunas noches de intentos y errores, ambas cosas se consideran un apoyo.
- sage：Este manual no tiene anuncios, ni muro de inicio de sesión, ni cursos bloqueados; lo recopila y mantiene una sola persona. Si te ha ahorrado unas cuantas noches de prueba y error, cualquiera de las dos cosas de abajo cuenta como apoyo.
- **建议：采用 sage** — 补出「算作支持」——cuenta como apoyo 比现译光秃秃的 cuenta 完整
- → 定稿：Este manual no tiene anuncios, ni muro de inicio de sesión, ni cursos bloqueados; lo recopila y mantiene una sola persona. Si te ha ahorrado unas cuantas noches de prueba y error, cualquiera de las dos cosas de abajo cuenta como apoyo.

**SP4** · 不花钱，但决定下一个搜 ESP32 的人能不能找到这里。点过 Star 之后，每次修订也会出现在你的 GitHub 首页。

- 现译：No cuesta nada, pero decide si la próxima persona que busque ESP32 encuentra esta página. Con tu Star, cada revisión también aparece en tu inicio de GitHub.
- glm：No gasto, pero decido si la próxima persona que busque ESP32 puede encontrar aquí. Después de dar un Star, cada revisión también aparecerá en tu página de inicio de GitHub.
- sage：No cuesta dinero, pero decide si la próxima persona que busque ESP32 podrá encontrar este sitio. Después de pulsar Star, cada revisión también aparecerá en tu página de inicio de GitHub.
- **建议：采用 sage** — 「GitHub 首页」写成 página de inicio de GitHub 更明确；pulsar Star 更常用
- → 定稿：No cuesta dinero, pero decide si la próxima persona que busque ESP32 podrá encontrar este sitio. Después de pulsar Star, cada revisión también aparecerá en tu página de inicio de GitHub.

**SP7** · 表格里的参数不对、链接失效，或者你的实测结果不一样，直接说。每条反馈都会变成下一次修订。

- 现译：Un dato equivocado, un enlace roto o un resultado que no coincide con tu placa: dilo. Cada aviso se convierte en la próxima revisión.
- glm：Los parámetros en la tabla no son correctos, los enlaces no funcionan o tus resultados de prueba son diferentes, dilo directamente. Cada comentario se convertirá en la próxima revisión.
- sage：Si los parámetros de la tabla son incorrectos, los enlaces no funcionan o tus resultados de prueba difieren, dímelo directamente. Cada comentario se convertirá en la próxima revisión.
- **建议：保持现译** — 现译一句三顿更利落，且保留了 placa 这个开发板说法

**SP9** · <b>更多内容</b> —— 把更多 ESP32 场景做成能点、能跳过的实验。

- 现译：<b>Más contenido</b> — más escenarios de ESP32 convertidos en experimentos que se pueden recorrer y saltar.
- glm：<b>Más contenido</b> — Convertir más escenarios de ESP32 en experimentos con capacidad de clic y salto.
- sage：<b>Más contenido</b> — convertir más escenarios de ESP32 en experimentos en los que se puede hacer clic y que se pueden omitir.
- **建议：采用 sage** — 「能点」译成 hacer clic，现译 recorrer（走一遍）偏了
- → 定稿：<b>Más contenido</b> — convertir más escenarios de ESP32 en experimentos en los que se puede hacer clic y que se pueden omitir.

**SP10** · <b>站点一直在线</b> —— 域名、托管，以及弱网也能打开的体积。

- 现译：<b>El sitio sigue en línea</b> — dominio, alojamiento y un peso que abre incluso con mala red.
- glm：<b>Site always online</b> - Domain, hosting, and compact size that can be accessed even on weak networks.
- sage：<b>El sitio siempre está en línea</b> — el dominio, el alojamiento y un peso que carga incluso con mala conexión.
- **建议：采用 sage** — 「一直在线」是 siempre está en línea，现译 sigue 弱化了「一直」
- → 定稿：<b>El sitio siempre está en línea</b> — el dominio, el alojamiento y un peso que carga incluso con mala conexión.

**SP11** · 打赏通道还没开，开了会挂在这里。在那之前，一个 Star 或一条具体的问题，比打赏更有用。

- 现译：Las donaciones aún no están abiertas; cuando lo estén, se publicarán aquí. Mientras tanto, una Star o una pregunta concreta sirve más.
- glm：Canal de donaciones aún no está abierto, cuando esté lo pondré aquí. Antes de eso, un Star o una pregunta específica es más útil que una donación.
- sage：El canal de donaciones aún no está abierto; cuando lo esté, se anunciará aquí. Hasta entonces, un Star o una pregunta concreta son más útiles que una donación.
- **建议：采用 sage** — 补出「比打赏更有用」的比较对象；Star 用阳性 un Star 前后一致
- → 定稿：El canal de donaciones aún no está abierto; cuando lo esté, se anunciará aquí. Hasta entonces, un Star o una pregunta concreta son más útiles que una donación.

**FT7** · 非官方个人项目，与 Espressif 无隶属关系；电气参数与型号命名以官方 datasheet 为准。

- 现译：Proyecto personal no oficial, sin relación con Espressif. Las especificaciones eléctricas y los nombres de modelo siguen el datasheet oficial.
- glm：Proyecto personal no oficial, sin relación de隶属 con Espressif; los parámetros eléctricos y los nombres de los modelos se deben ajustar al datasheet oficial. ⚠ 残留汉字：属隶
- sage：Proyecto personal no oficial, sin afiliación con Espressif; los parámetros eléctricos y la denominación de los modelos se rigen por el datasheet oficial.
- **建议：采用 sage** — sin afiliación / se rigen por 比 sin relación / siguen 更像法律声明
- → 定稿：Proyecto personal no oficial, sin afiliación con Espressif; los parámetros eléctricos y la denominación de los modelos se rigen por el datasheet oficial.

**FT8** · 板子会换，判据不变：先问「要连什么」，再问「要多快」。

- 现译：La placa cambia, el criterio no: primero qué hay que conectar, después a qué velocidad.
- glm：El board cambiará, pero los criterios no: primero pregunte "¿con qué se va a conectar?" y luego "¿cuán rápido debe ser?"
- sage：Las placas cambiarán, el criterio no: primero pregúntate «¿qué necesitas conectar?» y después «¿a qué velocidad?».
- **建议：保持现译** — 现译短句有标语感；只把 placa 改成复数 Las placas 更自然


## 葡萄牙语 `pt`

**SP2** · 这本手册没有广告、没有登录墙、也没有课程锁，由一个人整理和维护。如果它帮你省下了几个晚上的试错，下面两件事都算支持。

- 现译：Este manual não tem anúncios, nem tela de login, nem aulas bloqueadas; é mantido por uma só pessoa. Se economizou algumas noites de tentativa e erro, qualquer uma das duas opções abaixo conta.
- glm：Este manual não possui anúncios, não há parede de login nem travas de curso, mantido por uma pessoa. Se ele lhe economizou algumas noites de tentativas e erros, ambas as coisas contam como apoio.
- sage：Este manual não tem anúncios, nem login obrigatório, nem conteúdo bloqueado por cursos; é organizado e mantido por uma única pessoa. Se ele te poupou algumas noites de tentativa e erro, as duas coisas abaixo contam como apoio.
- **建议：保持现译** — 现译更紧凑；只把句尾改成 conta como apoio

**SP4** · 不花钱，但决定下一个搜 ESP32 的人能不能找到这里。点过 Star 之后，每次修订也会出现在你的 GitHub 首页。

- 现译：Não custa nada, mas decide se a próxima pessoa que procurar ESP32 encontra esta página. Com a Star, cada revisão também aparece no seu início do GitHub.
- glm：Grátis, mas decide se a próxima pessoa que procurar ESP32 vai encontrar aqui. Após clicar em Star, cada revisão também aparecerá na sua página inicial do GitHub.
- sage：Não custa nada, mas decide se a próxima pessoa que pesquisar por ESP32 conseguirá encontrar este lugar. Depois de clicar em Star, cada revisão também aparecerá na sua página inicial do GitHub.
- **建议：采用 sage** — página inicial 比 início 明确；clicar em Star 自然
- → 定稿：Não custa nada, mas decide se a próxima pessoa que pesquisar por ESP32 conseguirá encontrar este lugar. Depois de clicar em Star, cada revisão também aparecerá na sua página inicial do GitHub.

**SP7** · 表格里的参数不对、链接失效，或者你的实测结果不一样，直接说。每条反馈都会变成下一次修订。

- 现译：Um dado errado, um link quebrado ou um resultado que não bate com a sua placa: diga. Cada aviso vira a próxima revisão.
- glm：Se os parâmetros na tabela estão incorretos, os links estão inativos ou seus resultados de medição são diferentes, diga diretamente. Cada feedback se tornará a próxima revisão.
- sage：Se os parâmetros da tabela estiverem incorretos, os links estiverem quebrados ou seus resultados de teste prático forem diferentes, diga diretamente. Cada feedback se tornará a próxima revisão.
- **建议：保持现译** — 现译「Um dado errado…: diga」更有力，sage 版偏冗长

**SP9** · <b>更多内容</b> —— 把更多 ESP32 场景做成能点、能跳过的实验。

- 现译：<b>Mais conteúdo</b> — mais cenários de ESP32 transformados em experimentos que dá para percorrer e pular.
- glm：<b>Mais conteúdo</b> — Transformar mais cenários do ESP32 em experimentos que podem ser clicados e saltados.
- sage：<b>Mais conteúdo</b> — transformar mais cenários de ESP32 em experimentos clicáveis e que podem ser pulados.
- **建议：采用 sage** — clicáveis / podem ser pulados 准确；现译 percorrer 是「游走」
- → 定稿：<b>Mais conteúdo</b> — transformar mais cenários de ESP32 em experimentos clicáveis e que podem ser pulados.

**SP10** · <b>站点一直在线</b> —— 域名、托管，以及弱网也能打开的体积。

- 现译：<b>O site continua no ar</b> — domínio, hospedagem e um peso que abre até em rede fraca.
- glm：<b>Site always online</b> - Domain, hosting, and compact size that can be accessed even on weak networks.
- sage：<b>O site está sempre online</b> — domínio, hospedagem e um tamanho que abre mesmo com internet fraca
- **建议：采用 sage** — está sempre online 贴合「一直在线」；原句缺句末句号，补上
- → 定稿：<b>O site está sempre online</b> — domínio, hospedagem e um tamanho que abre mesmo com internet fraca.

**SP11** · 打赏通道还没开，开了会挂在这里。在那之前，一个 Star 或一条具体的问题，比打赏更有用。

- 现译：As doações ainda não estão abertas; quando estiverem, ficarão aqui. Até lá, uma Star ou uma pergunta concreta ajuda mais.
- glm：Canais de doação ainda não estão abertos, mas estarão aqui quando estiverem. Até lá, um Star ou uma pergunta específica são mais úteis do que uma doação.
- sage：O canal de doações ainda não está aberto; quando abrir, será divulgado aqui. Até lá, um Star ou uma pergunta específica é mais útil do que uma doação.
- **建议：采用 sage** — canal 用单数、补出「比打赏更有用」的比较
- → 定稿：O canal de doações ainda não está aberto; quando abrir, será divulgado aqui. Até lá, um Star ou uma pergunta específica é mais útil do que uma doação.

**FT7** · 非官方个人项目，与 Espressif 无隶属关系；电气参数与型号命名以官方 datasheet 为准。

- 现译：Projeto pessoal não oficial, sem vínculo com a Espressif. As especificações elétricas e os nomes de modelo seguem o datasheet oficial.
- glm：Projeto pessoal não-oficial, sem vínculo com a Espressif; os parâmetros elétricos e nomes dos modelos devem seguir o datasheet oficial.
- sage：Projeto pessoal não oficial, sem afiliação com a Espressif; para parâmetros elétricos e nomenclatura de modelos, prevalece o datasheet oficial.
- **建议：采用 sage** — prevalece o datasheet oficial 正是「以…为准」的法律语
- → 定稿：Projeto pessoal não oficial, sem afiliação com a Espressif; para parâmetros elétricos e nomenclatura de modelos, prevalece o datasheet oficial.

**FT8** · 板子会换，判据不变：先问「要连什么」，再问「要多快」。

- 现译：A placa muda, o critério não: primeiro o que precisa ser conectado, depois a que velocidade.
- glm：O board pode mudar, mas o critério não muda: primeiro pergunte "o que você quer conectar" e depois "quão rápido você precisa".
- sage：As placas mudam, os critérios não: primeiro pergunte «o que conectar», depois pergunte «quão rápido».
- **建议：保持现译** — 现译短句更像标语；placa 改复数 placas


## 法语 `fr`

**SP2** · 这本手册没有广告、没有登录墙、也没有课程锁，由一个人整理和维护。如果它帮你省下了几个晚上的试错，下面两件事都算支持。

- 现译：Ce manuel n'a ni publicité, ni mur de connexion, ni leçons verrouillées ; une seule personne le tient à jour. S'il vous a épargné quelques soirées d'essais, l'une ou l'autre des deux options ci-dessous compte.
- glm：Ce manuel ne contient pas d'annonces, pas de mur de connexion et pas de verrouillage de cours, il est mis en ordre et entretenu par une seule personne. Si il vous a économisé quelques soirs de tentatives et d'erreurs, les deux choses suivantes sont considérées comme un soutien.
- sage：Ce manuel n'a ni publicité, ni mur de connexion, ni cours verrouillés ; il est compilé et maintenu par une seule personne. S'il vous a épargné quelques soirées d'essais et d'erreurs, les deux gestes ci-dessous comptent comme un soutien.
- **建议：采用 sage** — gestes ci-dessous comptent comme un soutien 比 l'une ou l'autre…compte 精确
- → 定稿：Ce manuel n'a ni publicité, ni mur de connexion, ni cours verrouillés ; il est compilé et maintenu par une seule personne. S'il vous a épargné quelques soirées d'essais et d'erreurs, les deux gestes ci-dessous comptent comme un soutien.

**SP4** · 不花钱，但决定下一个搜 ESP32 的人能不能找到这里。点过 Star 之后，每次修订也会出现在你的 GitHub 首页。

- 现译：Ça ne coûte rien, mais cela décide si la prochaine personne qui cherche ESP32 trouve cette page. Avec une Star, chaque révision apparaît aussi sur votre accueil GitHub.
- glm：Gratuit, mais décide si la prochaine personne qui recherche ESP32 peut trouver ici. Après avoir cliqué sur Star, chaque mise à jour apparaîtra également sur votre page d'accueil GitHub.
- sage：C'est gratuit, mais cela détermine si la prochaine personne qui cherchera ESP32 pourra trouver ce site. Après avoir cliqué sur Star, chaque révision apparaîtra aussi sur votre page d'accueil GitHub.
- **建议：采用 sage** — C'est gratuit… détermine si… 比 Avec une Star 通顺
- → 定稿：C'est gratuit, mais cela détermine si la prochaine personne qui cherchera ESP32 pourra trouver ce site. Après avoir cliqué sur Star, chaque révision apparaîtra aussi sur votre page d'accueil GitHub.

**SP7** · 表格里的参数不对、链接失效，或者你的实测结果不一样，直接说。每条反馈都会变成下一次修订。

- 现译：Une valeur fausse, un lien mort, ou un résultat qui ne correspond pas à votre carte : dites-le. Chaque retour devient la révision suivante.
- glm：Les paramètres du tableau ne sont pas corrects, les liens ne fonctionnent pas ou vos résultats de test sont différents, dites-le directement. Chaque retour deviendra une prochaine révision.
- sage：Si les paramètres du tableau sont erronés, qu'un lien ne fonctionne plus ou que vos résultats de test diffèrent, dites-le directement. Chaque retour contribuera à la prochaine révision.
- **建议：保持现译** — 现译「Une valeur fausse, un lien mort…: dites-le」更利落

**SP9** · <b>更多内容</b> —— 把更多 ESP32 场景做成能点、能跳过的实验。

- 现译：<b>Plus de contenu</b> — plus de scénarios ESP32 transformés en expériences qu'on peut parcourir et passer.
- glm：<b>More content</b> - Turn more ESP32 scenarios into clickable, skippable experiments.
- sage：<b>Plus de contenu</b> — transformer davantage de scénarios ESP32 en expériences cliquables et que l'on peut passer.
- **建议：采用 sage** — cliquables 纠正了现译 parcourir（游走）对「能点」的误译
- → 定稿：<b>Plus de contenu</b> — transformer davantage de scénarios ESP32 en expériences cliquables et que l'on peut passer.

**SP10** · <b>站点一直在线</b> —— 域名、托管，以及弱网也能打开的体积。

- 现译：<b>Le site reste en ligne</b> — domaine, hébergement et un poids qui s'ouvre même en réseau faible.
- glm：<b>Site always online</b> - Domaine, hosting, and compact size that can be accessed even on weak networks.
- sage：<b>Le site reste toujours en ligne</b> — nom de domaine, hébergement, et un poids qui se charge même avec une connexion faible.
- **建议：保持现译** — 现译已准确；sage 的 reste toujours 语义重复

**SP11** · 打赏通道还没开，开了会挂在这里。在那之前，一个 Star 或一条具体的问题，比打赏更有用。

- 现译：Les dons ne sont pas encore ouverts ; quand ils le seront, ils apparaîtront ici. D'ici là, une Star ou une question précise aide davantage.
- glm：Le canal de dons n'est pas encore ouvert, il sera affiché ici une fois ouvert. Avant cela, un Star ou une question spécifique est plus utile que le don.
- sage：Le canal de dons n'est pas encore ouvert ; il sera affiché ici dès qu'il le sera. En attendant, un Star ou une question concrète est plus utile qu'un don.
- **建议：保持现译** — 现译 quand ils le seront 比 sage 的 dès qu'il le sera 少一处重复

**FT7** · 非官方个人项目，与 Espressif 无隶属关系；电气参数与型号命名以官方 datasheet 为准。

- 现译：Projet personnel non officiel, sans lien avec Espressif. Les caractéristiques électriques et les noms de modèle suivent le datasheet officiel.
- glm：Projet personnel non officiel, sans affiliation avec Espressif ; les paramètres électriques et les noms de modèle doivent suivre les datasheets officielles.
- sage：Projet personnel non officiel, sans affiliation avec Espressif ; pour les paramètres électriques et la nomenclature des modèles, seul le datasheet officiel fait foi
- **建议：采用 sage** — seul le datasheet officiel fait foi 是法语法律惯用；补句号
- → 定稿：Projet personnel non officiel, sans affiliation avec Espressif ; pour les paramètres électriques et la nomenclature des modèles, seul le datasheet officiel fait foi.

**FT8** · 板子会换，判据不变：先问「要连什么」，再问「要多快」。

- 现译：La carte change, le critère non : d'abord ce qu'il faut connecter, ensuite à quelle vitesse.
- glm：Le board change, mais les critères restent inchangés : d'abord demander "avec quoi vous voulez vous connecter", puis "à quelle vitesse".
- sage：Les cartes changent, les critères restent : demandez d'abord « qu'allez-vous connecter », puis « à quelle vitesse ».
- **建议：保持现译** — 现译保留标语节奏；carte 改复数 cartes


## 俄语 `ru`

**SP2** · 这本手册没有广告、没有登录墙、也没有课程锁，由一个人整理和维护。如果它帮你省下了几个晚上的试错，下面两件事都算支持。

- 现译：В этом руководстве нет рекламы, нет стены входа и нет закрытых уроков — его ведёт один человек. Если оно сэкономило вам пару вечеров проб и ошибок, подойдёт любой из двух способов ниже.
- glm：Этот руководствo не содержит рекламы, барьеров для входа и блокировок курсов, его собирает и обслуживает один человек. Если это помогло вам сэкономить несколько ночей на пробах и ошибках, обе следующие вещи считаются поддержкой.
- sage：В этом руководстве нет рекламы, нет обязательной регистрации и нет закрытых курсов — оно собрано и поддерживается одним человеком. Если оно сэкономило вам несколько вечеров проб и ошибок, то любое из двух действий ниже станет поддержкой.
- **建议：采用 sage** — стена входа 是照字面造的，обязательная регистрация 才是俄语自然说法
- → 定稿：В этом руководстве нет рекламы, нет обязательной регистрации и нет закрытых курсов — оно собрано и поддерживается одним человеком. Если оно сэкономило вам несколько вечеров проб и ошибок, то любое из двух действий ниже станет поддержкой.

**SP4** · 不花钱，但决定下一个搜 ESP32 的人能不能找到这里。点过 Star 之后，每次修订也会出现在你的 GitHub 首页。

- 现译：Это ничего не стоит, но решает, найдёт ли эту страницу следующий, кто ищет ESP32. После Star новые версии тоже появятся в вашей ленте GitHub.
- glm：Бесплатно, но решает,能不能找到这里 следующий, кто ищет ESP32. После того как поставите Star, каждая версия также будет出现在 вашей首页е GitHub. ⚠ 残留汉字：不出到在找现能这里页首
- sage：Это бесплатно, но от этого зависит, сможет ли следующий человек, который ищет ESP32, найти этот сайт. После того как вы поставите Star, каждое обновление будет появляться и на вашей главной странице GitHub.
- **建议：采用 sage** — 现译「После Star」过于电报式，sage 补全了主谓
- → 定稿：Это бесплатно, но от этого зависит, сможет ли следующий человек, который ищет ESP32, найти этот сайт. После того как вы поставите Star, каждое обновление будет появляться и на вашей главной странице GitHub.

**SP7** · 表格里的参数不对、链接失效，或者你的实测结果不一样，直接说。每条反馈都会变成下一次修订。

- 现译：Неверное значение в таблице, битая ссылка или результат, который не совпал с вашей платой, — просто напишите. Каждое замечание становится следующей правкой.
- glm：Если параметры в таблице не соответствуют, ссылка не работает или ваши измеренные результаты отличаются, просто скажите. Каждое обратное сообщение станет частью следующего обновления.
- sage：Если параметры в таблице неверны, ссылки не работают или ваши результаты измерений отличаются — говорите прямо. Каждый отзыв ляжет в основу следующей редакции.
- **建议：保持现译** — 现译更紧凑，битая ссылка 是俄语口语里地道的说法

**SP9** · <b>更多内容</b> —— 把更多 ESP32 场景做成能点、能跳过的实验。

- 现译：<b>Больше материалов</b> — больше сценариев ESP32, превращённых в эксперименты, которые можно пройти и пропустить.
- glm：<b>Больше контента</b> — создать больше экспериментов с ESP32, которые можно нажимать и пропускать.
- sage：<b>Больше материалов</b> — превращаем больше сценариев с ESP32 в эксперименты, которые можно запустить кликом и пропустить.
- **建议：采用 sage** — 「能点」= запустить кликом，现译 пройти 只表示「走完」
- → 定稿：<b>Больше материалов</b> — превращаем больше сценариев с ESP32 в эксперименты, которые можно запустить кликом и пропустить.

**SP10** · <b>站点一直在线</b> —— 域名、托管，以及弱网也能打开的体积。

- 现译：<b>Сайт остаётся онлайн</b> — домен, хостинг и вес, который открывается даже на слабой сети.
- glm：<b>Сайт всегда онлайн</b> — домен, хостинг и размер, который можно открыть даже при слабом интернете.
- sage：<b>Сайт всегда онлайн</b> — домен, хостинг и размер, позволяющий открывать его даже при слабом интернете.
- **建议：采用 sage** — всегда онлайн 贴合「一直在线」，现译 остаётся 只是「仍然」
- → 定稿：<b>Сайт всегда онлайн</b> — домен, хостинг и размер, позволяющий открывать его даже при слабом интернете.

**SP11** · 打赏通道还没开，开了会挂在这里。在那之前，一个 Star 或一条具体的问题，比打赏更有用。

- 现译：Донаты пока не открыты; когда откроются, будут здесь. До тех пор один Star или конкретный вопрос полезнее.
- glm：Канал для донатов еще не открыт, но как только он откроется, я добавлю его здесь. До этого времени, один Star или конкретный вопрос будет полезнее, чем донат.
- sage：Канал для донатов пока не открыт, когда откроется — ссылка появится здесь. А пока один Star или конкретный вопрос полезнее доната.
- **建议：采用 sage** — 「挂在这里」→ ссылка появится здесь 更具体；逗号改分号
- → 定稿：Канал для донатов пока не открыт; когда откроется — ссылка появится здесь. А пока один Star или конкретный вопрос полезнее доната.

**FT7** · 非官方个人项目，与 Espressif 无隶属关系；电气参数与型号命名以官方 datasheet 为准。

- 现译：Неофициальный личный проект, не связан с Espressif. Электрические параметры и названия моделей — по официальному datasheet.
- glm：Ненавязчивый личный проект, не связанный с Espressif; электрические параметры и наименование моделей должны соответствовать официальному datasheet.
- sage：Неофициальный личный проект, не связанный с Espressif; электрические параметры и наименования моделей уточняйте в официальном datasheet.
- **建议：保持现译** — 现译已准确；glm 的 Ненавязчивый 把「非官方」译成「不打扰」是错译

**FT8** · 板子会换，判据不变：先问「要连什么」，再问「要多快」。

- 现译：Плата меняется, критерий — нет: сначала что нужно подключить, потом как быстро.
- glm：Плата может меняться, но критерии остаются: сперва спросите "с чем нужно соединиться", затем "сколько нужно скорости".
- sage：Платы меняются, критерии остаются прежними: сначала спрашиваем «что нужно подключить», потом «какая нужна скорость».
- **建议：保持现译** — 现译短句贴合标语；плата 改复数 Платы

---

判读结果：采用 sage 20 条，保持现译 12 条；glm 有硬伤（SP10 四语全英文、FT7 西语混汉字、SP4 俄语混中文），一条未采用。
