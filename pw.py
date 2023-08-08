import re,time
from playwright.sync_api import sync_playwright
from threading import Thread

root_url ="http://45.33.199.28"  #"http://localhost:8080"
visited_urls = set()

def sanitize_href(href):
   return href.replace("/","-").replace("#","hash")

def scrape_url(url):
    visited_urls.add(url)
    print(url, " started...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(root_url+url)
        page.wait_for_selector('a')
        time.sleep(1)
        content = page.content()
        hrefs = re.findall(r'href="([a-z0-9_#\/]+)"', content)
        for href in hrefs:
            content = content.replace('href="'+href+'"', 'href="'+sanitize_href(href)+'.html"')
        content.replace("/global.css","global.css").replace("/build/","build/")
        content = content.replace("/global.css","global.css").replace("/build/","build/")
        fname = sanitize_href(url.replace(root_url,"")) + '.html'

        with open('out\\'+fname, "w+", encoding="utf-8") as f:
            # Remove allscript references
            f.write(re.sub("<script [^\\>]+></script>","", content))
        
        print(url, " saved")

        threads = []
        for a in page.query_selector_all('a'):
            href = a.get_attribute("href")
            if href not in visited_urls:
                t = Thread(target=scrape_url, args=(href,))
                threads.append(t)
                t.start()

        browser.close()

        for t in threads:
            t.join()
    print(url, " done")

scrape_url('/#/')
