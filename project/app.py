import base64

import streamlit as st
from gtts import gTTS
from io import BytesIO
import pygame
from openai import OpenAI

client = OpenAI()


def file_to_base64(uploaded_file):
    file_content = uploaded_file.read()
    base64_encoded = base64.b64encode(file_content).decode('utf-8')
    return base64_encoded

def image_to_text(base64_image):
    images = [file_to_base64(base64_image)]

    prompt = """Opisz mi szczegółowo załączone zdjęcie. Powiedz co przedstawia. Co widzisz na pierwszym i drugim planie? Jaka jest kolorystyka całego zdjęcia? Twoja odpowiedź ma nie być dłuższa niż 100 tokenów!"""

    PROMPT_MESSAGES = [
        {
            "role": "user",
            "content": [
                prompt,
                *map(lambda x: {"image": x, "resize": 768},
                     images),
            ],
        },
    ]
    params = {
        "model": "gpt-4-vision-preview",
        "messages": PROMPT_MESSAGES,
        "max_tokens": 200,
    }

    result = client.chat.completions.create(**params)
    print(result)
    print("=========================")
    print(result.choices[0].message.content)
    return result.choices[0].message.content


def say(text):
    tts = None

    with st.spinner('Przetwarzanie ...'):
        tts = gTTS(text=text, lang='pl')

    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)

    pygame.mixer.init()
    pygame.mixer.music.load(mp3_fp)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy(): 
        pygame.time.Clock().tick(10)


def main():
    pygame.init()
    st.set_page_config(page_title="Image description", page_icon=":bird:")

    # ================================================
    

    st.header("Generator opisu obrazu :bird:")
    uploaded_file = st.file_uploader("Wybierz plik")

    if uploaded_file is not None:
        st.image(uploaded_file)

    if st.button('Opisz', type="primary"):
        if uploaded_file is None:
            say("Nie dodałeś obrazka. Zrób to żebym mógł go opisać")

        else:
            try:
                say("Zaczynam przetwarzanie zdjęcia może to chwilę zająć")
                text = None
                
                with st.spinner('Przetwarzanie ...'):
                    text = image_to_text(uploaded_file)
                
                say(text)

            except Exception as e:
                print(e)
                say("Nie udało się przetworzyć obrazka. Proszę spróbuj ponownie")
            

if __name__ == '__main__':
    main()