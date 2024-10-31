import psycopg2
from sentence_transformers import SentenceTransformer
import requests
import json


def build_suggestions_json(user_query):

    model = SentenceTransformer('all-MiniLM-L6-v2')

    url = "http://localhost:11434/api/generate"

    # user_query = "I want a black tshirt for boys, pure cotton"

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
            ORDER BY embedding <=> %s::vector LIMIT 5
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
                        Expected output-
                        'MATCH': YES,
                        PERCENTAGE: 90,
                        DIFFERENCE: The product is a black casual T-shirt suitable for boys, matching the requested color and category. However, it’s labeled as a T-shirt instead of a formal shirt.
                """
            
            query_payload = {
                "model" : "mistral",
                "prompt" : prompt,
                "stream" : False
            }
            headers = {"Content-Type" : "application/json"}

            LLM_output = requests.post(url, json=query_payload, headers=headers)
            print("this is the llm output: \n\n",LLM_output)
            LLM_output.raise_for_status()
            
            LLM_response = LLM_output.json()['response']
            # print(LLM_output)

            if 'YES' in LLM_response:
                try:
                    percentage = int(LLM_response.split('PERCENTAGE:')[1].split(',')[0].strip())
                except(IndexError, ValueError):
                    percentage = 0
                product_data = {
                    "id" : id,
                    "category" : category,
                    "sub_category" : sub_category,
                    "uri" : uri,
                    "description" : pdt_desc,
                    "llm_response" : LLM_response,
                    "match_percentage" : percentage
                }

                product_list.append(product_data)

        top_products = sorted(product_list, key=lambda x: x["match_percentage"], reverse=True)
        final_suggestions = top_products[:min(4,len(product_list))]
        print('total suggested products: ', len(product_list))
        print('Final Suggestions: ', len(final_suggestions))

        return final_suggestions

    except Exception as e:
        print("could not fetch data : ", e)
        return json.dumps({"error": str(e)})

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

