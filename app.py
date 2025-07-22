from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import sqlite3
import aiohttp
import asyncio


app = Flask(__name__)
CORS(app)  # Allow CORS for all routes

# Your existing routes and code...
async def fetch(session, url, headers):
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None




def scrape_neet():
    base_url = "https://neet.nta.nic.in/"
    notifications = []

    try:
        response = requests.get(base_url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.select("div.vc_tta-panel-body div.gen-list ul li a")

        for link in links:
            text = link.text.strip()
            document_url = link.get('href')

            if document_url and document_url.startswith('http'):
                notifications.append({
                    "text": text,
                    "link": document_url,
                    "date": datetime.now().strftime("%d/%m/%Y")
                })
    except Exception as e:
        print(f"Error scraping NEET: {e}")

    return notifications

def scrape_jee():
    base_url = "https://jeemain.nta.nic.in/"
    notifications = []

    try:
        response = requests.get(base_url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.select("div.vc_tta-panel-body div.gen-list ul li a")

        for link in links:
            text = link.text.strip()
            document_url = link.get('href')

            if document_url and document_url.startswith('http'):
                notifications.append({
                    "text": text,
                    "link": document_url,
                    "date": datetime.now().strftime("%d/%m/%Y")
                })
    except Exception as e:
        print(f"Error scraping JEE: {e}")

    return notifications

def scrape_jkssb():
    base_url = "https://jkssb.nic.in/"
    target_url = urljoin(base_url, "Whatsnew.html")
    notifications = []

    try:
        response = requests.get(target_url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.select("td a.linkText")

        for link in links[:7]:  # Limit to first 7
            text = link.text.strip()
            document_url = urljoin(base_url, link.get('href').replace("..", ""))

            notifications.append({
                "text": text,
                "link": document_url,
                "date": datetime.now().strftime("%d/%m/%Y")
            })
    except Exception as e:
        print(f"Error scraping JKSSB: {e}")

    return notifications

def scrape_jkpsc():
    base_url = "http://www.jkpsc.nic.in/"
    notifications = []

    try:
        response = requests.get(base_url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        for item in soup.select('.notificationnews.myBox li:not([style*="display: none"])'):
            link = item.find('a')
            if link and link.text.strip():
                text = re.sub(r'\d{2}/\d{2}/\d{4}', '', link.text).strip()
                if any(keyword in text.lower() for keyword in ['exam', 'admit', 'result', 'syllabus']):
                    notifications.append({
                        "text": text,
                        "link": urljoin(base_url, link['href']),
                        "date": datetime.now().strftime("%d/%m/%Y")
                    })
    except Exception as e:
        print(f"Error scraping JKPSC: {e}")

    return notifications


@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    return jsonify({
        "neet": scrape_neet(),
        "jee": scrape_jee(),
        "jkssb": scrape_jkssb(),
        "jkpsc": scrape_jkpsc()
    })


async def scrape_news():
    urls = [
        'https://jkalerts.com/category/jammu-kashmir-jobs/govt-jobs-india/',
        'https://jkalerts.com/category/jammu-kashmir-jobs/'
    ]

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    articles_data = []

    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url, headers) for url in urls]
        responses = await asyncio.gather(*tasks)

        for response in responses:
            if response:
                soup = BeautifulSoup(response, 'html.parser')
                articles = soup.find_all('article', class_='post')

                for article in articles:
                    time_tag = article.find('div', class_='post-date-ribbon')
                    time_text = time_tag.get_text() if time_tag else "No date available"

                    title_tag = article.find('h2', class_='title')
                    title_text = title_tag.get_text() if title_tag else "No title available"

                    info_tag = article.find('div', class_='post-info')
                    info_text = info_tag.get_text() if info_tag else "No information available"

                    image_tag = article.find('img', class_='attachment-ribbon-lite-featured size-ribbon-lite-featured wp-post-image')
                    image_url = image_tag.get('src', '/static/m.png') if image_tag else '/static/m.png'

                    content_tag = article.find('div', class_='post-content')
                    content_text = content_tag.get_text() if content_tag else "No content available"

                    read_more_tag = article.find('div', class_='readMore').find('a')
                    read_more_url = read_more_tag['href'] if read_more_tag and 'href' in read_more_tag.attrs else "#"
                    read_more_title = read_more_tag['title'] if read_more_tag and 'title' in read_more_tag.attrs else "Read More"

                    articles_data.append({
                        'title': title_text,
                        'image_url': image_url,
                        'info': info_text,
                        'content': content_text,
                        'date': time_text,
                        'link': read_more_url,
                        'read_more_title': read_more_title
                    })
    
    return articles_data


async def scrape_articles_from_jkalerts():
    url = 'https://www.bing.com/news/search?q=kashmir&qs=n&form=QBNT&sp=-1&lq=0&pq=kashm&sc=10-5&sk=&cvid=0851B772B9E44B47A08030C01F2F8521&ghsh=0&ghacc=0&ghpl='
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    async with aiohttp.ClientSession() as session:
        response = await fetch(session, url, headers)

        if response:
            soup = BeautifulSoup(response, 'html.parser')
            articles = soup.find_all('div', class_='news-card')

            news_list = []
            for article in articles[:30]:
                title_tag = article.find('a', class_='title')
                title_text = title_tag.get_text() if title_tag else "No title available"

                image_tag = article.find('img', class_='rms_img')
                image_url = "https:" + image_tag['data-src-hq'] if image_tag and 'data-src-hq' in image_tag.attrs else "/static/m.png"

                link_tag = article.find('a', class_='title')
                link_url = link_tag['href'] if link_tag and 'href' in link_tag.attrs else "#"

                source_tag = article.find('a', class_='biglogo_link')
                source_text = source_tag['title'] if source_tag and 'title' in source_tag.attrs else "No source available"

                description = article.find('div', class_='snippet')
                desc = description.get_text() if description else "No description available"

                news_list.append({
                    'title': title_text,
                    'image_url': image_url,
                    'source': source_text,
                    'link': link_url,
                    'desc': desc,
                })
            return news_list
        else:
            return []

async def scrape_articles2():
    url = 'https://jkalerts.com/category/jammu-kashmir-news/kashmir-news/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    articles_data2 = []

    async with aiohttp.ClientSession() as session:
        response = await fetch(session, url, headers)

        if response:
            soup = BeautifulSoup(response, 'html.parser')
            articles = soup.find_all('article', class_='post')

            if not articles:
                return []

            for article in articles:
                time_tag = article.find('div', class_='post-date-ribbon')
                time_text = time_tag.get_text() if time_tag else "No date available"

                title_tag = article.find('h2', class_='title')
                title_text = title_tag.get_text() if title_tag else "No title available"

                info_tag = article.find('div', class_='post-info')
                info_text = info_tag.get_text() if info_tag else "No information available"

                image_tag = article.find('img', class_='attachment-ribbon-lite-featured size-ribbon-lite-featured wp-post-image')
                image_url = image_tag['src'] if image_tag and 'src' in image_tag.attrs else "No image available"

                content_tag = article.find('div', class_='post-content')
                content_text = content_tag.get_text() if content_tag else "No content available"

                read_more_tag = article.find('div', class_='readMore').find('a')
                read_more_url = read_more_tag['href'] if read_more_tag and 'href' in read_more_tag.attrs else "#"
                read_more_title = read_more_tag['title'] if read_more_tag and 'title' in read_more_tag.attrs else "Read More"

                articles_data2.append({
                    'title': title_text,
                    'image_url': image_url,
                    'info': info_text,
                    'content': content_text,
                    'date': time_text,
                    'read_more_url': read_more_url,
                    'read_more_title': read_more_title
                })
        else:
            return {'error': f'Failed to retrieve the articles from {url}'}

        if not articles_data2:
            return {'error': 'No articles found'}

        return articles_data2

# async def scrape_articles3():
#     url = 'https://linkingsky.com/government-exams/government-jobs-in-jammu-and-kashmir.html'
#     headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
#     response = requests.get(url, headers=headers)

#     if response.status_code == 200:
#         soup = BeautifulSoup(response.content, 'html.parser')
#         table_rows = soup.find_all('tr', class_='top_job')

#         job_list = []
#         for row in table_rows:
#             post_date = row.find('td', {'data-title': 'Post Date'}).get_text()
#             organization_td = row.find('td', {'data-title': 'Organization'})
#             organization_name = organization_td.get_text()
#             organization_link_tag = organization_td.find('a')
#             organization_link = organization_link_tag['href'] if organization_link_tag else "No link available"
            
#             if organization_link != "No link available":
#                 parsed_url = urlparse(organization_link)
#                 base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
#             else:
#                 base_url = organization_link

#             posts = row.find('td', {'data-title': 'Posts'}).get_text(strip=True)
#             qualification = row.find('td', {'data-title': 'Qualification'}).get_text(strip=True)
#             last_date = row.find('td', {'data-title': 'Last Date'}).get_text(strip=True)

#             job_list.append({
#                 'post_date': post_date,
#                 'organization': organization_name,
#                 'posts': posts,
#                 'qualification': qualification,
#                 'last_date': last_date,
#                 'link': base_url
#             })

#         return job_list
#     else:
#         return []
from urllib.parse import urljoin  # safer than manually making base_url

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

async def scrape_articles3():
    url = 'https://linkingsky.com/government-exams/government-jobs-in-jammu-and-kashmir.html'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', class_='tbl_states_jobs')
        rows = table.find('tbody').find_all('tr') if table else []

        job_list = []
        for row in rows:
            try:
                columns = row.find_all('td')
                if len(columns) < 7:
                    continue  # skip if not enough columns

                post_date = columns[0].get_text(strip=True)

                org_tag = columns[1].find('a')
                organization = org_tag.get_text(strip=True) if org_tag else columns[1].get_text(strip=True)
                link = urljoin(url, org_tag['href']) if org_tag and org_tag.has_attr('href') else "No link available"

                posts = columns[2].get_text(strip=True)
                qualification = columns[3].get_text(separator=", ", strip=True)
                job_type = columns[4].get_text(strip=True)
                tenure = columns[5].get_text(strip=True)
                last_date = columns[6].get_text(strip=True)

                job_list.append({
                    'post_date': post_date,
                    'organization': organization,
                    'posts': posts,
                    'qualification': qualification,
                    'type': job_type,
                    'tenure': tenure,
                    'last_date': last_date,
                    'link': link
                })
            except Exception as e:
                print(f"Error parsing row: {e}")
                continue

        return job_list
    else:
        print(f"Failed to fetch URL. Status code: {response.status_code}")
        return []




async def scrape_articles4():
    urls = [
        'https://jkalerts.com/category/jammu-kashmir-notifications/'
    ]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    articles_data4 = []

    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url, headers) for url in urls]
        responses = await asyncio.gather(*tasks)

        for response in responses:
            if response:
                soup = BeautifulSoup(response, 'html.parser')
                articles = soup.find_all('article', class_='post')

                for article in articles:
                    time_tag = article.find('div', class_='post-date-ribbon')
                    time_text = time_tag.get_text() if time_tag else "No date available"

                    title_tag = article.find('h2', class_='title')
                    title_text = title_tag.get_text() if title_tag else "No title available"

                    info_tag = article.find('div', class_='post-info')
                    info_text = info_tag.get_text() if info_tag else "No information available"

                    image_tag = article.find('img', class_='attachment-ribbon-lite-featured size-ribbon-lite-featured wp-post-image')
                    image_url = image_tag['src'] if image_tag and 'src' in image_tag.attrs else "/static/m.png"

                    content_tag = article.find('div', class_='post-content')
                    content_text = content_tag.get_text() if content_tag else "No content available"

                    read_more_tag = article.find('div', class_='readMore').find('a')
                    read_more_url = read_more_tag['href'] if read_more_tag and 'href' in read_more_tag.attrs else "#"
                    read_more_title = read_more_tag['title'] if read_more_tag and 'title' in read_more_tag.attrs else "Read More"

                    articles_data4.append({
                        'title': title_text,
                        'image_url': image_url,
                        'info': info_text,
                        'content': content_text,
                        'date': time_text,
                        'read_more_url': read_more_url,
                        'read_more_title': read_more_title
                    })

    return articles_data4

