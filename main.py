import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
from udr import udr_display
from ch import ch_display

st.set_page_config(
    page_title="DS Report",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    # menu_items={
    #     'About': "# TITE. This is an *extremely* cool app!"
    # }
)

st.header('DS REPORT', divider='gray')

with st.sidebar:
    udr_file = st.file_uploader("Upload Daily Remarks")
    ch_file = st.file_uploader("Call History")

@st.cache_data
def extract_data(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file)
    except:
        df = pd.read_csv(uploaded_file)

    return df

#if udr_file is not None and ch_file is not None:
if udr_file is not None:

    udr_df = udr_display(extract_data(udr_file))

    # st.dataframe(udr_df, hide_index=True)

    cf_df = ch_display(extract_data(ch_file))

    # st.dataframe(cf_df, hide_index=True)

    udr_df.rename(columns={'Call Type': ' '}, inplace=True)
    cf_df.rename(columns={'index': ' '}, inplace=True)

    udr_df_no_grand_total = udr_df.drop('Grand Total', axis=1)

    merged_df = pd.concat([udr_df, cf_df])

    # # Step 4: Re-add the 'Grand Total' column
    # merged_df['Grand Total'] = udr_df['Grand Total']

    # # Step 5: Display the final merged DataFrame in Streamlit
    st.dataframe(merged_df, hide_index=True, use_container_width=True)
