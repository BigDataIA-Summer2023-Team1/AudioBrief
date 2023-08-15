import os
import requests
import streamlit as st
from pydantic import BaseModel
from streamlit_option_menu import option_menu


# Streamlit app
st.title("AudioBrief - User Registration and Book Access")

# Define FastAPI API endpoint URLs
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000/api/v1")


class Users(BaseModel):
    email: str
    password: str
    plan: str


class UsersLogin(BaseModel):
    email: str
    password: str


h_menu_1 = option_menu(None, ['Login', 'Register User'], default_index=0, orientation="horizontal")
h_menu_1

st.session_state["access_token"] = ""
if h_menu_1 == "Register User":
    st.subheader("User Registration")
    reg_email = st.text_input("Email")
    reg_password = st.text_input("Password", type="password")
    reg_plan = st.text_input("Plan (basic or premium)")

    if st.button("Register"):
        user_data = {
            "email": reg_email,
            "password": reg_password,
            "plan": reg_plan
        }
        response = requests.post(f"{FASTAPI_URL}/users/signup/", json=user_data)
        if response.status_code == 200:
            st.success("User registered successfully!")
        else:
            print(response)
            error_detail = response.json().get("detail")
            if error_detail:
                st.error(f"Registration failed: {error_detail}")
            else:
                st.error("Registration failed. Please try again.")
else:
    # User login
    st.subheader("User Login")
    login_email = st.text_input("Email")
    login_password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_login_data = UsersLogin(email=login_email, password=login_password)
        login_response = requests.post(f"{FASTAPI_URL}/users/login/", json={"email": user_login_data.email,
                                                                            "password": user_login_data.password})
        if login_response.status_code == 200:
            resp = login_response.json()
            access_token = resp["access_token"]
            st.session_state["access_token"] = resp["access_token"]
            st.success("Login successful!")
            st.write("Access Token:", resp)

            # # Access book summaries and audio
            # if st.button("Access Book Summaries"):
            #     # Replace bookId and chapterId with actual values
            #     bookId = "book123"
            #     chapterId = "chapter456"
            #     headers = {"Authorization": f"Bearer {access_token}"}
            #     summary_response = requests.get(f"{FASTAPI_URL}/books/{bookId}/chapters/{chapterId}/summarize", headers=headers)
            #     if summary_response.status_code == 200:
            #         summary = summary_response.json()["summary"]
            #         st.subheader("Book Summary")
            #         st.write(summary)
            #     else:
            #         st.error("Error accessing book summary.")
            #
            # if st.button("Access Audio"):
            #     # Replace bookId and chapterId with actual values
            #     bookId = "book123"
            #     chapterId = "chapter456"
            #     headers = {"Authorization": f"Bearer {access_token}"}
            #     audio_response = requests.get(f"{FASTAPI_URL}/books/{bookId}/chapters/{chapterId}/audio", headers=headers)
            #     if audio_response.status_code == 200:
            #         # Assuming the audio is in mp3 format
            #         audio_data = audio_response.content
            #         st.audio(audio_data, format="audio/mp3")
            #     else:
            #         st.error("Error accessing audio chapter.")

        else:
            st.error("Login failed. Check your email and password.")