async def scrape_articles5():
    urls = [
        'https://jkalerts.com/category/jammu-kashmir-jobs/jk-jobs-updates/'
    ]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    articles_data5 = []

    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url, headers) for url in urls]
        responses = await asyncio.gather(*tasks)

        for response in responses:
            if response:
                soup = BeautifulSoup(response, 'html.parser')
                articles = soup.find_all('article', class_='post')

                for article in articles:
                    title_tag = article.find('h2', class_='title')
                    title_text = title_tag.get_text() if title_tag else "No title available"

                    articles_data5.append({
                        'title': title_text,
                        'link': urls[0]
                    })

    return articles_data5



@app.route('/api/news', methods=['GET'])
async def get_news():
    try:
        # Start scraping tasks concurrently
        tasks = [
            scrape_news(),
            scrape_articles_from_jkalerts(),
            scrape_articles2(),
            scrape_articles3(),
            scrape_articles4(),
            scrape_articles5()
        ]
        
        # Gather results
        news, articles_from_jkalerts, articles_data2, articles_data3, articles_data4, articles_data5 = await asyncio.gather(*tasks)

        # Combine all data
        combined_data = {
            'news': news,
            'articles_from_jkalerts': articles_from_jkalerts,
            'articles_data2': articles_data2,
            'articles_data3': articles_data3,
            'articles_data4': articles_data4,
            'articles_data5': articles_data5
        }

        return jsonify(combined_data)
    
    except Exception as e:
        print(f"Error in /api/news endpoint: {e}")
        return jsonify({'error': 'An error occurred while fetching news'}), 500


    pass
        


