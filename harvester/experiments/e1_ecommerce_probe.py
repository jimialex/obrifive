import asyncio
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
REQUEST_DELAY_SECONDS = 1.0
PLATFORM_SIGNATURES = {
    "shopify": ("cdn.shopify.com", "Shopify.theme", "myshopify.com"),
    "woocommerce": ("woocommerce", "wc-block", "/wp-content/plugins/woocommerce"),
    "wordpress": ("/wp-content/", "/wp-includes/"),
    "tiendanube": ("tiendanube", "nuvemshop", "d2r9epyceweg5n.cloudfront.net"),
    "jumpseller": ("jumpseller",),
    "vtex": ("vtex", "vteximg"),
    "magento": ("Magento_", "mage/cookies"),
    "prestashop": ("prestashop",),
    "wix": ("wix.com", "_wixCssImports", "wixstatic"),
    "framer": ("framer.com", "framerusercontent"),
    "construex": ("construex",),
}
JSON_LD_PATTERN = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.S | re.I)
LINK_PATTERN = re.compile(r'href=["\']([^"\'#]+)["\']', re.I)
SOCIAL_PATTERNS = {
    "facebook": re.compile(r"https?://(?:www\.|m\.|web\.)?facebook\.com/[^\s\"'<>?]+", re.I),
    "instagram": re.compile(r"https?://(?:www\.)?instagram\.com/[^\s\"'<>?]+", re.I),
    "tiktok": re.compile(r"https?://(?:www\.)?tiktok\.com/@[^\s\"'<>?]+", re.I),
    "whatsapp": re.compile(r"https?://(?:wa\.me|api\.whatsapp\.com|web\.whatsapp\.com|wa\.link)/[^\s\"'<>]+", re.I),
}
PRODUCT_PATH_PATTERN = re.compile(r"/(products?|productos?|producto|tienda|shop|item|p)/[^/?#]+", re.I)
SITEMAP_LOC_PATTERN = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>", re.I)


@dataclass
class SiteProbe:
    url: str
    status: int | None = None
    final_url: str | None = None
    error: str | None = None
    platforms: list[str] = field(default_factory=list)
    home_json_ld_types: list[str] = field(default_factory=list)
    product_page_url: str | None = None
    product_json_ld_types: list[str] = field(default_factory=list)
    product_has_price: bool = False
    sitemap_urls: int = 0
    sitemap_product_urls: int = 0
    shopify_products_json: int | None = None
    woocommerce_store_api: int | None = None
    robots_disallow_all: bool = False
    social_links: dict[str, list[str]] = field(default_factory=dict)


def _json_ld_types(html: str) -> tuple[list[str], bool]:
    found_types: list[str] = []
    has_price = False
    for raw_block in JSON_LD_PATTERN.findall(html):
        try:
            parsed_block = json.loads(raw_block.strip())
        except json.JSONDecodeError:
            found_types.append("invalid")
            continue
        pending_nodes = [parsed_block]
        while pending_nodes:
            node = pending_nodes.pop()
            if isinstance(node, list):
                pending_nodes.extend(node)
            elif isinstance(node, dict):
                node_type = node.get("@type")
                if isinstance(node_type, list):
                    found_types.extend(str(type_name) for type_name in node_type)
                elif node_type:
                    found_types.append(str(node_type))
                if "price" in node or "lowPrice" in node:
                    has_price = True
                pending_nodes.extend(value for value in node.values() if isinstance(value, (dict, list)))
    return sorted(set(found_types)), has_price


def _detect_platforms(html: str, final_url: str) -> list[str]:
    haystack = f"{final_url}\n{html}"
    return [
        platform_name
        for platform_name, signatures in PLATFORM_SIGNATURES.items()
        if any(signature.lower() in haystack.lower() for signature in signatures)
    ]


def _social_links(html: str) -> dict[str, list[str]]:
    social_links: dict[str, list[str]] = {}
    for network_name, network_pattern in SOCIAL_PATTERNS.items():
        matches = sorted({match.rstrip("/\\").replace("&amp;", "&") for match in network_pattern.findall(html)})
        if matches:
            social_links[network_name] = matches[:5]
    return social_links


def _first_product_link(html: str, base_url: str) -> str | None:
    base_host = urlparse(base_url).netloc
    for raw_link in LINK_PATTERN.findall(html):
        absolute_link = urljoin(base_url, raw_link)
        if urlparse(absolute_link).netloc == base_host and PRODUCT_PATH_PATTERN.search(urlparse(absolute_link).path):
            return absolute_link
    return None


