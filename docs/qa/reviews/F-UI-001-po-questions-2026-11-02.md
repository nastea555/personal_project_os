# Questions for the PO — F-UI-001 v0.3

| | |
|---|---|
| Spec | `specs/features/F-UI-001-ui-shell.md` |
| From | QA — 2026-11-02 |
| QA verdict | **Not ready for development** |
| Decisions needed | 1 blocking · 22 other |
| Full QA report | `docs/qa/reviews/F-UI-001-review-2026-11-02.md` |

## How to answer

Write your answer under **Answer:** for each question. A letter (A/B/…) or a value is enough. Add a reason if you pick something other than the recommended option. When all blocking questions are answered, update the spec (new version + change log) and send it back for re-review.

## Blocking — must be answered before development

### Q-01 · Can the owner use v1 from a phone? (D-8 vs product brief)
**Where:** §12 D-8; §10; TC-UI-032; AC-UI-024 (report F-01)
**Spec says:** «v1 работает только на `localhost`, без аутентификации (ADR-008 → Accepted)» because «Один пользователь на своём компьютере». §10: «Backend слушает `127.0.0.1`». The product brief says: «Использует приложение ежедневно с телефона (быстрый ввод) и с компьютера».
**Why it matters:** An app on the computer's localhost cannot be opened from the phone, so the brief's daily phone scenario is impossible in v1. In this spec, TC-UI-032 («реальный телефон») and the phone «Назад» gesture (AC-UI-024) cannot be run as written.
**Options:**
- **A.** Localhost only for all of v1. The brief is changed (no phone use in v1), and phone checks in F-UI-001 run in device emulation or over USB port forwarding.
- **B.** Localhost only until a named stage (e.g., before Stage 3, quick input), then access from the home network with authentication under a separate spec. F-UI-001 states how the real-phone checks run until then.
- **C.** Access from the home network without authentication from v1.

**Recommended:** B. It keeps D-8's security reasoning, and phone use first becomes essential at Stage 3 (quick input).
**Also needed:** how TC-UI-032 «реальный телефон» is executed at Stage 1.
**Answer:**

## Other questions — answer before the next spec version

### Q-02 · Which landmarks must exist on each screen?
**Where:** AC-UI-011; Термины (Мобильная панель, Выдвижное меню, Основная навигация); §7.1 ① (F-02)
**Spec says:** AC-UI-011: «ориентиры `header`, `nav` (с подписью «Основная навигация»), `main`». Glossary: the mobile panel (`header`) exists «Только при ширине < 1024 px»; the drawer (with the `nav`) exists «только в открытом состоянии».
**Why it matters:** By the glossary, a wide screen has no `header`, and a narrow screen with the drawer closed has no `nav`, so the landmark test fails on both. Example: `/` at 1440 px has no `header`.
**Options:**
- **A.** Landmarks are required only where the element exists: wide screen `nav` + `main`; narrow screen with the drawer closed `header` + `main`; drawer open, all three.
- **B.** All three are always present: the wide screen gets a `header` (holding «Life Hub» above the `nav`), and on a narrow screen the drawer's `nav` stays in the page, hidden, while the drawer is closed.

**Recommended:** A. It matches the glossary and the screen schematics without adding elements.
**Also needed:** on the wide screen, is «Life Hub» inside the «Основная навигация» `nav`? If it is, the nav holds 7 links while AC-UI-003 says «ровно 6 разделов».
**Answer:**

