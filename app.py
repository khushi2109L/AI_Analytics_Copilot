import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
from dotenv import load_dotenv
import os 
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

# Page title
st.set_page_config(page_title="AI Analytics Copilot", page_icon="📊")

# App title
st.title("📊 AI Analytics Copilot")
st.sidebar.title("📌 AI Analytics Copilot")
st.sidebar.markdown("""
Welcome to **AI Analytics Copilot**!

This application helps you:

- 📂 Upload CSV/Excel files
- 📊 Explore datasets
- 📈 Generate charts
- 🤖 Get AI Insights
- 💬 Chat with your data
""")


# File uploader
uploaded_file = st.sidebar.file_uploader(
    "📂 Upload your dataset",
    type=["csv", "xlsx"]
)

# Read the uploaded file
if uploaded_file is not None:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("File uploaded successfully!")

    st.subheader("Dataset Preview")

     #NULL values

    total_missing= df.isnull().sum().sum()
    missing_values= df.isnull().sum()
    missing_values= missing_values[missing_values>0]
    missing_values_df= missing_values.reset_index()
    
    #Duplicate Values

    duplicate_count= df.duplicated().sum()
    duplicate_values= df[df.duplicated(keep= False)]
   
    missing_values_df.columns = ['Columns','Values']

    st.dataframe(df)

    st.subheader("Dataset Information")

    #KPIs

    col1, col2 , col3 , col4 = st.columns(4)

    with col1:
        st.metric("Rows", df.shape[0])

    with col2:
        st.metric("Columns", df.shape[1])

    with col3: 
        st.metric("Missing values", total_missing)

    with col4:
        st.metric("Duplicate values", duplicate_count )

    #Statistics
    st.subheader("Summary Statistics")
    st.dataframe(df.describe())

    #Data Type Information
    datatype = df.dtypes
    datatype_df= datatype.reset_index()
    datatype_df.columns = ['Columns','Values']
    st.subheader('Column Data Types')
    st.dataframe(datatype_df)

    #Data Visualization
    st.subheader('Data Visualization')
    opt_selected= st.selectbox(
        "Select a column to visualize",
        df.columns
    )
    if pd.api.types.is_numeric_dtype(df[opt_selected]):

      fig = px.histogram(
        df,
        x=opt_selected,
        title=f"Distribution of {opt_selected}"
    )
    else:
  
      counts = df[opt_selected].value_counts()

      fig = px.bar(
        x=counts.index,
        y=counts.values,
        title=f"Count of {opt_selected}"
    )
     
    st.plotly_chart(fig)

 #Detailed information
    st.subheader("Misssing values with columns")
    st.dataframe(missing_values_df)
    st.subheader("Duplicate Rows")
    st.dataframe(duplicate_values)

    prompt = f"""
    You are an expert Data Analyst.

    Analyze the following dataset.

    Rows: {df.shape[0]}
    Columns: {df.shape[1]}

    Column Names:
    {list(df.columns)}

    Missing Values:
    {df.isnull().sum().to_string()}

    Duplicate Rows:
    {df.duplicated().sum()}

    Summary Statistics:
    {df.describe(include="all").to_string()}


    Provide: 
    1.Dataset Summary
    2.Data Quality Issues
    3.Cleaning Suggestions
    4.Interesting Business Insights
    5.Recommended Visualizations
    6.Short summary of the above summary 
    """

st.subheader("🤖 AI Insights")

button_clicked = st.button("Generate AI Insights")

if button_clicked:

    with st.spinner("🤖 Gemini is analyzing your dataset..."):

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

    st.success("Analysis Complete!")

    st.markdown(response.text)

    report = f"""
AI ANALYTICS COPILOT REPORT
===========================

Dataset Name: {uploaded_file.name}

Rows: {df.shape[0]}
Columns: {df.shape[1]}

=====================================

AI INSIGHTS

{response.text}
"""

    st.download_button(
        label="📥 Download AI Report",
        data=report,
        file_name="AI_Analytics_Report.txt",
        mime="text/plain"
    )
    
st.subheader("💬 Chat with your Dataset")

user_question = st.text_input(
    "Ask a question about your dataset"
)
chat_button = st.button("Ask AI")

if chat_button:

    if user_question == "":
        st.warning("Please enter a question.")

    else:
        prompt = f"""
        You are an expert Data Analyst.
        Answer the questions from the uploaded dataset only
        If you don't know the answer, clearly say so 
        Do not make up facts 
        Use bullet points wherever needed

        Here is information about the uploaded dataset.
 
        Rows: {df.shape[0]}
        Columns: {df.shape[1]}

        Dataset:
       {df.head(100).to_string()}

        Column Names:
        {list(df.columns)}

        Missing Values:
        {df.isnull().sum().to_string()}

        Duplicate Rows:
        {df.duplicated().sum()}

        Summary Statistics:
        {df.describe(include='all').to_string()}

        User Question:
        {user_question}

        Answer the user's question clearly and professionally.
        """
       try:
            with st.spinner("🤖 Gemini is thinking..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

        
            st.markdown(response.text)
        except Exception:
            st.error("Unable to generate a response. Please try again")

       
