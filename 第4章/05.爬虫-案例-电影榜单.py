import requests
from lxml import html
import csv
# 定义常量
CSV_FILE = "./csv_data/movies.csv"
TMDB_BASE_URL = "https://www.themoviedb.org"
TMDB_TOP_URL_1 = "https://www.themoviedb.org/movie/top-rated" # 高分电影榜单 第一页
TMDB_TOP_URL_2 = "https://www.themoviedb.org/discover/movie/items" # 高分电影榜单 第二页之后


# 获取电影详情数据
def get_movie_info(movie_info_url):
    # 发送请求，获取电影详情数据
    movie_response = requests.get(movie_info_url,timeout=60)
    print(f"发送请求:{movie_info_url}正在获取电影详情...")
    # 解析数据
    movie_document = html.fromstring(movie_response.text)
    # 获取电影标题
    movie_title = movie_document.xpath('//*[@id="original_header"]/div[2]/section/div[1]/h2/a/text()')
    # 获取电影年份
    movie_year = movie_document.xpath('//*[@id="original_header"]/div[2]/section/div[1]/h2/span/text()')
    # 获取电影上映时间 标签[@属性 = "value"]
    movie_release_date = movie_document.xpath('//*[@id="original_header"]/div[2]/section/div[1]/div/span[@class="release"]/text()')
    # 获取电影类型
    movie_type = movie_document.xpath('//*[@id="original_header"]/div[2]/section/div[1]/div/span[@class="genres"]/a/text()')
    # 获取电影时长
    movie_duration = movie_document.xpath('//*[@id="original_header"]/div[2]/section/div[1]/div/span[@class="runtime"]/text()')
    # 获取电影评分
    movie_score = movie_document.xpath('//*[@id="consensus_pill"]/div/div[1]/div/div/@data-percent')
    # 获取电影语言
    movie_language = movie_document.xpath('//*[@id="media_v4"]/div/div/div[2]/div/section/div[1]/div/section[1]/p[3]/text()')
    # 获取电影导演
    movie_director = movie_document.xpath('//*[@id="original_header"]/div[2]/section/div[3]/ol/li[1]/p[1]/a/text()')
    # 获取电影作者
    movie_author = movie_document.xpath('//*[@id="original_header"]/div[2]/section/div[3]/ol/li[2]/p[1]/a/text()')
    # 获取电影主演
    movie_actor = movie_document.xpath('//*[@id="cast_scroller"]/ol/li/p/a/text()')
    # 获取电影Slogan
    movie_slogan = movie_document.xpath('//*[@id="original_header"]/div[2]/section/div[3]/h3[1]/text()')
    # 获取电影简介
    movie_introduction = movie_document.xpath('//*[@id="original_header"]/div[2]/section/div[3]/div/p/text()')
    movie_info = {
        "电影标题": movie_title[0].strip() if movie_title else "",
        "电影年份": movie_year[0].strip(),
        "上映时间": movie_release_date[0].strip(),
        "电影类型": ",".join(movie_type) if movie_type else "",
        "电影时长": movie_duration[0].strip() if movie_duration else "",
        "电影评分": movie_score[0].strip() if movie_score else "",
        "电影语言": movie_language[0].strip() if movie_language else "",
        "导演": movie_director[0].strip() if movie_director else "",
        "作者": movie_author[0].strip() if movie_author else "",
        # 主演 [actor.strip() for actor in movie_actor if actor and actor.strip()] #
        # 核心作用：清洗 movie_actor 列表，剔除空值、None、仅含空白的元素，同时对有效元素去除首尾空白；
        # 关键逻辑：if actor and actor.strip() 是双重过滤（先排除假值，再排除仅空白的字符串），actor.strip() 是最终的清洗操作；
        # 本质：用列表推导式高效实现 “筛选 + 清洗”，替代繁琐的 for 循环 + 判断。
        "主演": ",".join([actor.strip() for actor in movie_actor if actor and actor.strip()]) if movie_actor else "",
        "电影Slogan": movie_slogan[0].strip() if movie_slogan else "",
        "电影简介": movie_introduction[0].strip() if movie_introduction else "",
    }
    print(movie_info)
    return movie_info

# 保存数据
def save_all_movies(all_movies):
    with open(CSV_FILE, "w", encoding="utf-8",newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["电影标题","电影年份","上映时间","电影类型","电影时长","电影评分","电影语言","导演","作者","主演","电影Slogan","电影简介"])
        writer.writeheader()
        for movie in all_movies:
            writer.writerow(movie)

def main():
    # 创建一个空列表，用于保存电影数据
    all_movies = []

    # 循环发送请求，获取高分电影榜单数据,获取5页数据，这个网站默认只返回1页数据，第一页为get请求，第二页开始为post请求
    for page_num in range(1,6):
        if page_num == 1:
            print(f"正在获取第{page_num}页数据...")
            # 1.发送请求，获取高分电影榜单数据
            response = requests.get(TMDB_TOP_URL_1, timeout=60)
        else:
            print(f"正在获取第{page_num}页数据...")
            response = requests.post(TMDB_TOP_URL_2,f"air_date.gte=&air_date.lte=&certification=&certification_country=CN&debug=&first_air_date.gte=&first_air_date.lte=&include_adult=false&latest_ceremony.gte=&latest_ceremony.lte=&page={page_num}&primary_release_date.gte=&primary_release_date.lte=&region=&release_date.gte=&release_date.lte=2026-09-16&show_me=everything&sort_by=vote_average.desc&vote_average.gte=0&vote_average.lte=10&vote_count.gte=300&watch_region=CN&with_genres=&with_keywords=&with_networks=&with_origin_country=&with_original_language=&with_watch_monetization_types=&with_watch_providers=&with_release_type=&with_runtime.gte=0&with_runtime.lte=400", timeout=60)

        # 2.解析数据，获取电影列表
        document = html.fromstring(response.text)
        movies_list = document.xpath(f"//*[@id='page_{page_num}']/div[@class='card style_1']")

        # 3.遍历电影列表，获取电影详情
        for movie in movies_list:
            movie_url = movie.xpath('./div/div/a/@href')
            # 电影详情的url movie_url[0] ['/movie/769-goodfellas', '#']
            movie_info_url = TMDB_BASE_URL+movie_url[0]
            # 发送请求，获取电影详情数据
            movie_info = get_movie_info(movie_info_url)
            all_movies.append(movie_info)
    # 4.保存数据，保存为csv文件
    save_all_movies(all_movies)
    print("数据获取完毕！")


if __name__ == '__main__':
    main()
