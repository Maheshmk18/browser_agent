from __future__ import annotations

import base64
from pathlib import Path

from playwright.async_api import Page


class ScreenshotCapture:
    """Captures screenshots as Base64 strings or saves them to disk."""

    def __init__(self, page: Page) -> None:
        self._page = page

    async def capture_base64(self, full_page: bool = False) -> str:
        try:
            raw = await self._page.screenshot(type="png", full_page=full_page)
            return base64.b64encode(raw).decode("utf-8")
        except Exception:
            return ""

    async def capture_bytes(self, full_page: bool = False) -> bytes:
        return await self._page.screenshot(type="png", full_page=full_page)

    async def capture_file(self, path: str, full_page: bool = False) -> str:
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        await self._page.screenshot(path=str(dest), type="png", full_page=full_page)
        return str(dest)

    async def capture_element(self, selector: str) -> str:
        el = await self._page.query_selector(selector)
        if el is None:
            raise ValueError(f"Element not found: {selector}")
        raw = await el.screenshot(type="png")
        return base64.b64encode(raw).decode("utf-8")
