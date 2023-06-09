import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))

import streamlit as st
from gptzero import ZeroAccount, ZeroVerdict, ZeroVerdictData
from originality import OriginalityAccount, OriginalityVerdict
import logging
from dataclasses import asdict

logging.basicConfig(level=logging.INFO)

def get_zero_scan(content: str) -> ZeroVerdictData:
    try:
        acc = ZeroAccount.get_from_local()
        if not acc:
            acc = ZeroAccount.create()
        
        res = ZeroVerdict.get(content, acc)
        return res

    except Exception as e:
        # Return error message if an exception occurs
        return (
            f'An error occurred: {e}. '
        )

def get_originality_scan(content: str):

    estimated_credits_cost = -(sum(1 for c in content if c in ' \t\n') // -50) # estimated if ai+plagiat (the negatives make a ciel)
    account = OriginalityAccount.get_from_local(estimated_credits_cost)
    if not account:
        account = ZeroAccount.create()
    res = OriginalityVerdict.get(content, account)
    return res
    
# Set page configuration and add header
st.set_page_config(
    page_title="GPT Scanner",
    initial_sidebar_state="expanded",
    layout="wide",
    page_icon="🔍",
    # menu_items={
    #     'Get Help': '',
    #     'Report a bug': "",
    #     'About': "",
    # },
)
st.header('GPT Scanner')

question_text_area = st.text_area('Paste content to scan :')

if st.button('🔍 Scan'):

    with st.container():
        left, right = st.columns(2)
        with left:
            zverdict = get_zero_scan(question_text_area)
            st.header("GPTZero")
            st.table(asdict(zverdict))
            st.caption(f"the burstiness is a measurement of the variation of the randomness of the text")
            st.caption("burstiness over 90 is often regarded as human")
        with right:
            st.header("Originality.ai")
            overdict = get_originality_scan(question_text_area)
            st.table(asdict(overdict))

hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
