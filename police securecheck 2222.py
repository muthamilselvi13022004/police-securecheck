import streamlit as st
import pandas as pd
import pymysql
import plotly.express as px

## data connection

def create_connection():
    try:
        conn = pymysql.connect(
    host="localhost",
    user="root",
    password="13022004",
    database="securecheck_db",
    cursorclass=pymysql.cursors.DictCursor
)
        return conn
    except Exception as e:
        st.error(f"database connection error:{e}")
        return None
## fetch from database
def fetch_data(query):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            df = pd.DataFrame(result)
            return df
        finally:
            conn.close()
    else:
        return pd.DataFrame()

## Streamlit UI

st.set_page_config(page_title="Securecheck Police Dashboard",layout="wide")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Mini Project"])

#-------------------------------- page-1 --------------------------------------------------------------
if page == "Project Introduction":
    st.title("🚨Securecheck: Police check Post Digital Ledger")
    st.markdown("Real-time monitoring and insights for law enforcement")
    st.write("""
This project manages and records police check post activities using a MySQL database.  
It ensures secure, transparent, and real-time logging of vehicle stops and inspections.  

**Features:**  
- Record details of vehicles, drivers, and violations.  
- Track search activities, outcomes, and stop durations.  
- Generate reports and visualizations for analysis.  
- Ensure transparency and accountability in police operations.  

**Database Used:** `securecheck_db.police_check`  
""")
    
## show full table
st.header("Police logs overview")
query = "select*from securecheck_db.police_check"
data = fetch_data(query)
st.dataframe(data,use_container_width=True)

# Charts
st.header("📊 Visual Insights")

tab1, tab2, tab3 = st.tabs(["Stops by Violation", "Driver Gender Distribution", "Drug-Related Stops"])

