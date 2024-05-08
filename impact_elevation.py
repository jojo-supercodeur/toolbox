import pandas as pd
import plotly.express as px
import streamlit as st

def display_altitude_and_gradient(course_data):
    """
    Function to display the altitude and gradient charts of a selected course.

    Arguments:
    - course_data: DataFrame containing 'Distance', 'Altitude', and 'Gradient' columns.
    """

    # Create an altitude chart
    fig_altitude = px.line(
        course_data,
        x="Distance",
        y="Altitude",
        title="Course Altitude Profile",
        labels={"Distance": "Distance (km)", "Altitude": "Altitude (m)"},
    )
    fig_altitude.update_layout(paper_bgcolor="white", plot_bgcolor="white")
    fig_altitude.update_traces(line_color="blue")

    # Create a gradient chart
    fig_gradient = px.line(
        course_data,
        x="Distance",
        y="Gradient",
        title="Course Gradient Profile",
        labels={"Distance": "Distance (km)", "Gradient": "Gradient (%)"},
    )
    fig_gradient.update_layout(paper_bgcolor="white", plot_bgcolor="white")
    fig_gradient.update_traces(line_color="red")

    # Display the charts in Streamlit
    st.plotly_chart(fig_altitude)
    st.plotly_chart(fig_gradient)

# Example simulated data
data = {
    "Distance": range(0, 100),
    "Altitude": [100 + i*10 for i in range(100)],
    "Gradient": [5 - i*0.05 for i in range(100)]
}

# Convert the data to a DataFrame
course_data = pd.DataFrame(data)

# Call the function to display the charts
st.title("Course Altitude and Gradient Profile")
display_altitude_and_gradient(course_data)
