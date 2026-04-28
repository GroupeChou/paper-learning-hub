from __future__ import annotations

import logging
import random
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models import CandidatePaper
from .utils import ensure_dir

logger = logging.getLogger(__name__)

# ============================================================
# 常量配置
# ============================================================

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 "
    "(+https://github.com/GroupeChou/paper-learning-hub; academic use)"
)

# arXiv 推荐的最低请求间隔（秒）
ARXIV_MIN_DELAY = 1.0
# 额外随机抖动范围（秒），避免固定节奏被识别为机器人
ARXIV_JITTER = (0.5, 2.0)

# 重试策略
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2  # 秒，指数退避基数
RETRY_STATUS_FORCELIST = (429, 500, 502, 503, 504)

# 下载超时（秒）
CONNECT_TIMEOUT = 15   # 连接超时
READ_TIMEOUT_MULTIPLIER = 10  # 读超时 = 文件大小(MB) * 此值，最小 30s
READ_TIMEOUT_MIN = 30
READ_TIMEOUT_MAX = 300


class DownloadError(RuntimeError):
    """下载失败的统一异常。"""


# ============================================================
# Session 工厂：带重试 + 连接池
# ============================================================

def _create_session() -> requests.Session:
    """创建一个带自动重试和连接池的 Session。

    - 同一个 host 复用 TCP 连接（pool_connections=10）
    - 遇到 429/5xx 自动重试最多 MAX_RETRIES 次
    - 重试间指数退避
    """
    session = requests.Session()

    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=1,
        status_forcelist=RETRY_STATUS_FORCELIST,
        allowed_methods=["GET", "HEAD"],
        raise_on_status=False,  # 我们自己处理状态码
    )
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=10,
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    session.headers.update({
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "application/pdf,*/*",
        "Accept-Language": "en-US,en;q=0.9",
    })
    return session


# 全局 Session 实例（模块级复用）
_session: requests.Session | None = None


def _get_session() -> requests.Session:
    global _session
    if _session is None:
        _session = _create_session()
    return _session


def close_session() -> None:
    """显式关闭全局 Session（用于 cleanup）。"""
    global _session
    if _session:
        _session.close()
        _session = None


# ============================================================
# URL 解析与候选生成
# ============================================================

def _normalize_arxiv_pdf(url: str) -> str:
    """将 arXiv abs 页面 URL 转为 PDF 直链。"""
    if "arxiv.org/abs/" in url and not url.endswith(".pdf"):
        return url.replace("/abs/", "/pdf/") + ".pdf"
    return url


def _get_arxiv_pdf_url_candidates(arxiv_id: str) -> list[str]:
    """为一个 arXiv ID 生成多个候选 PDF URL。

    优先级从高到低：
    1. ar5iv HTML 版本（轻量，可 fallback 用）
    2. 标准 PDF 直链
    3. export.arxiv.org API 格式（备用）
    """
    base_id = arxiv_id.replace("v1", "").replace("v2", "").replace("v3", "")
    return [
        f"https://arxiv.org/pdf/{arxiv_id}",                    # 标准直链
        f"https://export.arxiv.org/api/query?id_list={base_id}",  # API 备用
        f"https://ar5iv.labs.arxiv.org/html/{arxiv_id}",          # HTML 备用
    ]