@app.route('/news-details1')
def news_details1():
    news_link1 = request.args.get('news_link1')
    if not news_link1:
        return jsonify({'error': 'news1 link is missing'}), 400

    if not news_link1.startswith(('http://', 'https://')):
        news_link1 = 'https://' + news_link1

    soup = scrape_page(news_link1)
    if soup:
        news_info1 = extract_news_details1(soup, news_link1)
        if news_info1:
            return jsonify(news_info1)
    return jsonify({'error': f'news1 details not found with url {news_link1}'}), 404

def extract_news_details1(soup, url):
    try:
        if 'jkalerts.com' in url:
            news_title1 = soup.select_one('h1.title')
            news_title_text1 = news_title1.text.strip() if news_title1 else "No title available"

            description1 = soup.select_one('p')
            description_text1 = description1.text.strip() if description1 else "No description available"

            content_tag = soup.find('div', class_="tags")
            tags = content_tag.find('a') if content_tag else None
            tag = tags.text.strip() if tags else "No tags available"

        else:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            ar = soup.find_all('article', class_='article-reader-container')

            news_title1 = soup.select_one('h1.viewsHeaderText')
            news_title_text1 = news_title1.text.strip() if news_title1 else "No title available"

            description1 = soup.select_one('p')
            description_text1 = description1.text.strip() if description1 else "No description available"

            content_tag = soup.find('body', class_="article-body")
            tags = content_tag.find('p') if content_tag else None
            tag = tags.text.strip() if tags else "No tags available"

        return {
            'title': news_title_text1,
            'description': description_text1,
            'tag': tag,
            'url': url
        }
    except Exception as e:
        print(f"Error extracting news details: {str(e)}")
        return None

