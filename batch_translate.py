#!/usr/bin/env python3
"""
批量论文精读脚本 - 逐篇PDF解析+LLM全翻译
支持: 断点续传 | 失败重试(最多5次) | 进度追踪 | 并行控制
"""

import json
import os
import sqlite3
import sys
import time
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from paper_learning_hub.models import AppConfig, CandidatePaper
from paper_learning_hub.translator import translate_paper, create_translator
from paper_learning_hub.parser import parse_document
from paper_learning_hub.utils import ensure_dir

# ============================================================
# 配置
# ============================================================
PROJECT_DIR = Path(__file__).parent
DB_PATH = PROJECT_DIR / "papers.db"
ZH_DIR = PROJECT_DIR / "papers/zh"
RAW_DIR = PROJECT_DIR / "papers/raw"
JOBS_DIR = PROJECT_DIR / ".workbuddy" / "jobs"
RESULTS_DIR = PROJECT_DIR / ".workbuddy" / "results"

MAX_RETRIES = 5       # 单篇最大重试次数
CHUNK_DELAY = 2        # chunk间延迟(秒)
BATCH_SIZE = 5         # 每批处理数量(用于进度汇报)

# 加载配置
def load_config():
    import yaml
    with open(PROJECT_DIR / "config.yaml", "r") as f:
        cfg = yaml.safe_load(f)
    
    class TranslatorSettings:
        backend = cfg["translator"]["backend"]
        base_url = cfg["translator"]["base_url"]
        model = cfg["translator"]["model"]
        api_key_env = cfg["translator"]["api_key_env"]
        system_prompt = cfg["translator"]["system_prompt"]
        timeout_seconds = cfg["translator"].get("timeout_seconds", 120)
        chunk_chars = cfg["translator"].get("chunk_chars", 4000)
        max_images_per_paper = cfg["translator"].get("max_images_per_paper", 20)
    
    class SiteSettings:
        site_name = cfg["site"]["site_name"]
        site_url = cfg["site"]["site_url"]
        docs_dir = PROJECT_DIR / "site" / "docs"
    
    config = AppConfig(
        repo_name="paper-learning-hub",
        site=SiteSettings(),
        translator=TranslatorSettings(),
    )
    return config


# ============================================================
# 获取待精读论文列表
# ============================================================
def get_pending_papers():
    """获取所有有PDF但尚未完成精读的论文"""
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute("""
        SELECT p.paper_id, p.title, p.organization, p.publish_date, 
               p.theme, p.source_name, p.source_url, p.paper_url, 
               p.summary, p.priority, p.raw_path, p.status,
               CASE WHEN EXISTS(SELECT 1 FROM papers z WHERE z.paper_id=p.paper_id AND z.zh_path IS NOT NULL AND z.zh_path != '')
                    THEN (SELECT length(zh.content) FROM zh_files zh WHERE zh.paper_id=p.paper_id LIMIT 1)
                    ELSE 0 END as zh_size
        FROM papers p 
        WHERE p.status IN ('downloaded', 'queued', 'translated')
        ORDER BY 
            CASE WHEN p.status='translated' THEN 0 ELSE 1 END,
            p.priority DESC,
            p.paper_id
    """).fetchall()
    conn.close()
    
    pending = []
    for r in rows:
        # 检查是否已有有效精读文件
        zh_path = ZH_DIR / r[0] / "paper_zh.md"
        if zh_path.exists() and zh_path.stat().st_size > 500:
            continue  # 已有有效精读，跳过
        
        # 检查PDF是否存在
        raw_path = Path(r[10]) if r[10] else RAW_DIR / r[0] / "paper.pdf"
        if not raw_path.exists():
            print(f"  ⚠️ {r[0]} PDF不存在: {raw_path}")
            continue
            
        pending.append(CandidatePaper(
            paper_id=r[0], title=r[1], organization=r[2],
            publish_date=r[3], theme=r[4], source_name=r[5],
            source_url=r[6], paper_url=r[7], summary=r[8],
            priority=r[9], status=r[11] if r[11] else 'downloaded'
        ))
    
    return pending


# ============================================================
# 写入 result.json
# ============================================================
def write_result(paper_id: str, status: str, target_path: str = None, notes: str = "", retry_count: int = 0):
    ensure_dir(RESULTS_DIR)
    result_file = RESULTS_DIR / f"{paper_id}.json"
    result = {
        "paper_id": paper_id,
        "status": status,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "notes": notes,
        "retry_count": retry_count,
    }
    if target_path:
        result["target_markdown"] = str(target_path)
    result_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


# ============================================================
# 读取已存在的结果
# ============================================================
def read_result(paper_id: str) -> dict:
    result_file = RESULTS_DIR / f"{paper_id}.json"
    if result_file.exists():
        return json.loads(result_file.read_text(encoding="utf-8"))
    return None


