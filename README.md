
## Exotic India Library

### Books list page

### Command to crawl all books on a results page and export in CSV
```
scrapy crawl books_metadata -s JOBDIR=crawls/books_metadata -o books_metadata.csv
```

You can test with one book
```
scrapy crawl book_metadata -s JOBDIR=crawls/book_metadata -o book_metadata.csv
```

## To scrape the whole website

Install scrapy

`pip3 install scrapy`

The `books_metadata_spider.py` script needs to be used.

Run at the root of the folder
```
scrapy crawl books_metadata -s JOBDIR=crawls/books_metadata -o books_metadata.csv
```