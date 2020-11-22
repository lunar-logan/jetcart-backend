from typing import List, Union, Dict, Any

from bs4 import BeautifulSoup
import logging


def except_exceptions(fn):
    def decorator(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception:
            logging.error(f"exception during extraction {fn}", exc_info=True)
            return None

    return decorator


class FlipkartPLPExtractor:
    def extract(self, html: str) -> List[str]:
        """Returns a list of PDP URLs"""
        soup = BeautifulSoup(html, features="html5lib")
        links = []
        for div in soup.find_all('div', class_="_4ddWXP"):
            link = self._extract_link(div)
            if link:
                links.append(self._add_scheme(link))
        return links

    def _add_scheme(self, url: str) -> str:
        if not url.startswith('http:') or not url.startswith('https:'):
            return f"https://www.flipkart.com{url}"
        return url

    def _extract_link(self, div) -> Union[str, None]:
        if not div:
            return None
        a = div.find('a', class_="s1Q9rs")
        if a:
            return a['href']
        return None


class FlipkartPDPParser:
    def extract(self, html: str) -> Dict:
        soup = BeautifulSoup(html, features="html5lib")
        return {
            'title': self.extract_title(soup),
            'description': self.extract_description(soup),
            'price': self.extract_price(soup),
            'category': self.extract_categories(soup),
            'images': self.extract_images(soup)
        }

    def extract_categories(self, soup: BeautifulSoup) -> List[str]:
        parent = soup.find('div', class_="_1MR4o5")
        categories = []
        if parent:
            for div in parent.find_all('div', class_="_3GIHBu"):
                a = div.find('a', class_="_2whKao")
                if a:
                    categories.append(a.text)
        print(categories)
        return categories

    def extract_title(self, soup: BeautifulSoup) -> str:
        return soup.find('span', class_="B_NuCI").text

    def extract_price(self, soup: BeautifulSoup) -> str:
        price = soup.find('div', class_="_30jeq3 _16Jk6d").text
        return price.replace(',', '') if price else None

    def extract_description(self, soup: BeautifulSoup) -> str:
        try:
            return soup.find('div', class_="_1mXcCf RmoJUa").text
        except Exception as err:
            return ''

    def extract_images(self, soup: BeautifulSoup) -> List[str]:
        def _extract_img_url(style: str) -> str:
            i = style.index('url(')
            return style[i + 4:-1]

        def _transform_image_url(url: str) -> str:
            return url.replace('/128/', '/832/').replace('/128/', '/832/')

        orientation_thumbnail_parent = soup.find('ul', class_="_3GnUWp")
        return [
            _transform_image_url(_extract_img_url(div['style']))
            for div in orientation_thumbnail_parent.find_all('div', class_="q6DClP")
        ]
