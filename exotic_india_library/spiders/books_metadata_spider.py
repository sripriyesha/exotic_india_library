import logging
import time

import scrapy
from scrapy.http import Request

logging.getLogger("scrapy").propagate = False


class BooksMetadataSpider(scrapy.Spider):
    name = "books_metadata"
    start_urls = ["https://www.exoticindiaart.com/book/"]

    def parse(self, response):
        categories_links = response.css("div.categoryGrid-item a::attr(href)")
        yield from response.follow_all(categories_links, self.parse_category_page)

    def parse_category_page(self, response):
        print("parsing category page: " + response.url)
        # time.sleep(2)

        book_page_links = response.css(
            "div.bodyArea div.product-textarea-title a::attr(href)"
        )
        yield from response.follow_all(book_page_links, self.parse_book_page)

        li_index = 1
        next_page = False

        while not next_page and li_index < 10:
            next_page = (
                response.xpath(
                    "//a[contains(concat(' ',normalize-space(@class),' '),' is-current ')]"
                    + "/ancestor::li"
                    + "/following-sibling::li["
                    + str(li_index)
                    + "]//a/@href"
                )
                .get(default="")
                .strip()
            )
            li_index = li_index + 1

        if next_page:
            yield Request(response.urljoin(next_page), self.parse_category_page)
        else:
            print(f"last page reached: {response.url}")

    def parse_book_page(self, response):
        def extract_with_css(query):
            return response.css(query).get(default="").strip()

        def get_next_td_anchor_text(key):
            return (
                response.xpath(
                    "//td[contains(text(), '"
                    + key
                    + "')]"
                    + "/following-sibling::td[1]"
                    + "//a//text()"
                )
                .get(default="")
                .strip()
            )

        def get_next_td_text(key):
            return (
                response.xpath(
                    "//td[contains(text(), '"
                    + key
                    + "')]"
                    + "/following-sibling::td[1]"
                    + "//text()"
                )
                .get(default="")
                .strip()
            )

        def get_metadata():
            author = get_next_td_anchor_text("Author:")
            publisher = get_next_td_anchor_text("Publisher:")
            language = get_next_td_text("Language:")
            edition = get_next_td_text("Edition:")
            ISBN = get_next_td_text("ISBN:")
            pages = get_next_td_text("Pages:")
            cover = get_next_td_text("Cover:")
            other_details = get_next_td_text("Other Details:")
            book_weight_xpath_result = (
                response.xpath("//td[contains(text(), 'weight of the book:')]//text()")
                .get(default="")
                .strip()
            )
            book_weight = ""
            if book_weight_xpath_result != "":
                book_weight = book_weight_xpath_result.split(":")[1].strip()

            short_description = ""
            if author.strip() != "":
                short_description += "<strong>Author:</strong> " + author + "<br/>"

            if publisher.strip() != "":
                short_description += (
                    "<strong>Publisher:</strong> " + publisher + "<br/>"
                )

            if language.strip() != "":
                short_description += "<strong>Language:</strong> " + language + "<br/>"

            if edition.strip() != "":
                short_description += "<strong>Edition:</strong> " + edition + "<br/>"

            if ISBN.strip() != "":
                short_description += "<strong>ISBN:</strong> " + ISBN + "<br/>"

            if pages.strip() != "":
                short_description += "<strong>Pages:</strong> " + pages + "<br/>"

            if cover.strip() != "":
                short_description += "<strong>Cover:</strong> " + cover + "<br/>"

            if other_details.strip() != "":
                short_description += (
                    "<strong>Other Details:</strong> " + other_details + "<br/>"
                )

            if book_weight.strip() != "":
                short_description += (
                    "<strong>Book weight:</strong> " + book_weight + "<br/>"
                )

            title = extract_with_css("h1.product-details-page-title::text")
            category = (
                response.xpath(
                    "//nav[contains(concat(' ',normalize-space(@class),' '),' breadcrumb ')]"
                    + "/ul/li[3]//@href"
                )
                .get(default="")
                .strip()
                .split("/")[2]
            )

            print("parsing book page: " + response.url)
            print("book: " + title)
            print("category: " + category)
            # time.sleep(5)

            return {
                "title": title,
                "images": extract_with_css(
                    "div.product-details-primary-image img::attr(src)"
                ),
                "price": extract_with_css("span.product-details-finalprice::text"),
                "short_description": short_description,
                "categories": category,
                "description": response.xpath("string(//div[@rel='description'])")
                .get(default="")
                .strip(),
                "meta:author": author,
                "meta:publisher": publisher,
                "meta:language": language,
                "meta:edition": edition,
                "meta:ISBN": ISBN,
                "meta:pages": pages,
                "meta:cover": cover,
                "meta:other_details": other_details,
                "meta:book_weight": book_weight,
            }

        yield get_metadata()