async def _get(http_client: httpx.AsyncClient, url: str) -> httpx.Response | None:
    await asyncio.sleep(REQUEST_DELAY_SECONDS)
    try:
        return await http_client.get(url, follow_redirects=True)
    except httpx.HTTPError:
        return None


async def _count_json_items(http_client: httpx.AsyncClient, url: str, items_key: str | None) -> int | None:
    http_response = await _get(http_client, url)
    if http_response is None or http_response.status_code != 200:
        return None
    try:
        payload = http_response.json()
    except ValueError:
        return None
    items = payload.get(items_key) if items_key and isinstance(payload, dict) else payload
    return len(items) if isinstance(items, list) else None


async def _probe_sitemap(http_client: httpx.AsyncClient, base_url: str, site_probe: SiteProbe) -> None:
    sitemap_candidates = [urljoin(base_url, "/sitemap.xml")]
    robots_response = await _get(http_client, urljoin(base_url, "/robots.txt"))
    if robots_response is not None and robots_response.status_code == 200:
        robots_parser = RobotFileParser()
        robots_parser.parse(robots_response.text.splitlines())
        site_probe.robots_disallow_all = not robots_parser.can_fetch(USER_AGENT, base_url + "/")
        sitemap_candidates = [
            line.split(":", 1)[1].strip()
            for line in robots_response.text.splitlines()
            if line.lower().startswith("sitemap:")
        ] or sitemap_candidates
    visited_sitemaps = 0
    pending_sitemaps = sitemap_candidates[:3]
    while pending_sitemaps and visited_sitemaps < 6:
        sitemap_url = pending_sitemaps.pop(0)
        visited_sitemaps += 1
        sitemap_response = await _get(http_client, sitemap_url)
        if sitemap_response is None or sitemap_response.status_code != 200:
            continue
        locations = SITEMAP_LOC_PATTERN.findall(sitemap_response.text)
        if "<sitemapindex" in sitemap_response.text:
            product_sitemaps = [location for location in locations if "product" in location.lower()]
            pending_sitemaps.extend((product_sitemaps or locations)[:3])
            continue
        site_probe.sitemap_urls += len(locations)
        site_probe.sitemap_product_urls += sum(
            1 for location in locations if PRODUCT_PATH_PATTERN.search(urlparse(location).path)
        )
        if site_probe.product_page_url is None:
            site_probe.product_page_url = next(
                (location for location in locations if PRODUCT_PATH_PATTERN.search(urlparse(location).path)), None
            )


async def probe_site(http_client: httpx.AsyncClient, url: str) -> SiteProbe:
    site_probe = SiteProbe(url=url)
    home_response = await _get(http_client, url)
    if home_response is None:
        site_probe.error = "unreachable"
        return site_probe
    site_probe.status = home_response.status_code
    site_probe.final_url = str(home_response.url)
    if home_response.status_code >= 400:
        site_probe.error = f"http {home_response.status_code}"
        return site_probe
    home_html = home_response.text
    site_probe.platforms = _detect_platforms(home_html, site_probe.final_url)
    site_probe.home_json_ld_types, _ = _json_ld_types(home_html)
    site_probe.social_links = _social_links(home_html)
    site_probe.product_page_url = _first_product_link(home_html, site_probe.final_url)
    base_url = f"{urlparse(site_probe.final_url).scheme}://{urlparse(site_probe.final_url).netloc}"
    await _probe_sitemap(http_client, base_url, site_probe)
    if "shopify" in site_probe.platforms:
        site_probe.shopify_products_json = await _count_json_items(
            http_client, urljoin(base_url, "/products.json?limit=250"), "products"
        )
    if "woocommerce" in site_probe.platforms or "wordpress" in site_probe.platforms:
        site_probe.woocommerce_store_api = await _count_json_items(
            http_client, urljoin(base_url, "/wp-json/wc/store/v1/products?per_page=100"), None
        )
    if site_probe.product_page_url:
        product_response = await _get(http_client, site_probe.product_page_url)
        if product_response is not None and product_response.status_code == 200:
            site_probe.product_json_ld_types, site_probe.product_has_price = _json_ld_types(product_response.text)
    return site_probe


async def main(urls: list[str]) -> None:
    async with httpx.AsyncClient(timeout=25, headers={"User-Agent": USER_AGENT}) as http_client:
        site_probes = [await probe_site(http_client, url) for url in urls]
    print(json.dumps([asdict(site_probe) for site_probe in site_probes], indent=2, ensure_ascii=False))  # noqa: T201


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
