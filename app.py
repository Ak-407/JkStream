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

                    read_more_div = article.find('div', class_='readMore')
                    read_more_tag = read_more_div.find('a') if read_more_div else None
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
    headers = {'User-Agent': 'Mozilla/5.0'}
    articles_data2 = []

    async with aiohttp.ClientSession() as session:
        response = await fetch(session, url, headers)

        if response:
            soup = BeautifulSoup(response, 'html.parser')
            articles = soup.find_all('article', class_='post')

            for article in articles:
                try:
                    time_tag = article.find('div', class_='post-date-ribbon')
                    time_text = time_tag.get_text(strip=True) if time_tag else "No date available"

                    title_tag = article.find('h2', class_='title')
                    title_text = title_tag.get_text(strip=True) if title_tag else "No title available"

                    info_tag = article.find('div', class_='post-info')
                    info_text = info_tag.get_text(strip=True) if info_tag else "No information available"

                    image_tag = article.find('img', class_='attachment-ribbon-lite-featured size-ribbon-lite-featured wp-post-image')
                    image_url = image_tag.get('src', '/static/m.png') if image_tag else '/static/m.png'

                    content_tag = article.find('div', class_='post-content')
                    content_text = content_tag.get_text(strip=True) if content_tag else "No content available"

                    read_more_div = article.find('div', class_='readMore')
                    read_more_tag = read_more_div.find('a') if read_more_div else None
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
                except Exception as e:
                    print(f"Error parsing article in scrape_articles2: {e}")
        return articles_data2


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

                    read_more_div = article.find('div', class_='readMore')
                    read_more_tag = read_more_div.find('a') if read_more_div else None
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
        print(f"Scraping error: {str(e)}")
        return None


def format_notifications(notifications):
    """Formats notifications into an HTML format with clickable 'Download' links."""
    response = "\n📢 <b>Latest JKPSC Updates:</b><br><br>"  # Added HTML tags for bold and line breaks
    
    for i, notif in enumerate(notifications[:5], start=1):
        text = notif['text']
        date = notif.get('date', 'N/A')
        link = notif['link']
        
        response += f"{i}. {text}<br>   📅 {date}<br>  🔗 <a href='{link}' target='_blank'>Download</a><br><br>"
    
    return response




@app.route("/chat", methods=["POST"])
def chat():
    """Handles chatbot interactions"""
    try:
        user_message = request.json.get("message", "").lower().strip()

        if not user_message:
            return jsonify({"response": "Please enter a valid question"})

        # Model processing
        sentence = tokenize(user_message)
        X = bag_of_words(sentence, all_words)
        X = X.reshape(1, X.shape[0])
        X = torch.from_numpy(X).to(device)

        output = model(X)
        _, predicted = torch.max(output, dim=1)
        tag = tags[predicted.item()]
        probs = torch.softmax(output, dim=1)
        prob = probs[0][predicted.item()]

        # Handling notifications
        exam_keywords = ['exam', 'admit', 'result', 'test', 'notification']
        if any(keyword in user_message for keyword in exam_keywords):
            notifications = fetch_notifications()
            if notifications:
                return jsonify({
                    "response": format_notifications(notifications),
                    "type": "exam_updates"
                })
            return jsonify({
                "response": "No recent exam updates found. Check the official website: http://jkpsc.nic.in",
                "type": "error"
            })

        # Intent matching
        if prob.item() > 0.65:
            for intent in intents['intents']:
                if tag == intent["tag"]:
                    if tag == "notifications":
                        notifications = fetch_notifications()
                        print("dsjhhbdjlcdbaskldbvsk;bask;bk;")
                        print(notifications)
                        if notifications:
                            return jsonify({"response": format_notifications(notifications)})
                        return jsonify({"response": "⚠️ Couldn't fetch updates. Try visiting: http://jkpsc.nic.in"})

                    return jsonify({"response": random.choice(intent['responses'])})

        return jsonify({"response": "I specialize in JKPSC notifications. Ask me about:\n- Latest exam updates\n- Recent circulars\n- Government job news"})

    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({"response": "Service temporarily unavailable. Please try again later."}), 500
























import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))  # Default to port 5000 if not set
    app.run(host='0.0.0.0', port=port, debug=True)

