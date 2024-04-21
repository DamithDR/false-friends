import json
import sys
import time
import pandas as pd

from openai import OpenAI
from tqdm import tqdm

api_key = input("Please enter your OpenAI API key")

client = OpenAI(
    api_key=api_key
)

# with open('data/en.txt', 'r') as en:
#     english = en.readlines()
# with open('data/es.txt', 'r') as es:
#     spanish = es.readlines()
#
# english = english[:10000]
# spanish = spanish[:10000]

df = pd.read_excel('data/false_friends.xlsx')
df = df.dropna()
english = df['English'].tolist()
spanish = df['Spanish'].tolist()

print(f'Total no of sentences : {len(english)}')
en_sent = []
es_sent = []
responses = []
with tqdm(total=len(english)) as pbar:
    for english_sentence, spanish_sentence in zip(english, spanish):
        message = """

        A "false friend" is a linguistic term referring to words in different languages that look or sound similar but have different meanings. These similarities can often lead to confusion or misunderstandings for language learners or even native speakers who encounter them in unfamiliar contexts. For example, the English word "embarrassed" and the Spanish word "embarazada" sound similar, but "embarazada" means "pregnant" in Spanish, not "embarrassed." So, "embarazada" is a false friend for English speakers trying to communicate in Spanish.

        You will be given sentences as pairs, the english sentence and the spanish translation of it.
        Your task is to detect false-friends based terms in the given Spanish sentence and then return a json object saying
        if there is a false-friend term Yes/No and the false-friend spanish term if you find any. Make sure you do not detect any country names, state names or any names.
        
        For example : "captura y secuestro del carbono" is a term based on false friend translated from "carbon capture and sequestration", because the lexical unit "secuestro" is a false friend of "sequestration"
        
        Example json object : {false_friend_term_found : 'yes',false_friend_term = ['term1','term2']}

        Do not provide any other explanation. Just return json object with the results.
        English :""" + english_sentence + "" \
                                          "Spanish : " + spanish_sentence

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ],
            model="gpt-3.5-turbo-0125",
            response_format={"type": "json_object"},
            temperature=0.1,
            # max_tokens=max_tokens,
        )

        resp = response.choices[0].message.content
        object = json.loads(resp)

        if str(object['false_friend_term_found']).lower() == 'yes':
            en_sent.append(english_sentence)
            es_sent.append(spanish_sentence)
            responses.append(object)
        time.sleep(0.1)
        pbar.update(1)

df = pd.DataFrame({"english": en_sent, "spanish": es_sent, "response": responses})

df.to_excel("selected_results.xlsx", sheet_name="results")

