import xml.etree.ElementTree as ET
import requests
from urllib.parse import urlparse
from playwright.async_api import async_playwright

processed_urls = set()

async def scrape_sitemap(url):
    if url in processed_urls:
        return []
    processed_urls.add(url)

    urls = []
    xml_urls = []

    # Try fetching and processing the URL as an HTML page
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=10000)
            all_urls = await page.eval_on_selector_all('a', 'elements => elements.map(element => element.href)')
            sitemap_domain = urlparse(url).netloc
            for u in all_urls:
                if urlparse(u).netloc == sitemap_domain:
                    if u.endswith('.xml'):
                        xml_urls.extend(await scrape_sitemap(u))
                    else:
                        urls.append(u)
        except Exception as e:
            print(f"Failed to process {url} as HTML: {e}")
        finally:
            await browser.close()

    # If no URLs found and the url ends with .xml, try processing as an XML sitemap
    if not urls and url.endswith('.xml'):
        response = requests.get(url)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            for sitemap in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
                loc = sitemap.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
                if loc is not None:
                    u = loc.text
                    if urlparse(u).netloc == urlparse(url).netloc:
                        if u.endswith('.xml'):
                            xml_urls.extend(await scrape_sitemap(u))
                        else:
                            urls.append(u)

    urls.extend(xml_urls)
    return urls
