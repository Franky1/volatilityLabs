import streamlit as st
import matplotlib.pyplot as plt


from pages import formalSpecPage, vecmPage, nftPage
from pages import ivSurfacePage, monteCarloPage
from pages import garchPage, skewPage

plt.style.use('ggplot')

pwd = st.secrets['labsPassword']
moralisKey = st.secrets['moralisKey']

topic = ['Latent Prices Using VECM', 
         'Formal Specification', 
         'NFT Analytics', 
         'Volatility Skew', 
         'Implied Volatility Surface', 
         'Liquidation Risk', 
         'GARCH Model']

st.title('Volatility Labs')

pwdText = st.sidebar.text_input('Password: ', type='password')

topicSelection = st.sidebar.selectbox(
    'Select Research Topic:',
    topic
)

if pwdText == pwd:

    if topicSelection == topic[0]:
        vecmPage.render(st.secrets)

    elif topicSelection == topic[1]:
        formalSpecPage.render()

    elif topicSelection == topic[2]:
        nftPage.render(moralisKey)

    elif topicSelection == topic[3]:
        skewPage.render(st.secrets)

    elif topicSelection == topic[4]:
        ivSurfacePage.render(st.secrets)

    elif topicSelection == topic[5]:
        monteCarloPage.render(st.secrets)

    elif topicSelection == topic[6]:
        garchPage.render(st.secrets)

