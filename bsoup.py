from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time
import pandas as pd


#page fetcher
def pagefetch(url):
    r = requests.get(url)
    if r.status_code !=200:
        print("Failed to Load")
        return None
    return BeautifulSoup(r.text, "html.parser")

#top ten list
def toptenpage(base):
    driver = webdriver.Chrome()
    driver.get(base)
    time.sleep(3)

    ttp_soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    ttpl = []
    ul = ttp_soup.find("ul", class_ = "top-ten-results")
    if ul:
        items = ul.find_all("li", recursive = False)
        for item in items:
            a = item.find("a", href = True)
            if a:
                nm = a.find("span").get_text(strip = True)
                link = a["href"]
                if link =="#" or link == "":
                    continue
                ttpl.append({"make": nm, "link": link})

    return ttpl

def toptenloop(ttpl):
    rv_data = []
    for item in ttpl:
        mk = item["make"]
        link = item["link"]

        soup = pagefetch(link)

        pages = [
            int(li["data-page"])
            for li in soup.select("ul.p-nation li[data-page]")
            if li["data-page"].isdigit()
        ]

        end = max(pages, default=1)
        data = pageloop(link, end, mk)
        rv_data.extend(data)

    return rv_data

def pageloop(link, end, mk):
    rvws = []
    for p in range(1, end + 1):
        url = f"{link}&page={p}"

        soup = pagefetch(url)

        cards = soup.find_all("div", class_="rvws-card")

        for c in cards:
            data = parse(c, mk)
            rvws.append(data)

    return rvws

#parse the html
def parse(c, mk):

    #model
    mdl = c.find("span", class_ = "rvwr-title-text").find(text=True, recursive=False)

    #state
    st_tag = c.find("p", class_="rvwr-locl")
    st = st_tag.find(text=True, recursive=False).strip() if st_tag else None
    if st:
        st = st.replace(", USA", "")

    #date reviewed
    dt = c.find("p", class_="rvwr-date").find(text=True, recursive=False)
    dt = dt.replace("Reviewed on ","")

    #criteria
    #crit_blk = c.find_all("div", class_="rvwr-item")
    #crit = []
    #for item in crit_blk:
     #   scr = item.find("span", class_="rate-num")
     #   if scr:
      #      try:
       #         crit.append(float(scr.get_text(strip=True)))
        #    except ValueError:
         #       crit.append(None)

    #avg criteria
    #avg = round(sum(crit)/ len(crit), 2)

    #review text
    rvwt = c.find("div", class_="rvwr-text full-text-review").find(text=True, recursive=False).strip()

    return {
        "make": mk,
        "model": mdl,
        "state": st,
        #"avg_score": avg,
        #"livibility": crit[0],
        #"quality": crit[1],
        #"floorplan": crit[2],
        #"driving/towing": crit[3],
        #"factory_warranty/support": crit[4],
        "review": rvwt,
        "date": dt
    }

def main():
    base = "https://www.rvinsider.com/RV-Reviews"
    ttpl = toptenpage(base)
    rv_data = toptenloop(ttpl)
    df = pd.DataFrame(rv_data)

    print(df.head())


if __name__ == "__main__":
    main()
