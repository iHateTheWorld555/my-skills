#!/usr/bin/env python3
"""chinese-doc-writing 句子层机械化自检。

用法：
    python3 check.py <file.md> [file2.md ...]

只检查可机械化的句子层规则（见 SKILL.md 规则分档中 [CHECK] 项）。
结构、意图、豁免判断（被动句分支 3、公文体豁免等）需人工对表检查，
脚本不会给出，也不应给出。

检查项与依据：
- 弱动词（进行/作出/加以/实施/造成 + 抽象名词）—— 余光中 + 平克
- 单句「的」字 >= 3 —— 余光中
- 长定语（>12 字的「X 的 Y」）—— 余光中前后饰（近似检测）
- 句子构件分级（20/40 字）与整句 100 字 —— 阮一峰
- 段落 250 字 —— zh-style-guide
- 双重因果（由于…所以/使得）—— 余光中
- 中英文/数字间空格 —— 文案排版指北
- 全角标点旁空格、连续空格 —— 指北
- 语气与禁用词 —— zh-style-guide + Google
"""
import re
import sys
from pathlib import Path

# ---- 弱动词：万能动词 + 抽象名词后缀词 ----
WEAK_VERB = re.compile(
    r'(进行|作出|做出|加以|实施|给予|造成)(了|一|一個|一次|一頓)?'
    r'([一-鿿]{1,8}?(化|性|度|率|研究|分析|讨论|处理|修改|调整|改进|优化|说明|描述|介绍|评估|审查|调查|总结|确定|确认|安排|管理|控制|测试|试验|计算|部署|配置|备份|检查))'
)

# ---- 双重因果 ----
DOUBLE_CAUSAL = re.compile(r'由于[^。？！\n]{2,40}(所以|使得|因而造成)')

# ---- 禁用词（分档） ----
BANNED_MUST = [
    # 推销腔 / 不可验证断言（Google excessive-claims + MS 绝对化）
    '很简单', '只需三步', '轻松搞定', '业界领先', '最佳实践之一',
    # 黑话（ZH 禁用词表）
    '魔改', '墙裂', '童鞋', '不明觉厉', '喜大普奔',
]
BANNED_SHOULD = [
    # 占位语（Google please note 的中文形态）
    '需要注意的是', '值得注意的是', '值得一提的是',
    # 强调词（应换具体数据；豁免：引用原文、真正的强度判断）
    '非常', '极其', '高度',
    # 缓冲垫（配额在报告里给，不逐个判罚）
]
# 反问句与感叹号单独检测（有豁免逻辑）

BANNED_ABBREV = re.compile(r'\b(Ts|h5|RJS|nextjs)\b')

# ---- 中英文之间空格检测 ----
# 中文紧贴英文/数字（无空格）—— 指北 MUST
CJK_LATIN_NO_SPACE = re.compile(r'[一-鿿][A-Za-z0-9]|[A-Za-z0-9][一-鿿]')
# 排除：中文标点旁（如「，GitHub」虽也贴但那是标点规则）、纯数字与中文标点
# 全角标点旁的半角空格（MUST 禁止）。% $ 是半角符号不在此列——「30% 的折扣」合法。
FULLWIDTH_SPACE = re.compile(r'[，。；：？！、）】」』] | [（【「『]')
# 中文句子里夹半角标点（MUST 禁止，完整英文句除外）
HALF_PUNCT_IN_CJK = re.compile(r'[一-鿿][,;:!?][一-鿿]|[一-鿿][,;:!?]$|[,;:!?][一-鿿]')
MULTI_SPACE = re.compile(r'[^\n] {2,}')
# ---- AI 腔（ai-slop.md） ----
# 素材：本 agent 自己 63 万字历史输出的实测统计，不是外网词表。
# 外网 AI slop 词表（delve/赋能/抓手）在本 agent 语料中密度≈0，查它们等于查错对象。
# 本 agent 的腔长在句式结构上：纠正式揭示、数字化枚举、破折号澄清。
# 以下阈值取实测密度的高分位；单个命中正常，超阈值才是指纹。

