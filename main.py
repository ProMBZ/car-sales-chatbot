import streamlit as st
import random
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from tavily import TavilyClient
from dotenv import load_dotenv
import os
from langchain.tools import Tool

# Ensure set_page_config is the first Streamlit command
st.set_page_config(page_title="Used Car Sales Chatbot", page_icon="🚗", layout="wide") #Combined layout parameter

# Load environment variables from .env file
load_dotenv()

# Configure API Keys using os.environ
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

if not GOOGLE_API_KEY or not TAVILY_API_KEY:
    st.error("API keys not found in .env file. Please add GOOGLE_API_KEY and TAVILY_API_KEY.")
    st.stop()

# Initialize Gemini 2.0 Flash LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

# Tavily Client
tavily_client = TavilyClient(TAVILY_API_KEY)

# Extensive Dummy Used Car Stock Data
used_car_stock = {
    "toyota corolla": {"price": 18000, "mileage": 60000, "interior": "Leather seats, well-maintained", "details": "2018 Toyota Corolla, good condition, low mileage for its age, sunroof, new tires.", "benefits": "Reliable, fuel-efficient, perfect for commutes."},
    "honda vezel": {"price": 22000, "mileage": 45000, "interior": "Fabric seats, minor wear", "details": "2019 Honda Vezel, hybrid, well-maintained, navigation system, recent oil change.", "benefits": "Eco-friendly, spacious, advanced features."},
    "ford mustang": {"price": 30000, "mileage": 30000, "interior": "Premium leather, like new", "details": "2020 Ford Mustang, sports edition, powerful engine, leather interior, upgraded sound system.", "benefits": "Performance-driven, stylish, thrilling to drive."},
    "nissan rogue": {"price": 24000, "mileage": 50000, "interior": "Clean cloth, family-friendly", "details": "2020 Nissan Rogue, AWD, family-friendly, spacious cargo, backup camera.", "benefits": "Safe, comfortable, ideal for road trips."},
    "chevrolet silverado": {"price": 35000, "mileage": 70000, "interior": "Durable vinyl, work-ready", "details": "2017 Chevrolet Silverado, truck, heavy duty, tow package, bed liner.", "benefits": "Powerful, durable, perfect for work or play."},
    "mercedes-benz c-class": {"price": 40000, "mileage": 40000, "interior": "Luxury leather, excellent condition", "details": "2020 Mercedes-Benz C-Class, luxury sedan, premium sound, advanced safety, ambient lighting.", "benefits": "Luxurious, refined, top-tier performance."},
    "bmw 3 series": {"price": 38000, "mileage": 42000, "interior": "Sports leather, minimal wear", "details": "2021 BMW 3 Series, sports sedan, dynamic handling, tech-packed, heads-up display.", "benefits": "Sporty, agile, cutting-edge technology."},
    "audi a4": {"price": 39000, "mileage": 41000, "interior": "Premium cloth, heated seats", "details": "2021 Audi A4, premium sedan, quattro AWD, virtual cockpit, lane assist.", "benefits": "Elegant, all-weather capable, sophisticated design."},
    "volkswagen golf": {"price": 20000, "mileage": 55000, "interior": "Standard cloth, good condition", "details": "2019 Volkswagen Golf, hatchback, sporty, fuel-efficient, Bluetooth connectivity.", "benefits": "Practical, fun to drive, economical."},
    "hyundai tucson": {"price": 23000, "mileage": 48000, "interior": "Modern cloth, touch screen", "details": "2020 Hyundai Tucson, SUV, modern design, smart features, keyless entry.", "benefits": "Stylish, spacious, feature-rich."},
    "kia sportage": {"price": 22500, "mileage": 49000, "interior": "Comfortable cloth, rear camera", "details": "2019 Kia Sportage, SUV, reliable, comfortable ride, panoramic sunroof.", "benefits": "Dependable, comfortable, value-packed."},
    "subaru outback": {"price": 28000, "mileage": 38000, "interior": "Durable cloth, all-weather mats", "details": "2021 Subaru Outback, AWD, adventure-ready, spacious interior, roof rack.", "benefits": "Rugged, safe, perfect for outdoor enthusiasts."},
    "lexus rx": {"price": 45000, "mileage": 35000, "interior": "Luxury leather, ventilated seats", "details": "2021 Lexus RX, smooth ride, premium features, mark levinson sound system.", "benefits": "Luxurious, comfortable, exceptional reliability."},
    "tesla model 3": {"price": 43000, "mileage": 32000, "interior": "Vegan leather, minimalist design", "details": "2022 Tesla Model 3, electric sedan, autopilot, long range, supercharger access.", "benefits": "Electric, high-tech, environmentally friendly."},
    "porsche 911": {"price": 110000, "mileage": 20000, "interior": "Full leather, sport seats", "details": "2020 Porsche 911, sports car, high performance, iconic design, sport chrono package.", "benefits": "High-performance, iconic, luxury sports car."},
    "jeep wrangler": {"price": 33000, "mileage": 46000, "interior": "Washable interior, rugged design", "details": "2021 Jeep Wrangler, off-road, rugged, convertible, upgraded suspension.", "benefits": "Off-road capable, adventurous, iconic design."},
    "ram 1500": {"price": 37000, "mileage": 52000, "interior": "Comfortable cloth, spacious cabin", "details": "2020 Ram 1500, pickup truck, powerful, comfortable interior, trailer brake controller.", "benefits": "Powerful, versatile, comfortable for work or play."},
    "mini cooper": {"price": 21000, "mileage": 58000, "interior": "Unique cloth, retro design", "details": "2019 Mini Cooper, compact, stylish, fun to drive, panoramic glass roof.", "benefits": "Stylish, compact, fun and agile."},
    "land rover defender": {"price": 55000, "mileage": 30000, "interior": "Premium leather, robust interior", "details": "2022 Land Rover Defender, off-road SUV, luxurious, robust, expedition package.", "benefits": "Luxurious, off-road capable, robust and reliable."},
    "volvo xc90": {"price": 50000, "mileage": 36000, "interior": "Scandinavian leather, child booster seats", "details": "2021 Volvo XC90, safest features, spacious, pilot assist.", "benefits": "Safe, spacious, luxurious and dependable."},
}