def scrape_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        return None

@app.route('/scrape')
def scrape():
    page_number = int(request.args.get('page', 1))
    query = request.args.get('q', '')
    base_url = "https://www.google.com/about/careers/applications/jobs/results"
    url = f"{base_url}?start={166 * (page_number - 1)}"

    if query:
        url += f"&q={query}"

    soup = scrape_page(url)
    if soup:
        job_elements = soup.select('div.sMn82b')
        jobs = []
        for job in job_elements[:3]:
            try:
                title_element = job.select_one('h3.QJPWVe')
                title = title_element.text if title_element else "No title found"
                
                place_elements = job.select('span.r0wTof')
                places = [element.text for element in place_elements if element.text]
                place = ", ".join(places) if places else "No location found"
                
                qualifications_element = job.select_one('div.Xsxa1e')
                qualifications_list = qualifications_element.select('ul li') if qualifications_element else []
                qualifications = [li.text for li in qualifications_list if li.text]
                
                link_element = job.select_one('a[jsname="hSRGPd"]')
                job_link = link_element['href'] if link_element else "#"
                
                if job_link.startswith('/'):
                    job_link = f"https://www.google.com{job_link}"
                
                job_info = {
                    'title': title,
                    'place': place,
                    'qualifications': qualifications,
                    'link': job_link
                }
                jobs.append(job_info)
            except Exception as e:
                print(f"Error processing job element: {str(e)}")
                continue
        return jsonify(jobs)
    return jsonify({'error': 'Failed to retrieve data'}), 500