# ============================================================
# 单篇精读（带重试）
# ============================================================
def process_single_paper(config, paper: CandidatePaper) -> bool:
    """处理单篇论文，返回是否成功"""
    paper_id = paper.paper_id
    
    # 检查已有的重试次数
    existing = read_result(paper_id)
    retry_count = existing.get("retry_count", 0) if existing else 0
    
    if retry_count >= MAX_RETRIES:
        print(f"  ❌ {paper_id} 已达最大重试次数({MAX_RETRIES})，跳过")
        write_result(paper_id, "failed", notes=f"超过最大重试次数{MAX_RETRIES}", retry_count=retry_count)
        return False
    
    raw_path = RAW_DIR / paper_id / "paper.pdf"
    
    for attempt in range(retry_count + 1, MAX_RETRIES + 1):
        try:
            print(f"  📝 [{paper_id}] 第{attempt}次尝试翻译...")
            
            output_path = translate_paper(config, paper, raw_path)
            
            file_size = output_path.stat().st_size
            if file_size < 500:
                raise ValueError(f"输出文件过小({file_size}B)，可能是翻译失败")
            
            print(f"  ✅ {paper_id} 精读完成 ({file_size/1024:.0f}KB)")
            
            # 更新DB状态
            conn = sqlite3.connect(str(DB_PATH))
            ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
            zh_rel = f"papers/zh/{paper_id}/paper_zh.md"
            conn.execute("""UPDATE papers SET status='translated', zh_path=?, updated_at=? WHERE paper_id=?""",
                         (zh_rel, ts, paper_id))
            conn.commit(); conn.close()
            
            write_result(paper_id, "completed", str(output_path), notes=f"第{attempt}次成功", retry_count=attempt)
            return True
            
        except Exception as e:
            err_msg = str(e)[:200]
            print(f"  ⚠️ {paper_id} 第{attempt}次失败: {err_msg}")
            write_result(paper_id, "failed", notes=f"尝试{attempt}: {err_msg}", retry_count=attempt)
            
            if attempt < MAX_RETRIES:
                wait = min(30, 2 ** attempt)
                print(f"  ⏳ 等待{wait}秒后重试...")
                time.sleep(wait)
    
    # 全部重试失败
    write_result(paper_id, "failed", notes="全部重试耗尽", retry_count=MAX_RETRIES)
    return False


# ============================================================
# 主流程
# ============================================================
def main():
    print("=" * 60)
    print("📚 Paper Learning Hub - 批量精读模式")
    print("=" * 60)
    
    # 检查 API Key
    api_key_env = os.environ.get("OPENAI_API_KEY", "")
    if not api_key_env:
        print("❌ 错误: 未设置 OPENAI_API_KEY 环境变量")
        print("   请运行: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    print(f"✅ API Key 已配置 ({api_key_env[:10]}...)")
    
    # 加载配置
    try:
        config = load_config()
        print(f"✅ 配置加载成功 | 模型: {config.translator.model} | 后端: {config.translator.backend}")
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        sys.exit(1)
    
    # 创建目录
    ensure_dir(ZH_DIR)
    ensure_dir(JOBS_DIR)
    ensure_dir(RESULTS_DIR)
    
    # 获取待处理列表
    pending = get_pending_papers()
    total = len(pending)
    print(f"\n📋 待精读论文: {total} 篇")
    
    if total == 0:
        print("\n🎉 所有论文已完成精读！")
        return
    
    # 列出前10篇预览
    print("\n前10篇:")
    for i, p in enumerate(pending[:10]):
        print(f"  {i+1}. [{p.paper_id}] {p.title[:60]}")
    if total > 10:
        print(f"  ... 还有 {total-10} 篇")
    
    # 统计变量
    success_count = 0
    fail_count = 0
    start_time = time.time()
    
    print(f"\n{'='*60}")
    print(f"⏱️  开始精读 ({time.strftime('%H:%M:%S')})")
    print(f"{'='*60}\n")
    
    for idx, paper in enumerate(pending):
        print(f"\n[{idx+1}/{total}] 📄 {paper.title[:55]}")
        print(f"  ID: {paper.paper_id} | 方向: {paper.theme}")
        
        ok = process_single_paper(config, paper)
        
        if ok:
            success_count += 1
        else:
            fail_count += 1
        
        # 批量进度汇报
        if (idx + 1) % BATCH_SIZE == 0 or idx == total - 1:
            elapsed = time.time() - start_time
            rate = (idx + 1) / elapsed * 60 if elapsed > 0 else 0
            print(f"\n--- 进度: {idx+1}/{total} | ✅{success_count} ❌{fail_count} | {rate:.1f}篇/分钟 | 已耗时{elapsed/60:.1f}min ---")
        
        # 篇间延迟（避免API限流）
        if idx < total - 1:
            time.sleep(CHUNK_DELAY)
    
    # 最终报告
    total_time = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"📊 精读完成!")
    print(f"{'='*60}")
    print(f"  总计: {total} 篇 | 成功: {success_count} | 失败: {fail_count}")
    print(f"  总耗时: {total_time/60:.1f} 分钟")
    print(f"  平均每篇: {total_time/max(total,1):.0f} 秒")
    
    if fail_count > 0:
        print(f"\n⚠️ {fail_count} 篇失败，可重新运行此脚本进行重试")


if __name__ == "__main__":
    main()
