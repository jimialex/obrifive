import asyncio
import json
import re
import sys
from pathlib import Path

from playwright.async_api import Response, async_playwright

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
SETTLE_SECONDS = 6
SCROLL_ROUNDS = 3
PRICE_PATTERN = re.compile(r"(?i)(bs\.?\s*[0-9][0-9.,]*|[0-9][0-9.,]*\s*bs\b|precio[^\n]{0,40}|cotiza[^\n]{0,40})")
LOGIN_WALL_PATTERN = re.compile(r"(?i)(inicia sesión|iniciar sesión|log in|registrarte|sign up|crear cuenta nueva)")


async def probe(url: str, output_dir: Path) -> tuple[dict, str]:
    json_responses: list[dict] = []

    async def record_response(network_response: Response) -> None:
        content_type = network_response.headers.get("content-type", "")
        if "json" in content_type and network_response.request.resource_type in ("xhr", "fetch"):
            json_responses.append({"url": network_response.url[:200], "status": network_response.status})

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        browser_context = await browser.new_context(
            user_agent=USER_AGENT, locale="es-BO", viewport={"width": 1280, "height": 900}
        )
        page = await browser_context.new_page()
        page.on("response", record_response)
        navigation_response = await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(SETTLE_SECONDS * 1000)
        for _ in range(SCROLL_ROUNDS):
            await page.mouse.wheel(0, 2500)
            await page.wait_for_timeout(1500)
        rendered_text = await page.inner_text("body")
        await page.screenshot(path=str(output_dir / "screenshot.png"), full_page=False)
        probe_result = {
            "url": url,
            "final_url": page.url,
            "status": navigation_response.status if navigation_response else None,
            "title": await page.title(),
            "text_chars": len(rendered_text),
            "price_mentions": sorted({match.strip() for match in PRICE_PATTERN.findall(rendered_text)})[:25],
            "login_wall_mentions": sorted({match for match in LOGIN_WALL_PATTERN.findall(rendered_text)}),
            "json_responses": json_responses[:30],
        }
        await browser.close()
        return probe_result, rendered_text


if __name__ == "__main__":
    output_dir = Path(sys.argv[2])
    output_dir.mkdir(parents=True, exist_ok=True)
    probe_result, rendered_text = asyncio.run(probe(sys.argv[1], output_dir))
    (output_dir / "text.txt").write_text(rendered_text)
    (output_dir / "probe.json").write_text(json.dumps(probe_result, indent=2, ensure_ascii=False))
    print(json.dumps(probe_result, indent=2, ensure_ascii=False))  # noqa: T201