@app.route('/job-details')
def job_details():
    job_link = request.args.get('job_link')
    if not job_link:
        return jsonify({'error': 'Job link is missing'}), 400

    if not job_link.startswith(('http://', 'https://')):
        job_link = 'https://www.google.com/about/careers/applications/' + job_link

    soup = scrape_page(job_link)
    if soup:
        job_info = extract_job_details(soup)
        if job_info:
            return jsonify(job_info)
    return jsonify({'error': f'Job details not found with url {job_link}'}), 404


def extract_job_details(soup):
    try:
        job_title = soup.select_one('h2.p1N2lc').text.strip()
        Postion = soup.select_one('span.r0wTof').text.strip()
        qualifications = [li.text.strip() for li in soup.select('div.KwJkGe')]
        description = soup.select_one('div.aG5W3 > p').text.strip()
        apply_button = soup.select_one('a#apply-action-button')
        apply_url = apply_button['href'] if apply_button and 'href' in apply_button.attrs else None
        
        return {
            'title': job_title,
            'Postion': Postion,
            'qualifications': qualifications,
            'description': description,
            'apply_url': 'https://www.google.com/about/careers/applications/' + apply_url
        }
    except AttributeError as e:
        print(f"Error extracting job details: {str(e)}")
        return None
def get_db_connection():
    conn = sqlite3.connect('jobnew.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database and create table (runs only once)
def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Company_Name TEXT,
            Postion TEXT,
            Email TEXT,
            Phone TEXT,
            salary TEXT,
            Apply_Link TEXT,
            industry_type TEXT,
            Location TEXT,
            skills TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

# Run the initialization at startup
initialize_database()

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs')
    jobs = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in jobs])  # Convert rows to dictionaries

@app.route('/api/jobs', methods=['POST'])
def post_job():
    conn = None  
    try:
        job_data = request.get_json()
        print("Received Data:", job_data)  # Debugging: Print the incoming data

        if not job_data:
            return jsonify({'error': 'Invalid JSON or empty request body'}), 400

        # Validate required fields
        required_fields = ['Company_Name', 'Postion', 'Email', 'Phone', 'salary', 
                           'Apply_Link', 'industry_type', 'Location', 'skills']
        missing_fields = [field for field in required_fields if field not in job_data]
        
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO jobs (Company_Name, Postion, Email, Phone, salary, 
                              Apply_Link, industry_type, Location, skills)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_data['Company_Name'], job_data['Postion'], job_data['Email'], 
            job_data['Phone'], job_data['salary'], job_data['Apply_Link'], 
            job_data['industry_type'], job_data['Location'], job_data['skills']
        ))

        conn.commit()
        return jsonify({'message': 'Job posted successfully'}), 201

    except Exception as e:
        import traceback
        print("Error:", traceback.format_exc())  
        return jsonify({'error': str(e)}), 500

    finally:
        if conn:
            conn.close()









# from flask import Flask, jsonify, request
# import json
# import random
# import torch
# from model import NeuralNet
# from nltk_utils import bag_of_words, tokenize


# # Load model and data
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# FILE = "data.pth"
# data = torch.load(FILE)

# input_size = data["input_size"]
# hidden_size = data["hidden_size"]
# output_size = data["output_size"]
# all_words = data['all_words']
# tags = data['tags']
# model_state = data["model_state"]

# model = NeuralNet(input_size, hidden_size, output_size).to(device)
# model.load_state_dict(model_state)
# model.eval()

# with open('intents.json', 'r') as json_data:
#     intents = json.load(json_data)

# bot_name = "Amaan"

# @app.route("/chat", methods=["POST"])
# def chat():
#     user_message = request.json.get("message")
#     if not user_message:
#         return jsonify({"error": "Empty message"}), 400

#     sentence = tokenize(user_message)
#     X = bag_of_words(sentence, all_words)
#     X = X.reshape(1, X.shape[0])
#     X = torch.from_numpy(X).to(device)

#     output = model(X)
#     _, predicted = torch.max(output, dim=1)

#     tag = tags[predicted.item()]
#     probs = torch.softmax(output, dim=1)
#     prob = probs[0][predicted.item()]

#     if prob.item() > 0.75:
#         for intent in intents['intents']:
#             if tag == intent["tag"]:
#                 response = random.choice(intent['responses'])
#                 return jsonify({"bot": response})
#     else:
#         return jsonify({"bot": "I do not understand..."})





