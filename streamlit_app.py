import streamlit as st
from streamlit_image_select import image_select
from main import build_suggestions_json
# from main import dummy
# import time

if 'messages' not in st.session_state:
    st.session_state.messages = []
    # st.session_state.messages.append({"role": "assistant", "content": "Hello 👋", "image_urls":[]})

st.title("Smart Shopping AI Agent")
# st.write("## Smart Shopping AI Agent")

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        if message['role'] == 'assistant':
            st.write(message['content'])
            cols = st.columns(len(message['image_urls']))  # Create a column for each image
            for col, img_url in zip(cols, message['image_urls']):
                with col:
                    st.image(img_url, caption='Product Image', use_column_width='auto')  # Use 'auto' for better fit
        else:
            st.write(message['content'])

# with st.chat_message("assistant"):
#     st.write("Hello 👋")

prompt = st.chat_input("Search...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.spinner("Generating response...."):
        # time.sleep(2)
        LLM_response = build_suggestions_json(prompt)
    
    image_urls = []
    bot_answer = "this are the products retived as per your query!"
    for item in LLM_response:
        image_urls.append(item['uri'])

    st.session_state.messages.append({"role": "assistant", "content": bot_answer, "image_urls" : image_urls})

    with st.chat_message("assistant"):
        st.write(bot_answer)
        # for img_url in image_urls:
        #     st.image(img_url)
        cols = st.columns(len(image_urls))  # Create a column for each image
        for col, img_url in zip(cols, image_urls):
            with col:
                st.image(img_url, caption='Product Image', use_column_width='auto') 
    