# 纠正式揭示：「不是X，是Y」「才是」（密度指标，见 SLOP_DENSITY）
REVEAL_NOT_X_IS_Y = re.compile(r'不是[^。！？\n]{2,22}[，,]\s?(?:\*\*)?是[^。！？\n]{2,25}')
REVEAL_CAI_SHI = re.compile(r'[^。！？\n]{2,12}才是[^。！？\n]{2,20}')
# 验证腔配方（同一条回复里各 >1 次报警）
VERIFY_KIT = ['根因', '暴露了', '对得上', '对不上']
# 评价词通胀（合计 >3 报警）
PRAISE_KIT = ['干净', '稳妥', '齐了', '到位', '优雅', '更稳']
# 固定起手式/引出式
SLOP_STRUCT = [
    (r'(先说结论|确切结论|结论[：:]是?[^。！？\n]{0,3}核心)', '「先说结论」起手式'),
    (r'暴露了(一|两|三|几)?个?(真?问题|问题)', '「暴露了 N 个问题」引出'),
    (r'希望(这|以上|本).{0,10}(帮助|对你|有所)', '对话收尾泄漏'),
    (r'(如有|若)(任何)?(疑问|问题).{0,6}(请|随时|欢迎)', '对话收尾泄漏'),
    (r'(好的|当然)[！!]', '开场白泄漏'),
    (r'截至.{0,6}(知识|训练|数据)(更新|截止)', '知识截止声明'),
    (r'基于(现有|可用|公开)(资料|信息)', '免责声明泄漏'),
    (r'综上所述|总的来说|总而言之|不难看出|由此可见', '概括套话'),
    (r'深入(探讨|解析)|深度解析|全面解析|一文读懂', '标题套话'),
]
# 「不是X的问题，是Y」变体
NOT_A_PROBLEM = re.compile(r'不是[^。！？\n]{1,18}的问题[，,]\s?(?:\*\*)?是')

# 比喻词降载（ai-slop.md 第二节词表）：物理动词隐喻施于技术对象，密度 >2/千字报警
METAPHOR_VERBS = re.compile(
    r'卡(在|住|了)|塞(进|回|到)|挤(在|进|成|在一起)|拦(住|下)|绕(开|过)|埋(在|进|了)|'
    r'藏(在|进)|顶掉|兜(底|住)|漂移|残留|钉死|锁死|定死|躺在|洗牌|压扁|啃掉|误伤|'
    r'大胜利|归零消失|硬塞|撑成|挤成|压成'
)
# 警句式插入（10b）
APHORISM = re.compile(
    r'你其实一直在付|比[^。！？\n]{1,10}更(糟|可怕|危险)|这才是[^。！？\n]{0,12}(正确|诚实|真正)|'
    r'没人会用第二次|免费的午餐'
)
# 自我庆祝（10d，0 容忍）
SELF_CELEBRATE = re.compile(r'完美[！!]|完美(对应|还原)|大胜利|大功告成|漂亮仗')
# 行内标题列表：「**术语**：描述」×3 以上
INLINE_HEADER_LIST = re.compile(r'\*\*[^*\n]{2,20}\*\*[：:]\s')
EMOJI_FMT = re.compile(r'[\U0001F300-\U0001FAFF✅❌⭐✨❗]')

DOUBLE_NEG = re.compile(r'不[^。？！\n]{1,12}就不|不是不|不[^。？！\n]{1,8}不')


def strip_code_and_links(md: str) -> str:
    """剥离代码块、行内代码、链接 URL、frontmatter —— 它们不参与句子检查。"""
    t = re.sub(r'^---\n.*?\n---\n', '', md, flags=re.S)
    t = re.sub(r'```.*?```', ' ', t, flags=re.S)
    t = re.sub(r'`[^`]+`', 'CODE', t)
    t = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', t)  # 链接只留锚文本
    return t


def split_sentences(text: str):
    """整句：以。？！；分句。"""
    return [s for s in re.split(r'(?<=[。？！；])', text) if len(s.strip()) > 1]


def clause_units(sent: str):
    """句子构件：整句内按逗号、顿号切分。"""
    return [c for c in re.split(r'[，、]', sent) if c.strip()]


