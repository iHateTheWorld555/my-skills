import json
import os
import re
import subprocess
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
CLI = PACK / "bin/docdev"


class DocdevTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "project"

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *args, payload=None, now="2026-08-13 15:00", check=True):
        env = os.environ.copy()
        env["DOCDEV_NOW"] = now
        process = subprocess.run(
            [str(CLI), *map(str, args)],
            input=json.dumps(payload, ensure_ascii=False) if payload is not None else None,
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        stream = process.stdout if process.returncode == 0 else process.stderr
        result = json.loads(stream) if stream.strip() else None
        if check and process.returncode:
            self.fail(f"{process.args}\nstdout={process.stdout}\nstderr={process.stderr}")
        return process, result

    def init(self):
        self.initialized = self.run_cli("init", self.root, "--name", "科研项目")[1]
        return self.initialized

    def create(self, kind, content, title=None, now="2026-08-13 15:01"):
        payload = {"content": content}
        if title:
            payload["title"] = title
        return self.run_cli("doc", kind, "--project", self.root, payload=payload, now=now)[1]

    def work_days(self, *days, target=None):
        """把给定日期记入活跃日历（模拟这些天真的用过 docdev）。

        归档按活跃日计数，所以测试必须显式累积活跃日，
        不能像自然日那样直接把时钟拨到未来。
        """
        for day in days:
            self.run_cli(
                "read", target or self.initialized["index_id"],
                "--project", self.root, "--quiet", now=f"{day} 09:00",
            )

    def test_init_is_complete_and_idempotent(self):
        result = self.init()
        self.assertEqual(set(result["landing_ids"]), {"dataset", "model", "pipeline"})
        for relative in (
            "docs/ideas", "docs/landing", "docs/exps", "docs/decisions", "docs/lessons", "docs/assets",
            "exp", "src/model", "src/modules", "src/train", "src/infer", "src/preprocess", "src/eval",
            "src/util", "src/dashboard", "data", "pretrained", "dashboard", "scripts", "configs",
        ):
            self.assertTrue((self.root / relative).is_dir(), relative)
        for document_id in result["landing_ids"].values():
            record = json.loads((self.root / f"docs/.docdev/records/{document_id}.json").read_text())
            self.assertEqual(record["revision"], 1)
        second = self.run_cli("init", self.root)[1]
        self.assertTrue(second["existing"])
        self.assertEqual(second["landing_ids"], result["landing_ids"])
        self.assertTrue(set((self.root / ".gitignore").read_text().splitlines()) >= {"docs/", "assets/", "exp/"})

    def test_minimal_content_and_automatic_title_filename_time(self):
        self.init()
        idea = self.create("idea", "# 条件编码\n\n验证一种新方法。")
        self.assertEqual(idea["id"], "idea-20260813-条件编码")
        record = json.loads((self.root / f"docs/.docdev/records/{idea['id']}.json").read_text())
        self.assertEqual(record["data"], {"title": "条件编码", "content": "# 条件编码\n\n验证一种新方法。"})
        self.assertEqual(record["created_at"], "2026-08-13 15:01")
        self.assertEqual(record["updated_at"], "2026-08-13 15:01")
        self.assertTrue((self.root / idea["path"]).is_file())

    def test_landing_revision_and_no_op(self):
        initialized = self.init()
        payload = {"content": "路径：`data/train`\n\n切分种子：42"}
        changed = self.run_cli(
            "doc", "landing", "--id", "dataset", "--project", self.root,
            payload=payload, now="2026-08-13 15:02",
        )[1]
        self.assertEqual(changed["revision"], 2)
        no_op = self.run_cli(
            "doc", "landing", "--id", "dataset", "--project", self.root,
            payload=payload, now="2026-08-13 15:03",
        )[1]
        self.assertFalse(no_op["changed"])
        self.assertEqual(no_op["revision"], 2)
        self.assertEqual(no_op["updated_at"], "2026-08-13 15:02")
        renamed = self.run_cli(
            "doc", "landing", "--id", "dataset", "--project", self.root,
            payload={"title": "训练数据", "content": payload["content"]}, now="2026-08-13 15:04",
        )[1]
        self.assertEqual(renamed["revision"], 2)
        self.assertEqual(renamed["updated_at"], "2026-08-13 15:04")
        self.assertEqual(changed["id"], initialized["landing_ids"]["dataset"])

    def test_wikilinks_render_validate_search_and_reverse_refs(self):
        self.init()
        idea = self.create("idea", "研究条件编码", title="条件编码")
        exp = self.create("exp", f"验证 [[{idea['id']}|条件编码假设]]。", title="baseline")
        decision = self.create("decision", f"采用 [[{idea['id']}]]。", title="采用方案")
        text = (self.root / exp["path"]).read_text()
        self.assertIn("../ideas/", text)
        self.assertNotIn("[[", text)
        self.assertIn("条件编码", (self.root / decision["path"]).read_text())
        found = self.run_cli("search", "条件 编码", "--project", self.root)[1]
        self.assertIn(idea["id"], {item["id"] for item in found["results"]})
        reverse = self.run_cli("search", "", "--ref", idea["id"], "--project", self.root)[1]
        reverse_ids = {item["id"] for item in reverse["results"]}
        self.assertIn(exp["id"], reverse_ids)
        self.assertIn(decision["id"], reverse_ids)
        forward = self.run_cli("search", "", "--ref", decision["id"], "--project", self.root)[1]
        self.assertIn(idea["id"], {item["id"] for item in forward["results"]})
        self.run_cli(
            "doc", "idea", "--id", idea["id"], "--project", self.root,
            payload={"title": "新条件编码", "content": "研究条件编码"}, now="2026-08-13 15:05",
        )
        self.assertIn("新条件编码", (self.root / decision["path"]).read_text())
        self.assertTrue(self.run_cli("validate", "--project", self.root)[1]["ok"])

    def test_bad_reference_and_extra_slots_are_rejected(self):
        self.init()
        process, error = self.run_cli(
            "doc", "idea", "--project", self.root,
            payload={"content": "[[idea-20260813-missing]]"}, check=False,
        )
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("unresolved reference", error["error"])
        process, error = self.run_cli(
            "doc", "idea", "--project", self.root,
            payload={"content": "内容", "status": "candidate"}, check=False,
        )
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("unknown fields", error["error"])

    def test_exp_append_uses_only_content_and_time(self):
        self.init()
        exp = self.create("exp", "第一轮实验", title="baseline")
        appended = self.run_cli(
            "doc", "exp", "--id", exp["id"], "--append", "--project", self.root,
            payload={"content": "loss 正常下降。", "title": "启动检查"}, now="2026-08-13 15:10",
        )[1]
        self.assertEqual(appended["updated_at"], "2026-08-13 15:10")
        text = (self.root / exp["path"]).read_text()
        self.assertIn("2026-08-13 15:10 — 启动检查", text)
        self.assertIn("loss 正常下降", text)

    def test_clean_removes_only_debug_and_smoke_directories(self):
        self.init()
        for relative in ("exp/run-smoke", "exp/debug_case", "exp/keep", "exp/group/nested-smoke"):
            path = self.root / relative
            path.mkdir(parents=True)
            (path / "artifact.txt").write_text("x")
        keep = self.root / "exp/keep"
        debug_link = self.root / "exp/debug-link"
        debug_link.symlink_to(keep, target_is_directory=True)
        dry = self.run_cli("clean", "--dry-run", "--project", self.root)[1]
        self.assertEqual(dry["count"], 3)
        self.assertNotIn("exp/debug-link", dry["removed"])
        self.assertTrue((self.root / "exp/run-smoke").exists())
        cleaned = self.run_cli("clean", "--project", self.root)[1]
        self.assertEqual(cleaned["count"], 3)
        self.assertFalse((self.root / "exp/run-smoke").exists())
        self.assertFalse((self.root / "exp/debug_case").exists())
        self.assertFalse((self.root / "exp/group/nested-smoke").exists())
        self.assertTrue((self.root / "exp/keep").exists())
        self.assertTrue(debug_link.is_symlink())

    def test_clean_rejects_symlinked_exp_root(self):
        self.init()
        exp_root = self.root / "exp"
        exp_root.rmdir()
        exp_root.symlink_to(self.root / "data", target_is_directory=True)
        outside = self.root / "data/run-debug"
        outside.mkdir()
        process, error = self.run_cli("clean", "--project", self.root, check=False)
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("is a symlink", error["error"])
        self.assertTrue(outside.exists())

    def test_validate_fix_uses_records_as_source(self):
        self.init()
        idea = self.create("idea", "真实内容", title="真实标题")
        path = self.root / idea["path"]
        path.write_text("手工污染")
        self.assertEqual(self.run_cli("search", "手工污染", "--project", self.root)[1]["count"], 0)
        process, error = self.run_cli("validate", "--project", self.root, check=False)
        self.assertEqual(process.returncode, 4)
        self.assertTrue(any("differs" in issue for issue in error["issues"]))
        self.assertTrue(self.run_cli("validate", "--fix", "--project", self.root)[1]["ok"])
        self.assertIn("真实内容", path.read_text())

    def test_concurrent_same_title_allocates_unique_names(self):
        self.init()

        def create(index):
            return self.create("idea", f"不同内容 {index}", title="并发想法")["id"]

        with ThreadPoolExecutor(max_workers=4) as executor:
            ids = set(executor.map(create, range(4)))
        self.assertEqual(len(ids), 4)
        self.assertTrue(self.run_cli("validate", "--project", self.root)[1]["ok"])

    def test_interrupted_create_and_init_reconcile(self):
        initialized = self.init()
        idea = self.create("idea", "可恢复内容", title="可恢复")
        (self.root / idea["path"]).unlink()
        recovered = self.create("idea", "可恢复内容", title="可恢复")
        self.assertEqual(recovered["action"], "recover")
        self.assertTrue((self.root / idea["path"]).exists())
        marker = self.root / "docs/.docdev/project.json"
        marker.unlink()
        reinit = self.run_cli("init", self.root, "--name", "科研项目")[1]
        self.assertTrue(reinit["recovered"])
        self.assertEqual(reinit["landing_ids"], initialized["landing_ids"])

    def test_board_renders_sections_and_bidirectional_refs(self):
        self.init()
        idea = self.create("idea", "研究条件编码", title="条件编码")
        exp = self.create("exp", f"验证 [[{idea['id']}|条件编码假设]]。", title="baseline")
        decision = self.create("decision", f"采用 [[{idea['id']}]] 与 [[{exp['id']}]]。", title="采用方案")
        self.run_cli(
            "doc", "exp", "--id", exp["id"], "--append", "--project", self.root,
            payload={"content": "loss 正常下降。", "title": "启动检查"}, now="2026-08-13 15:10",
        )
        result = self.run_cli("board", "--project", self.root, now="2026-08-13 15:20")[1]
        self.assertEqual(result["path"], "docs/board.md")
        self.assertEqual(result["documents"], 7)
        self.assertEqual(result["counts"]["landing"], 3)
        self.assertEqual(result["edges"], 3)
        self.assertTrue(result["graph"])
        board = self.root / "docs/board.md"
        text = board.read_text()
        self.assertNotIn("[[", text)
        self.assertIn("```mermaid", text)
        for heading in ("## 项目脉搏", "## 交叉引用图谱", "## 交叉引用明细", "## 孤立文档",
                        "## 实验看板", "## Landing 状态", "## 决策速查", "## 经验速查", "## 最近活动"):
            self.assertIn(heading, text)
        self.assertIn(f"ideas/{idea['id']}.md", text)
        self.assertIn(f"exps/{exp['id']}.md", text)
        self.assertIn(decision["id"], text)
        forward = next(line for line in text.splitlines() if line.startswith(f"| [{exp['id']}]"))
        self.assertIn(idea["id"], forward)
        self.assertIn(decision["id"], forward)
        for link in re.findall(r"\]\(([^)]+)\)", text):
            self.assertTrue((board.parent / link).is_file(), link)

    def test_board_handles_empty_project_and_orphans(self):
        self.init()
        empty = self.run_cli("board", "--project", self.root, now="2026-08-13 15:21")[1]
        self.assertEqual(empty["edges"], 0)
        self.assertFalse(empty["graph"])
        self.assertEqual(empty["orphans"], 0)
        text = (self.root / "docs/board.md").read_text()
        self.assertNotIn("```mermaid", text)
        self.assertIn("暂无交叉引用", text)
        orphan = self.create("idea", "没人引用这个想法", title="孤立想法")
        result = self.run_cli("board", "--project", self.root, now="2026-08-13 15:22")[1]
        self.assertEqual(result["orphans"], 1)
        section = (self.root / "docs/board.md").read_text().split("## 孤立文档")[1].split("##")[0]
        self.assertIn(orphan["id"], section)

    def test_board_degrades_graph(self):
        self.init()
        idea = self.create("idea", "研究条件编码", title="条件编码")
        self.create("exp", f"验证 [[{idea['id']}]]。", title="baseline")
        capped = self.run_cli("board", "--project", self.root, "--max-nodes", "1", now="2026-08-13 15:23")[1]
        self.assertFalse(capped["graph"])
        self.assertEqual(capped["edges"], 1)
        text = (self.root / "docs/board.md").read_text()
        self.assertNotIn("```mermaid", text)
        self.assertIn("--max-nodes 1", text)
        self.assertIn("## 交叉引用明细", text)
        disabled = self.run_cli("board", "--project", self.root, "--no-graph", now="2026-08-13 15:24")[1]
        self.assertFalse(disabled["graph"])
        self.assertIn("--no-graph", (self.root / "docs/board.md").read_text())
        process, error = self.run_cli(
            "board", "--project", self.root, "--max-nodes", "0", check=False,
        )
        self.assertEqual(process.returncode, 2)
        self.assertIn("positive integer", error["error"])

    def test_board_is_side_effect_free(self):
        initialized = self.init()
        idea = self.create("idea", "研究条件编码", title="条件编码")
        self.create("decision", f"采用 [[{idea['id']}]]。", title="采用方案")
        self.run_cli(
            "doc", "index", "--project", self.root,
            payload={"content": f"当前目标：验证 [[{idea['id']}]]。"}, now="2026-08-13 15:30",
        )
        index_record = self.root / f"docs/.docdev/records/{initialized['index_id']}.json"
        before = index_record.read_text()
        documents = {path: path.read_text() for path in (self.root / "docs").rglob("*.md")}
        self.run_cli("board", "--project", self.root, now="2026-08-13 16:00")
        self.assertEqual(index_record.read_text(), before)
        self.assertIn("2026-08-13 15:30", before)
        for path, content in documents.items():
            self.assertEqual(path.read_text(), content, path.name)
        self.assertTrue(self.run_cli("validate", "--project", self.root)[1]["ok"])
        self.assertEqual(self.run_cli("search", "文档看板", "--project", self.root)[1]["count"], 0)
        polluted = self.root / idea["path"]
        polluted.write_text("手工污染")
        self.run_cli("board", "--project", self.root, now="2026-08-13 16:10")
        self.assertEqual(polluted.read_text(), "手工污染")
        process, error = self.run_cli("validate", "--project", self.root, check=False)
        self.assertEqual(process.returncode, 4)
        self.assertTrue(any("differs" in issue for issue in error["issues"]))

    def test_rm_reports_impact_and_refuses_referenced_documents(self):
        self.init()
        idea = self.create("idea", "研究条件编码", title="条件编码")
        exp = self.create("exp", f"验证 [[{idea['id']}|条件编码假设]]。", title="baseline")
        dry = self.run_cli("rm", idea["id"], "--project", self.root, "--dry-run")[1]
        self.assertEqual(dry["referenced_by"], [exp["id"]])
        self.assertFalse(dry["removed"])
        self.assertTrue((self.root / idea["path"]).is_file())
        process, error = self.run_cli("rm", idea["id"], "--project", self.root, check=False)
        self.assertEqual(process.returncode, 5)
        self.assertEqual(error["referenced_by"], [exp["id"]])
        self.assertTrue((self.root / idea["path"]).is_file())
        for kind in ("index", "landing"):
            target = self.run_cli("search", "", "--type", kind, "--project", self.root)[1]["results"][0]["id"]
            process, error = self.run_cli("rm", target, "--project", self.root, "--force", check=False)
            self.assertNotEqual(process.returncode, 0)
            self.assertIn("cannot be removed", error["error"])

    def test_rm_force_strips_references_and_keeps_project_valid(self):
        self.init()
        idea = self.create("idea", "研究条件编码", title="条件编码")
        exp = self.create("exp", f"验证 [[{idea['id']}|条件编码假设]] 与其他内容。", title="baseline")
        decision = self.create("decision", f"采用 [[{idea['id']}]]。", title="采用方案")
        self.run_cli(
            "doc", "exp", "--id", exp["id"], "--append", "--project", self.root,
            payload={"content": f"日志引用 [[{idea['id']}]]。", "title": "启动检查"}, now="2026-08-13 15:10",
        )
        removed = self.run_cli("rm", idea["id"], "--project", self.root, "--force", now="2026-08-13 15:20")[1]
        self.assertTrue(removed["removed"])
        self.assertEqual(removed["rewritten"], sorted([decision["id"], exp["id"]]))
        self.assertFalse((self.root / idea["path"]).exists())
        self.assertFalse((self.root / f"docs/.docdev/records/{idea['id']}.json").exists())
        exp_text = (self.root / exp["path"]).read_text()
        self.assertNotIn("[[", exp_text)
        self.assertIn("验证 条件编码假设 与其他内容", exp_text)
        self.assertIn("日志引用 条件编码。", exp_text)
        self.assertIn("采用 条件编码。", (self.root / decision["path"]).read_text())
        self.assertTrue(self.run_cli("validate", "--project", self.root)[1]["ok"])
        self.assertEqual(self.run_cli("search", "", "--ref", idea["id"], "--project", self.root)[1]["count"], 0)

    def test_search_is_lean_by_default_and_verbose_on_demand(self):
        self.init()
        idea = self.create("idea", "正文里写了 独有关键词 而标题没有", title="条件编码")
        self.create("exp", f"验证 [[{idea['id']}]]。", title="baseline")
        lean = self.run_cli("search", "独有关键词", "--project", self.root)[1]
        self.assertEqual(lean["count"], 1)
        self.assertEqual(set(lean["results"][0]), {"id", "type", "title", "updated_at"})
        verbose = self.run_cli("search", "独有关键词", "--verbose", "--project", self.root)[1]
        item = verbose["results"][0]
        self.assertEqual(item["id"], idea["id"])
        self.assertIn("独有关键词", item["snippet"])
        self.assertEqual(item["path"], idea["path"])
        self.assertIn("referenced_by", item)
        reverse = self.run_cli("search", "", "--ref", idea["id"], "--verbose", "--project", self.root)[1]
        self.assertEqual(reverse["results"][0]["referenced_by"], [])

    def test_index_has_no_catalog_only_a_pointer(self):
        initialized = self.init()
        self.create("idea", "研究条件编码", title="条件编码")
        self.create("lesson", "踩了一个坑", title="经验一")
        text = (self.root / f"docs/{initialized['index_id']}.md").read_text()
        for stale in ("## 想法索引", "## 经验索引", "| ID |", "- ["):
            self.assertNotIn(stale, text)
        self.assertIn("docs/ideas", text)
        self.assertIn("docs/archive/", text)
        self.assertIn("docdev read <id>", text)
        self.assertLess(len(text), 900, "index 应当只剩脉搏正文与一行指引")
        self.assertTrue(self.run_cli("validate", "--project", self.root)[1]["ok"])

    def test_schema_v2_records_migrate_to_v3(self):
        initialized = self.init()
        for path in (self.root / "docs/.docdev/records").glob("*.json"):
            record = json.loads(path.read_text())
            record["schema_version"] = 2
            record.pop("last_read", None)
            record.pop("archived", None)
            path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        marker = self.root / "docs/.docdev/project.json"
        project = json.loads(marker.read_text())
        project["schema_version"] = 2
        marker.write_text(json.dumps(project, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        self.assertTrue(self.run_cli("validate", "--project", self.root, now="2026-08-20 09:00")[1]["ok"])
        for path in (self.root / "docs/.docdev/records").glob("*.json"):
            record = json.loads(path.read_text())
            self.assertEqual(record["schema_version"], 3)
            self.assertFalse(record["archived"])
            # 迁移时刻即计时起点，不追溯历史 updated_at
            self.assertEqual(record["last_read"], "2026-08-20 09:00")
        self.assertEqual(json.loads(marker.read_text())["schema_version"], 3)
        self.assertEqual(json.loads(marker.read_text())["index_id"], initialized["index_id"])

    def test_read_records_access_without_touching_markdown(self):
        self.init()
        lesson = self.create("lesson", "# 经验\n\n正文内容。", title="经验")
        path = self.root / lesson["path"]
        before = path.read_bytes()
        result = self.run_cli("read", lesson["id"], "--project", self.root, now="2026-08-15 09:00")[1]
        self.assertEqual(result["last_read"], "2026-08-15 09:00")
        self.assertIn("正文内容", result["content"])
        self.assertFalse(result["archived"])
        self.assertEqual(path.read_bytes(), before, "read 不得改动生成的 Markdown")
        record = json.loads((self.root / f"docs/.docdev/records/{lesson['id']}.json").read_text())
        self.assertEqual(record["last_read"], "2026-08-15 09:00")
        self.assertEqual(record["updated_at"], lesson["updated_at"], "read 不是修改，updated_at 不变")
        quiet = self.run_cli("read", lesson["id"], "--project", self.root, "--quiet", now="2026-08-15 10:00")[1]
        self.assertNotIn("content", quiet)
        self.assertTrue(self.run_cli("validate", "--project", self.root)[1]["ok"])

    def test_archive_dry_run_then_apply_and_unarchive(self):
        self.init()
        lesson = self.create("lesson", "很久没读的经验", title="旧经验")
        active = self.root / lesson["path"]
        archived = self.root / f"docs/archive/lessons/{lesson['id']}.md"
        # 之后又工作了 6 个活跃日（读 index，不碰这篇 lesson）
        self.work_days("2026-08-14", "2026-08-15", "2026-08-16", "2026-08-17", "2026-08-18", "2026-08-19")
        dry = self.run_cli("archive", "--project", self.root, now="2026-08-20 09:00")[1]
        self.assertEqual(dry["action"], "dry-run")
        self.assertEqual([c["id"] for c in dry["candidates"]], [lesson["id"]])
        # 6 个补记的活跃日 + archive 当天（今天也算活跃）= 7
        self.assertEqual(dry["candidates"][0]["idle_active_days"], 7)
        self.assertEqual(dry["active_days_recorded"], 8)
        self.assertTrue(active.is_file(), "dry-run 不得移动文件")
        applied = self.run_cli("archive", "--apply", "--project", self.root, now="2026-08-20 09:00")[1]
        self.assertEqual(applied["archived"], [lesson["id"]])
        self.assertFalse(active.exists())
        self.assertTrue(archived.is_file())
        self.assertTrue(self.run_cli("validate", "--project", self.root)[1]["ok"])
        self.assertEqual(self.run_cli("search", "旧经验", "--project", self.root)[1]["count"], 0)
        found = self.run_cli("search", "旧经验", "--archived", "--project", self.root)[1]
        self.assertEqual(found["count"], 1)
        self.assertTrue(found["results"][0]["archived"])
        self.assertEqual(self.run_cli("search", "旧经验", "--all", "--project", self.root)[1]["count"], 1)
        restored = self.run_cli("unarchive", lesson["id"], "--project", self.root, now="2026-08-20 10:00")[1]
        self.assertTrue(restored["changed"])
        self.assertTrue(active.is_file())
        self.assertFalse(archived.exists())
        self.assertTrue(self.run_cli("validate", "--project", self.root)[1]["ok"])
        self.assertEqual(self.run_cli("search", "旧经验", "--project", self.root)[1]["count"], 1)

    def test_archive_protects_index_landing_and_idea(self):
        initialized = self.init()
        idea = self.create("idea", "常驻想法", title="想法")
        self.work_days(*[f"2026-08-{d:02d}" for d in range(14, 26)])
        dry = self.run_cli("archive", "--project", self.root, now="2026-09-30 09:00")[1]
        protected = {initialized["index_id"], idea["id"], *initialized["landing_ids"].values()}
        self.assertFalse(protected & {c["id"] for c in dry["candidates"]})
        process, error = self.run_cli("unarchive", idea["id"], "--project", self.root, check=False)
        self.assertTrue(error["ok"])
        self.assertFalse(error["changed"])

    def test_auto_archive_on_write_respects_recent_reads(self):
        self.init()
        stale = self.create("lesson", "没人读的经验", title="冷门经验")
        fresh = self.create("lesson", "会被读的经验", title="热门经验")
        self.work_days("2026-08-14", "2026-08-15", "2026-08-16")
        self.run_cli("read", fresh["id"], "--project", self.root, "--quiet", now="2026-08-17 09:00")
        self.work_days("2026-08-18", "2026-08-19")
        created = self.run_cli(
            "doc", "decision", "--project", self.root,
            payload={"content": "新决策"}, now="2026-08-20 09:00",
        )[1]
        self.assertEqual(created["auto_archived"], [stale["id"]])
        self.assertFalse((self.root / stale["path"]).exists())
        self.assertTrue((self.root / f"docs/archive/lessons/{stale['id']}.md").is_file())
        self.assertTrue((self.root / fresh["path"]).is_file(), "3 天前读过的文档不该被归档")
        self.assertTrue(self.run_cli("validate", "--project", self.root)[1]["ok"])

    def test_archived_references_stay_resolvable(self):
        self.init()
        lesson = self.create("lesson", "被引用的经验", title="经验")
        exp = self.create("exp", f"参考 [[{lesson['id']}|那条经验]]。", title="baseline")
        self.work_days("2026-08-14", "2026-08-15", "2026-08-16", "2026-08-17", "2026-08-18")
        self.run_cli("read", exp["id"], "--project", self.root, "--quiet", now="2026-08-19 09:00")
        applied = self.run_cli("archive", "--apply", "--project", self.root, now="2026-08-20 09:00")[1]
        self.assertEqual(applied["archived"], [lesson["id"]])
        exp_file = self.root / exp["path"]
        self.assertTrue(exp_file.is_file(), "刚读过的 exp 应留在活跃区")
        text = exp_file.read_text()
        self.assertNotIn("[[", text)
        links = re.findall(r"\]\(([^)]+)\)", text)
        self.assertTrue(any("archive/lessons" in link for link in links), links)
        for link in links:
            self.assertTrue((exp_file.parent / link).resolve().is_file(), f"死链: {link}")
        self.assertTrue(self.run_cli("validate", "--project", self.root)[1]["ok"])

    def test_idle_calendar_days_never_trigger_archiving(self):
        """长期不干活不该让文档被归档——这是活跃日计数存在的理由。"""
        self.init()
        lesson = self.create("lesson", "一条经验", title="经验")
        # 直接把时钟拨到三个月后：自然日过了 100 天，但期间零活跃日
        dry = self.run_cli("archive", "--project", self.root, now="2026-11-21 09:00")[1]
        self.assertEqual(dry["count"], 0, "休假期间不该有任何文档到期")
        self.assertTrue((self.root / lesson["path"]).is_file())
        # 回来以后陆续工作，到第 5 个活跃日仍未到期（阈值是“超过 5 个”）
        self.work_days("2026-11-22", "2026-11-23", "2026-11-24")
        still = self.run_cli("archive", "--project", self.root, now="2026-11-25 09:00")[1]
        self.assertEqual(still["count"], 0)
        # 第 6 个活跃日到来才归档
        now_due = self.run_cli("archive", "--project", self.root, now="2026-11-26 09:00")[1]
        self.assertEqual([c["id"] for c in now_due["candidates"]], [lesson["id"]])
        self.assertEqual(now_due["candidates"][0]["idle_active_days"], 6)
        calendar = json.loads((self.root / "docs/.docdev/calendar.json").read_text())
        self.assertNotIn("2026-09-15", calendar["active_days"], "没干活的日子不进日历")
        self.assertEqual(calendar["active_days"], sorted(set(calendar["active_days"])))

    def test_calendar_records_every_command_day(self):
        self.init()
        self.create("lesson", "经验", title="经验")
        self.run_cli("read", self.initialized["index_id"], "--project", self.root, "--quiet", now="2026-08-14 09:00")
        self.run_cli("archive", "--project", self.root, now="2026-08-15 09:00")
        calendar = json.loads((self.root / "docs/.docdev/calendar.json").read_text())
        self.assertEqual(calendar["active_days"], ["2026-08-13", "2026-08-14", "2026-08-15"])
        # 同一天多次调用只记一次
        self.run_cli("read", self.initialized["index_id"], "--project", self.root, "--quiet", now="2026-08-15 18:00")
        calendar = json.loads((self.root / "docs/.docdev/calendar.json").read_text())
        self.assertEqual(calendar["active_days"].count("2026-08-15"), 1)
        self.assertTrue(self.run_cli("validate", "--project", self.root)[1]["ok"])

    def test_cli_errors_are_json_and_limits_positive(self):
        process = subprocess.run([str(CLI), "doc", "bogus"], text=True, capture_output=True, check=False)
        self.assertEqual(process.returncode, 2)
        self.assertFalse(json.loads(process.stderr)["ok"])
        self.init()
        process, error = self.run_cli("search", "", "--limit", "0", "--project", self.root, check=False)
        self.assertEqual(process.returncode, 2)
        self.assertIn("positive integer", error["error"])


if __name__ == "__main__":
    unittest.main()
