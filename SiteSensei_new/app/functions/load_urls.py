from langchain_community.document_loaders import PlaywrightURLLoader
from urllib.parse import urlparse

async def load_urls(xmlurls):
    urls = []
    xml_urls = []
    sitemap_domain = urlparse(xmlurls[0]).netloc  # Assuming all URLs have the same domain

    for u in xmlurls:
        if urlparse(u).netloc == sitemap_domain:
            if u.endswith('.xml'):
                xml_urls.extend(await scrape_sitemap(u))  # scrape_sitemap needs to be imported
            else:
                urls.append(u)

    loader = PlaywrightURLLoader(urls=urls, remove_selectors=["header", "footer"])
    data = await loader.aload()
    
    return data