# Tavily Search Tool
def tavily_search_with_images(query):
    try:
        response = tavily_client.search(query=query, include_images=True)
        return response
    except Exception as e:
        return f"Error during Tavily search: {e}"

# Price Comparison (Enhanced)
def compare_prices(car_model):
    search_query = f"{car_model} used car price comparison"
    results = tavily_search_with_images(search_query)
    if isinstance(results, dict) and results.get('results'):
        competitor_price_info = results['results'][0]['content']
        search_url = results['results'][0]['url'] if results['results'] else "No search URL found."
        if car_model.lower() in used_car_stock:
            our_interior = used_car_stock[car_model.lower()]["interior"]
            our_price = used_car_stock[car_model.lower()]["price"]

            try:
                import re
                prices = re.findall(r'\$\d+(?:,\d+)?', competitor_price_info)
                if prices:
                    online_prices = [int(price.replace('$', '').replace(',', '')) for price in prices]
                    if online_prices:
                        average_online_price = sum(online_prices) / len(online_prices)
                        price_difference = our_price - average_online_price

                        if price_difference > 0:
                            comparison_message = f"Our {car_model} is priced at ${our_price:,}, which is ${price_difference:,.0f} less than the average online price. "
                        elif price_difference < 0:
                            comparison_message = f"Our {car_model} is priced at ${our_price:,}. While online prices average ${average_online_price:,.0f}, we offer added value through our dealership's benefits. "
                        else:
                            comparison_message = f"Our {car_model} is competitively priced at ${our_price:,}, matching the average online price. "

                        return f"{comparison_message} It features {our_interior}. Check online prices here: [{search_url}]({search_url}). We also offer [mention dealership benefits here]."
                    else:
                        return f"Our {car_model} is priced at ${our_price:,} and features {our_interior}. We couldn't find comparable online prices, but we offer [mention dealership benefits here]."
            except Exception as e:
                print(f"Error adjusting competitor price: {e}")
                return f"Our {car_model} is priced at ${our_price:,} and features {our_interior}. We encountered an error comparing prices, but we offer [mention dealership benefits here]."
        else:
            return f"Other dealers are selling the {car_model} at these prices: {competitor_price_info} Check it out here: [{search_url}]({search_url})."
    else:
        return "Could not retrieve competitor price information at this time."

