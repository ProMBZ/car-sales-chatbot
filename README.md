# Used Car Sales Chatbot

**What is it?**

This is an interactive chatbot application built with Streamlit, LangChain, and Google's Gemini 2.0 Flash LLM. It's designed to simulate a used car sales assistant, helping users find, compare, and learn about used cars.

**What can it do?**

* **Interactive Chat:** Provides a user-friendly chat interface to interact with the chatbot.
* **Simulated Inventory:** Offers a simulated used car inventory with details like price, mileage, and features.
* **Price Comparisons:** Fetches and compares used car prices from online sources using the Tavily API.
* **Car Details:** Retrieves detailed information about specific car models, including images.
* **Client Information:** Collects client information for potential sales leads.
* **Price Comparison:** Compares the local dealer's price to the prices found online, and shows the difference to the user.
* **Price Manipulation (Demonstration):** Demonstrates a feature to manipulate competitor prices (for educational purposes only and not recommended for production).

**Prerequisites:**

* Python 3.7+
* Streamlit
* LangChain
* LangChain Google GenAI
* Tavily
* python-dotenv
* Google Gemini API Key
* Tavily API Key

**Installation:**

1.  Clone the repository.
2.  Create a virtual environment (recommended).
3.  Install the required packages: `pip install streamlit langchain langchain-google-genai tavily python-dotenv`
4.  Create a `.env` file and add your API keys.

**Usage:**

1.  Run the Streamlit app: `streamlit run main.py`
2.  Open the app in your browser.
3.  Interact with the chatbot.
