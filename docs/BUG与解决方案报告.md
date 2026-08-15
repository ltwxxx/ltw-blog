# 第二版个人博客 — Bug 与解决方案报告

本文档汇总了项目使用与开发过程中遇到的各类问题及对应解决办法，便于日后查阅与排查。

---

## 一、环境与运行相关

### 1.1 只运行 gen.py 后，页面没有变化

**现象**：执行 `python3 gen.py all` 或 `gen.py home` 后，在浏览器访问页面（如 http://localhost:8082/home.html）看不到更新。

**原因**：  
- 若通过 **Docker**（如 8082 端口）访问，页面来自**容器内构建时复制的静态文件**，不会随本机 `gen.py` 的生成结果变化。  
- `gen.py` 只更新本机项目下的 `html/` 目录，不会改写已运行容器里的文件。

**解决办法**：  
- **要看最新生成效果**：用本地静态服务或 Live Server 打开本机 `html/`。  
  - 运行 `./serve.sh`，浏览器访问 http://localhost:9000/home.html  
  - 或在 Cursor 中右键 `html` 文件夹 →「Open with Live Server」，再打开 `home.html`  
- **要让 Docker 里的页面也更新**：需重新构建并启动容器，例如执行 `./run-docker.sh` 或 `HOMEPAGE_PORT=8082 ./run-docker.sh`。

---

### 1.2 使用 Live Server 时，gen.py 生成后仍显示旧标题

**现象**：用 Live Server 打开首页，已运行 `gen.py home`，但主标题仍是一行「数据驱动 · Python开发 · 机器学习」，没有变成两行。

**原因**：  
- 标题原先由「一个带 `\n` 的字符串」+ 页面内 i18n 脚本用 `hero.title` 覆盖。  
- 若 i18n 加载的是旧数据、或路径/缓存导致未更新，或换行在部分环境下未正确保留，就会出现“改了数据但页面没变”的情况。

**解决办法**：  
- 改为**两行独立数据 + 两行独立 DOM**，不依赖单个字符串里的 `\n` 和 i18n 覆盖顺序：  
  - 在 `scripts/home/generator.py` 中按 `\n` 拆分 `hero_title`，得到 `hero_title_line1`、`hero_title_line2` 传给模板。  
  - 在 `templates/hero.html` 中用两个带 `data-i18n-key="hero.title_line1"` 和 `hero.title_line2"` 的块级 `<span>` 分别渲染两行。  
  - 在 `data/i18n.json`（及复制目标 `html/data/i18n.json`）中增加 `hero.title_line1`、`hero.title_line2`（中英文）。  
- 这样无论 i18n 是否加载、是否缓存，生成的 HTML 本身就是两行，Live Server 刷新即可看到「数据驱动 · Python」与「开发 · 机器学习」分两行显示。

---

### 1.3 从非项目根目录运行 gen.py 导致导入失败

**现象**：在其它目录执行 `python3 /path/to/gen.py all` 时，报错找不到 `scripts` 等模块。

**原因**：动态导入 `scripts.xxx` 时依赖当前 Python 路径；若工作目录不在项目根，项目根可能不在 `sys.path` 中。

**解决办法**：  
- 在 `gen.py` 的 `main()` 开头增加：  
  `sys.path.insert(0, str(Path(__file__).resolve().parent))`  
- 这样无论从哪个目录执行 `gen.py`，都能正确解析 `scripts` 包。

---

### 1.4 local_update.sh 显示「未跟踪」或无法执行

**现象**：  
- 在 Git 中看到 `local_update.sh` 为「未跟踪」。  
- 或执行 `./local_update.sh` 时提示权限不足。

**说明与处理**：  
- 「未跟踪」是 **Git 状态**（文件未 `git add`），与能否执行脚本无关。若希望纳入版本控制，执行 `git add local_update.sh`。  
- 无法执行多为**没有可执行权限**。在项目根执行：  
  `chmod +x local_update.sh`  
- 然后再执行：  
  `./local_update.sh`  
  或：  
  `bash local_update.sh`

---

### 1.5 执行 local_update.sh 时 SSH/上传失败

**现象**：运行 `./local_update.sh` 出现 `Host key verification failed` 或 `Permission denied`（如对 `/root/.ssh/known_hosts`），导致无法连接服务器或上传失败。

**原因**：  
- 脚本通过 SSH/SCP 连接服务器并上传代码，需要访问本机 `~/.ssh`（如 `known_hosts`、私钥）。  
- 在受限环境（如部分 IDE 终端沙箱）中可能无法访问这些文件。

