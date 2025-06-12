import streamlit as st
import pandas as pd
from openai import OpenAI
import os
import dotenv
import json

dotenv.load_dotenv()

FLIGHTS = [
    {"flight_id": "FL101", "departure": "Karachi", "destination": "Dubai", "time": "07:00 AM", "price": 65000, "airline": "Emirates", "available_seats": 120},
    {"flight_id": "FL102", "departure": "Karachi", "destination": "Dubai", "time": "11:00 AM", "price": 62000, "airline": "PIA", "available_seats": 100},
    {"flight_id": "FL103", "departure": "Karachi", "destination": "Doha", "time": "02:00 PM", "price": 68000, "airline": "Qatar Airways", "available_seats": 80},
    {"flight_id": "FL104", "departure": "Karachi", "destination": "London", "time": "09:00 PM", "price": 115000, "airline": "Etihad", "available_seats": 140},
    {"flight_id": "FL105", "departure": "Karachi", "destination": "London", "time": "01:00 AM", "price": 112000, "airline": "PIA", "available_seats": 130},
    {"flight_id": "FL106", "departure": "Karachi", "destination": "Istanbul", "time": "06:00 PM", "price": 78000, "airline": "Turkish Airlines", "available_seats": 90},

    {"flight_id": "FL201", "departure": "Lahore", "destination": "Dubai", "time": "08:00 AM", "price": 64000, "airline": "Emirates", "available_seats": 110},
    {"flight_id": "FL202", "departure": "Lahore", "destination": "Dubai", "time": "05:00 PM", "price": 60000, "airline": "PIA", "available_seats": 100},
    {"flight_id": "FL203", "departure": "Lahore", "destination": "Jeddah", "time": "10:00 AM", "price": 70000, "airline": "Saudi Airlines", "available_seats": 90},
    {"flight_id": "FL204", "departure": "Lahore", "destination": "Doha", "time": "03:00 PM", "price": 71000, "airline": "Qatar Airways", "available_seats": 75},
    {"flight_id": "FL205", "departure": "Lahore", "destination": "Istanbul", "time": "09:00 AM", "price": 76000, "airline": "Turkish Airlines", "available_seats": 85},
    {"flight_id": "FL206", "departure": "Lahore", "destination": "London", "time": "12:00 PM", "price": 118000, "airline": "Etihad", "available_seats": 110},

    {"flight_id": "FL301", "departure": "Islamabad", "destination": "Dubai", "time": "09:00 AM", "price": 63000, "airline": "Emirates", "available_seats": 115},
    {"flight_id": "FL302", "departure": "Islamabad", "destination": "Dubai", "time": "04:00 PM", "price": 61000, "airline": "PIA", "available_seats": 95},
    {"flight_id": "FL303", "departure": "Islamabad", "destination": "Jeddah", "time": "01:00 PM", "price": 70500, "airline": "Saudi Airlines", "available_seats": 100},
    {"flight_id": "FL304", "departure": "Islamabad", "destination": "Doha", "time": "06:00 AM", "price": 69500, "airline": "Qatar Airways", "available_seats": 80},
    {"flight_id": "FL305", "departure": "Islamabad", "destination": "Istanbul", "time": "08:00 PM", "price": 77000, "airline": "Turkish Airlines", "available_seats": 90},
    {"flight_id": "FL306", "departure": "Islamabad", "destination": "London", "time": "02:00 AM", "price": 114000, "airline": "Etihad", "available_seats": 120},
]

st.set_page_config(page_title="AI Flight Booking Agent", layout="wide")

