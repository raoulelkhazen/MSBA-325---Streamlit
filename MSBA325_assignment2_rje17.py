
# Data Cleaning

import pandas as pd
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.express as px
import streamlit as st



st.set_page_config(layout="wide")

st.title('Hotel Reservation Cancelation')

@st.cache(allow_output_mutation=True)
def load_data():
    data = pd.read_csv('hotel_bookings.csv')
    data.info()
    data.isna().sum()
    data.duplicated().sum()
    data.drop_duplicates(inplace = True)
    data.dropna(subset=['country', 'children', 'arrival_date_week_number'], axis=0, inplace = True)
    # data.drop(columns = ['company', 'agent'], inplace = True)
    data.reset_index(inplace = True, drop = True)
    data.head()

    data['Total Guests'] = data['adults'] + data['children']

    data['Total Stays'] = data['stays_in_weekend_nights'] + data['stays_in_week_nights']
    
    Canceled_reservation = data[data['is_canceled'] == 1]
    Confirmed_reservation = data[data['is_canceled'] == 0]
    
    Resort_hotel = data[data['hotel'] == 'Resort Hotel']
    City_hotel = data[data['hotel'] == 'City Hotel']
    
    country_dist = pd.DataFrame(data['country'].value_counts())
    
    return data, Canceled_reservation, Confirmed_reservation, Resort_hotel, City_hotel, country_dist

df, canceled, confirmed, resort, city, country = load_data()



Resort_arrival_month = pd.DataFrame(resort['arrival_date_month'].value_counts())

City_arrival_month = pd.DataFrame(city['arrival_date_month'].value_counts())

new_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
Resort_arrival_month = Resort_arrival_month.reindex(new_order, axis=0, copy=False)
City_arrival_month = City_arrival_month.reindex(new_order, axis=0, copy=False)


def season(x):
    if x in ['December','January','February']:
        return "Winter"
    if x in['March','April','May']:
        return "Spring"
    if x in['June','July', 'August']:
        return "Summer"
    if x in['September', 'October', 'November']:
        return "Autum"
    
df['Seasons']=df['arrival_date_month'].apply(season)



# Visualizations

st.sidebar.title('Navigation')
options = st.sidebar.radio('Select what you want to display:', ['Home', 'Data Summary', 'Visualizations'])


def home():
    st.caption("MSBA325 Assignment 2 - Prepared by Raoul El Khazen")
    st.markdown("""
                > ## This dataset was used in the previous Spring semester in the Machine Learning course:
                - It contains 119,390 observations
                - 2 types of Hotels: City and Resort
                - We were building a ML model to predict whether a reservation will be canceled or confirmed
                
                >  ## 5 types of Visualizations were applied on this dataset:
                - Map Visualization
                - Scatter Plot
                - Histogram
                - Pie Chart
                - Distribution Plot""")


def data_summary():
    st.header('Explore the Data')
    if st.checkbox('Show raw data', value=True):
       st.subheader('Raw data')
       st.write(df)
       
    st.header('Statistics of Dataframe')
    st.write(df.describe())



def visualization():
    st.header('Plot of Data')
    
    st.subheader('Home Country of Guests')
    fig = px.choropleth(country,
                    locations=country.index,
                    color=country["country"], 
                    hover_name=country.index, 
                    color_continuous_scale=px.colors.sequential.Sunset)

    fig.update_traces(marker=dict(line=dict(color='#000000', width=1)))
    st.plotly_chart(fig, use_container_width=True)

    
    col1, col2 = st.columns(2)
    
    with col1:    
        st.subheader('Distribution of Market Segment by different Hotel Types')
        fig = px.histogram(df, x="market_segment", color='hotel')
        fig.update_layout(barmode='group', xaxis={'categoryorder': 'total descending'})
        fig.update_traces(marker=dict(line=dict(color='#000000', width=1)))
        st.plotly_chart(fig, use_container_width=True)
        

    with col2:
        st.subheader('Distribution of the Reservation Status')
        reservation_status = df['reservation_status'].value_counts()
        fig = go.Figure(data=[go.Pie(labels=reservation_status.index, values=reservation_status, opacity=0.8)])
        fig.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#000000', width=2)))
        st.plotly_chart(fig, use_container_width=True)


    st.subheader('Monthly Distribution of Guests')
    fig = go.Figure()
    if st.checkbox('Resort Hotel', value=True):
        fig.add_trace(go.Scatter(x=Resort_arrival_month.index, y=Resort_arrival_month['arrival_date_month'], name="Resort Hotel",
                         hovertext=Resort_arrival_month['arrival_date_month']))
    if st.checkbox('City Hotel', value=True):
        fig.add_trace(go.Scatter(x=City_arrival_month.index, y=City_arrival_month['arrival_date_month'], name="City Hotel",
                         hovertext=City_arrival_month['arrival_date_month']))
    fig.update_layout(
        xaxis_title="Arrival Month",
        yaxis_title="Number of Guests")
    st.plotly_chart(fig, use_container_width=True)


    st.subheader('Effect of Lead Time Over Reservation Cancelation')
    fig = ff.create_distplot([canceled.lead_time, confirmed.lead_time], ["Canceled Reservation", "Confirmed Reservation"],bin_size=100, colors=["blue","yellow"])
    fig.update_layout(xaxis_title="lead time", yaxis_title="Distribution")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader('Over the Season')
    plot_options = st.selectbox('Select Variable', ['is_canceled', 'adr'])
    y1=df.groupby('Seasons')[plot_options].mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=y1.index, y=y1))
    fig.update_layout(
         xaxis_title="Season",
         yaxis_title="Avg. Price of Room OR Cancelation %")
    st.plotly_chart(fig, use_container_width=True)

    


if options == 'Home':
    home()
elif options == 'Data Summary':
    data_summary()
elif options == 'Visualizations':
    visualization()