import json
import torch
import random
import re
import urllib3
from datetime import datetime
from flask import Flask, request, jsonify
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

bot_name = "Amaan"
def fetch_notifications():
    """Scrapes latest JKPSC notifications"""
    base_url = "http://www.jkpsc.nic.in/"
    try:
        response = requests.get(base_url, timeout=15, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        notifications = []

        for item in soup.select('.notificationnews.myBox li:not([style*="display: none"])'):
            link = item.find('a')
            if link and link.text.strip():
                text = re.sub(r'\d{2}/\d{2}/\d{4}', '', link.text).strip()
                if any(keyword in text.lower() for keyword in ['exam', 'admit', 'result', 'syllabus']):
                    notifications.append({
                        "text": text,
                        "link": urljoin(base_url, link['href']),
                        "date": datetime.now().strftime("%d/%m/%Y")
                    })

        return notifications[:5]  # Return top 5 notifications

    except Exception as e:
        print(f"JKPSC Scraping error: {str(e)}")
        return None

def fetch_notifications_jkssb():
    """Scrapes latest JKSSB notifications with document download links"""
    base_url = "https://jkssb.nic.in/"
    target_url = urljoin(base_url, "Whatsnew.html")

    try:
        response = requests.get(target_url, timeout=15, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        notifications = []

        # Select all relevant links
        links = soup.select("td a.linkText")

        for link in links[:7]:  # Limit to first 7
            text = link.text.strip()
            document_url = urljoin(base_url, link.get('href').replace("..", ""))

            notifications.append({
                "text": text,
                "link": document_url,
                "date": datetime.now().strftime("%d/%m/%Y")
            })

        return notifications

    except Exception as e:
        print(f"JKSSB Scraping error: {str(e)}")
        return None

def fetch_neet_notifications():
    """Scrapes all NEET 2025 notifications with document download links"""
    base_url = "https://neet.nta.nic.in/"
    try:
        response = requests.get(base_url, timeout=15, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        notifications = []

        # Select <ul><li><a> structure for NEET notifications
        links = soup.select("div.vc_tta-panel-body div.gen-list ul li a")

        for link in links:  # Scraping all available notifications
            text = link.text.strip()
            document_url = link.get('href')

            # Make sure it's a valid absolute URL
            if document_url and document_url.startswith('http'):
                notifications.append({
                    "text": text,
                    "link": document_url,
                    "date": datetime.now().strftime("%d/%m/%Y")
                })

        return notifications

    except Exception as e:
        print(f"NEET Scraping error: {str(e)}")
        return None

def fetch_jee_notifications():
    """Scrapes all JEE notifications with document download links"""
    base_url = "https://jeemain.nta.nic.in/"
    try:
        # Send a request to the JEE notifications page
        response = requests.get(base_url, timeout=15, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        notifications = []

        # Select <ul><li><a> structure for JEE notifications (assumed)
        links = soup.select("div.vc_tta-panel-body div.gen-list ul li a")

        for link in links:  # Scraping all available notifications
            text = link.text.strip()
            document_url = link.get('href')

            # Ensure the URL is valid
            if document_url and document_url.startswith('http'):
                notifications.append({
                    "text": text,
                    "link": document_url,
                    "date": datetime.now().strftime("%d/%m/%Y")
                })

        return notifications

    except Exception as e:
        print(f"JEE Scraping error: {str(e)}")
        return None

def format_notifications(notifications, source="JKPSC"):
    """Formats notifications into an HTML format with clickable 'Download' links."""
    response = f"\n📢 <b>Latest {source} Updates:</b><br><br>"
    
    if not notifications:
        return f"No recent {source} updates found."
    
    for i, notif in enumerate(notifications[:7], start=1):  # Increased to 7 items
        text = notif['text']
        date = notif.get('date', 'N/A')
        link = notif['link']
        
        response += f"{i}. {text}<br>   📅 {date}<br>  🔗 <a href='{link}' target='_blank'>Download</a><br><br>"
    
    return response

def detect_exam_type(user_message):
    """Detects which exam type the user is asking about"""
    user_message = user_message.lower()
    
    # Check for specific exam mentions
    if any(keyword in user_message for keyword in ['jkssb', 'ssb']):
        return 'jkssb'
    elif any(keyword in user_message for keyword in ['neet', 'medical']):
        return 'neet'
    elif any(keyword in user_message for keyword in ['jee', 'engineering', 'iit']):
        return 'jee'
    elif any(keyword in user_message for keyword in ['jkpsc', 'psc']):
        return 'jkpsc'
    
    # Default to JKPSC if no specific exam is mentioned but exam keywords are present
    exam_keywords = ['exam', 'admit', 'result', 'test', 'notification', 'update']
    if any(keyword in user_message for keyword in exam_keywords):
        return 'jkpsc'
    
    return None

def fetch_all_notifications():
    """Fetches notifications from all sources and combines them"""
    all_notifications = {
        'JKPSC': fetch_notifications(),
        'JKSSB': fetch_notifications_jkssb(),
        'NEET': fetch_neet_notifications(),
        'JEE': fetch_jee_notifications()
    }
    
    combined_response = ""
    for source, notifications in all_notifications.items():
        if notifications:
            combined_response += format_notifications(notifications, source) + "<br>"
    
    return combined_response if combined_response else "No recent updates found from any source."

@app.route("/chat", methods=["POST"])
def chat():
    """Handles chatbot interactions with multiple exam sources"""
    try:
        user_message = request.json.get("message", "").lower().strip()

        if not user_message:
            return jsonify({"response": "Please enter a valid question"})

        # Detect exam type from user message
        exam_type = detect_exam_type(user_message)
        
        # Handle specific exam notifications
        if exam_type:
            notifications = None
            source_name = ""
            fallback_url = ""
            
            if exam_type == 'jkpsc':
                notifications = fetch_notifications()
                source_name = "JKPSC"
                fallback_url = "http://jkpsc.nic.in"
            elif exam_type == 'jkssb':
                notifications = fetch_notifications_jkssb()
                source_name = "JKSSB"
                fallback_url = "https://jkssb.nic.in"
            elif exam_type == 'neet':
                notifications = fetch_neet_notifications()
                source_name = "NEET"
                fallback_url = "https://neet.nta.nic.in"
            elif exam_type == 'jee':
                notifications = fetch_jee_notifications()
                source_name = "JEE"
                fallback_url = "https://jeemain.nta.nic.in"
            
            if notifications:
                return jsonify({
                    "response": format_notifications(notifications, source_name),
                    "type": "exam_updates"
                })
            else:
                return jsonify({
                    "response": f"⚠️ No recent {source_name} updates found. Check the official website: {fallback_url}",
                    "type": "error"
                })

        # Check for requests for all notifications
        if any(phrase in user_message for phrase in ['all updates', 'all notifications', 'everything', 'all exams']):
            combined_notifications = fetch_all_notifications()
            return jsonify({
                "response": combined_notifications,
                "type": "exam_updates"
            })

        # Model processing for other intents
        sentence = tokenize(user_message)
        X = bag_of_words(sentence, all_words)
        X = X.reshape(1, X.shape[0])
        X = torch.from_numpy(X).to(device)

        output = model(X)
        _, predicted = torch.max(output, dim=1)
        tag = tags[predicted.item()]
        probs = torch.softmax(output, dim=1)
        prob = probs[0][predicted.item()]

        # Intent matching for other responses
        if prob.item() > 0.65:
            for intent in intents['intents']:
                if tag == intent["tag"]:
                    if tag == "notifications":
                        # Default to JKPSC notifications for general notification requests
                        notifications = fetch_notifications()
                        if notifications:
                            return jsonify({
                                "response": format_notifications(notifications, "JKPSC"),
                                "type": "exam_updates"
                            })
                        return jsonify({
                            "response": "⚠️ Couldn't fetch updates. Try visiting: http://jkpsc.nic.in",
                            "type": "error"
                        })

                    return jsonify({"response": random.choice(intent['responses'])})

        # Default response with available exam types
        return jsonify({
            "response": "I can help you with notifications from:\n🏛️ JKPSC - Jammu & Kashmir Public Service Commission\n🏢 JKSSB - Jammu & Kashmir Services Selection Board\n🏥 NEET - National Eligibility cum Entrance Test\n🎓 JEE - Joint Entrance Examination\n\nJust ask about any specific exam or say 'all updates' for everything!"
        })

    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({
            "response": "Service temporarily unavailable. Please try again later.",
            "type": "error"
        }), 500

























if __name__ == '__main__':
    app.run(debug=True)
