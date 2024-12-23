import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px

def ch_display(df):

    report_df = df.copy()
    report_df['Talk Time Duration'] = pd.to_datetime(report_df['Talk Time Duration'], format='%H:%M:%S')
    report_df['Time'] = report_df['Talk Time Duration'].dt.hour * 3600 + report_df['Talk Time Duration'].dt.minute * 60 + report_df['Talk Time Duration'].dt.second

    report_df['Call Time'] = pd.to_datetime(report_df['Call Time'], format='%H:%M:%S', errors='coerce')
    report_df['Hour'] = report_df['Call Time'].dt.hour

    summary_df = report_df.groupby(['Hour']).agg(
        agent_count=('Collector', 'nunique'),
        total_login_hours=('Collector', 'nunique'),
        total_talk_time=('Time', 'sum')
    ).reset_index()

    
    # st.dataframe(summary_df)

    summary_df['total_talk_time'] = summary_df['total_talk_time'] / 3600
    summary_df['total_talk_time'] = summary_df['total_talk_time'].round(2)

    summary_df.rename(columns={
        'total_login_hours': 'Login Hours',
        'total_talk_time': 'Talk Time',
        'agent_count': 'Agent Count',
        }, inplace=True)

    fig = px.line(summary_df, x='Hour', y=['Agent Count', 'Talk Time'], 
              title='Talk Time Vs. Login By Hour',
              markers=True)
    
    st.plotly_chart(fig)

    summary_df['Occupancy Rate'] = (summary_df['Talk Time'] / summary_df['Login Hours']) * 100
    summary_df['Occupancy Rate'] = summary_df['Occupancy Rate'].round(2)
    summary_df['Occupancy Rate'] = summary_df['Occupancy Rate'].astype(str) + '%'

    # pivot_df = summary_df.pivot_table(index='Call Type', columns='Hour', values='debtor_connected_count', fill_value=0)
    metrics_df = pd.DataFrame({
        'Hour': summary_df['Hour'].unique(),  # Unique hours
        'Total Agents': summary_df.groupby('Hour')['Agent Count'].last().values,
        'Total Login (Hours)': summary_df.groupby('Hour')['Login Hours'].last().values,
        'Total Talk Time (Hours)': summary_df.groupby('Hour')['Talk Time'].last().values,
        'Occupancy Rate': summary_df.groupby('Hour')['Occupancy Rate'].last().values
    })

    metrics_df = metrics_df.set_index('Hour').T  # Transpose

    metrics_df = metrics_df.fillna(0)
    
    return metrics_df.reset_index()