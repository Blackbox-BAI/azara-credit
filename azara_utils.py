import re
from io import BytesIO
from typing import Any, Dict, List, Tuple
import fitz
import docx2txt
import tiktoken
import yaml

# Load the YAML file
with open('costing.yaml', 'r') as f:
    config = yaml.safe_load(f)

def parse_docx(file: BytesIO) -> str:
    text = docx2txt.process(file)
    text = re.sub(r"\s*\n\s*", " ", text)
    return text

def parse_pdf(file: BytesIO) -> str:
    def trim(text):
        text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
        text = re.sub("\s*\n\s*", " ", text)
        return text
    doc = fitz.open(stream=file.read(), filetype="pdf")
    total_pages = doc.page_count
    text_list = []

    for page in range(total_pages):
        text = doc.load_page(page).get_text()
        text = trim(text)
        text_list.append(text)

    doc.close()
    return "".join(text_list)

def parse_txt(file: BytesIO) -> str:
    text = file.read().decode("utf-8")
    text = re.sub(r"\s*\n\s*", " ", text)
    return text

def count_tokens_return_length_price(text: str, model: str) -> Tuple[int, float]:
    if model not in config['models']:
        raise ValueError("Invalid model. Choose either gpt-4-8k, gpt-4-32k or gpt-3.5-turbo.")

    encoding = tiktoken.encoding_for_model(config['models'][model]['encoding'])
    length = len(encoding.encode(text))
    price = (length / 1000) * config['models'][model]['cost']

    return length, price


# def calculate_azara_credit(number_words, pinecode_pods, pinecode_per_hour_cost, pinecone_costs, model, pinecone_retrievel_duration=0):
#     if model not in config['models']:
#         raise ValueError("Invalid model. Choose either gpt-4-8k, gpt-4-32k or gpt-3.5-turbo.")

#     # Token costs based on context length for GPT model
#     prompt_cost_per_token = config['models'][model]['prompt_cost_per_token'] / 1000

#     def words_to_tokens(word_count):
#         """Convert number of words to an estimated number of tokens for GPT based on rule of thumb."""
#         TOKENS_PER_WORD = 4/3  # 1 word is roughly 3/4 of a token
#         return int(word_count * TOKENS_PER_WORD)

#     # Convert words to tokens
#     number_of_tokens_from_words = words_to_tokens(number_words)

#     total_prompt_cost = number_of_tokens_from_words * prompt_cost_per_token
#     total_pinecone_cost = pinecode_pods * pinecode_per_hour_cost * pinecone_costs
#     retrieval_cost = pinecode_pods * pinecone_retrievel_duration * pinecone_costs

#     # Sum up all the costs
#     total_cost = total_prompt_cost + total_pinecone_cost + retrieval_cost

#     # Convert total cost to Azara Credit (assuming 1:1 conversion for now)
#     return total_cost

def calculate_azara_credit(number_words, pinecone_pods, pinecone_duration_hours, model, cloud_provider, storage_type, instance_type):
    if model not in config['models']:
        raise ValueError("Invalid model. Choose either gpt-4-8k, gpt-4-32k or gpt-3.5-turbo.")
    if cloud_provider not in config['pinecone_cloud_providers']:
        raise ValueError("Invalid cloud provider. Choose either aws, gcp or azure.")
    if storage_type not in config['pinecone_cloud_providers'][cloud_provider]:
        raise ValueError("Invalid storage type.")
    if instance_type not in config['pinecone_cloud_providers'][cloud_provider][storage_type]:
        raise ValueError("Invalid instance type.")

    # Token costs based on context length for GPT model
    prompt_cost_per_token = config['models'][model]['prompt_cost_per_token']

    def words_to_tokens(word_count):
        """Convert number of words to an estimated number of tokens for GPT based on rule of thumb."""
        TOKENS_PER_WORD = 4/3  # 1 word is roughly 3/4 of a token
        return int(word_count * TOKENS_PER_WORD)

    # Convert words to tokens
    number_of_tokens_from_words = words_to_tokens(number_words)

    total_prompt_cost = number_of_tokens_from_words * prompt_cost_per_token
    pinecone_cost_per_hour = config['pinecone_cloud_providers'][cloud_provider][storage_type][instance_type]['cost_per_hour']
    total_pinecone_cost = pinecone_pods * pinecone_duration_hours * pinecone_cost_per_hour

    # Sum up all the costs
    total_cost = total_prompt_cost + total_pinecone_cost

    # Convert total cost to Azara Credit (assuming 1:1 conversion for now)
    return total_cost


