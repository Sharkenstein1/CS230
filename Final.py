"""
Name: Yi Zhang
Professor. Frydenberg
CS 230 Final Project
Data: Cannabis_MA.xlsx
Date: May 01 2023

Description:

This Program is a Cannabis Licence Webpage based on Streamlit with features:
    1. A map that can show where Cannabis License holder business are in real life web
    2. A Pie hart demonstrate Cannabis License applicant type within year to year in different license type
    3. A Bar chart demonstrate how many Cannabis Licence was applied within year to year in different license type
    4. A Line chart demonstrate how much does an average Cannabis License cost within year to year in different license type
    5. A detailed sorted data for users to look at.
"""


import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set()

data = pd.read_excel("Cannabis_MA.xlsx")
data['Region'] = data['Region'].fillna("Not Provided").astype(str)
data['year'] = data['ORIGINAL_SUBMITTED_DATE'].map(lambda x: int(x.split(' ')[3]))

def plot_pie(data, count=True, pie_metric='APPLICATION_CLASSIFICATION', year_start_str='', year_end_str='', license_type='', region=''):
    def make_autopct(values):  # exact number of each type applicants
        def my_autopct(pct):
            total = sum(values)
            val = int(round(pct * total / 100.0))
            if pct > 1:  #if pct greater than 1, the pie chart will show it
                return '{p:.2f}% ({v:.0f})'.format(p=pct, v=val)
        return my_autopct

    if count:
        df_count = data[pie_metric].value_counts().reset_index()  # reset_index to create new index instead of using classifaction as index
    else:
        raise ValueError('label should not be None when count = False')

    fig = plt.figure(figsize=(15, 15))
    plt.pie(data=df_count, x=pie_metric, labels=df_count['index'], autopct=make_autopct(df_count[pie_metric]), shadow=False)

    pie_title = f"{year_start_str}-{year_end_str} {license_type} License Applicant Type in {region}"
    plt.title(pie_title)

    plt.tight_layout()
    return fig

def plot_bar_chart(data, year_start_str, year_end_str, license_type, region):
    fig = plt.figure(figsize=(8, 6))
    count = data.groupby('year').count()['license_type']
    bars = plt.bar(count.index, count)

    for bar in bars:
        height = bar.get_height()  # to get a num above bar
        plt.text(bar.get_x() + bar.get_width() / 2, height, str(height), ha='center', va='bottom')

    plt.title(f"{year_start_str}-{year_end_str} Number of {license_type} License Applied in {region}")
    plt.xlabel('Year')
    plt.ylabel('License Count')

    return fig

def plot_line_chart(data, x, y, title='', xlabel='', ylabel=''):
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=data, x=x, y=y)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    return plt.gcf()

def filter_data(data, year_start, year_end, license_type='ALL', region='ALL'):
    if region == 'ALL':
        filtered_data = data[(data['year'] <= year_end) & (data['year'] >= year_start)].copy()
    else:
        filtered_data = data[(data['year'] <= year_end) & (data['year'] >= year_start) & (data['Region'] == region)].copy()
    if license_type == 'ALL':
        pass
    else:
        filtered_data = filtered_data[filtered_data['license_type'] == license_type].copy()
    return filtered_data

def setup_page():
    st.sidebar.title("Select Function")
    page = st.sidebar.radio("", ["Map", "Charts", "Data Analysis"])
    return page

def setup_chart_page():
    st.sidebar.title("Select Chart Type")
    chart_type = st.sidebar.radio("", ['Pie', 'Bar', 'Line'])
    return chart_type


def setup_data_filter():  # User can choose what they want
    st.markdown("## Filter")
    year_start = st.slider("Year Start", min_value=int(data['year'].min()), max_value=int(data['year'].max()))
    year_end = st.slider("Year End", min_value=int(year_start), max_value=int(data['year'].max()))
    region = st.selectbox("Region", ["ALL"] + list(data['Region'].dropna().unique()))
    license_type = st.selectbox("License Type", ["ALL"] + list(data['license_type'].unique()))
    return year_start, year_end, region, license_type

def show_map(data):
    df = data[['latitude', 'longitude']].copy()
    df[['latitude', 'longitude']] = df[['latitude', 'longitude']].fillna(method='ffill') # in case there is a NaN value
    st.map(df, zoom=10, use_container_width=False)

def show_charts(chart_type, data, year_start_str, year_end_str, license_type, region):
    if chart_type == 'Pie':
        fig = plot_pie(data, count=True, pie_metric='APPLICATION_CLASSIFICATION', year_start_str=year_start_str, year_end_str=year_end_str, license_type=license_type, region=region)
    elif chart_type == 'Bar':
        fig = plot_bar_chart(data, year_start_str, year_end_str, license_type, region)
    elif chart_type == 'Line':
        fig = plot_line_chart(data, x='year', y='LIC_FEE_AMOUNT', title=f"Average License Fee Amount for {license_type} in {region} ({year_start_str}-{year_end_str})", xlabel='Year', ylabel='Average License Fee Amount')
    st.pyplot(fig)


def show_data_analysis(data):
    # Filter and combine columns
    data = data[['business_name', 'license_type', 'APPLICATION_CLASSIFICATION', 'lic_status', 'license_number',
                 'business_address_1', 'business_city', 'business_state', 'LIC_FEE_AMOUNT']]
    data['Business Address'] = data['business_address_1'] + ', ' + data['business_city'] + ', ' + data['business_state']
    data = data.drop(['business_address_1', 'business_city', 'business_state'], axis=1)

    # Rename columns
    data = data.rename(columns={
        'business_name': 'Business Name',
        'license_type': 'License Type',
        'APPLICATION_CLASSIFICATION': 'Classification',
        'lic_status': 'License Status',
        'license_number': 'License Number',
        'LIC_FEE_AMOUNT': 'License Fee Amount'
    })

    st.markdown("## Data Analysis")
    st.dataframe(data)

    # Sorting functionality
    st.markdown("### Sorting")
    column = st.selectbox("Select column for sorting", data.columns)
    order = st.selectbox("Select sorting order", ["Ascending", "Descending"])
    if order == "Ascending":
        data = data.sort_values(by=column, ascending=True)
    else:
        data = data.sort_values(by=column, ascending=False)
    st.write(data.style.highlight_max(subset=column, color='yellow', axis=0))



def main():
    page = setup_page()

    if page == "Map":
        show_map(data)

    elif page == "Charts":
        chart_type = setup_chart_page()
        year_start, year_end, region, license_type = setup_data_filter()
        show = st.button("Show")
        if show:
            filtered_data = filter_data(data, year_start, year_end, license_type, region)
            year_start_str = str(year_start)
            year_end_str = str(year_end)
            show_charts(chart_type, filtered_data, year_start_str, year_end_str, license_type, region)

    elif page == "Data Analysis":
        year_start, year_end, region, license_type = setup_data_filter()
        filtered_data = filter_data(data, year_start, year_end, license_type, region)
        show_data_analysis(filtered_data)

if __name__ == "__main__":
    main()









