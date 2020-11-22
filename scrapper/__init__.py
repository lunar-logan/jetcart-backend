# from bs4 import BeautifulSoup
#
# from scrapper import fetcher
#
# html = fetcher.fetch(
#     'https://www.flipkart.com/google-pixel-4a-just-black-128-gb/p/itm023b9677aa45d?pid=MOBFUSBNAZGY7HQU&lid=LSTMOBFUSBNAZGY7HQUWHTF0C&marketplace=FLIPKART&srno=s_1_1&otracker=AS_QueryStore_OrganicAutoSuggest_1_4_na_na_na&otracker1=AS_QueryStore_OrganicAutoSuggest_1_4_na_na_na&fm=SEARCH&iid=0dbf06f0-a6ac-4070-823c-20c653e2bfcf.MOBFUSBNAZGY7HQU.SEARCH&ppt=sp&ppn=sp&ssid=58drk86f5s0000001605800076207&qH=680e649af610418f'
# )
#
# # print(html)
# soup = BeautifulSoup(html, features="html5lib")
# # print(soup.prettify())
# el = soup.find_all("div", class_="_1MR4o5")[0]
# for ell in el.find_all('div', class_="_3GIHBu"):
#     for a in ell.find_all('a'):
#         print(a.text)
# print("--"*80)
#
