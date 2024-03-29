import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
from langdetect import detect
import streamlit as st
from gptzero import ZeroAccount, ZeroVerdict, ZeroVerdictData
from originality import OriginalityAccount, OriginalityVerdict
from zeroGPT import zeroGPTVerdict
import logging
from paraphraser import paraphrase
from plagiarism import turnitinPlagaiarsimChecker
import random
from math import ceil

logging.basicConfig(
    filename="logs.txt",
    filemode='a',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

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

def modeToNum():
    if option =="Creative":
        return "3"
    elif option == "Smart":
        return "4"
    return "5"
st.title('GPT Scanner')

container_style = """
    background-color: #262730;
    padding: 20px;
    margin-top: 30px;
    border-radius: 5px;
    overflow-y: auto;
    height: 205px; 
    width: 100%;    
"""
metric_style = """
.css-1xarl3l{
    font-size: 1.2rem;
}
"""
button_style = """
.css-b3z5c9    {
    width: 100%;
}
.css-ocqkz7 {

}

"""
st.markdown(f"<style>{button_style}</style>",unsafe_allow_html=True)
st.markdown(f"<style>{metric_style}</style>",unsafe_allow_html=True)
def custom_progress_bar(value):
    
    if value <= 15:
        background_color = '#4CAF50'  # Green
    elif value <= 50:
        background_color = '#FFC300'  # Yellow
    elif value <= 75:
        background_color = '#FF5733'  # Orange
    else:
        background_color = 'red'  # Red

    progress_bar_html = f"""
    <div style ="width: 70%; border-radius: 5px; background-color: #262730;">
        <div style="width: {value}%; height: 10px; text-align: center; line-height: 10px; border-radius: 5px; background-color: {background_color}; display: flex; flex-direction: column; align-items: center; margin: -12px 0;"></div>
    </div>
    """
    st.markdown(progress_bar_html, unsafe_allow_html=True)

with st.container():
    textInput, paraphraseText = st.columns(2)
    with textInput:
        question_text_area = st.text_area('Paste content to scan (minimum 100 words for better AI scan):',height=200,max_chars=2000)
        c1,c2,c3 = st.columns(3)
        with c1:
            scan = st.button('🔍 scan for AI')
        with c2:
            plagiarism = st.button("📜 check plagiarism")
        with c3:
            if question_text_area:
                lang = detect(question_text_area)
                count = sum(1 for c in question_text_area if c in ' \t\n') + 1
                st.write(f"word count: {count}")
    with paraphraseText:
        if 'paraphrase' not in st.session_state:
            st.markdown(
                f'<div style="{container_style}">'
                '<p></p>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div style="{container_style}">'
                f'<p>"{st.session_state.paraphrase}"</p>'
                '</div>',
                unsafe_allow_html=True,)


        st.markdown("<br>",unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        with c1:
            paraphraseButton = st.button('✍🏻 paraphrase text')
            option = st.selectbox('paraphrase method',('Smart', 'Creative', 'Shorten'))
        with c2:
            rescan = st.button("🔍 rescan for AI",disabled=st.session_state.scan_paraphrased)
        with c3:
            reCheckPlagiarism = st.button("📜 recheck plagiarism",disabled=st.session_state.recheck_plagiarism)

with st.container():
    if plagiarism:
        if count < 15:
            st.error("to check for plagiarism you need to provide 15 word at least!")
        else:
            with st.spinner(random.choice(loading_msgs)):
                plagiarism_result = turnitinPlagaiarsimChecker(question_text_area,lang)
                st.session_state.plagiarism = plagiarism_result
                st.session_state.plagiarismDelta = plagiarism_result["turnitin_index"]
    if scan:
        with st.spinner(random.choice(loading_msgs)):
            zverdict = get_zero_scan(question_text_area)
            st.session_state.zverdict = zverdict
            st.session_state.zverdictDelta = ceil(zverdict.completely_generated_prob * 100)
            verdict = zeroGPTVerdict(question_text_area)
            st.session_state.zeroGPTVerdict = verdict
            st.session_state.zeroGPTVerdictDelta = verdict["ai_percentage"]
            
    if paraphraseButton:   
        with st.spinner(random.choice(loading_msgs)):
            st.session_state.scan_paraphrased = False
            st.session_state.recheck_plagiarism = False
            st.session_state.paraphrase = paraphrase(question_text_area,lang=lang, mode=modeToNum())
            st.session_state.paraphrase = st.session_state.paraphrase.replace("\"","") 
            st.experimental_rerun()
            
    if rescan:    
        with st.spinner(random.choice(loading_msgs)):
            text = st.session_state.paraphrase.replace("<b>","")
            text = text.replace("</b>","")
            text = text.replace("<br>","")
            
            zverdict = get_zero_scan(text)
            if "zverdict" not in st.session_state:
                st.session_state.zverdict = ZeroVerdictData(
                    average_generated_prob=0,
                    completely_generated_prob=0,
                    overall_burstiness=0
                    )
            st.session_state.zverdictDelta = ceil(zverdict.completely_generated_prob * 100 - st.session_state.zverdict.completely_generated_prob *100)
            st.session_state.zverdict = zverdict

            verdict = zeroGPTVerdict(text)
            if "zeroGPTVerdict" not in st.session_state:
                st.session_state.zeroGPTVerdict = {"ai_percentage":0} 
            st.session_state.zeroGPTVerdictDelta = verdict['ai_percentage'] - st.session_state.zeroGPTVerdict['ai_percentage']
            st.session_state.zeroGPTVerdict = verdict
            
    if reCheckPlagiarism:
        with st.spinner(random.choice(loading_msgs)):
            if 'plagiarism' not in st.session_state:
                st.session_state.plagiarism = {"turnitin_index":0}
            text = st.session_state.paraphrase.replace("<b>","")
            text = text.replace("</b>","")
            text = text.replace("<br>","")
            plagiarism_result = turnitinPlagaiarsimChecker(text,lang)
            if "plagiarism" not in st.session_state:
                st.session_state.plagiarism = {"turnitin_index":0}
            st.session_state.plagiarismDelta = float(plagiarism_result["turnitin_index"]) - float(st.session_state.plagiarism["turnitin_index"])
            st.session_state.plagiarism = plagiarism_result
            
    
    
    left, middle ,right = st.columns(3)
    
    with left:
        try :
            if 'zverdict' in st.session_state:
                st.header("GPTZero")
                gptZeroValue = ceil(st.session_state.zverdict.completely_generated_prob * 100)
                st.metric(label="Average generated probability:",value=f"{gptZeroValue}%", delta=f"{st.session_state.zverdictDelta}%", delta_color="inverse")
                custom_progress_bar(gptZeroValue)   
                st.text("Overall burstiness*")
                st.write(round(st.session_state.zverdict.overall_burstiness,2))
                st.caption(f"*: burstiness is a measurement of the variation of the randomness of the text (burstiness over 90 is often regarded as human)")
        except Exception as e:
            st.write(f"GPTzero error: {e}")
   
    with middle:
        if 'zeroGPTVerdict' in st.session_state:
            st.header("ZeroGPT")
            with st.container():
                    zeroGptValue = ceil(st.session_state.zeroGPTVerdict['ai_percentage'])
                    st.metric(label="Average generated probability:",value=f"{zeroGptValue}%", delta=f"{ceil(st.session_state.zeroGPTVerdictDelta)}%", delta_color="inverse")
                    custom_progress_bar(zeroGptValue) 
            with st.container():
                st.text("Suspected Generated Text:")
                st.write(st.session_state.zeroGPTVerdict["suspected_text"])
                
            with st.container():
                st.write("Additional Feedback:")
                st.write(f"<p style='color:orange';>{st.session_state.zeroGPTVerdict['additional_feedback']}</p>",unsafe_allow_html=True)
    with right:
        if 'plagiarism' in st.session_state:
            st.header("Turnitin Plagiarism checker")
            plagiarismValue = ceil(float(st.session_state.plagiarism['turnitin_index']))
            st.metric(label="Your overall text plagirism:",value=f"{plagiarismValue}%", delta=f"{ceil(float(st.session_state.plagiarismDelta))}%", delta_color="inverse")
            custom_progress_bar(plagiarismValue)   
            if st.session_state.plagiarism["match"] is not None:
                suspected_text = []
                st.text("Highest match website:")
                st.write(st.session_state.plagiarism['match']['url'] )
                st.text("text detected:")
                splited_text = question_text_area.split()
                for i in st.session_state.plagiarism['match']['highlight']:
                    suspected_text.append(' '.join(splited_text[int(i[0]):int(i[1])]))
                st.write(suspected_text)
            else:
                st.write("None")
                st.text("text detected:")
                st.write("your text is unique")
            st.caption("Turnitin is powerful tool for plagiarism check and it is widely used by multiple universities, naming few tunisian universities using turnitin \
                       Université de Carthage, université de sousse, INAT, ENIM...")

hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

