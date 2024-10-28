import streamlit as st
from main import build_suggestions_json

# Initialize session state for messages if not already done
if 'messages' not in st.session_state:
    st.session_state.messages = []
    # Add initial greeting message from the assistant
    st.session_state.messages.append({"role": "assistant", "content": "Hello! 👋 Welcome to Smart Shopping AI Agent. How can I assist you today?", "image_urls": []})

st.title("Smart Shopping AI Agent")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.write(message['content'])
        
        # Only create columns if there are image URLs
        if message['role'] == 'assistant' and message['image_urls']:
            cols = st.columns(len(message['image_urls']))  # Create a column for each image
            for col, img_url in zip(cols, message['image_urls']):
                with col:
                    st.image(img_url, caption='Product Image', use_column_width='auto')  # Use 'auto' for better fit

# User input for search prompt
prompt = st.chat_input("Search...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.spinner("Generating response...."):
        LLM_response = build_suggestions_json(prompt)
    
    image_urls = []
    if LLM_response:
        bot_answer = "These are the products retrieved as per your query!"
        for item in LLM_response:
            image_urls.append(item['uri'])
    else:
        bot_answer = "I'm sorry, but I couldn't find any products matching your query."

    st.session_state.messages.append({"role": "assistant", "content": bot_answer, "image_urls": image_urls})

    with st.chat_message("assistant"):
        st.write(bot_answer)
        # Only create columns if there are image URLs
        if image_urls:
            cols = st.columns(len(image_urls))  # Create a column for each image
            for col, img_url in zip(cols, image_urls):
                with col:
                    st.image(img_url, caption='Product Image', use_column_width='auto')
