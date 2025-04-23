# 🍽️ OpenTable Scraper

A powerful Scrapy spider for scraping restaurant data from [OpenTable](https://www.opentable.com) with pagination support and Google search integration.

---

## 📦 Features

- ✅ Scrapes OpenTable Dallas search listings with pagination
- ✅ Extracts name, address, and profile link of restaurants
- ✅ Performs Google search to find social media links

---

## 🔧 Setup

### 1. Install dependencies

```bash
scrapy 
curl-cffi
lxml 
```

## 🚀 Run the Spider

```
scrapy crawl opentable
```

## 🗃️ Output Files
```
restaurants.csv → includes full restaurant + social link info

listing_page.csv → raw listing data from OpenTable
```

## 📁 Project Structure

```
opentable/
├── items.py               # Defines RestaurantData, ListingPageData
├── middlewares.py         # Custom CurlCFFIMiddleware
├── settings.py            
├── spiders/
│   └── opentable_spider.py  # Main spider logic
```
