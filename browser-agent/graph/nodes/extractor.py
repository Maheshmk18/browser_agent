from __future__ import annotations

import asyncio
from typing import Callable

from browser.actions import BrowserActions
from graph.state import AgentState
from llm.chains import run_extractor


def make_extractor_node(actions: BrowserActions) -> Callable:

    async def run(state: AgentState) -> dict:
        try:
            # Wait for page to settle after last browser action
            await asyncio.sleep(2)

            current_url = await actions.get_current_url()
            page_title = await actions.get_page_title()

            # Wait for YouTube search results to appear (up to 10s)
            await actions.wait_for_selector("a#video-title", timeout=10000)

            # Scrape real video titles and links directly from the page
            all_links = await actions.query_all_links("a#video-title")
            video_links = [
                {
                    "title": lnk["text"],
                    "url": "https://www.youtube.com" + lnk["href"]
                }
                for lnk in all_links
                if lnk.get("href", "").startswith("/watch") and lnk.get("text", "").strip()
            ]

            if video_links:
                # Click the first video to open it in the browser
                try:
                    await actions.click("a#video-title")
                    await asyncio.sleep(3)
                    video_page_url = await actions.get_current_url()
                    video_links[0]["opened_url"] = video_page_url
                except Exception:
                    pass

                extracted = {
                    "page_url": current_url,
                    "page_title": page_title,
                    "videos": video_links[:10],
                }
            else:
                # Fallback: send truncated HTML to LLM
                page_content = await actions.get_page_content()
                extracted = await run_extractor(
                    task=state["clarified_task"],
                    page_content=page_content[:6000],
                )

        except Exception as exc:
            extracted = {"error": str(exc)}

        return {"extracted_data": extracted}

    return run
