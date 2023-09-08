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
from plagiarism import turnitinPlagaiarsimChecker
import random

logging.basicConfig(level=logging.INFO)

loading_msgs=[
      "Upgrading Windows, your PC will restart several times. Sit back and relax.",
        "Have a good day.",
        "We're building the buildings as fast as we can",
        "Don't worry - a few bits tried to escape, but we caught them",
        "The server is powered by a potato and two electrodes.",
        "We're testing your patience",
        "Just count to 5",
        "Mining some bitcoins...",
        "Downloading more RAM..",
        "Updating to Windows Vista...",
        "Deleting System32 folder",
        "ctrl-w speeds things up.",
        "doing our best 💪",
]

if 'scan_paraphrased' not in  st.session_state:
    st.session_state.scan_paraphrased = True

if "recheck_plagiarism" not in st.session_state:
    st.session_state.recheck_plagiarism = True

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
        question_text_area = st.text_area('Paste content to scan (minimum 100 words for better AI scan):',height=200,max_chars=2000)
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            scan = st.button('🔍 Scan for AI')
        with c2:
            plagiarism = st.button("📜 check plagiarism")

    with paraphraseText:

        if 'paraphrase' in st.session_state:
                st.markdown(
                    f'<div style="{container_style}">'
                    f'<p>"{st.session_state.paraphrase}"</p>'
                    '</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                f'<div style="{container_style}">'
                '<p></p>'
                '</div>',
                unsafe_allow_html=True,
            )
        st.markdown("<br>",unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            paraphraseButton = st.button('✍🏻 Paraphrase text')
        with c2:
            rescan = st.button("🔍 Rescan for AI",disabled=st.session_state.scan_paraphrased)
        with c3:
            reCheckPlagiarism = st.button("📜 recheck plagiarism",disabled=st.session_state.recheck_plagiarism)

if question_text_area:
    lang = detect(question_text_area)
    count = sum(1 for c in question_text_area if c in ' \t\n') + 1
    st.write(f"word count: {count}")


with st.container():
    if plagiarism:
        with st.spinner(random.choice(loading_msgs)):
            plagiarism_result = turnitinPlagaiarsimChecker(question_text_area,lang)
            st.session_state.plagiarism = plagiarism_result
    if scan:
        with st.spinner(random.choice(loading_msgs)):
            zverdict = get_zero_scan(question_text_area)
            st.session_state.zverdict = zverdict
            verdict = zeroGPTVerdict(question_text_area)
            st.session_state.zeroGPTVerdict = verdict
            
    if paraphraseButton:   
        with st.spinner(random.choice(loading_msgs)):
            st.session_state.paraphrase = paraphrase(question_text_area,lang=lang)
            st.session_state.scan_paraphrased = False
            st.session_state.recheck_plagiarism = False
            st.experimental_rerun()  
    if rescan:    
        with st.spinner(random.choice(loading_msgs)):
            text = st.session_state.paraphrase.replace("<b>","")
            text = text.replace("</b>","")
            text = text.replace("<br>","")
            zverdict = get_zero_scan(text)
            st.session_state.zverdict = zverdict
            verdict = zeroGPTVerdict(text)
            st.session_state.zeroGPTVerdict = verdict
            st.experimental_rerun()
    if reCheckPlagiarism:
        with st.spinner(random.choice(loading_msgs)):
            text = st.session_state.paraphrase.replace("<b>","")
            text = text.replace("</b>","")
            text = text.replace("<br>","")
            plagiarism_result = turnitinPlagaiarsimChecker(text,lang)
            st.session_state.plagiarism = plagiarism_result
            st.experimental_rerun()
    
    
    left, middle ,right = st.columns(3)
    
    with left:
        try :
            if 'zverdict' in st.session_state:
                st.header("GPTZero")
                st.write("Average generated probability:")
                st.write(round(st.session_state.zverdict.completely_generated_prob * 100,2) )
                st.write("Overall burstiness*")
                st.write(round(st.session_state.zverdict.overall_burstiness,2))
                st.caption(f"*: burstiness is a measurement of the variation of the randomness of the text (burstiness over 90 is often regarded as human)")
        except Exception as e:
            st.write(f"GPTzero error: {e}")
   
    with middle:
        if 'zeroGPTVerdict' in st.session_state:
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
        if 'plagiarism' in st.session_state:
            st.header("Turnitin Plagiarism checker")
            st.write(f"Your overall text plagirism:")
            st.write(float(st.session_state.plagiarism['turnitin_index']))
            st.write("highest match website:")
            if st.session_state.plagiarism["match"] is not None:
                st.write(st.session_state.plagiarism['match']['url'] )
                st.write("text detected")
                splited_text = question_text_area.split()
                for i in st.session_state.plagiarism['match']['highlight']:
                    st.write(f"<b>{' '.join(splited_text[int(i[0]):int(i[1])])}</b>",unsafe_allow_html=True)
            else:
                st.write("None")
                st.write("text detected")
                st.write("your text is unique")
            st.caption("Turnitin is powerful tool for plagiarism check and it is widely used by multiple universities, naming few tunisian universities using turnitin \
                       Université de Carthage, université de sousse, INAT, ENIM...")

hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
