# from tiktoken import Tokenizer

# # Define the text
# text = """
# The rapid development of artificial intelligence (AI) and machine learning (ML) technologies has revolutionized various industries,
# including healthcare, finance, and transportation. These technologies enable computers to learn from and make decisions based on data,
# leading to more efficient and effective solutions. For example, in healthcare, AI-powered systems can analyze large amounts of data to
# identify patterns and predict diseases before they occur. In finance, ML algorithms can analyze market trends and make investment
# recommendations. In transportation, AI systems can optimize routes and reduce fuel consumption. However, despite the many benefits,
# there are also challenges and concerns related to privacy, security, and ethical considerations.
# """

# # Define the models and their costs
# models = {
#     "gpt-4-8k": 0.003,
#     "gpt-4-32k": 0.006,
# }

# # Calculate token count, word count, and cost for each model
# tokenizer = Tokenizer()
# tokens = tokenizer.encode(text)
# token_count = len(tokens)
# word_count = len(text.split())
# costs = {model: token_count * cost / 1000 for model, cost in models.items()}

# print("Token Count:", token_count)
# print("Word Count:", word_count)
# print("Costs:", costs)