# my-skills

个人 skill 收藏库：自用的 skills 直接以 `<name>/SKILL.md` 结构放本仓库，收藏的第三方 skills 只记录地址在 [`THIRD-PARTY-SKILLS.md`](THIRD-PARTY-SKILLS.md)，不复制源码。

## 直接下载某个 skill

```bash
git clone --depth 1 https://github.com/iHateTheWorld555/my-skills
```

把仓库里想用的 skill 目录（含 `SKILL.md`）复制到你 agent 的 skills 目录即可，例如：

```bash
cp -R my-skills/paper-review ~/.workbuddy/skills/
cp -R my-skills/doc-driven-dev ~/.workbuddy/skills/
```

不想 clone 整个仓库的话，也可以直接在 GitHub 网页上打开某个 skill 目录，用右上角 "Download" 或逐文件下载。

## 安装到 Claude Code / Codex / OpenClaw

多数 agent 的 skills 目录都是 `~/.<agent>/.claude/skills/` 或 `~/.<agent>/skills/`（workbuddy 用 `~/.workbuddy/skills/`）。把 skill 目录放进去后重启会话即可识别。目录名即 skill 名，见各 skill 内 `SKILL.md` 的 `name` 字段。
