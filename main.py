import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go


df = pd.read_csv('skills_by_month.csv')

def get_top_skills(data):
    m_values = list(data[data['group']=='m'].nlargest(5, 'freq_count')['skills'])
    f_values = list(data[data['group']=='o'].nlargest(5, 'freq_count')['skills'])
    focus_skills = data[data['skills'].isin(list(set(f_values + m_values)))]
    focus_skills = focus_skills.pivot_table('freq_count', 'skills', 'group').reset_index()
    return focus_skills

def viz(data):
    st.subheader('   Top MLE Skills for February & March')
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
      r=list(data['o']),
      theta= list(data['skills']),
      fill='toself',
      name='February'
    ))
    fig.add_trace(go.Scatterpolar(
      r=list(data['m']),
      theta= list(data['skills']),
      fill='toself',
      name='March'
    ))

    fig.update_layout(
        polar=dict(
        radialaxis=dict(
        visible=True,
      # range=[0, 100]
    )),
    showlegend=False
    )
    return fig


def main_page():
    data = get_top_skills(df)
    fig = viz(data)
    st.plotly_chart(fig,use_container_width=True,config={'displayModeBar': False})



if __name__ == "__main__":
    main_page()