**解决办法**：  
- 在**具备完整权限的终端**中执行脚本（例如系统终端或已授予「全部权限」的 Cursor 终端）。  
- 确保本机已配置好对目标服务器的 SSH 免密登录（公钥已加入服务器 `authorized_keys`）。

---

## 二、内容与链接相关

### 2.1 首页「项目经历」卡片点击打不开

**现象**：首页项目预览区的项目卡片点击后无法跳转到项目详情页。

**原因**：  
- 模板中使用了 `project.link`，但生成首页预览时只给每个项目设置了 `url`，没有设置 `link`，导致 `project.link` 为空，点击无效。

**解决办法**：  
- 在 `scripts/sections/project/generator.py` 的 `generate_projects_preview_html()` 中，对每个预览项目设置：  
  `project['link'] = project.get('url', '') or f"project/{project.get('project_path', '')}/content.html"`  
- 这样首页卡片使用的 `project.link` 会正确指向 `project/项目名/content.html`。

---

### 2.2 点击「Visit Projects Hub」进入项目列表后，项目详情链接打不开

**现象**：在 `project/index.html` 项目列表页点击某个项目的「查看详情」，地址变成类似 `.../project/project/项目名/content.html`，无法打开。

**原因**：  
- 列表页位于 `project/index.html`，即当前路径是 `.../project/`。  
- 若链接写成相对站点的 `project/项目名/content.html`，从 `project/` 解析会变成 `project/project/项目名/content.html`，路径错误。

**解决办法**：  
- 在 `generate_project_list_page()` 中，为列表页使用的项目数据设置**相对于 project 目录**的 URL：  
  `project['url'] = f"{project.get('project_path', '')}/content.html"`  
- 这样在 `project/index.html` 下点击会正确跳转到 `项目名/content.html`（即 `project/项目名/content.html`）。

---

### 2.3 项目列表页标题、描述为空，封面图不显示

**现象**：项目列表页（project/index.html）顶部大标题和描述为空，卡片封面图也不显示。

**原因**：  
- 模板使用了 `frame.page_main_title`、`frame.page_description`，但 `data/project/frame.json` 里没有这两个字段。  
- 模板使用了 `project.cover` 显示封面，而生成逻辑只提供了 `project.image`，没有 `cover`。

**解决办法**：  
- 在 `data/project/frame.json` 中增加：  
  `"page_main_title": "项目经历"`、`"page_description": "展示个人技术作品和项目实践"`。  
- 在 `generate_project_list_page()` 中，在渲染前为每个项目设置封面：  
  - 若有本地图片：`project['cover'] = f"{project.get('project_path', '')}/{project['image']}".lstrip('/')`（相对 project 目录的路径）；  
  - 否则：`project['cover'] = project.get('image') or ''`。

---

## 三、数据与脚本逻辑 Bug（已按计划修复）

### 3.1 博客预览：load_json_file 重复定义 + 缺少 article_name

**现象**：  
- 若某篇博客卡片使用本地图片且路径以 `./` 开头，生成首页博客预览时可能报 `KeyError: 'article_name'`。  
- 代码中存在两个完全相同的 `load_json_file` 定义，后者覆盖前者，造成冗余和困惑。

**解决办法**：  
- 在 `scripts/home/blog_preview.py` 中删除重复的 `load_json_file` 定义（保留一处）。  
- 在 `prepare_card_data()` 中根据 `article_path` 设置：  
  `card['article_name'] = article_path.split('/')[-1] if '/' in article_path else article_path`，  
  供后续图片路径拼接使用。

---

### 3.2 Docker 健康检查一直失败

**现象**：使用 `docker-compose` 时，服务健康检查持续失败。

**原因**：  
- 健康检查在**容器内**执行，而 Nginx 在容器内监听的是 **83** 端口。  
- 配置中误写为 `http://localhost:8081/`（8081 是宿主机映射端口），导致容器内 curl 无法访问。

**解决办法**：  
- 在 `docker-compose.yml` 的 healthcheck 中，将 URL 改为：  
  `http://localhost:83/`。

---

### 3.3 robots_generator 使用裸 except

**现象**：在 `scripts/common/robots_generator.py` 中使用 `except:` 会捕获包括 `KeyboardInterrupt`、`SystemExit` 在内的所有异常，影响调试和正常退出。

**解决办法**：  
- 将 `except:` 改为 `except Exception:`，仅在需要时记录日志或做降级处理。

