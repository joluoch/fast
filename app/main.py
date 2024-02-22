from flask import Flask,request,jsonify
import warnings
import openai
import requests
import re
import json
import os
import time
warnings.filterwarnings('ignore')

app = Flask(__name__)

def get_meta(link):
    try:
        url = "https://metadata.p.rapidapi.com/metadata"

        querystring = {"url":link}

        headers = {
            "X-RapidAPI-Key": "87c0893836msh6fbc6b90fbe0f03p1ae02ajsn6805c0e169a3",
            "X-RapidAPI-Host": "metadata.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        result = response.json()
        image = result['opengraph']['image']
        
        
    except Exception as e:
            print(f"Error getting meta one  : {e} for url={link}")
            image = None


    return image


def get_article(url):
    api_url = "https://article-extractor2.p.rapidapi.com/article/parse"
    querystring = {
        "url": url,
        "word_per_minute": "300",
        "desc_truncate_len": "210",
        "desc_len_min": "180",
        "content_len_min": "200"
    }
    headers = {
        "X-RapidAPI-Key": "87c0893836msh6fbc6b90fbe0f03p1ae02ajsn6805c0e169a3",
        "X-RapidAPI-Host": "article-extractor2.p.rapidapi.com"
    }
    response = requests.get(api_url, headers=headers, params=querystring)
    response = response.json()
    content = re.sub('\s+', ' ', re.sub('<[^<]+?>', '', response['data']['content'])).strip()
    return content

def get_summary(text_for_gpt):
    prompt = f"""
                reference: {text_for_gpt}
                Generate an article based on the provided reference with the following specifications:
                1. The title should be engaging and no longer than 95 characters.
                2. Summarize the main points with at least 5 highlights without excessive detail.
                3. Write an informative introduction utilizing the '5 W's' rule (who, what, when, where, why).
                4. Include exact quotes from the original authors as they appear in the reference text.
                5. article should be longer then 300 words.
                6. Ensure a high Flesch-Kincaid readability score to appear human-written and evade AI detectors.
                7. Integrate images from the reference article at the end if they are provided.
                8. Identify 3 to 5 keywords pertinent to the subject matter.
                9. Format content with page breaks suitable for JSON representation.
                The result should be returned in a valid JSON structure:
                "title": "Sample Title", "image": "http://url_to_image.jpg", "highlights": ["highlight1", "highlight2", "highlight3"], "content": "Sample content", "keywords": ["keyword1", "keyword2", "keyword3"], "url": "http://article_url.com"
                Please ensure JSON validity by properly escaping any double quotes or special characters within the fields.
                """

    openai.api_key = "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"
    counter = 0
    max_attempts = 0  # Maximum number of attempts before stopping

   
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=1,
        max_tokens=3100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    res_json = response["choices"][0]["message"]["content"]
    
        
    return res_json


def api_people_also_ask(query):
    url = "https://people-also-ask-api.p.rapidapi.com/people_also_ask"
    querystring = {"query": query}

    headers = {
        "X-RapidAPI-Key": "87c0893836msh6fbc6b90fbe0f03p1ae02ajsn6805c0e169a3",
        "X-RapidAPI-Host": "people-also-ask-api.p.rapidapi.com"
    }

    max_attempts = 0
   
    response = requests.get(url, headers=headers, params=querystring)
    text = response.json()['data']['people_also_ask']

    qa_list = [
        {
            'question': entry['question'],
            'answer': entry.get('answers', [{}])[0].get('value', {}).get('text')
        }
        for entry in text[:3]
    ]

    return qa_list


def generate_sum(url):
    
    content = get_article(url)
    try:
        summary= get_summary(content)
        summary_loaded = json.loads(summary)
        keywords = summary_loaded['keywords']
        keywords = '+'.join(keywords)
    except:
        time.sleep(10)
        summary = get_summary(content)
        summary_loaded = json.loads(summary)
        keywords = summary_loaded['keywords']
        keywords = '+'.join(keywords)

    return keywords
    

def get_article_fast(url):
    #print(url)
    api_url = "https://article-extractor2.p.rapidapi.com/article/parse"
    querystring = {
        "url": url,
        "word_per_minute": "300",
        "desc_truncate_len": "210",
        "desc_len_min": "180",
        "content_len_min": "200"
    }
    headers = {
        "X-RapidAPI-Key": "87c0893836msh6fbc6b90fbe0f03p1ae02ajsn6805c0e169a3",
        "X-RapidAPI-Host": "article-extractor2.p.rapidapi.com"
    }
    response = requests.get(api_url, headers=headers, params=querystring)
    response = response.json()
    try:
        content = re.sub('\s+', ' ', re.sub('<[^<]+?>', '', response['data']['content'])).strip()
        return content
    except:
        print( "No content found")
        
def get_summary_fast(text_for_gpt):
    prompt = f"""
                references: {text_for_gpt}
                Generate an article based on the provided references with the following specifications:
                1. The title should be engaging and no longer than 95 characters.
                2. Summarize the main points with at least 5 highlights without excessive detail.
                3. Write an informative introduction utilizing the '5 W's' rule (who, what, when, where, why).
                4. Include exact quotes from the original authors as they appear in the reference text.
                5. article should be longer then 300 words.
                6. Ensure a high Flesch-Kincaid readability score to appear human-written and evade AI detectors.
                7. Integrate images from the reference article at the end if they are provided.
                8. Identify 3 to 5 keywords pertinent to the subject matter.
                9. Format content with page breaks suitable for JSON representation.
                The result should be returned in a valid JSON structure:
                "title": "Sample Title", "image": "http://url_to_image.jpg", "highlights": ["highlight1", "highlight2", "highlight3"], "content": "Sample content", "keywords": ["keyword1", "keyword2", "keyword3"], "url": "http://article_url.com"
                Please ensure JSON validity by properly escaping any double quotes or special characters within the fields.
                """

    openai.api_key = "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"
    counter = 0
    max_attempts = 0  # Maximum number of attempts before stopping

   
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=1,
        max_tokens=3100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    res_json = response["choices"][0]["message"]["content"]
    
        
    return res_json

def get_similar_news(keywords):

	url = "https://real-time-news-data.p.rapidapi.com/search"

	querystring = {"query":f"{keywords}","country":"US","lang":"en"}

	headers = {
		"X-RapidAPI-Key": "87c0893836msh6fbc6b90fbe0f03p1ae02ajsn6805c0e169a3",
		"X-RapidAPI-Host": "real-time-news-data.p.rapidapi.com"
	}

	response = requests.get(url, headers=headers, params=querystring)

	data = response.json()
	links = [item['link'] for item in data['data'][:4]]

	return links
def json_to_html_string(article_data):
    highlights = article_data.get('highlights', [])

    # Create the HTML content
    html_content = f"""
    <html>
    <body>
        <ul>
    """

    # Add each highlight as list items
    for highlight in highlights:
        html_content += f"<li>{highlight}</li>"

    # Close the unordered list and add the promptV
    html_content += f"""
        </ul>

    </body>
    </html>
    """

    return html_content

def json_to_html_stringPAA(PAA_json):
    # Create the HTML content
    html_content = f"""
    <html>
    <body>
        <ul>
    """

    questions = PAA_json["questions"]
    answers = PAA_json["answers"]

    if questions and answers:
        for question, answer in zip(questions, answers):
            html_content += f"<li> {question} : {answer}</li>"
    else:
        html_content += "<li>Empty questions/answers, contact administrator if problems persist</li>"

    # Close the unordered list
    html_content += f"""
        </ul>
    </body>
    </html>
    """

    return html_content

def make_ycode_article_json(data, html, htmlPAA, prompt_v):
    payload = {
        "Name": None,
        "Description": None,
        "Image": None,
        "Content": None,
        "Prompt_V": None,
        "Google_Highlights": None,
        "Original_Link": None
    }
    payload["Name"] = data["title"]
    payload["Image"] = data["image"]
    keywords = data["keywords"]
    if keywords is not None:
        payload["Description"] = ', '.join(keywords)
    else:
        payload["Description"] = data["title"]
    payload["Content"] = html
    payload["Prompt_V"] = prompt_v
    payload["Google_Highlights"] = htmlPAA
    payload["Original_Link"] = data["References"]
    return payload

def get_tags(summarys):
    prompt = f"""article summary : {summarys}
            Analyze the provided article summary and generate a list of categorisation tags:
            - 1 main category based on IAB Content Taxonomy v3.0 (for example "Arts & Entertainment (IAB-1)")
            - 1 main subcategory (child of main category) based on IAB Content Taxonomy v3.0 (for example "Celebrity Fan/Gossip (IAB-1-2)")
            - up to 3 people tags, that were the focal points of the story, use full well-known names (for example "Kanye West")
            - up to 3 location tags, that were the focal points of the story, use full location name (for example "New York, USA")
            - up to 3 event tags, that were the focal points of the story, tag only specific events, use full event name without year (for example "Grammy Awards")
            - up to 3 occasion tags, that were the focal points of the story, tag only specific global occasions (for example "Christmas")
            - up to 3 additional topic tags, that describe the focal points of the story, up to 3 words each

            Use JSON format:
            "type_name":["tag_name"]
            If N/A - empty array.
          """
    openai.api_key = "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"
    counter = 0
    max_attempts = 0  # Maximum number of attempts before stopping


    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=1,
        max_tokens=3100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    gpt_response = response["choices"][0]["message"]["content"]
    gpt_response = json.loads(gpt_response)

    return gpt_response

def send_fastnews_to_ycode(fastnews):
    key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiZjZjYjIxZDEzOGY2OWI5NmM1NDIxMzY4YjNmYWU3MWQ0NjcwMTFmNTA4OTE3OTU1ZjJkYzgyM2RkZWQyMTQ1ZDQ2NjhiNTU2M2ZjMTUyNGUiLCJpYXQiOjE3MDY2MDEwMzMuNTcwMDMzLCJuYmYiOjE3MDY2MDEwMzMuNTcwMDM1LCJleHAiOjQ4NjIyNzQ2MzMuNTUyODU3LCJzdWIiOiIxNDc5MSIsInNjb3BlcyI6WyJ0b2tlbnNfZnVsbCIsIndlYmhvb2tzX2Z1bGwiLCJkYXRhYmFzZV90YWJsZXNfZnVsbCJdfQ.QXsZLJa51sJ-S2zfR0aU03fzWQM1UAWAZTBnFLrSNdCMJPLZfsU5ZLAULyTXtraYQ2xZLv7Vxgz7V_Pi-2twnxXWniX8jSB_YUnWLy5mqW1__-kaTR1xTawYEeDEfmvwhhIhx8pxejvk87Rh_cg0Pq50PaMdbeWDZATlqi9gu8tTFVwQPmGhQfA0dJNs721N5UG-P1B6Sl6qVobkrhpcp7y9E50N73bBy93-jGf2oIKM1QM-2P_nV4sOonYfAO9KaieN97UtxYTnXxK14OWvfuraB354kuh4ZB23Sn0_5u1Gy9__REwcnPy4O5iupc_87HMRYtQ3QKRKbjzFG-fRbO1FsMpJ9TFllOZnSQdYJYtXOQd2naMKBCPS8vELM-xKTC7x_GzyYl9gyZJYC9H4JdLF59XxpoGrnUHJbvUMBI8F-9zwNM0zX2CgFyNuIecEfPk91FXnZF62XvVl8KgIeS6Sqs1-Ahjj2ahdX-axhL5PGPYHoPWAVw-tPZ7tq1Ok-2w2SyxGZrLYNPjRtXklQlkfRg6J0q2FOt9V-coNXlGPqQrR_HCDXoEo5XHP9mBZIrrK08FgMMQLiKyR8nM-mrom7VifevWnisXwpRnCnIBo8Q2XbA4fbjGKbFIuCuv4tCDLo4gTi0vZfJgU5YdX7uXIDzZ3Uu28oUtrfTtxHwU'
    url = "https://app.ycode.com/api/v1/collections/65b893e33b7b7/items"

    payload = {
        "Name": fastnews['Name'],
        "Description": fastnews['Description'],
        "Image": fastnews['Image'],
        "Content": fastnews['Content'],
        "Prompt_V": fastnews["Prompt_V"],
        "Google_Highlights": fastnews["Google_Highlights"],
        "Original_Link": fastnews["Original_Link"],
        'main_category': fastnews['main_category'], 
        'main_subcategory': fastnews['main_subcategory'],
        'people': fastnews['people'],
        'location': fastnews['location'],
        'event': fastnews['event'],
        'occasion': fastnews['occasion'],
        'topic_': fastnews['additional_topic']
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Bearer " + key
    }

    response = requests.post(url, json=payload, headers=headers)
    print("posted")
    print(response.text)

    return response.text

def rename_keys(data):
    new_keys_map = {
        "people": ["people", "peoples","people_tags"],
        "location": ["location", "locations","location_tags"],
        "event": ["event", "events","event_tags"],
        "occasion": ["occasion", "occasions","occasion_tags"],
        "additional_topic": ["additional_topic", "additional_topics","additional_topic_tags"]
    }

    # Flatten the new_keys_map to a reverse mapping
    reverse_map = {trigger: new_key for new_key, triggers in new_keys_map.items() for trigger in triggers}

    # Create a new dictionary to store the renamed keys and their values
    new_data = {reverse_map.get(key, key): value for key, value in data.items()}

    return new_data
def post_to_ycode(summarised_article):
    if isinstance(summarised_article, dict):
        summary_loaded = summarised_article
    else:
        try:
            summary_loaded = json.loads(summarised_article)
        except json.JSONDecodeError:
            return "Invalid JSON"

    html = json_to_html_string(summary_loaded)
    
    if summary_loaded.get("questions"):
        htmlPAA = json_to_html_stringPAA(summary_loaded)
        ycode = make_ycode_article_json(summary_loaded, html, htmlPAA, "0.0.1")
    else:
        ycode = make_ycode_article_json(summary_loaded, html, None, "0.0.1")
    
    summarys = summary_loaded['content']
    js = get_tags(summarys)
    for key, value in js.items():
        if isinstance(value, list):
            js[key] = ",".join(value)
    if js is None:
        js = get_tags(summarys)
        for key, value in js.items():
            if isinstance(value, list):
                js[key] = ",".join(value)
    js = rename_keys(js)
    print(js)
    ycode.update(js)
    resp = send_fastnews_to_ycode(ycode)
    print("sent to ycode")

    return resp

def api_people_also_ask(query):
    url = "https://people-also-ask-api.p.rapidapi.com/people_also_ask"
    querystring = {"query": query}

    headers = {
        "X-RapidAPI-Key": "87c0893836msh6fbc6b90fbe0f03p1ae02ajsn6805c0e169a3",
        "X-RapidAPI-Host": "people-also-ask-api.p.rapidapi.com"
    }

    max_attempts = 0
   
    response = requests.get(url, headers=headers, params=querystring)
    text = response.json()['data']['people_also_ask']

    qa_list = [
        {
            'question': entry['question'],
            'answer': entry.get('answers', [{}])[0].get('value', {}).get('text')
        }
        for entry in text[:3]
    ]

    return qa_list

def article_to_ycode(url,image,keywords):
    links= get_similar_news(keywords)
    articles = {"reference {}: {}".format(i+1, get_article_fast(link)) for i, link in enumerate(links) if get_article_fast(link) is not None}
    try:
        summary_fast= get_summary_fast(articles)
        summary_loaded_fast = json.loads(summary_fast)
    except:
        summary_fast= get_summary_fast(articles)
        summary_loaded_fast = json.loads(summary_fast)
    keyword_one = summary_loaded_fast['keywords'][0]
    question_answers = api_people_also_ask(keyword_one)
    links.insert(0, url)
    link_string = ','.join(links)

    if question_answers:
        PAAjson = {
            'questions': [item['question'] for item in question_answers],
            'answers': [item['answer'] for item in question_answers]
        }
        
        summary_loaded_fast['References'] = link_string
        summary_loaded_fast.update(PAAjson)
        summary_loaded_fast.pop('url', None)
        if image is not None:
           summary_loaded_fast["image"] = image
        else:
            summary_loaded_fast["image"] = None
    else:
        summary_loaded_fast['References'] = link_string
        if image is not None:
            summary_loaded_fast["image"] = image
        else:
           summary_loaded_fast["image"] = None

    return summary_loaded_fast

def singles(url):
    fast_attempts = 0
    success = False
    while fast_attempts < 3 and not success:
        try:
            image = get_meta(url)
            keywords  = generate_sum(url)
            fastnews = article_to_ycode(url, image, keywords)
            resp = post_to_ycode(fastnews)
            success = True
        except Exception as e:
            print(e)
            fast_attempts += 1
    
    return resp

@app.route('/get_summary/', methods=['GET'])
def get_summary_api():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter is missing."}), 400
    try:
        resp = singles(url)
        if resp:
            return jsonify(resp), 200
        else:
            return jsonify({"error": "Failed to process URL after multiple attempts."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    


if __name__ ==  "__main__":

    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    