# Car Details with Image Retrieval
def get_car_details(car_model):
    car_model_lower = car_model.lower()
    if car_model_lower in used_car_stock:
        details = used_car_stock[car_model_lower]
        search_results = tavily_search_with_images(f"{car_model} used car")
        image_urls = []
        if isinstance(search_results, dict) and search_results.get('images'):
            image_urls = search_results['images']
        detail_string = (
            f"Absolutely! We have a {car_model.capitalize()} available. "
            f"Mileage: {details['mileage']:,} miles. "
            f"Interior: {details['interior']}. "
            f"Details: {details['details']}. "
            f"Price: ${details['price']:,}. "
            f"Benefits: {details['benefits']}."
        )
        return {"details": detail_string, "images": image_urls}
    else:
        return {"details": f"Sorry, the {car_model.capitalize()} is not currently in our stock.", "images": []}

# List Cars
def list_available_cars():
    if not used_car_stock:
        return "Our stock is currently empty."
    else:
        cars = ", ".join(car.capitalize() for car in used_car_stock)
        return f"We currently have the following used cars in stock: {cars}."

# Collect Client Info
def collect_client_info():
    name = st.text_input("Please enter your name:")
    email = st.text_input("Please enter your email:")
    phone = st.text_input("Please enter your phone number:")
    if name and email and phone:
        return f"Client info: Name: {name}, Email: {email}, Phone: {phone}"
    else:
        return None

# LangChain Agent Setup
tools = [
    Tool(name="ComparePrices", func=lambda car_model: compare_prices(car_model), description="Compares used car prices with other dealers and provides links and interior details."),
    Tool(name="GetCarDetails", func=lambda car_model: get_car_details(car_model), description="Retrieves used car details, mileage, interior, and images."),
    Tool(name="ListAvailableCars", func=lambda _: list_available_cars(), description="Lists all available used cars in stock."),
    Tool(name="CollectClientInfo", func=collect_client_info, description="Collects client information for sales purposes.")
]

# Memory Initialization
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = initialize_agent(tools, llm, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory=st.session_state.memory)

st.markdown(
    """
    <style>

   body {
        font-family: 'Roboto', sans-serif;
        color: #e0e0e0; /* Light text */
        margin: 0;
        padding: 0;
    }

    .stApp {
        max-width: 1200px;
        margin: auto;
        padding: 2rem;
    }
    .st-eb {
        background-color: black; /* Darker card background */
        border-radius: 10px;
        box-shadow: 0 4px 8px rgb(255, 255, 255);
        padding: 2rem;
        margin-bottom: 2rem;
    }
    .st-bb {
        background-color:rgb(9, 9, 9); /* Even darker message background */
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        color: white /* White text color for messages */
    }
    .st-bb:last-child {
        margin-bottom: 0;
    }
    /* Ensure markdown content in chat messages is white */
    .st-bb p, .st-bb span, .st-bb div {
        color: white;
    }
    .stTextInput > div > input {
        background-color: #333; /* Dark input background */
        border: 1px solid #555;
        border-radius: 5px;
        padding: 0.75rem;
        width: 100%;
        color: #ffffff !important; /* Force input text color to white */
        caret-color: #ffffff; /* Change caret color to white for better visibility */
    }

    /* Additional styles to ensure visibility */
    .stTextInput > div > input:focus {
        outline: none; /* Remove default outline */
        border-color: #64b5f6; /* Change border color on focus */
    }
    .stButton>button {
        background-color: #64b5f6; /* Blue button */
        color:rgb(255, 255, 255); /* Dark button text */
        padding: 0.75rem 1.5rem;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    .stImage>img {
        border-radius: 8px;
        max-width: 100%;
        height: auto;
        margin-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🚗 Used Car Sales Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I assist you with your car needs today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            results = agent.run(prompt)
            if isinstance(results, dict) and 'images' in results:
                full_response = results['details']
                message_placeholder.markdown(full_response)
                if results['images']:
                    for image_url in results['images']:
                        st.image(image_url, caption="Search Result Image", use_column_width=True)
            else:
                full_response = str(results)
                message_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"An error occurred: {e}"
            message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