---

## 四、路径与配置书写

### 4.1 local_update.sh 中 LOCAL_CODE_DIR 路径错误

**现象**：将 `LOCAL_CODE_DIR` 写成 `\home\ltw\files\第二版个人博客` 等形式，在 Linux/WSL 下路径无效。

**原因**：在 Linux/bash 中路径分隔符应为**正斜杠 `/`**，反斜杠 `\` 会被当作转义符，导致路径解析错误。

**解决办法**：  
- 使用正确格式，例如：  
  `LOCAL_CODE_DIR="/home/ltw/files/第二版个人博客"`  
- 确保脚本中所有路径都使用 `/`，不要使用 `\`。

---

## 五、移动端相关（功能修复与体验优化）

本节汇总手机端遇到的问题与优化项，部分参考 [UI/UX Pro Max Skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) 与 WCAG 触摸目标建议。

### 5.1 移动端搜索不可用

**现象**：在手机端点击导航栏搜索图标无反应，输入关键词后结果不展示。

**原因**：`templates/base.html` 中搜索逻辑依赖不存在的 DOM 元素：`mobile-search-container`、`mobile-search-input`、`mobile-search-results`，而 `templates/nav.html` 只提供一套 `search-container` / `search-input` / `search-results`。

**解决办法**（`templates/base.html`）：

- 删除对上述三个“移动端专用”元素的引用，桌面端与移动端共用同一套搜索 UI。
- 移动端搜索按钮（`mobile-search-btn`）点击时：切换 `search-container` 显示，并对 `search-input` 执行 `focus()`。
- 搜索输入与结果渲染只保留一套，结果统一输出到 `search-results`。
- 点击页面其他区域关闭搜索时，排除 `search-btn` 与 `mobile-search-btn`，避免误关。

---

### 5.2 导航栏：触摸目标、菜单滚动、安全区域

**现象 / 需求**：移动端按钮过小难点；菜单展开时背景仍可滚动；刘海屏下导航被遮挡。

**解决办法**：

- **触摸目标**（`templates/nav.html`）：移动端搜索按钮、菜单按钮增加 `min-w-[44px] min-h-[44px]` 与 `flex items-center justify-center`，满足约 44×44px 可点区域。
- **菜单展开时锁定背景滚动**（`templates/base.html`）：菜单展开时设置 `document.body.style.overflow = 'hidden'` 与 `document.documentElement.style.overflow = 'hidden'`，收起或点击锚点关闭菜单时恢复。
- **安全区域**（`templates/nav.html`）：导航栏增加 `pt-[env(safe-area-inset-top)]`；占位 div 改为 `min-h-[calc(4rem+env(safe-area-inset-top))] md:min-h-[calc(5rem+env(safe-area-inset-top))]`，与导航总高一致。

---

### 5.3 Viewport 与全局安全区域

**文件**：`templates/base.html`

- Viewport meta 增加 `viewport-fit=cover`，以便使用 `env(safe-area-inset-*)`。
- Body 增加 `pl-[env(safe-area-inset-left)] pr-[env(safe-area-inset-right)]`，横屏或刘海机左右不贴边。

---

### 5.4 Hero 区域：移动端蓝条、按钮与标题

**文件**：`templates/hero.html`

- **标题下蓝条**：波浪线 SVG 增加 `hidden md:block`，在宽度 &lt; 768px 时不显示。
- **按钮**：主 CTA 与「Download CV / Resume」增加 `min-h-[44px]`。
- **小屏标题**：标题增加 `text-3xl min-[375px]:text-4xl sm:text-5xl ...`，窄屏下减少拥挤。

---

### 5.5 博客区域：移动端每分类只显示一张卡片

**现象 / 需求**：移动端技术分享、机器学习、随想录下原为横向滑动多张卡片，存在展示/滑动体验问题，希望每分类只显示一张卡片。

**解决办法**（`templates/home/blog_preview.html`）：

- 移动端每个分类只展示该分类的第一张精选卡片（`category_cards[0]`），下方保留「查看全部 X 篇文章」按钮。
- 桌面端仍为网格布局不变。卡片组件根节点增加 class `card`（`templates/components/card.html`），便于统一样式。

---

### 5.6 页脚与项目卡片

**页脚**（`templates/footer.html`）：列表内链接增加 `block py-2.5 min-h-[44px] flex items-center`，列表容器使用 `space-y-0`，保证移动端可点区域足够。

**项目卡片**（`templates/home/project_preview.html`）：原为 `<div onclick="...">` 整卡跳转，改为 `<a href="{{ project.link }}">` 包裹整块内容，并增加 `focus-visible:ring-2` 等焦点样式，便于键盘与无障碍，且支持右键「在新标签页打开」。

---

### 5.7 移动端涉及文件一览

| 文件 | 修改要点 |
|------|----------|
| `templates/base.html` | 移动端搜索共用 UI、菜单展开时 body 滚动锁定、viewport-fit=cover、body 左右 safe-area |
| `templates/nav.html` | 导航 safe-area 顶部、占位高度、移动端按钮 44px 触摸目标 |
| `templates/hero.html` | 波浪线移动端隐藏、按钮 min-h-[44px]、标题小屏字号 |
| `templates/home/blog_preview.html` | 移动端每分类单卡片展示 |
| `templates/home/project_preview.html` | 项目卡片改为 `<a>` 包裹 |
| `templates/footer.html` | 链接触摸目标 py-2.5、min-h-[44px] |
| `templates/components/card.html` | 根节点增加 class `card` |

**验证建议**：真机或 Chrome 设备模式（如 375×667）检查搜索、菜单、博客单卡片、项目卡片、页脚链接；刘海屏下确认导航与内容不被遮挡；菜单打开时背景不滚动；Tab 切换时焦点环可见。

---

## 六、用 data copy 覆盖 data 目录

**需求**：用「data copy」文件夹的内容覆盖并同步到 `data` 目录。

**做法**：  
- 在项目根目录执行：  
  `rsync -av --delete "/path/to/第二版个人博客/data copy/" "/path/to/第二版个人博客/data/"`  
- 这样会以 `data copy/` 为源，覆盖 `data/` 并删除目标中多余文件，使两边一致。  
- 若之后需要重新生成整站，再执行 `python3 gen.py all`。

---

## 七、小结表

| 类别         | 现象简述                           | 处理要点 |
|--------------|------------------------------------|----------|
| 环境/运行    | gen.py 后页面不变                  | 区分 Docker 与本地：用 serve.sh/Live Server 看本地 html/，或重建容器 |
| 环境/运行    | Live Server 下标题仍是一行         | 改为两行变量 + 两行 DOM + i18n 的 title_line1/line2 |
| 环境/运行    | 非项目根运行 gen.py 导入失败       | main() 开头 sys.path.insert(0, 项目根) |
| 环境/运行    | local_update 未跟踪/无法执行       | Git 未跟踪需 git add；执行需 chmod +x |
| 环境/运行    | local_update SSH/上传失败          | 在完整权限终端运行，并确保 SSH 免密已配置 |
| 链接         | 首页项目卡片点不开                 | 预览数据中设置 project['link'] |
| 链接         | 项目列表页详情链接多一层 project/  | 列表页用相对 project/ 的 url（项目名/content.html） |
| 内容/展示    | 项目列表标题、描述、封面为空       | frame 增加 page_main_title/description；设置 project['cover'] |
| 脚本逻辑     | 博客预览 article_name KeyError     | prepare_card_data 中设置 card['article_name']；删除重复 load_json_file |
| 脚本逻辑     | Docker 健康检查失败               | healthcheck 用容器内端口 83 |
| 脚本逻辑     | robots 裸 except                   | 改为 except Exception |
| 路径/配置    | LOCAL_CODE_DIR 路径无效            | 使用 `/` 而非 `\` |
| 移动端       | 手机端搜索无反应、结果不展示       | 共用 search-container/input/results，mobile-search-btn 切换同一套 UI |
| 移动端       | 导航按钮过小、菜单展开时背景滚动   | 按钮 min-w/min-h 44px；菜单展开时 body/documentElement overflow hidden |
| 移动端       | 刘海屏遮挡、内容贴边               | viewport-fit=cover；nav pt safe-area；body pl/pr safe-area；占位高度含 safe-area |
| 移动端       | Hero 蓝条、按钮、标题小屏体验      | 波浪线 hidden md:block；按钮 min-h-[44px]；标题小屏字号断点 |
| 移动端       | 博客每分类多卡滑动体验问题         | 移动端每分类只显示第一张卡片，保留「查看全部」 |
| 移动端       | 页脚/项目卡片可点区域与无障碍     | 页脚链接 py-2.5 min-h-[44px]；项目卡片用 \<a\> 包裹并加 focus-visible 环 |

---

*报告生成自实际排查与修复记录，若后续有新增问题可继续追加到本文档。*
