from urllib.parse import urlparse
from playwright.async_api import async_playwright


processed_urls = set()


async def scrape_sitemap(url):
    if url in processed_urls:
        return []
    processed_urls.add(url)

    urls = []
    xml_urls = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=10000)  # You can adjust the timeout as needed
            all_urls = await page.eval_on_selector_all('a', 'elements => elements.map(element => element.href)')

            sitemap_domain = urlparse(url).netloc

            for u in all_urls:
                if urlparse(u).netloc == sitemap_domain:
                    if u.endswith('.xml'):
                        xml_urls.extend(await scrape_sitemap(u))
                    else:
                        urls.append(u)
        except Exception as e:
            print(f"Failed to process {url}: {e}")  # Log the error or handle it as needed
        finally:
            await browser.close()

    urls.extend(xml_urls)
    return urls
