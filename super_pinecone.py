from flask import Flask, request
import requests
import numpy as np
import uuid
import threading
from typing import List

app = Flask(__name__)

BATCH_SIZE = 100  # define your batch size here (pinecone recommends max 100)

def count_tokens(data):
    return len(data.split())

def get_embeddings(content_chunks: List[str], openAIAPIkey: str) -> List[np.array]:
    embeddings = []
    for i in range(0, len(content_chunks), BATCH_SIZE):
        batch = content_chunks[i:i+BATCH_SIZE]
        headers = {
            'Authorization': f'Bearer {openAIAPIkey}',
            'Content-Type': 'application/json'
        }

        data = {
            "model": "text-embedding-ada-002",
            "input": batch
        }

        response = requests.post('https://api.openai.com/v1/embeddings', headers=headers, json=data)

        if response.status_code != 200:
            raise Exception('OpenAI API request failed')

        embeddings.extend([item['embedding'] for item in response.json()['data']])
    return embeddings

def upsert_to_pinecone(pinecone_url: str, vectors: List[dict], namespace: str, pinecone_api_key: str):
    ids = []
    for i in range(0, len(vectors), BATCH_SIZE):
        batch = vectors[i:i+BATCH_SIZE]
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'Api-Key': pinecone_api_key
        }

        data = {
            "vectors": batch,
            "namespace": namespace
        }

        response = requests.post(f'{pinecone_url}/vectors/upsert', headers=headers, json=data)

        if response.status_code != 200:
            error_info = {
                'request': {
                    'url': f'{pinecone_url}/vectors/upsert',
                    'headers': headers,
                    'data': data
                },
                'response': {
                    'status_code': response.status_code,
                    'content': response.content
                }
            }
            raise Exception(f'Pinecone API request failed: {error_info}')

        # Collect the unique IDs of the vectors upserted in this batch
        ids.extend([vector['id'] for vector in batch])

    return ids

def send_webhook(webhook_url: str, processed: int, total: int, unique_id: str, unique_ids: List[str]):
    data = {
        'processed': processed,
        'total': total,
        'uniqueID': unique_id,
        'uniqueIDs': unique_ids  # Send the unique IDs of the vectors
    }
    response = requests.post(webhook_url, json=data)
    if response.status_code != 200:
        raise Exception(f'Webhook trigger failed with status code: {response.status_code}')


def process_data(data):
    content = data['content']
    word_limit = data['wordLimit']
    unique_id = data['uniqueID']
    pinecone_url = data['pineconeURL']
    pinecone_api_key = data['pineconeAPIkey']
    openai_api_key = data['openAIAPIkey']
    namespace = data['namespace']
    webhook_url = data['webhookURL']
    category = data.get('category', None)

    # Split the content into chunks of size 'wordLimit'
    words = content.split()
    content_chunks = [' '.join(words[i:i+word_limit]) for i in range(0, len(words), word_limit)]

    # Get embeddings for each chunk using the OpenAI API
    embeddings = get_embeddings(content_chunks, openai_api_key)

    # Prepare the vectors for upsert to Pinecone
    vectors = []
    for i, embedding in enumerate(embeddings):
        metadata = {
            "content": content_chunks[i],
            "memoryID": unique_id
        }
        if category is not None:
            metadata['category'] = category

        vectors.append({
            "values": embedding,
            "metadata": metadata,
            "id": str(uuid.uuid4()).replace('-', '')  # Generate a 32 character unique ID
        })

    # Upsert the embeddings into the Pinecone database in batches and send a webhook for each batch
    for i in range(0, len(vectors), BATCH_SIZE):
        batch = vectors[i:i+BATCH_SIZE]
        unique_ids = upsert_to_pinecone(pinecone_url, batch, namespace, pinecone_api_key)
        send_webhook(webhook_url, len(batch), len(content_chunks), unique_id, unique_ids)


@app.route('/upsert', methods=['POST'])
def process_content():
    data = request.json

    # Count tokens in the content
    num_tokens = count_tokens(data['content'])

    # Start the processing in a new thread
    threading.Thread(target=process_data, args=(data,)).start()

    return {'status': 'processing started', 'numTokens': num_tokens}

if __name__ == '__main__':
    # This is used when running locally only.
    app.run(host='localhost', port=8080, debug=True)