def _best_document_link(page_url: str, html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    page_host = urlparse(page_url).netloc
    pdf_candidates: list[str] = []
    arxiv_candidates: list[str] = []
    for anchor in soup.select("a[href]"):
        href = urljoin(page_url, anchor["href"])
        if href.endswith(".pdf"):
            if urlparse(href).netloc == page_host:
                return href, "pdf"
            pdf_candidates.append(href)
        if "arxiv.org/abs/" in href or "arxiv.org/pdf/" in href:
            arxiv_candidates.append(_normalize_arxiv_pdf(href))
    if pdf_candidates:
        return pdf_candidates[0], "pdf"
    if arxiv_candidates:
        return arxiv_candidates[0], "pdf"
    return page_url, "html"


# ============================================================
# 核心：智能下载（带重试 + 限流 + 流式写入）
# ============================================================

def resolve_download_target(candidate: CandidatePaper, timeout: int = 30) -> tuple[str, str]:
    """解析论文的真实下载目标 URL。"""
    paper_url = _normalize_arxiv_pdf(candidate.paper_url)
    if paper_url.endswith(".pdf"):
        return paper_url, "pdf"

    session = _get_session()
    response = session.get(paper_url, timeout=(CONNECT_TIMEOUT, timeout))
    response.raise_for_status()
    content_type = response.headers.get("content-type", "")
    if "pdf" in content_type:
        return paper_url, "pdf"
    return _best_document_link(paper_url, response.text)


def _download_with_retry(
    url: str,
    output_path: Path,
    *,
    session: requests.Session | None = None,
    max_retries: int = MAX_RETRIES,
    chunk_size: int = 8192,
) -> None:
    """带重试、流式写入的下载核心函数。

    Args:
        url: 下载目标 URL
        output_path: 输出文件路径
        session: 可选的复用 Session
        max_retries: 最大重试次数
        chunk_size: 写入块大小（字节）

    Raises:
        DownloadError: 所有重试均失败后抛出
    """
    sesh = session or _get_session()
    last_exc: Exception | None = None

    for attempt in range(1, max_retries + 1):
        # ---- 限流延迟（首次不等待）----
        if attempt > 1:
            delay = RETRY_BACKOFF_BASE ** (attempt - 1) + random.uniform(*ARXIV_JITTER)
            logger.info("[attempt %d/%d] 等待 %.1fs 后重试 %s", attempt, max_retries, delay, url)
            time.sleep(delay)

        try:
            # ---- 先 HEAD 获取文件大小（用于动态设置读超时）----
            head_resp = sesh.head(
                url,
                timeout=(CONNECT_TIMEOUT, 15),
                allow_redirects=True,
            )
            head_resp.raise_for_status()

            content_length = head_resp.headers.get("content-length")
            file_mb = int(content_length) / (1024 * 1024) if content_length else 5  # 默认 5MB
            read_timeout = min(max(int(file_mb) * READ_TIMEOUT_MULTIPLIER, READ_TIMEOUT_MIN), READ_TIMEOUT_MAX)

            logger.info("下载 %s (~%.1f MB, timeout=%ds) [尝试 %d/%d]", url, file_mb, read_timeout, attempt, max_retries)

            # ---- 流式 GET 写入磁盘 ----
            with sesh.get(
                url,
                timeout=(CONNECT_TIMEOUT, read_timeout),
                stream=True,
            ) as resp:
                resp.raise_for_status()

                # 验证 Content-Type
                ct = resp.headers.get("content-type", "")
                if "html" in ct.lower() and "pdf" not in ct.lower():
                    body_preview = resp.content[:500].decode("utf-8", errors="replace")
                    if "<title>" in body_preview.lower() and ("not found" in body_preview.lower() or "404" in body_preview.lower()):
                        raise DownloadError(f"服务器返回 404 页面 (Content-Type: {ct})")

                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "wb") as f:
                    downloaded = 0
                    for chunk in resp.iter_content(chunk_size=chunk_size):
                        if chunk:  # 过滤 keep-alive 空块
                            f.write(chunk)
                            downloaded += len(chunk)

            # ---- 校验 ----
            if output_path.stat().st_size == 0:
                output_path.unlink(missing_ok=True)
                raise DownloadError(f"下载文件为空: {url}")

            logger.info("✅ 下载成功 %s (%d bytes)", url, output_path.stat().st_size)
            return  # 成功，退出重试循环

        except requests.exceptions.HTTPError as e:
            last_exc = e
            status = e.response.status_code if e.response is not None else 0
            logger.warning("HTTP %d [尝试 %d/%d]: %s", status, attempt, max_retries, e)
            if status in (404, 403, 410):
                # 404/403/410 不值得重试
                raise DownloadError(f"不可恢复的 HTTP 错误 {status}: {url}") from e

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            last_exc = e
            logger.warning("网络异常 [尝试 %d/%d]: %s", attempt, max_retries, e)

        except DownloadError as e:
            last_exc = e
            logger.warning("下载错误 [尝试 %d/%d]: %s", attempt, max_retries, e)

        except Exception as e:
            last_exc = e
            logger.warning("未知错误 [尝试 %d/%d]: %s", attempt, max_retries, e)

    # 所有重试均失败
    raise DownloadError(f"下载失败（已重试 {max_retries} 次）: {url} — {last_exc}") from last_exc


