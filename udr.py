import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px

def udr_display(df):

    report_df = df[~df['Call Status'].isna()]
    report_df['IsConnected'] = np.where(report_df['Talk Time Duration'] > 0, 'CONNECTED', 'NOT CONNECTED')
    report_df['Call Type'] = np.where((report_df['Remark Type'].str.lower() == 'predictive') | (report_df['Remark'].str.contains('predictive', case=False)), 'Predictive', 'Manual')


    report_df['Time'] = pd.to_datetime(report_df['Time'], format='%H:%M:%S', errors='coerce')
    report_df['Hour'] = report_df['Time'].dt.hour

    # st.dataframe(report_df)
    # st.dataframe(report_df[['Debtor', 'Hour', 'Talk Time Duration', 'IsConnected', 'Call Type']])

    summary_df = report_df.groupby(['Hour', 'Call Type', 'IsConnected']).agg(
        debtor_connected_count=('Debtor', 'nunique')
    ).reset_index()

    summary_connected_df = report_df[report_df['IsConnected'] == 'CONNECTED'].groupby(['Hour', 'Call Type']).agg(
        debtor_connected_count=('Debtor', 'nunique')
    ).reset_index()

    # st.dataframe(summary_connected_df)

    total_connected_predictive = report_df[(report_df['IsConnected'] == 'CONNECTED') & (report_df['Call Type'] == 'Predictive')]['Debtor'].nunique()
    total_connected_manual = report_df[(report_df['IsConnected'] == 'CONNECTED') & (report_df['Call Type'] == 'Manual')]['Debtor'].nunique()
    total_rpc = report_df[(report_df['Relation'] == 'Related Party Contact')]['Debtor'].nunique()
    total_debtor = report_df[(report_df['Relation'] == 'Debtor')]['Debtor'].nunique()
    total_unk = report_df[(report_df['Relation'] == 'Unknown Party Contact')]['Debtor'].nunique()

    total_not_connected_predictive = report_df[(report_df['IsConnected'] == 'NOT CONNECTED') & (report_df['Call Type'] == 'Predictive')]['Debtor'].nunique()
    total_not_connected_manual = report_df[(report_df['IsConnected'] == 'NOT CONNECTED') & (report_df['Call Type'] == 'Manual')]['Debtor'].nunique()

    summary_df['CallType_IsConnected'] = summary_df['Call Type'] + ' (' + summary_df['IsConnected'] + ')'
    
    pivot_df = summary_connected_df.pivot_table(index='Call Type', columns='Hour', values='debtor_connected_count', fill_value=0)

    pivot_df = pivot_df.reindex(['Predictive', 'Manual'], fill_value=0)

    pivot_df['Grand Total'] = pivot_df.index.map({
        'Manual': total_connected_manual,
        'Predictive': total_connected_predictive
    })

    pivot_df.loc['Total Connected Calls'] = pivot_df.sum(axis=0)
    pivot_df = pivot_df.rename(index={'Predictive': 'Predictive Calls', 'Manual': 'Manual Calls'})

    pivot_df_reset = pivot_df.reset_index()

    pivot_overall_df = summary_df.pivot_table(index='CallType_IsConnected', columns='Hour', values='debtor_connected_count', fill_value=0)
    pivot_overall_df = pivot_overall_df.reindex(['Manual (CONNECTED)', 'Manual (NOT CONNECTED)', 'Predictive (CONNECTED)', 'Predictive (NOT CONNECTED)'], fill_value=0)

    pivot_overall_df['Grand Total'] = pivot_overall_df.index.map({
        'Manual (CONNECTED)': total_connected_manual,
        'Manual (NOT CONNECTED)': total_not_connected_manual,
        'Predictive (CONNECTED)': total_connected_predictive,
        'Predictive (NOT CONNECTED)': total_not_connected_predictive
    })

    pivot_overall_df.loc['Total Calls'] = pivot_overall_df.sum(axis=0)
    # pivot_overall_df = pivot_overall_df.rename(index={'Predictive': 'Predictive Calls', 'Manual': 'Manual Calls'})

    pivot_overall_df_reset = pivot_overall_df.reset_index()


    fig = px.line(summary_connected_df, x='Hour', y='debtor_connected_count', color='Call Type', 
              title='Unique Connected Calls per Hour by Call Types',
              labels={'debtor_connected_count': 'Connected Calls', 'Hour': 'Hour'},
              markers=True)
    
    st.plotly_chart(fig)

    st.dataframe(pivot_overall_df_reset, hide_index=True, use_container_width=True)

    data = {
    'Relation': ['Related Party Contact', 'Debtor', 'Unknown Party Contact'],
    'Count': [total_rpc, total_debtor, total_unk]
    }
    
    # Creating the pie chart
    fig1 = px.pie(
        data, 
        names='Relation', 
        values='Count', 
        title='Distribution of Contacts by Relations',
        hole=0.3  # Optional: To create a donut chart
    )
    
    # Display the chart

    fig_pie_call_type = px.pie(summary_connected_df, names='Call Type', values='debtor_connected_count',
                            title='Distribution of Connected Calls by Call Type')

    fig_pie_call_hour = px.pie(summary_connected_df, names='Hour', values='debtor_connected_count',
                            title='Distribution of Connected Calls per Hour')

    col1, col2, col3 = st.columns(3)

    with col1:
        st.plotly_chart(fig_pie_call_type)
    with col2:
        st.plotly_chart(fig_pie_call_hour)
    with col3:
        st.plotly_chart(fig1)

    return pivot_df_reset
