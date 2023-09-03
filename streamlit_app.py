import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
from langdetect import detect
import streamlit as st
from gptzero import ZeroAccount, ZeroVerdict, ZeroVerdictData
from originality import OriginalityAccount, OriginalityVerdict
from zeroGPT import zeroGPTVerdict
import logging
from dataclasses import asdict
import pandas as pd
from paraphraser import paraphrase

logging.basicConfig(level=logging.INFO)

def get_zero_scan(content: str) -> ZeroVerdictData:

    acc = ZeroAccount.get_from_local()
    if not acc:
        acc = ZeroAccount.create()
    
    res = ZeroVerdict.get(content, acc)
    return res
def get_originality_scan(content: str):

    estimated_credits_cost = -(sum(1 for c in content if c in ' \t\n') // -50) 
    account = OriginalityAccount.get_from_local(estimated_credits_cost)
    if not account and estimated_credits_cost < 50:
        account = ZeroAccount.create()

    res = OriginalityVerdict.free_get(content, account, )
    return res

def display_word_count(text):
    count = sum(1 for c in text if c in ' \t\n')
    return st.write(f"word count: {count}")

# Set page configuration and add header
st.set_page_config(
    page_title="GPT Scanner",
    initial_sidebar_state="expanded",
    layout="wide",
    page_icon="🔍",
    menu_items={
        'Get Help': 'https://github.com/Capital2/GPT-Scanner/blob/master/README.md',
        'Report a bug': "https://github.com/Capital2/GPT-Scanner/issues",
        'About': "https://github.com/Capital2/GPT-Scanner",
    },
)
st.header('GPT Scanner')

container_style = """
    background-color: #262730;
    padding: 20px;
    margin-top: 30px;
    border-radius: 5px;
    overflow-y: auto;
    height: 205px; 
    width: 100%;
"""

with st.container():
    textInput, paraphraseText = st.columns(2)
    with textInput:
        question_text_area = st.text_area('Paste content to scan (minimum 100 words):',height=200)
    with paraphraseText:
        if 'paraphrase' in st.session_state:
            print("exist")
            st.markdown(
                f'<div style="{container_style}">'
                f'<p>"{st.session_state.paraphrase}"</p>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            print("not exist")
            st.markdown(
                f'<div style="{container_style}">'
                '<p></p>'
                '</div>',
                unsafe_allow_html=True,
            )
             

if question_text_area:
    count = sum(1 for c in question_text_area if c in ' \t\n') + 1
    st.write(f"word count: {count}")


if st.button('✍🏻 Paraphrase'):
    lang = detect(question_text_area)
    st.session_state.paraphrase = paraphrase(question_text_area,lang=lang)
    print("finished")            


if st.button('🔍 Scan'):
    zverdict = get_zero_scan(question_text_area)
    st.session_state.zverdict = zverdict
    verdict = zeroGPTVerdict(question_text_area)
    st.session_state.zeroGPTVerdict = verdict

with st.container():
    left, middle, right = st.columns(3)
    with left:
        try :
            if 'zverdict' in st.session_state:
                st.header("GPTZero")
                st.markdown(f"""
                |Metric|Value|
                |:--|--:|
                Average generated probability | {st.session_state.zverdict.average_generated_prob}
                Completely generated probablity | {st.session_state.zverdict.completely_generated_prob}
                Overall burstiness* | {st.session_state.zverdict.overall_burstiness}""")
                st.caption(f"*: burstiness is a measurement of the variation of the randomness of the text (burstiness over 90 is often regarded as human)")
        except Exception as e:
            st.write(f"GPTzero error: {e}")
    with middle:
        if 'zeroGPTVerdict' in st.session_state:
            c1, c2 = st.columns(2)
            st.header("ZeroGPT")
            
            with st.container():
                    st.write("Average generated probability:")
                    st.write(st.session_state.zeroGPTVerdict["ai_percentage"])
                    
            with st.container():
                st.write("Suspected Generated Text:")
                st.write(st.session_state.zeroGPTVerdict["suspected_text"])
                
            with st.container():
                st.write("Additional Feedback:")
                st.write(st.session_state.zeroGPTVerdict["additional_feedback"])

    with right:
        st.header("Originality.ai")
        #st.write("originality Ai is under maintenance")
        # overdict = get_originality_scan(question_text_area)
        # st.markdown(f"""
        # |Metric|Value|
        # |:--|------:|
        # AI score | {overdict.ai_score}
        # Plagiarism score | {overdict.plagiarism_score}
        # Public link | [Originality.ai site]({overdict.public_link})""")


hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
