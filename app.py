import streamlit as st
import base64
from openai import OpenAI
import time

# configures page settings 
st.set_page_config(
    page_title="Image Analyzer",
    initial_sidebar_state="expanded",
    layout="centered", #wide
    page_icon="🌋"
)

# Suntikkan CSS custom untuk menyembunyikan menu hamburger
hide_streamlit_style =""" 
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.header("BurstByte® - 🎢 Playground", divider="orange", anchor=False)
st.markdown("Powered by **BurstByte® Technology**")

with st.sidebar:
    # st.subheader("⚙️ Settings")
    st.subheader("Settings")

    provider = ["OpenAI"]
    model_provider = st.selectbox("Choose Provider", provider, help="Pilih LLM Provider.")
    if model_provider == 'OpenAI':
        api_key = st.sidebar.text_input("Enter your OpenAI API Key:", type="password")
    else:
        api_key = ''

    img_source = st.radio(
        "Image Source",
        ["File", "Camera"],
        captions= ["Upload image from file.", "Take picture from camera."],
        horizontal=False
    )
    if img_source == 'File':
        input_img = st.file_uploader("Choose image file", type=['png', 'jpg', 'jpeg'] )
    else:
        input_img = st.camera_input('Take a picture')

    uploaded_file = input_img
        
    # Bagian untuk menampilkan hak cipta di bagian bawah halaman
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("© 2024 - BurstByte® Technology", unsafe_allow_html=True)

# Function to encode the image to base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

if model_provider == 'OpenAI':
    selected_client = OpenAI(api_key=api_key)
else:
    selected_client = OpenAI(
                            base_url = '', # Ollama Server
                            api_key=api_key, # required, but unused
                            )

client = selected_client

if uploaded_file:
    # Display the uploaded image
    with st.expander("Image", expanded = True):
        st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)

# Toggle for showing additional details input
show_details = st.toggle("Add details about the image", value=False)

if show_details:
    # Text input for additional details about the image, shown only if toggle is True
    additional_details = st.text_area(
        "Add any additional details or context about the image here:",
        disabled=not show_details
    )

# Button to trigger the analysis
analyze_button = st.button("Analyse the Scientific Image", type="secondary")

# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if uploaded_file is not None and api_key and analyze_button:

    with st.spinner("Analysing the image ..."):
        # Encode the image
        base64_image = encode_image(uploaded_file)
    
        # Optimized prompt for additional clarity and detail
        prompt_text = (
            "You are a highly knowledgeable scientific image analysis expert. "
            "Your task is to examine the following image in detail. "
            "Provide a comprehensive, factual, and scientifically accurate explanation of what the image depicts. "
            "Highlight key elements and their significance, and present your analysis in clear, well-structured markdown format. "
            "If applicable, include any relevant scientific terminology to enhance the explanation. "
            "Assume the reader has a basic understanding of scientific concepts."
            "Create a detailed image caption in bold explaining in short."
        )
    
        if show_details and additional_details:
            prompt_text += (
                f"\n\nAdditional Context Provided by the User:\n{additional_details}"
            )
    
        # Create the payload for the completion request
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ]
    
        # Make the request to the OpenAI API
        try:
            # Without Stream
            
            # response = client.chat.completions.create(
            #     model="gpt-4-vision-preview", messages=messages, max_tokens=500, stream=False
            # )
    
            # Stream the response
            full_response = ""
            message_placeholder = st.empty()
            
            if model_provider == 'OpenAI':
                selected_model = "gpt-4-vision-preview"
            else:
                selected_model = ""

            for completion in client.chat.completions.create(
                model=selected_model, messages=messages, 
                max_tokens=1200, stream=True
            ):
                # Check if there is content to display
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            # Final update to placeholder after the stream ends
            message_placeholder.markdown(full_response)
    
            # Display the response in the app
            # st.write(response.choices[0].message.content)
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    # Warnings for user action required
    if not uploaded_file and analyze_button:
        st.warning("Please upload an image.")
    if not api_key:
        st.warning("Please enter your OpenAI API key.")

