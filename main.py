import psycopg2
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import os
import json

model = SentenceTransformer('all-MiniLM-L6-v2')

API_KEY = "AIzaSyA-mo1K9o-vYyb-Xtbrnde_E_oCaMupkVs"
genai.configure(api_key=API_KEY)
llm_model = genai.GenerativeModel("gemini-1.5-flash")

user_query = "I want a black tshirt for boys, pure cotton"

query_embedding = model.encode(user_query).tolist()

try:
    conn = psycopg2.connect(
        dbname = "shopping_data",
        user = "postgres",
        password = "Pj262001@",
        host = "localhost"
    )

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, category, sub_category, uri, content, pdt_desc as description
        FROM apparels
        ORDER BY embedding <=> %s::vector LIMIT 10
    """, (query_embedding,)
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
                    Compare it against the product record: '{pdt_desc}' 
                    Return a response with 3 values:
                    1) MATCH: if the 2 products are at least 85% matching or not: YES or NO
                    2) PERCENTAGE: percentage of match, make sure that this percentage is accurate
                    3) DIFFERENCE: A clear short easy description of the difference between the 2 products.
                    Remember if the user search text says that some attribute should not be there, and the product record has it, it should be a NO match.
                    """
        
        LLM_output = llm_model.generate_content(prompt).text.strip()
        # print(LLM_output)

        if '**MATCH:** YES' in LLM_output:
            product_data = {
                "id" : id,
                "category" : category,
                "sub_category" : sub_category,
                "uri" : uri,
                "description" : pdt_desc,
                "llm_response" : LLM_output
            }

            product_list.append(product_data)

    final_suggestions = product_list[:min(4,len(product_list))]
    json_output = json.dumps(product_list)
    print('total suggested products: ', len(product_list))
    print('Final Suggestions: ', len(final_suggestions))

except Exception as e:
    print("could not fetch data : ", e)

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()