### Q-03 · What does "Этап N" on a Dashboard card promise?
**Where:** §7.4 card table; §4 section map; product brief §4 (F-04)
**Spec says:** «Калории за день … В разработке · Этап 2». Map: Обзор «5 (данные)». Brief: «Dashboard (реальные данные) … 5».
**Why it matters:** Right after Stage 2 ships, the «Калории за день» card would either still say «В разработке · Этап 2» (a stage that is already done) or show real calories (which contradicts the brief's Stage 5 plan).
**Options:**
- **A.** The stage on a card is the stage when that *card* shows data: «Этап 5» on all five cards.
- **B.** Each card gets data in its module's stage (2/3/4/5), and the brief's Dashboard row changes to match.

**Recommended:** A. It matches the brief and the map and stays true until Stage 5.
**Answer:**

### Q-04 · What does «Повторить» do while a background check is running?
**Where:** AC-UI-021; AC-UI-008; §7.7; §7.8 (F-05)
**Spec says:** «Пока запрос по «Повторить» выполняется, кнопка в состоянии loading…»; «одновременно выполняется не больше одного запроса»; §7.7: «Пока идёт повторная проверка, кнопка в состоянии loading».
**Why it matters:** Example: the banner is shown and the 60-second check has been running for 1 s when the user clicks «Повторить». No second request may be sent, so if the button looks active the click silently does nothing, which BR-2 forbids.
**Options:**
- **A.** The button is in the loading state during *any* running check (60-second, tab-return or «Повторить»).
- **B.** The button is loading only after it is clicked. A click during a background check joins that check: the button shows loading until it ends, and no new request is sent.

**Recommended:** A. It is the simplest behaviour, matches §7.8, and never leaves an active-looking button that does nothing.
**Answer:**

### Q-05 · What are the 60 seconds between checks counted from?
**Where:** AC-UI-008; TC-UI-038 (F-06)
**Spec says:** «каждые 60 с, пока вкладка видима»
**Why it matters:** Example: check at load t=0, tab hidden at 50 s, shown again at 70 s (check). The next periodic check is at 130 s if counting restarts, or at 120 s on a fixed schedule. The test with fake timers needs one exact value.
**Options:**
- **A.** 60 s after the previous check of any kind (load, tab return or «Повторить») finished.
- **B.** 60 s after the previous check started.
- **C.** A fixed 60-second schedule from app load, not reset by other checks.

**Recommended:** A. It avoids two checks seconds apart and is easy to test.
**Answer:**

### Q-06 · Which section is highlighted on a 404 page?
**Where:** AC-UI-003; Термины «Неизвестный путь»; AC-UI-005 (F-07)
**Spec says:** «Активный раздел визуально выделен и имеет `aria-current="page"`; у остальных этого атрибута нет.» An unknown path includes «вложенный в известный раздел (`/nutrition/abc`)».
**Why it matters:** On `/nutrition/abc`, default router behaviour highlights «Питание» and announces it as the current page, although the user sees a 404.
**Options:**
- **A.** On any 404 (including nested paths) no section is highlighted and none has `aria-current`.
- **B.** On a nested unknown path the parent section is highlighted; on other 404 pages none is.

**Recommended:** A. The user is not on «Питание», so announcing it as the current page is wrong.
**Answer:**

### Q-07 · How does browser history behave around the drawer?
**Where:** AC-UI-024; AC-UI-004 (F-08)
**Spec says:** «кнопка «Назад» браузера … закрывает выдвижное меню; раздел и адрес страницы не меняются». AC-UI-004: «Кнопки браузера «Назад/Вперёд» переключают разделы в порядке посещения.»
**Why it matters:** Example 1: on `/tasks`, open the drawer, close it with Esc, press Back. Does Back go to the previous section, or does the first press do nothing visible? Example 2: open the drawer, press Back (it closes), press Forward. Does the drawer reopen?
**Options:**
- **A.** The drawer is never a step in history. After it is closed by any means, one Back goes to the previous section, and Forward never reopens the drawer.
- **B.** The drawer is a step in history: Back closes it and Forward reopens it. After an Esc close, the first Back does nothing visible.

**Recommended:** A. It matches «в порядке посещения»: the drawer is not a visited section.
**Answer:**

### Q-08 · What does the user see while a section's code is loading?
**Where:** §7.8 «загрузка раздела (Spinner/скелетон)»; glossary «Ленивая загрузка» (F-09)
**Spec says:** «\| Рабочая область \| загрузка раздела (Spinner/скелетон) · содержимое · 404 · ошибка отрисовки \|». No acceptance criterion describes this state.
**Why it matters:** On a slow first open of `/tasks`, one developer shows a spinner and another shows grey placeholder blocks. A skeleton imitates content that does not exist, which is close to what BR-1 forbids.
**Options:**
- **A.** `Spinner` in the work area, shown only if loading takes longer than a threshold (e.g., 300 ms).
- **B.** Skeleton placeholders.

**Recommended:** A. There is nothing to imitate at Stage 1, and a spinner is simpler to test.
**Also needed:** if the section code fails to download, does the user see «Что-то пошло не так» (AC-UI-014)?
**Answer:**

### Q-09 · Where does focus go when the banner disappears?
**Where:** AC-UI-021; US-7 (F-10)
**Spec says:** «его появление не перемещает фокус … Когда очередная проверка возвращает «Система работает», баннер исчезает.»
**Why it matters:** A keyboard user presses Enter on «Повторить»; the check succeeds and the banner, with the focused button, disappears. Focus is either placed somewhere useful or lost, in which case the next Tab starts from the top of the page.
**Options:**
- **A.** Focus moves to the page heading (`h1`) of the work area.
- **B.** Focus moves to `main`.
- **C.** Not specified (browser default).

**Recommended:** A. The user stays in the content and hears where they are.
**Answer:**

### Q-10 · What is the "visual" Tab order on the wide screen?
**Where:** AC-UI-011; TC-UI-026 (F-11)
**Spec says:** «порядок перехода по Tab совпадает с визуальным порядком (сверху вниз, слева направо)»
**Why it matters:** At 1440 px with the banner shown, «Повторить» sits on the same row as «Life Hub». After «Life Hub», does Tab go to «Обзор» (sidebar first) or to «Повторить» (row by row)?
**Options:**
- **A.** Region by region: the whole sidebar (or mobile panel) top to bottom, then the work area top to bottom, left to right.
- **B.** Strictly row by row across both columns.

**Recommended:** A. It is the standard and expected order and matches the skip link.
**Answer:**

### Q-11 · Are the texts drawn in the screen schematics binding?
**Where:** §7 intro; §7.6; §7.1 schematic; AC-UI-005; AC-UI-014 (F-12)
**Spec says:** «Схемы нормативны по расположению и порядку элементов; размеры и тексты в таблицах — тоже». The 404 explanation «Такой страницы нет. Возможно, ссылка устарела или в адресе опечатка.» and «Страницу не удалось показать.» appear only in schematics. §7.1 draws «[i] Голосовой...» and «[i] Привычки ...».
**Why it matters:** If the developer writes «Адрес не найден.» as the 404 explanation, one tester passes it and another fails it. The ellipses may be copied into the UI, although AC-UI-012 says text is not cut.
**Options:**
- **A.** Texts in schematics are exact and binding. The ellipses in §7.1 are drawing shortcuts and the full labels are shown. The two texts are added to AC-UI-005 and AC-UI-014.
- **B.** Only texts in tables are binding; schematic texts are examples.

**Recommended:** A. It gives TC-UI-011/033 an exact expected result.
**Answer:**

### Q-12 · How exactly must sizes from §7 match?
**Where:** AC-UI-025; §7.1 ③; §7.2 ③; TC-UI-041 (F-13)
**Spec says:** «Колонка 240 px …; граница справа 1 px `--border`»; «Высота 56 px …; граница снизу 1 px `--border`»; AC-UI-025: «размеры элементов экранов соответствуют схемам и таблицам элементов §7».
**Why it matters:** The sidebar may measure 241 px (240 + border). Is that a pass?
**Options:**
- **A.** Sizes are outer sizes including borders and must match exactly (whole CSS px) at 1440 and 390 px.
- **B.** Sizes exclude borders; ±1 px tolerance.

**Recommended:** A. One exact value per element is the easiest to test and to build.
**Answer:**

### Q-13 · In production, does `/dev/ui` return an HTTP 404 or show the 404 page?
**Where:** AC-UI-010; §4 map; TC-UI-025 (F-14)
**Spec says:** «В production-сборке `/dev/ui` отдаёт 404»; other unknown paths «показывает страницу 404» (AC-UI-005).
**Why it matters:** A typical static server answers 200 and lets the app show its 404 page. A test that expects HTTP status 404 would then fail although the user sees the right page.
**Options:**
- **A.** The app shows its 404 page, the same as for any unknown path; the HTTP status is not checked.
- **B.** The server responds with HTTP status 404.

**Recommended:** A. It is consistent with AC-UI-005 and needs no server rules.
**Also needed:** what serves the production build that the E2E tests run against.
**Answer:**

### Q-14 · How is the 200 KB first-load budget measured?
**Where:** NFR-UI-001; TC-UI-035 (F-15)
**Spec says:** «JavaScript, который скачивается при первом открытии `/`, — не больше 200 KB в сжатом виде (gzip) по отчёту production-сборки (`vite build`).»
**Why it matters:** The build report lists file sizes, not which files the browser downloads for `/`. With lazy loading, opening `/` downloads the entry file and the Dashboard file. Example: 170 KB + 40 KB. Counting the entry file only passes (170); counting everything downloaded fails (210).
**Options:**
- **A.** The sum of the gzip sizes of all JS files the browser downloads when `/` is opened with an empty cache, measured against the production build. 1 KB = 1000 bytes.
- **B.** The size of the entry file in the `vite build` report only.

**Recommended:** A. It measures what the requirement actually says («скачивается при первом открытии»).
**Answer:**

### Q-15 · Which console messages are allowed?
**Where:** NFR-UI-002 (F-16)
**Spec says:** «Ни на одном маршруте нет ошибок и предупреждений в консоли браузера (кроме ожидаемых в TC-UI-016/017/033).»
**Why it matters:** TC-UI-016 is the healthy case and logs nothing. The backend-down cases (TC-UI-018, TC-UI-020) log browser errors for the failed health request but are not listed. A run with the backend stopped would fail this requirement.
**Options:**
- **A.** Define the exceptions by situation: (1) browser messages about the failed `GET /api/v1/system/health` while the server or DB is unavailable; (2) the error logged by AC-UI-014. Nothing else.
- **B.** Keep the list of test cases, corrected to TC-UI-017/018/020/033.

**Recommended:** A. It does not break when test cases are renumbered.
**Answer:**

### Q-16 · Does "503 DOWN" mean only "database unavailable"?
**Where:** §8; AC-UI-008 (F-18)
**Spec says:** «Spring Boot Actuator … `show-details: never`»; «\| БД недоступна \| 503 \| `{"status":"DOWN"}` \|»; ««База данных недоступна» — 503 и `status: DOWN`».
**Why it matters:** By default the overall health status also includes other checks (e.g., free disk space). If the disk runs low while the DB works, the user would see «База данных недоступна», which is untrue.
**Options:**
- **A.** The health response reflects only the application and the database; other checks do not affect it.
- **B.** Any failing check gives 503 DOWN, and the banner text is changed to something general.

**Recommended:** A. It keeps the banner text true.
**Answer:**

### Q-17 · Where does focus go when the drawer is closed by Back or by widening the window?
**Where:** AC-UI-015; AC-UI-024; AC-UI-018 (F-20)
**Spec says:** «Выдвижное меню закрывается каждым из способов: выбором раздела, кнопкой «Закрыть меню», клавишей Esc, нажатием на затемнённый фон. После закрытия фокус возвращается на кнопку «Открыть меню».»
**Why it matters:** Back and widening the window also close the drawer. After widening, «Открыть меню» no longer exists, so focus may be lost.
**Options:**
- **A.** Back: focus goes to «Открыть меню» (as for the other ways). Widening: focus goes to the active item of the side navigation.
- **B.** Back as in A; widening: focus goes to `main`.

**Recommended:** A. It keeps the user in the navigation they were using.
**Answer:**

### Q-18 · Is «Life Hub» in the open drawer a link?
**Where:** §7.1 ①, §7.2 ①, §7.3 ① (F-21)
**Spec says:** §7.1/§7.2: «Ссылка на `/`»; §7.3: «\| ① \| Название «Life Hub» \| Вверху выдвижного меню, 16 px, полужирный \| — \|».
**Why it matters:** If it is a link, it is not said whether tapping it closes the drawer (AC-UI-015 lists only «выбором раздела»).
**Options:**
- **A.** Plain text in the drawer (not a link).
- **B.** A link to `/` that closes the drawer, like choosing «Обзор».

**Recommended:** A. «Обзор» is right below it, and one less focus stop inside the drawer.
**Answer:**

### Q-19 · Are the §9 token values final for Stage 1?
**Where:** §9 heading; D-2; AC-UI-025 (F-23)
**Spec says:** «Дизайн-токены (предложение, финал — после ручного визуального ревью)»; D-2: «`#3DD6B5` сохраняется»; AC-UI-025: «цвета — токены §9».
**Why it matters:** If the manual visual review (TC-UI-034) changes, say, `--text-muted`, the build either deviates from the spec or is fine, depending on the reading.
**Options:**
- **A.** §9 values are final for Stage 1; any change after the visual review means a new spec version.
- **B.** §9 values are provisional; AC-UI-025 checks that tokens are used, not their values.

**Recommended:** A. It matches D-2 and D-11 and keeps the contrast figures valid.
**Answer:**

### Q-20 · D-2: must the accent be distinguishable from the success colour?
**Where:** D-2; §9 (F-24)
**Spec says:** «бирюзовый не совпадает ни с одним цветом состояний (danger / warning / success)»
**Why it matters:** Any two different colours "do not coincide". The accent `#3DD6B5` and success `#4CC38A` are close (contrast 1.21:1 between them, similar hue and lightness), so the reason does not show they cannot be confused.
**Options:**
- **A.** Distinguishability is required: success states always carry an icon and text, so colour is never the only cue (added as a rule).
- **B.** Not required at Stage 1: reword the reason and revisit when success states appear.

**Recommended:** B. No success state is used at Stage 1; decide when one appears.
**Answer:**

### Q-21 · D-4: should «Дневник» be renamed to avoid confusion with «дневник питания»?
**Where:** D-4; §7.4; §7.5 (F-25)
**Spec says:** D-4: «Короткие, совпадают с модулями product brief». «Питание» is described as «Дневник питания и рецепты…», and a Dashboard card says «по дневнику питания».
**Why it matters:** A user who wants to log a meal ("дневник питания") may tap «Дневник» and land in the notes journal. The brief's module is «Journal & Ideas», so the name does not exactly «match the brief».
**Options:**
- **A.** Keep «Дневник»; reword the reason.
- **B.** Rename the section (e.g., «Заметки») so «дневник» means only the food diary.

**Recommended:** B. It removes the collision before the name appears in more places.
**Answer:**

### Q-22 · D-6: should the Dashboard date update at midnight on an open page?
**Where:** D-6; AC-UI-007; D-3 (F-26)
**Spec says:** D-6: «До Этапа 5 на Dashboard нет данных, зависящих от даты.» AC-UI-007: «Дата … не меняется, пока страница открыта». D-3: «Повторная проверка нужна, чтобы баннер появлялся и исчезал вовремя (BR-1)».
**Why it matters:** The date on the Dashboard is itself date-dependent: opened at 23:50 on 27 Oct, at 00:10 it still says «вторник, 27 октября». D-3 uses "show the true state on time" as its reason; D-6 accepts a wrong date.
**Options:**
- **A.** Keep D-6 (date fixed until reload) and correct the reason.
- **B.** The date updates at local midnight on an open Dashboard.

**Recommended:** B. The date is the only live content on the Dashboard, so it should be true; it costs one timer and one test.
**Answer:**

### Q-23 · Which numbers use JetBrains Mono?
**Where:** §9 «Шрифты» (F-28)
**Spec says:** «Inter (текст), JetBrains Mono (числа)»
**Why it matters:** In «вторник, 27 октября» and «Этап 4», is the number set in the mono font inside an Inter sentence, or not?
**Options:**
- **A.** Every number anywhere is in JetBrains Mono.
- **B.** Only numeric data values (measurements, totals) are in JetBrains Mono; numbers inside text (dates, stage numbers) stay in Inter.

**Recommended:** B. Mixing fonts inside a short phrase looks broken, and Stage 1 has no data values.
**Answer:**

## Fixes that need no decision

| # | Where | Fix |
|---|---|---|
| 1 | AC-UI-006, §7.5, TC-UI-013 | Add «кроме баннера ошибки (AC-UI-021)» to «В рабочей области нет кнопок…» and to «Других элементов в рабочей области нет»; run TC-UI-013 with health UP (mocked) so that «0 кнопок» holds (F-03). |
| 2 | AC-UI-003, 007, 008, 009, 011, 021 | Split into single-behaviour criteria (new IDs, as was done for AC-UI-002 in v0.1+); update TC links and the matrix (F-17). |
| 3 | §7.2 schematic | Change «(карточки — по одной в ряд)» to «при 390 px — по одной в ряд; число колонок — §7.4» (F-19). |
| 4 | §9, §7.3 ⑤ | Add a token for the dimmed background (e.g., `--overlay` = black at 60 %) and refer to it in §7.3 ⑤ (F-22). |
| 5 | BR-2 | State that the dev showcase `/dev/ui` (development only) is exempt (F-27). |
| 6 | Термины, §2, BR-4, §7.3, D-10, TC-UI-001/003 | Replace bare «меню» with «выдвижное меню»; replace «компьютер / телефон / мобильный layout / Desktop / Mobile» with «широкий / узкий экран» outside the user stories (F-29). |
| 7 | Термины «Выдвижное меню» | «закрывается способами из AC-UI-002» → «закрывается способами из AC-UI-015, AC-UI-018, AC-UI-024» (F-30). |
| 8 | TC-UI-018, TC-UI-015, TC-UI-041 | Add: a response at 4.9 s gives no banner; an open Dashboard keeps its date across 23:59:59 → 00:00:00 (or the opposite, per Q-22); card columns at work-area widths 559/560 and 899/900 px (F-31). |

## After you answer

QA re-reviews the new version, checks that every answer above is reflected in the spec, and closes the questions.