with tab1:
    if not data.empty and 'violation' in data.columns:
        violation_data = data['violation'].value_counts().reset_index()
        violation_data.columns = ['Violation', 'Count']
        fig = px.bar(
            violation_data, 
            x='Violation', 
            y='Count', 
            title="Stops by Violation Type", 
            color='Violation'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for Violation chart.")

with tab2:
    if not data.empty and 'driver_gender' in data.columns:
        gender_data = data['driver_gender'].value_counts().reset_index()
        gender_data.columns = ['Gender', 'Count']
        fig = px.pie(
            gender_data, 
            names='Gender', 
            values='Count', 
            title="Driver Gender Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for Driver Gender chart.")

with tab3:
    if not data.empty and 'drugs_stop' in data.columns:
        drug_data = data['drugs_stop'].value_counts().reset_index()
        drug_data.columns = ['Drug Related Stop', 'Count']
        fig = px.bar(
            drug_data, 
            x='Drug Related Stop', 
            y='Count', 
            title="Drug-Related Stops", 
            color='Drug Related Stop'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for Drug-Related Stops chart.")

## Advanced Queries

st.header("🚀Advanced insights")

selected_query = st.selectbox("select a query to run",[  

"Top 10 vehicle_Number involved in drug-related stops",
"Vehicles were most frequently searched",
"Driver age group had the highest arrest rate",
"Gender distribution of drivers stopped in each country",
"Race and gender combination has the highest search rate",
"Time of day sees the most traffic stops",
"Average stop duration for different violations",
"Stops during the night more likely to lead to arrests",
"Violations are most associated with searches or arrests",
"Violations are most common among younger drivers (<25)",
"Is there a violation that rarely results in search or arrest",
"Which countries report the highest rate of drug-related stops",
"What is the arrest rate by country and violation",
"Which country has the most stops with search conducted"


])

query_map = {
    "Top 10 vehicle_Number involved in drug-related stops": "SELECT vehicle_number, COUNT(*) AS drug_related_count FROM police_check WHERE drugs_stop = TRUE GROUP BY vehicle_number ORDER BY drug_related_count DESC LIMIT 10",
    "Vehicles were most frequently searched": "SELECT vehicle_number, COUNT(*) AS search_count FROM police_check WHERE search_conducted = TRUE GROUP BY vehicle_number ORDER BY search_count DESC LIMIT 10",
    "Driver age group had the highest arrest rate": "SELECT CASE WHEN driver_age < 18 THEN '<18' WHEN driver_age BETWEEN 18 AND 25 THEN '18-25' WHEN driver_age BETWEEN 26 AND 40 THEN '26-40' WHEN driver_age BETWEEN 41 AND 60 THEN '41-60' ELSE '60+' END AS age_group, SUM(CASE WHEN s_outcome LIKE '%arrest%' THEN 1 ELSE 0 END)*100.0/COUNT(*) AS arrest_rate FROM police_check GROUP BY age_group ORDER BY arrest_rate DESC",
    "Gender distribution of drivers stopped in each country": "SELECT country_name, driver_gender, COUNT(*) AS count FROM police_check GROUP BY country_name, driver_gender",
    "Race and gender combination has the highest search rate": "SELECT driver_race, driver_gender, SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END)*100.0/COUNT(*) AS search_rate FROM police_check GROUP BY driver_race, driver_gender ORDER BY search_rate DESC LIMIT 5",
    "Time of day sees the most traffic stops": "SELECT HOUR(stop_time) AS hour, COUNT(*) AS count FROM police_check GROUP BY hour ORDER BY count DESC LIMIT 5",
    "Average stop duration for different violations": "SELECT violation, AVG(stop_duration) AS avg_duration FROM police_check GROUP BY violation",
    "Stops during the night more likely to lead to arrests": "SELECT CASE WHEN HOUR(stop_time) BETWEEN 20 AND 23 OR HOUR(stop_time) BETWEEN 0 AND 4 THEN 'Night' ELSE 'Day' END AS time_period, SUM(CASE WHEN s_outcome LIKE '%arrest%' THEN 1 ELSE 0 END)*100.0/COUNT(*) AS arrest_rate FROM police_check GROUP BY time_period LIMIT 5",
    "Violations are most associated with searches or arrests": "SELECT violation, SUM(CASE WHEN search_conducted = TRUE OR s_outcome LIKE '%arrest%' THEN 1 ELSE 0 END) AS count FROM police_check GROUP BY violation ORDER BY count DESC LIMIT 5",
    "Violations are most common among younger drivers (<25)": "SELECT violation, COUNT(*) AS count FROM police_check WHERE driver_age < 25 GROUP BY violation ORDER BY count DESC LIMIT 5",
    "Is there a violation that rarely results in search or arrest": "SELECT violation, SUM(CASE WHEN search_conducted = TRUE OR s_outcome LIKE '%arrest%' THEN 1 ELSE 0 END)*100.0/COUNT(*) AS rate FROM police_check GROUP BY violation ORDER BY rate ASC LIMIT 5",
    "Which countries report the highest rate of drug-related stops": "SELECT country_name, SUM(CASE WHEN drugs_stop = TRUE THEN 1 ELSE 0 END)*100.0/COUNT(*) AS drug_rate FROM police_check GROUP BY country_name ORDER BY drug_rate DESC LIMIT 5",
    "What is the arrest rate by country and violation": "SELECT country_name, violation, SUM(CASE WHEN s_outcome LIKE '%arrest%' THEN 1 ELSE 0 END)*100.0/COUNT(*) AS arrest_rate FROM police_check GROUP BY country_name, violation ORDER BY arrest_rate DESC LIMIT 5",
    "Which country has the most stops with search conducted": "SELECT country_name, COUNT(*) AS search_count FROM police_check WHERE search_conducted = TRUE GROUP BY country_name ORDER BY search_count DESC LIMIT 5"

}


if st.button("Run Query"):
    result = fetch_data(query_map[selected_query])
    if not result.empty:
        st.write(result)
    else:
        st.warning("No results found for the selected query")

## Complex Queries

st.header("🙁 Complex Insights")

selected_query = st.selectbox("select a query to run",[

"Yearly Breakdown of Stops and Arrests by Country",
"Driver Violation Trends Based on Age and Race",
"Time Period Analysis of Stops, Number of Stops by Year,Month, Hour of the Day",
"Violations with High Search and Arrest Rates",
"Driver Demographics by Country",
"Top 5 Violations with Highest Arrest Rates"
])


query_map ={
    "Yearly Breakdown of Stops and Arrests by Country": "SELECT country_name, stop_year, total_stops, total_arrests, ROUND(total_arrests * 100.0 / total_stops, 2) AS arrest_rate_percent, SUM(total_stops) OVER (PARTITION BY country_name ORDER BY stop_year) AS cumulative_stops, SUM(total_arrests) OVER (PARTITION BY country_name ORDER BY stop_year) AS cumulative_arrests FROM (SELECT country_name, YEAR(stop_date) AS stop_year, COUNT(*) AS total_stops, SUM(CASE WHEN s_outcome = 'Arrest' THEN 1 ELSE 0 END) AS total_arrests FROM securecheck_db.police_check GROUP BY country_name, YEAR(stop_date)) AS yearly_stats ORDER BY country_name, stop_year",
    "Driver Violation Trends Based on Age and Race": "SELECT v.driver_race, v.age_group, v.total_violations, COALESCE(s.total_searches, 0) AS total_searches, ROUND(COALESCE(s.total_searches, 0) * 100.0 / v.total_violations, 2) AS search_rate_percentage FROM (SELECT driver_race, CASE WHEN driver_age < 25 THEN '<25' WHEN driver_age BETWEEN 25 AND 34 THEN '25-34' WHEN driver_age BETWEEN 35 AND 44 THEN '35-44' WHEN driver_age BETWEEN 45 AND 54 THEN '45-54' ELSE '55+' END AS age_group, COUNT(*) AS total_violations FROM securecheck_db.police_check GROUP BY driver_race, age_group) v LEFT JOIN (SELECT driver_race, CASE WHEN driver_age < 25 THEN '<25' WHEN driver_age BETWEEN 25 AND 34 THEN '25-34' WHEN driver_age BETWEEN 35 AND 44 THEN '35-44' WHEN driver_age BETWEEN 45 AND 54 THEN '45-54' ELSE '55+' END AS age_group, COUNT(*) AS total_searches FROM securecheck_db.police_check WHERE search_conducted = 'Yes' GROUP BY driver_race, age_group) s ON v.driver_race = s.driver_race AND v.age_group = s.age_group ORDER BY v.driver_race, v.age_group",
    "Time Period Analysis of Stops, Number of Stops by Year,Month, Hour of the Day": "SELECT YEAR(timestamp) AS stop_year, MONTH(timestamp) AS stop_month, HOUR(timestamp) AS stop_hour, COUNT(*) AS number_of_stops FROM securecheck_db.police_check GROUP BY stop_year, stop_month, stop_hour ORDER BY stop_year, stop_month, stop_hour",
    "Violations with High Search and Arrest Rates": "SELECT violation, SUM(search_conducted) AS high_search, SUM(CASE WHEN s_outcome = 'Arrest' THEN 1 ELSE 0 END) AS total_arrests, RANK() OVER (ORDER BY SUM(search_conducted) DESC) AS highsearch_rank, RANK() OVER (ORDER BY SUM(CASE WHEN s_outcome = 'Arrest' THEN 1 ELSE 0 END) DESC) AS arrest_rates FROM securecheck_db.police_check GROUP BY violation",
    "Driver Demographics by Country": "SELECT country_name, driver_gender, driver_race, CASE WHEN driver_age < 20 THEN 'Under 20' WHEN driver_age BETWEEN 20 AND 29 THEN '20-29' WHEN driver_age BETWEEN 30 AND 39 THEN '30-39' WHEN driver_age BETWEEN 40 AND 49 THEN '40-49' WHEN driver_age BETWEEN 50 AND 59 THEN '50-59' WHEN driver_age BETWEEN 60 AND 69 THEN '60-69' ELSE '70+' END AS age_group, COUNT(*) AS total_drivers FROM securecheck_db.police_check GROUP BY country_name, driver_gender, driver_race, age_group ORDER BY country_name, driver_gender, driver_race, age_group",
    "Top 5 Violations with Highest Arrest Rates": "SELECT violation, COUNT(*) AS total_stops, SUM(CASE WHEN s_outcome = 'Arrest' THEN 1 ELSE 0 END) AS total_arrests, (SUM(CASE WHEN s_outcome = 'Arrest' THEN 1 ELSE 0 END) / COUNT(*)) * 100 AS highestarrest_rate FROM securecheck_db.police_check GROUP BY violation ORDER BY highestarrest_rate DESC LIMIT 5"
 }

if st.button("Run Complex Query"):
    result = fetch_data(query_map[selected_query])
    if not result.empty:
        st.write(result)
    else:
        st.warning("No results found for the selected query")

st.markdown("----")
st.markdown("Built with 🖤For Law Enforcement by Securecheck")
st.header("🔎Custom Natural Language Fliter")

st.markdown("Fill in the details below to get a natural language prediction of the stop outcome based on existing data")



st.header("📝Add New Police Logs & predict outcome and violation")

with st.form("log_form"):
    stop_date = st.date_input("Stop Date")
    stop_time = st.time_input("Stop Time")
    country_name = st.text_input("Country Name")
    driver_gender = st.selectbox("Driver Gender", ["male", "female"])
    driver_age = st.number_input("Driver Age", min_value=16, max_value=100, value=27)
    driver_race = st.text_input("Driver Race")
    search_conducted = st.selectbox("Was a Search Conducted?", ["0", "1"])
    search_type = st.text_input("Search Type")
    drugs_stop = st.selectbox("Was it Drug Related?", ["0", "1"])
    stop_duration = st.selectbox("Stop Duration", data['stop_duration'].dropna().unique())
    vehicle_number = st.text_input("Vehicle Number")
    timestamp = pd.Timestamp.now()

    
    submitted = st.form_submit_button("Predict Stop Outcome & Violation")

if submitted:
    # Filter data
    filtered_data = data[
        (data['driver_gender'] == driver_gender) &
        (data['driver_age'] == driver_age) &
        (data['search_conducted'] == int(search_conducted)) &
        (data['stop_duration'] == stop_duration) &
        (data['drugs_stop'] == int(drugs_stop))
    ]

    # Predict stop outcome
    if not filtered_data.empty:
        predicted_outcome = filtered_data['stop_outcome'].mode()[0]
        predicted_violation = filtered_data['violation'].mode()[0]
    else:
        predicted_outcome = "Warning"   # default fallback
        predicted_violation = "Speeding"  # default fallback

    # Natural language summary
    search_text = "A search was conducted" if int(search_conducted) else "No search was conducted"
    drugs_text = "was drug-related" if int(drugs_stop) else "was not drug-related"

    
    st.markdown(f"""
    🔮** Prediction Summary**
                
    - Predicted Violation:{predicted_violation}
    - Predicted S_Outcome:{predicted_outcome}
    - Drug Status: {drugs_stop}


🚔 A **{driver_age}**-year-old **{driver_gender}** driver in **{country_name}**  
was stopped at **{stop_time.strftime('%I:%M %p')}** on **{stop_date}**.  

- {search_text}, and the stop {drugs_stop}.  
- Stop duration: **{stop_duration}**  
- Vehicle Number: **{vehicle_number}**
""")

    
