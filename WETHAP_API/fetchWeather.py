import requests
from bs4 import BeautifulSoup


def fetchWeather():
    r = requests.get(
        "https://weathernews.jp/onebox/35.731350/139.798464/q=%E5%8D%97%E5%8D%83%E4%BD%8F%EF%BC%88%E6%9D%B1%E4%BA%AC%E9%83%BD%EF%BC%89&v=e8be546f5505407d1788791e7e7b3b0c15fbfd38af41f3dab5a6d2b88cb74d84&temp=c&lang=ja"
    )
    soup = BeautifulSoup(r.text, "html.parser")
    return soup.find(class_="weather-now__ul").li.text[2:]
