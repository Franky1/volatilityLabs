import streamlit as st
import matplotlib.pyplot as plt
import datetime
import os, sys

vecmPath = os.path.dirname(__file__) + '/../skew'
sys.path.append(vecmPath)
#import skewStreamlit as skew

plt.style.use('ggplot')

SECONDSBACKTORETRIEVE = 3600

def render(secretDict):
    skewBlurb = "Skew is the implied volatility disparity between different strike prices with the same expiration. Below we graph the skew as a function of time."
    
    st.write(skewBlurb)
    timestampUpper = datetime.datetime.now(datetime.timezone.utc)
    timestampLower = timestampUpper - datetime.timedelta(seconds=SECONDSBACKTORETRIEVE)

    '''
    fig0, temp = skew.skewFigures(secretDict, timestampLower, timestampUpper)
    st.plotly_chart(fig0, use_container_width=True)

    if temp is not None:
        st.write(temp)
    '''