def check(path: Path):
    md = path.read_text(encoding='utf-8')
    t = strip_code_and_links(md)

    # 逐行保留行号；跳过标题行与列表标记对句子检查的影响
    lines = t.split('\n')
    issues = []   # (level, line_no, kind, detail)
    para_lengths = []

    cur_para: list[str] = []
    cur_para_start = 0

    def flush_para():
        if cur_para:
            body = ''.join(cur_para)
            n = len(re.sub(r'\s', '', body))
            para_lengths.append((n, cur_para_start))
        cur_para.clear()

    for i, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line:
            flush_para()
            continue
        if line.startswith(('#', '>', '|', '- [ ]')):
            flush_para()
            continue
        content = re.sub(r'^(\d+\.|[-*])\s*', '', line)
        if not cur_para:
            cur_para_start = i
        cur_para.append(content)

        # --- 弱动词 ---
        for m in WEAK_VERB.finditer(content):
            issues.append(('MUST', i, '弱动词', f'「{m.group()}」→ 还原为单一动词'))

        # --- 双重因果 ---
        for m in DOUBLE_CAUSAL.finditer(content):
            issues.append(('MUST', i, '双重因果', f'「{m.group(0)[:30]}…」→ 删「由于」或「{m.group(1)}」其一'))

        # --- 的字密度 ---
        de_count = content.count('的')
        if de_count >= 3:
            issues.append(('MUST', i, '的字连用', f'{de_count} 个「的」→ 并列改「而」或删可省的'))

        # --- 禁用词 ---
        for w in BANNED_MUST:
            if w in content:
                issues.append(('MUST', i, '禁用词', f'「{w}」'))
        if re.search(r'成功地|有效地|顺利地', content):
            issues.append(('SHOULD', i, 'junk 副词', '「成功地/有效地」多为冗余（余光中）'))
        if '们' in content and re.search(r'[一-鿿]们', content):
            issues.append(('SHOULD', i, '复数「们」', '「用户们」→「用户」或「各位用户」'))
        if '您' in content and '你' in content:
            issues.append(('MUST', i, '人称混用', '「你」与「您」同篇出现，禁混用'))
        for m in DOUBLE_NEG.finditer(content):
            issues.append(('SHOULD', i, '疑似双重否定', f'「{m.group()[:14]}」→ 改肯定句'))
        # --- AI 腔（逐行级：泄漏与格式指纹；密度级指标在文末统一算） ---
        for pat, kind in SLOP_STRUCT:
            for m in re.finditer(pat, content):
                lvl = 'MUST' if '泄漏' in kind or kind in ('知识截止声明', '免责声明泄漏') else 'SHOULD'
                issues.append((lvl, i, kind, f'「{m.group()[:22]}」'))
        n_ihl = len(INLINE_HEADER_LIST.findall(content))
        if n_ihl >= 3:
            issues.append(('MUST', i, '行内标题列表', f'{n_ihl} 个「**X**：」→ 改表格或小节'))
        for m in EMOJI_FMT.finditer(content):
            issues.append(('MUST', i, 'emoji 作格式', f'{m.group()} → 删（文档正文 0 容忍）'))
            break
        for m in SELF_CELEBRATE.finditer(content):
            issues.append(('MUST', i, '自我庆祝', f'「{m.group()}」→ 平叙验证结果'))
        for m in HALF_PUNCT_IN_CJK.finditer(content):
            frag = content[max(0, m.start() - 4):m.end() + 4]
            issues.append(('MUST', i, '中文句夹半角标点', f'…{frag}…'))
            break
        for w in BANNED_SHOULD:
            if w in content:
                issues.append(('SHOULD', i, '占位/强调词', f'「{w}」→ 删或换具体表述'))
        for m in BANNED_ABBREV.finditer(content):
            issues.append(('MUST', i, '不地道缩写', f'「{m.group()}」'))

        # --- 感叹号（豁免：警告行） ---
        if '！' in content and not re.search(r'(警告|危险|将永久|不可恢复|无法恢复|数据丢失)', content):
            issues.append(('MUST', i, '感叹号', '文档中禁用（强警示除外）'))

        # --- 反问句 ---
        if re.search(r'难道|岂不|何尝', content):
            issues.append(('MUST', i, '反问句', '反问让读者感觉被质疑'))

        # --- 中英混排空格 ---
        # 先移除数字与单位（10 GB 已带空格）、百分比、度数
        probe = re.sub(r'[0-9]+(\.[0-9]+)?\s?(GB|MB|KB|TB|ms|s|kHz|Hz|%|°)', 'UNIT', content)
        probe = re.sub(r'[A-Za-z][A-Za-z0-9.\-]*', 'ENG', probe)
        for m in CJK_LATIN_NO_SPACE.finditer(probe):
            frag = content[max(0, m.start() - 4):m.end() + 4]
            issues.append(('MUST', i, '中英文间缺空格', f'…{frag}…'))
            break  # 每行报一次即可

        # --- 全角标点旁空格 / 连续空格 ---
        for m in FULLWIDTH_SPACE.finditer(content):
            frag = content[max(0, m.start() - 3):m.end() + 3]
            issues.append(('MUST', i, '全角标点旁有空格', f'…{frag}…'))
            break
        for m in MULTI_SPACE.finditer(content):
            issues.append(('MUST', i, '连续半角空格', f'…{m.group()[:12]}…'))
            break

    flush_para()

    # --- 句长（全文级别） ---
    text_all = '\n'.join(lines)
    body_text = re.sub(r'^[#>|\-*\s]+', '', text_all, flags=re.M)
    sents = split_sentences(body_text)

    # --- 段落字数 ---
    for n, ln in para_lengths:
        if n > 250:
            issues.append(('MUST', ln, '段落过长', f'{n} 字 > 250（ZH 上限）'))

    # --- 输出 ---
    print(f'\n{"=" * 64}\n{path}\n{"=" * 64}')
    print(f'正文整句 {len(sents)} 句\n')

    if not issues:
        print('全部机械化检查项：0 命中')
    for level, ln, kind, detail in issues:
        mark = '!!' if level == 'MUST' else ' ~'
        print(f'{mark} L{ln:<5} [{level}] {kind}：{detail}')

    # 缓冲垫配额
    char_total = len(re.sub(r'\s', '', body_text))
    k = max(char_total / 1000, 0.001)
    buf = sum(body_text.count(w) for w in ('基本上', '某种程度上', '一般而言', '相对较好', '大概'))
    per_k = buf / k
    status = 'OK' if per_k <= 2 else '超标（逐个问：这个判断想承担多少责任）'
    print(f'\n-- 缓冲垫：{buf} 处 / {per_k:.1f} 每千字（配额 2） {status}')

    # 句子构件分级统计（阮一峰口径）
    lens = [len(c.strip()) for s in sents for c in clause_units(s)]
    if lens:
        over20 = sum(1 for x in lens if x > 20) / len(lens) * 100
        over40 = sum(1 for x in lens if x > 40)
        print(f'-- 构件：{len(lens)} 个，>20 字占 {over20:.0f}%（≤20 为佳），>40 字 {over40} 个（硬上限，应为 0）')
        for s in sents:
            for c in clause_units(s):
                if len(c.strip()) > 40:
                    ln = body_text[:body_text.find(c)].count('\n') + 1
                    print(f'   ~ L{ln} 构件 {len(c.strip())} 字：{c.strip()[:24]}…')

    must = sum(1 for x in issues if x[0] == 'MUST')
    should = sum(1 for x in issues if x[0] == 'SHOULD')

    # --- AI 腔密度级指标（ai-slop.md，阈值取本 agent 实测密度高分位） ---
    full = strip_code_and_links(md)
    kchar = max(len(re.sub(r'\s', '', full)) / 1000, 0.001)
    n_reveal = len(REVEAL_NOT_X_IS_Y.findall(full)) + len(REVEAL_CAI_SHI.findall(full)) + len(NOT_A_PROBLEM.findall(full))
    n_dash = full.count('——')
    n_ihl_total = len(INLINE_HEADER_LIST.findall(full))
    verify_counts = {w: full.count(w) for w in VERIFY_KIT if full.count(w) > 1}
    praise_total = sum(full.count(w) for w in PRAISE_KIT)
    n_metaphor = len(METAPHOR_VERBS.findall(full))
    n_aphorism = len(APHORISM.findall(full))

    slop_flags = []
    if n_reveal / kchar > 0.5:
        slop_flags.append(f'纠正式揭示 {n_reveal} 处/{n_reveal / kchar:.1f} 每千字（>0.5）：删掉没人预期的假象，直接陈述')
    if n_dash / kchar > 0.5:
        slop_flags.append(f'破折号 {n_dash} 处/{n_dash / kchar:.1f} 每千字（>0.5）：换逗号、括号、冒号')
    if n_ihl_total > 3 and n_ihl_total / kchar > 1.0:
        slop_flags.append(f'「**X**：」行内标题 {n_ihl_total} 处：连续 3 个改表格或小节')
    for w, n in verify_counts.items():
        if n >= 3:
            slop_flags.append(f'「{w}」{n} 次（配方词）：第二处换成实义表述')
    if praise_total > 3:
        slop_flags.append(f'评价词 {praise_total} 次（干净/稳妥/齐了/到位/优雅）：换事实，或保留 1 处')
    if n_metaphor / kchar > 2:
        slop_flags.append(f'物理动词隐喻 {n_metaphor} 处/{n_metaphor / kchar:.1f} 每千字（>2，10a 表）：换直述词')
    if n_aphorism >= 2:
        slop_flags.append(f'警句式插入 {n_aphorism} 处（10b）：同回复最多 1 处，其余平叙')

    print(f'\n-- AI 腔密度（阈值见 references/ai-slop.md） --')
    print(f'   揭示 {n_reveal} · 破折号 {n_dash}（{n_dash / kchar:.2f}/千字）· 行内标题 {n_ihl_total} · '
          f'评价词 {praise_total} · 动词隐喻 {n_metaphor} · 警句 {n_aphorism}')
    for f_ in slop_flags:
        print(f'   !! {f_}')
    if not slop_flags:
        print('   OK')

    print(f'\n合计：MUST {must} 项，SHOULD {should} 项')
    print('人工对表项（脚本不查）：被动句三分支豁免、公文体豁免、术语首现全称、'
          'scope 声明、标题系统、single intent、枚举成瘾、完成宣告、责任移交。')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    for a in sys.argv[1:]:
        p = Path(a).expanduser()
        if p.exists():
            check(p)
        else:
            print(f'文件不存在：{p}')
