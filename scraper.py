from datetime import datetime
import scrapy
from scrapy.crawler import CrawlerProcess



def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'{timestamp} [Crss.Scraper] {msg}')


def convert_size(size_string):
    [base, unit] = size_string.split(' ')
    sizes = {
        'Bytes': 1,
        'KiB': 1024,
        'MiB': 1048576,
        'GiB': 1073741824,
        'TiB': 1099511627776
    }
    size = float(base) * sizes[unit]
    return int(size)




class CrssSpider(scrapy.Spider):
    name = 'crss'
    allowed_domains = ['nyaa.si']
    base_url = 'https://nyaa.si'

    def __init__(self):
        self.databasePipeline = None
    
    def start_requests(self):
        user_entries = self.databasePipeline.get_user_entries()
        for (user_id, _, url, comments, _) in user_entries:
            yield scrapy.Request(url, callback=self.parse_user, meta={
                'proxy': self.settings.get('_PROXY'),
                'user_id': user_id,
                '_comm_enabled': comments,
            })
    
    def parse_user(self, response):
        for entry in response.css('table.torrent-list > tbody > tr'):
            try:
                torrent_info = {
                    'torrent_id': int( entry.css('td:nth-of-type(2n) > a:last-of-type::attr(href)').get().split('/')[-1] ),
                    'title': entry.css('td:nth-of-type(2n) > a:last-of-type::attr(title)').get(),
                    'category': int( entry.css('td:nth-of-type(1n) > a::attr(href)').get()[-3:-2] ),
                    'subcategory': int( entry.css('td:nth-of-type(1n) > a::attr(href)').get()[-1:] ),
                    'remake': True if entry.css('tr.danger').get() else False,
                }
                comments = int( entry.css('a.comments::text')[-1].get() if entry.css('a.comments::text') else 0 )
                com_count = comments if response.meta.get('_comm_enabled') else None
                update = self.databasePipeline.check_torrent(torrent_info, com_count)
                if(update == False):
                    continue
                url = f'''https://nyaa.si/view/{torrent_info['torrent_id']}'''
                yield response.follow(url, callback=self.parse_torrent, meta={
                    **response.meta,
                    **torrent_info,
                    '_update': update,
                })
            except:
                pass
        
        try:
            next_page = response.css('ul.pagination > li:last-of-type > a::attr(href)').get()
            if next_page is not None and next_page != '#':
                if response.meta.get('_comm_enabled') or next_page[-1] != '4':
                    yield response.follow(self.base_url + next_page, callback=self.parse_user, meta={**response.meta})
        except:
            pass

    def parse_torrent(self, response):
        try:
            comment_list = []
            for entry in response.css('div.comment-panel'):
                comment_list.append({
                    'comment_id': int( entry.css('div.comment-content::attr(id)').get()[15:] ),
                    'user_id': response.meta['user_id'],
                    'torrent_id': response.meta.get('torrent_id'),
                    'ref': int( entry.css('div.comment-details a::attr(href)').get()[5:] ),
                    'author': entry.css('div.col-md-2 > p > a::text').get().strip(),
                    'date': datetime.fromtimestamp( int( entry.css('div.comment-details small::attr(data-timestamp)').get() )),
                    'content': entry.css('div.comment-content::text').get().strip(),
                    'image': entry.css('img.avatar::attr(src)').get(),
                })
            yield {
                **response.meta,
                'submitter': response.css('div.panel-body > div:nth-of-type(2n) > div:nth-of-type(2n) > a::text').get(),
                'filesize': response.css('div.panel-body > div:nth-of-type(4n) > div:nth-of-type(2n)::text').get(),
                'filesize_raw': convert_size( response.css('div.panel-body > div:nth-of-type(4n) > div:nth-of-type(2n)::text').get() ),
                'datetime': datetime.fromtimestamp( int( response.css('div.panel-body > div:nth-of-type(1n) > div:nth-of-type(4n)::attr(data-timestamp)').get() )),
                'trusted': True if response.css('div.panel-success h3').get() or response.css('div.panel-body > div:nth-of-type(2n) a.text-success').get() else False,
                'magnet': response.css('a.card-footer-item::attr(href)').get(),
                'mkv_files': response.css('div.torrent-file-list li').get().count('.mkv') if response.css('div.torrent-file-list li').get().count('.mkv') else 0,
                'comments': int( response.css('#comments h3::text').get().strip()[11:] ) if response.meta.get('_comm_enabled') else 0,
                'comments_list': comment_list,
            }
        except:
            pass


def init_scraper(db_user, db_pwd, db_host, db_port, db_name, nyaa_delay, nyaa_retries, nyaa_proxy, verbosity):
    scraper_settings = {
        'DOWNLOAD_DELAY': nyaa_delay,
        'RETRY_TIMES': nyaa_retries,
        'CONCURRENT_REQUESTS': 50,
        'LOG_LEVEL': verbosity,
        'RETRY_ENABLED': True,
        'REDIRECT_ENABLED': False,
        'COOKIES_ENABLED': False,
        'ROBOTSTXT_OBEY': False,
        'TELNETCONSOLE_ENABLED': False,
        'USER_AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0",
        'ITEM_PIPELINES': {
            'crss.pipelines.DatabasePipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'crss.middlewares.CrssSpiderMiddleware': 300,
        },
        '_DB_USER': db_user,
        '_DB_PASSWORD': db_pwd,
        '_DB_HOST': db_host,
        '_DB_PORT': db_port,
        '_DB_NAME': db_name,
        '_PROXY': nyaa_proxy,
    }
    process = CrawlerProcess(settings=scraper_settings)
    process.crawl(CrssSpider)
    process.start()