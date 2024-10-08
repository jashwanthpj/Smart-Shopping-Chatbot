import psycopg2
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import os
import json

model = SentenceTransformer('all-MiniLM-L6-v2')
genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")
# API_KEY = "AIzaSyA-mo1K9o-vYyb-Xtbrnde_E_oCaMupkVs"
# API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=${API_KEY}"

user_query = "I want a black shirt, only cotton for men"

query_embedding = model.encode(user_query).tolist()

try:
    conn = psycopg2.connect(
        dbname = "shopping_data",
        username = "postgres",
        password = "Pj262001@",
        host = "localhost"
    )

    cursor = conn.cursor()

    cursor.execute(
        f"SELECT id, category, sub_category, uri, content, pdt_desc as description FROM apparels ORDER BY embedding <=> {query_embedding}:: vector LIMIT 10"
    )

    responses = cursor.fetchall()
    product_list = []

    for response in responses:
        id = response[0]
        category = response[1]
        sub_category = response[2]
        uri = response[3]
        content = response[4]
        pdt_desc = response[5]

        prompt = f"""Read this user search text: '{user_query}' 
                    Compare it against the product record: '{response}' 
                    Return a response with 3 values:
                    1) MATCH: if the 2 products are at least 85% matching or not: YES or NO
                    2) PERCENTAGE: percentage of match, make sure that this percentage is accurate
                    3) DIFFERENCE: A clear short easy description of the difference between the 2 products.
                    Remember if the user search text says that some attribute should not be there, and the product record has it, it should be a NO match.
                    """
        
        LLM_output = genai.generate_text(model = "gemini-1.5-flash", prompt = prompt).text.strip()
        print(LLM_output)

        product_data = {
            "id" : id,
            "category" : category,
            "sub_category" : sub_category,
            "uri" : uri,
            "description" : pdt_desc,
            "llm_response" : LLM_output
        }

        product_list.append(product_data)

    json_output = json.dumps(product_list)
    print(json_output)

except Exception as e:
    print("could not fetch data : ", e)