st.title("✈️ AI Flight Booking Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key_configured" not in st.session_state:
    st.session_state.api_key_configured = False
if "conversation_stage" not in st.session_state:
    st.session_state.conversation_stage = 'initial'
if "selected_flight" not in st.session_state:
    st.session_state.selected_flight = None
if "departure_city" not in st.session_state:
    st.session_state.departure_city = ""
if "destination_city" not in st.session_state:
    st.session_state.destination_city = ""

openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key:
    if not st.session_state.api_key_configured:
        try:
            client = OpenAI(api_key=openai_api_key)
            client.models.list()
            st.session_state.api_key_configured = True
            st.session_state.client = client
            if not st.session_state.messages:
                st.session_state.messages.append({"role": "assistant", "content": "Hello! I am your AI flight booking agent. What is your departure city and desired destination?"})
            st.session_state.conversation_stage = 'awaiting_cities'
            st.success("API Key configured successfully!")
        except Exception as e:
            st.error(f"Invalid OpenAI API Key loaded from environment: {e}. Please check your `.env` file or environment variables.")
            st.session_state.api_key_configured = False
            if not st.session_state.messages:
                st.session_state.messages.append({"role": "assistant", "content": "Hello! I am your AI flight booking agent. Please configure your OpenAI API key in a `.env` file to start (for local development). For Streamlit Cloud, use Streamlit Secrets."})
else:
    st.warning("OpenAI API Key not found in environment variables. Please configure it to use the agent.")
    st.info("For local development, create a `.env` file in your project's root directory. For Streamlit Cloud, add secrets directly in the app settings.")
    if not st.session_state.messages:
        st.session_state.messages.append({"role": "assistant", "content": "Hello! I am your AI flight booking agent. Please configure your OpenAI API key to start."})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def get_openai_response(prompt_text, chat_history):
    if not st.session_state.api_key_configured:
        return "Please configure your OpenAI API key before we can chat."

    messages_for_openai = [
        {"role": "system", "content": "You are an AI flight booking agent. Your goal is to help users find and book flights. Keep responses concise and guide the user step-by-step. Only provide information related to flight booking. If a user tries to go off-topic, gently steer them back to flight booking. Be friendly and helpful."},
    ] + chat_history + [{"role": "user", "content": prompt_text}]

    try:
        completion = st.session_state.client.chat.completions.create(
            model="gpt-4o-mini", # Changed model to gpt-4o-mini
            messages=messages_for_openai,
            max_tokens=200,
            temperature=0.7,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"An error occurred with the OpenAI API: {e}"

def find_flights(departure, destination):
    found_flights = [
        flight for flight in FLIGHTS
        if flight["departure"].lower() == departure.lower() and
           flight["destination"].lower() == destination.lower()
    ]
    return found_flights

def format_flights_for_llm(flights_list):
    if not flights_list:
        return "No flights found for this route."
    
    flight_str = "Here are the available flights:\n\n"
    for flight in flights_list:
        flight_str += (
            f"**Flight ID:** {flight['flight_id']}\n"
            f"  - **Route:** {flight['departure']} to {flight['destination']}\n"
            f"  - **Time:** {flight['time']}\n"
            f"  - **Price:** Rs{flight['price']}\n"
            f"  - **Airline:** {flight['airline']}\n"
            f"  - **Available Seats:** {flight['available_seats']}\n\n"
        )
    flight_str += "Please tell me the **Flight ID** you are interested in booking (e.g., FL001)."
    return flight_str

def simulate_booking(flight_id, passenger_names):
    num_tickets = len(passenger_names)
    flight = next((f for f in FLIGHTS if f["flight_id"] == flight_id), None)
    
    if flight and flight["available_seats"] >= num_tickets:
        names_str = ", ".join(passenger_names)
        return (
            f"Congratulations! Your booking for **{num_tickets}** ticket(s) for passengers: "
            f"**{names_str}** on **Flight {flight_id}** from **{flight['departure']} to {flight['destination']}** "
            f"at **{flight['time']}** with **{flight['airline']}** for a total of **Rs{flight['price'] * num_tickets}** has been confirmed.\n\n"
            "Enjoy your flight! To book another flight, please refresh the page."
        )
    elif flight:
        return f"Sorry, Flight {flight_id} only has {flight['available_seats']} seats left. You requested {num_tickets}."
    else:
        return "Flight ID not found. Please select a valid Flight ID."

if st.session_state.api_key_configured:
    if prompt := st.chat_input("Type your message here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        response = ""
        if st.session_state.conversation_stage == 'awaiting_cities':
            llm_parse_prompt = f"The user said: '{prompt}'. Extract the departure city and destination city. Respond only with 'DEPARTURE: CityA|DESTINATION: CityB'. If not clear, respond with 'DEPARTURE: |DESTINATION: '."
            parsed_cities_str = get_openai_response(llm_parse_prompt, [])
            
            try:
                parsed_cities_str = parsed_cities_str.strip()
                departure_prefix = "DEPARTURE: "
                destination_prefix = "DESTINATION: "
                
                departure_start = parsed_cities_str.find(departure_prefix)
                destination_start = parsed_cities_str.find(destination_prefix)

                dep_city = ""
                dest_city = ""

                if departure_start != -1 and destination_start != -1:
                    dep_city_end = parsed_cities_str.find("|", departure_start)
                    if dep_city_end == -1:
                        if destination_start < departure_start:
                            dep_city_end = len(parsed_cities_str)
                        else:
                            dep_city_end = destination_start - 1 if destination_start > departure_start + len(departure_prefix) else len(parsed_cities_str)
                    
                    dep_city = parsed_cities_str[departure_start + len(departure_prefix) : dep_city_end].strip()
                    dest_city = parsed_cities_str[destination_start + len(destination_prefix) :].strip()

                st.session_state.departure_city = dep_city
                st.session_state.destination_city = dest_city

                if st.session_state.departure_city and st.session_state.destination_city:
                    flights_found = find_flights(st.session_state.departure_city, st.session_state.destination_city)
                    if flights_found:
                        st.session_state.available_flights = flights_found
                        response = format_flights_for_llm(flights_found)
                        st.session_state.conversation_stage = 'awaiting_flight_selection'
                    else:
                        response = f"I couldn't find any flights from {st.session_state.departure_city} to {st.session_state.destination_city}. Please try different cities or routes."
                        st.session_state.conversation_stage = 'awaiting_cities'
                else:
                    response = "I couldn't understand the departure and destination cities. Could you please specify them clearly? (e.g., 'I want to fly from Karachi to London')"
            except Exception as e:
                response = f"There was an issue parsing your request. Please try again. Error: {e}"

            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)

        elif st.session_state.conversation_stage == 'awaiting_flight_selection':
            flight_id_match = False
            potential_flight_id = prompt.strip().upper()
            if potential_flight_id.startswith("FL") and len(potential_flight_id) == 5:
                selected_flight = next((f for f in st.session_state.available_flights if f["flight_id"] == potential_flight_id), None)
                if selected_flight:
                    st.session_state.selected_flight = selected_flight
                    response = f"You've selected Flight {selected_flight['flight_id']}. Great choice! To proceed with the booking, please provide the **full names of all passengers (comma-separated)** and the **total number of tickets** you wish to book. (e.g., 'Names: John Doe, Jane Smith; Tickets: 2')"
                    st.session_state.conversation_stage = 'awaiting_booking_details'
                    flight_id_match = True
                else:
                    response = "That Flight ID doesn't seem to be in the list of available flights. Please choose from the displayed options."
            
            if not flight_id_match:
                llm_parse_prompt = f"The user selected a flight. Their input was '{prompt}'. Try to identify the Flight ID (e.g., FL001) from this input. Respond with only the Flight ID (like FL001), or 'NONE' if not found."
                parsed_flight_id = get_openai_response(llm_parse_prompt, []).strip().upper()

                if parsed_flight_id != 'NONE' and parsed_flight_id.startswith("FL"):
                    selected_flight = next((f for f in st.session_state.available_flights if f["flight_id"] == parsed_flight_id), None)
                    if selected_flight:
                        st.session_state.selected_flight = selected_flight
                        response = f"You've selected Flight {selected_flight['flight_id']}. Great choice! To proceed with the booking, please provide the **full names of all passengers (comma-separated)** and the **total number of tickets** you wish to book. (e.g., 'Names: John Doe, Jane Smith; Tickets: 2')"
                        st.session_state.conversation_stage = 'awaiting_booking_details'
                    else:
                        response = "I found a Flight ID in your message, but it doesn't match any of the available flights. Please choose from the displayed options."
                else:
                    response = "I couldn't identify the Flight ID. Please provide the exact Flight ID (e.g., FL001) from the list."

            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)

        elif st.session_state.conversation_stage == 'awaiting_booking_details':
            if st.session_state.selected_flight:
                llm_parse_prompt = f"The user wants to book a flight. Their input is '{prompt}'. Extract the full names of passengers (comma-separated) and the total number of tickets. Respond only with 'NAMES: Name1, Name2|TICKETS: X'. If information is missing, respond with 'NAMES: |TICKETS: 0'."
                parsed_booking_details_str = get_openai_response(llm_parse_prompt, [])
                
                try:
                    parsed_booking_details_str = parsed_booking_details_str.strip()
                    names_prefix = "NAMES: "
                    tickets_prefix = "TICKETS: "
                    
                    names_start = parsed_booking_details_str.find(names_prefix)
                    tickets_start = parsed_booking_details_str.find(tickets_prefix)

                    passenger_names = []
                    num_tickets = 0

                    if names_start != -1 and tickets_start != -1:
                        names_end = parsed_booking_details_str.find("|", names_start)
                        if names_end == -1:
                            names_end = tickets_start - 1 if tickets_start > names_start else len(parsed_booking_details_str)

                        names_raw = parsed_booking_details_str[names_start + len(names_prefix) : names_end].strip()
                        if names_raw:
                            passenger_names = [name.strip() for name in names_raw.split(',')]
                        
                        tickets_raw = parsed_booking_details_str[tickets_start + len(tickets_prefix) :].strip()
                        if tickets_raw.isdigit():
                            num_tickets = int(tickets_raw)

                    if passenger_names and num_tickets > 0 and len(passenger_names) == num_tickets:
                        booking_confirmation = simulate_booking(st.session_state.selected_flight['flight_id'], passenger_names)
                        response = booking_confirmation
                        st.session_state.conversation_stage = 'booking_confirmed'
                    elif passenger_names and num_tickets > 0 and len(passenger_names) != num_tickets:
                        response = "It looks like the number of names provided doesn't match the number of tickets. Please provide the full names for ALL passengers (comma-separated) and the total number of tickets. (e.g., 'Names: John Doe, Jane Smith; Tickets: 2')"
                    else:
                        response = "I couldn't get the passenger names or the total number of tickets. Please provide both to complete the booking. (e.g., 'Names: Jane Smith; Tickets: 1')"
                except Exception as e:
                    response = f"There was an issue processing your booking details. Please try again. Error: {e}"
            else:
                response = "It seems we lost track of your flight selection. Let's start over. What is your departure city and desired destination?"
                st.session_state.conversation_stage = 'awaiting_cities'
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
                if st.session_state.conversation_stage == 'booking_confirmed':
                    st.info("Booking process completed. To book another flight, please refresh the page.")
        elif st.session_state.conversation_stage == 'booking_confirmed':
            response = "Your previous booking is complete. If you wish to book another flight, please refresh the page."
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
        else:
            response = get_openai_response(prompt, st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
else:
    pass
