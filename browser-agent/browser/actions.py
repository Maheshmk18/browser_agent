from __future__ import annotations

from typing import Optional

from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

from config.settings import settings


class BrowserActions:
    """High-level browser actions the agent nodes call during task execution."""

    def __init__(self, page: Page) -> None:
        self._page = page

    
    # Navigation
    
    async def navigate(self, url: str) -> str:
        await self._page.goto(url, wait_until="load",
                              timeout=settings.BROWSER_TIMEOUT_MS)
        # Wait for any post-load redirects (e.g. YouTube consent page) to settle
        try:
            await self._page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass
        return self._page.url

    async def go_back(self) -> None:
        await self._page.go_back(wait_until="domcontentloaded")

    async def reload(self) -> None:
        await self._page.reload(wait_until="domcontentloaded")

   
    # Interaction
    

    async def click(self, selector: str, timeout: Optional[int] = None) -> None:
        await self._page.wait_for_selector(
            selector, state="visible", timeout=timeout or settings.BROWSER_TIMEOUT_MS
        )
        await self._page.click(selector)

    async def type_text(self, selector: str, text: str, delay: int = 50) -> None:
        await self._page.wait_for_selector(
            selector, state="visible", timeout=settings.BROWSER_TIMEOUT_MS
        )
        await self._page.fill(selector, "")
        await self._page.type(selector, text, delay=delay)

    async def press_key(self, key: str) -> None:
        await self._page.keyboard.press(key)

    async def hover(self, selector: str) -> None:
        await self._page.hover(selector)

    async def select_option(self, selector: str, value: str) -> None:
        await self._page.select_option(selector, value)

    async def scroll(self, direction: str = "down", pixels: int = 300) -> None:
        delta = pixels if direction == "down" else -pixels
        await self._page.mouse.wheel(0, delta)

    
    # Waiting
    
    async def wait_for_selector(
        self, selector: str, state: str = "visible", timeout: Optional[int] = None
    ) -> bool:
        try:
            await self._page.wait_for_selector(
                selector,
                state=state,
                timeout=timeout or settings.BROWSER_TIMEOUT_MS,
            )
            return True
        except PlaywrightTimeout:
            return False

    async def wait_for_navigation(self, timeout: Optional[int] = None) -> None:
        await self._page.wait_for_load_state(
            "domcontentloaded", timeout=timeout or settings.BROWSER_TIMEOUT_MS
        )

    
    # Reading page state

    async def get_text(self, selector: str) -> str:
        el = await self._page.query_selector(selector)
        return (await el.inner_text()).strip() if el else ""

    async def get_attribute(self, selector: str, attr: str) -> Optional[str]:
        return await self._page.get_attribute(selector, attr)

    async def get_page_title(self) -> str:
        return await self._page.title()

    async def get_current_url(self) -> str:
        return self._page.url

    async def get_page_content(self) -> str:
        return await self._page.content()

    async def is_visible(self, selector: str) -> bool:
        try:
            return await self._page.is_visible(selector)
        except Exception:
            return False

    async def query_all_text(self, selector: str) -> list[str]:
        elements = await self._page.query_selector_all(selector)
        texts = []
        for el in elements:
            t = (await el.inner_text()).strip()
            if t:
                texts.append(t)
        return texts

    async def query_all_links(self, selector: str = "a[href]") -> list[dict]:
        elements = await self._page.query_selector_all(selector)
        links = []
        for el in elements:
            href = await el.get_attribute("href")
            text = (await el.inner_text()).strip()
            if href:
                links.append({"text": text, "href": href})
        return links
