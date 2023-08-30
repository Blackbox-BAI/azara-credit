Azara Credit Estimator
======================

Introduction
------------

This is a simple application to estimate the amount of Azara Credit needed to run a specific operation, like embedding a document or retrieving data via a chat with an agent. Azara Credit is a unit of currency used to pay for Pinecone index usage, where 1 Azara Credit is equivalent to 1 USD.

Features
--------

-   Document Embedding: Estimate the cost when a user uploads a document for embedding.
-   Data Retrieval: Estimate the cost when a user chats with an agent for data retrieval.
-   Token Count and Price Estimation: A function that estimates the number of tokens and the price for a given text and model.
-  Token Count and Price Estimation: A function that estimates the number of tokens and the price for a given text and model.
- Margin Estimation: A function that estimates the margin given the Azara credit price and the price of the service.

Requirements
------------

- Python 3.6+
- Streamlit
- tiktoken

Installation
-----------------------------

`pip install -r requirements.txt`

Usage
-----

### Web Application

Run the Streamlit application by executing the following command:

```streamlit run calculation.py```

### Cloud Deploy

The application is deployed on Streamlit Cloud on branch master. You can access it via the following link:

https://azara-credit-calculator.streamlit.app/