def _rate_limit_delay(paper_index: int, total: int) -> None:
    """在两次下载之间插入限流延迟。

    策略：
    - 第一篇不等待
    - 之后每篇至少 ARXIV_MIN_DELAY 秒
    - 加上随机抖动避免被检测为机器人行为
    """
    if paper_index <= 0:
        return
    base_delay = ARXIV_MIN_DELAY
    jitter = random.uniform(*ARXIV_JITTER)
    total_delay = base_delay + jitter
    logger.info("[限流] 第 %d/%d 篇，等待 %.1fs ...", paper_index + 1, total, total_delay)
    time.sleep(total_delay)


# ============================================================
# 公开接口（保持向后兼容）
# ============================================================

def download_paper(candidate: CandidatePaper, raw_root: Path, timeout: int = 60) -> Path:
    """下载单篇论文 PDF 到本地（增强版：重试+限流+流式写入）。

    保持与原始接口签名一致，可无缝替换。
    """
    paper_dir = ensure_dir(raw_root / candidate.paper_id)
    target_url, target_type = resolve_download_target(candidate, timeout=timeout)
    suffix = ".pdf" if target_type == "pdf" else ".html"
    output_path = paper_dir / f"paper{suffix}"

    # 已存在则跳过
    if output_path.exists() and output_path.stat().st_size > 0:
        logger.info("⏭️ 已存在，跳过: %s (%d bytes)", candidate.paper_id, output_path.stat().st_size)
        return output_path

    # 尝试主 URL 下载
    _download_with_retry(target_url, output_path)

    # 如果主 URL 返回了 HTML（可能是重定向到了 abs 页面），尝试备用 arXiv 格式
    if target_type != "pdf":
        return output_path

    # 验证是否真的是 PDF（防止被重定向到 HTML 错误页）
    if output_path.exists() and output_path.stat().st_size < 1024:
        head_bytes = output_path.read_bytes()[:20]
        if b"%PDF" not in head_bytes:
            logger.warning("下载内容不是有效 PDF，尝试备用 URL ...")
            output_path.unlink(missing_ok=True)
            # 尝试备选 URL
            candidates = _get_arxiv_pdf_url_candidates(candidate.paper_id)
            for alt_url in candidates[1:]:  # 跳过第一个（已经试过的主 URL）
                try:
                    _download_with_retry(alt_url, output_path)
                    break
                except DownloadError:
                    continue
            else:
                raise DownloadError(f"所有候选 URL 均失败: {candidate.paper_id}")

    return output_path


def batch_download_papers(
    papers: list[CandidatePaper],
    raw_root: Path,
    *,
    skip_existing: bool = True,
    on_progress=None,
) -> dict[str, tuple[Path | None, str | None]]:
    """批量下载多篇论文，内置限流和进度回调。

    Args:
        papers: 待下载的论文列表
        raw_root: 原始文件根目录
        skip_existing: 是否跳过已有文件
        on_progress: 可选的进度回调 `(index, total, paper_title, success, error_msg)`

    Returns:
        dict[paper_id] -> (output_path_or_None, error_msg_or_None)
    """
    results: dict[str, tuple[Path | None, str | None]] = {}
    total = len(papers)

    for i, paper in enumerate(papers):
        title_short = paper.title[:60] + ("..." if len(paper.title) > 60 else "")

        # 跳过已有
        if skip_existing and paper.raw_path:
            existing = Path(paper.raw_path)
            if existing.exists() and existing.stat().st_size > 0:
                results[paper.paper_id] = (existing, None)
                if on_progress:
                    on_progress(i, total, title_short, True, "已存在")
                continue

        # 限流
        _rate_limit_delay(i, total)

        # 下载
        try:
            path = download_paper(paper, raw_root)
            results[paper.paper_id] = (path, None)
            if on_progress:
                on_progress(i, total, title_short, True, None)
        except Exception as exc:
            error_msg = str(exc)
            results[paper.paper_id] = (None, error_msg)
            logger.error("❌ [%d/%d] 下载失败: %s — %s", i + 1, total, title_short, error_msg)
            if on_progress:
                on_progress(i, total, title_short, False, error_msg)

    success_count = sum(1 for _, err in results.values() if err is None)
    logger.info("=" * 50)
    logger.info("批量下载完成: %d/%d 成功", success_count, total)
    return results
