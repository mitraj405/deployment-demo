from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import sqlite3
from plotly.subplots import make_subplots

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import sqlitecloud
import time
import inspect
import mysql.connector
from mysql.connector import Error

def create_chart(title: str, x_label: str, y_label: str, secondary_y_label: str = None):
    """Creates a new chart. You can only call create_chart once, at the start of a query.

    NOTE:
    - You must call this function to begin a response with charts.
    - Prefer to use the same type of chart in a single response unless explicitly told to create a different one.
    - You can only create on chart at a time.

    Args:
        title (str): The title of the chart.
        x_label (str): The label for the x-axis.
        y_label (str): The label for the y-axis.
        secondary_y_label (str): The label for the secondary y-axis. (only for dual-axis charts) (Default: None)
    """
    show_grid = secondary_y_label is None

    figure = make_subplots(specs=[[{"secondary_y": True}]])
    figure.update_layout(title_text=title)

    figure.update_xaxes(title_text=x_label)

    figure.update_yaxes(title_text=y_label, secondary_y=False, showgrid=show_grid)
    figure.update_yaxes(
        title_text=secondary_y_label, secondary_y=True, showgrid=show_grid
    )

    # figure.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    traces = list()

    return figure, traces


def show_chart(message: str):
    """Displays the chart on the screen. It is called at the end of a query.

    NOTE: You cannot call this function more than once per query.

    Args:
        message (str): The message to be displayed with the chart.
    """

    return None


def year_over_year(
    expression: str,
    name: str,
    secondary_y: bool,
    frequency: str = "daily",
    start_date: str = "",
    end_date: str = "",
    filter_criteria: str = "",
):
    """Adds two lines for current year and previous year respectively to pre-existing chart. This function is only used for year over year comparisons. If you haven't been asked to compare, use the line function.

    Note:
    - This function adds two lines for current year and previous year. Therefore, you do not need to filter this function by period reference.

    Args:
        expression (str): Give an expression using column names from the database.
        name (str): The name of the trace.
        secondary_y (bool): Whether the y-axis is secondary.
        frequency (str): The frequency of the data. (Choose between daily and monthly) (Default: "daily")
        start_date (str): The start date of the data, chooses chosen date for current year and previous year. (only enter this if user asks for a range) (Default: "")
        end_date (str): The end date of the data, chooses chosen date for current year and previous year. (only enter this if user asks for a range) (Default: "")
        filter_criteria (str): The criteria to filter the data by (filter criteria cannot contain period reference). MUST BE SQL CRITERIA FORMAT. (Default: "")
    """

    print(
        f"year_over_year(\n  {expression=},\n  {frequency=},\n  {name=},\n  {secondary_y=},\n  {start_date=},\n  {end_date=}\n, {filter_criteria=}\n)"
    )

    crit = "flight_date"
    group_by = "flight_date"
    format_str = "%Y-%m-%d"
    if frequency == "monthly":
        crit = "strftime('%Y-%m', flight_date) AS month"
        group_by = "month"
        format_str = "%Y-%m"

    py_flight_date = ""
    cy_flight_date = ""
    if start_date != "" and end_date != "":
        cy_flight_date = f"AND flight_date BETWEEN '{start_date}' AND '{end_date}'"
        print(
            f"SELECT {crit}, {expression} FROM Booked_KPIs WHERE period_reference = 'CY' {cy_flight_date} GROUP BY {group_by} ORDER BY {group_by}"
        )

        if frequency == "daily":
            py_start_date = datetime.strptime(start_date, "%Y-%m-%d") - timedelta(
                weeks=52, days=1
            )
            py_end_date = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(weeks=52)
            py_flight_date = f"AND flight_date BETWEEN '{py_start_date.strftime('%Y-%m-%d')}' AND '{py_end_date.strftime('%Y-%m-%d')}'"
        else:
            py_start_date = (
                str(int(start_date.split("-")[0]) - 1)
                + "-"
                + start_date.split("-")[1]
                + "-"
                + start_date.split("-")[2]
            )
            py_end_date = (
                str(int(end_date.split("-")[0]) - 1)
                + "-"
                + end_date.split("-")[1]
                + "-"
                + end_date.split("-")[2]
            )
            py_flight_date = (
                f"AND flight_date BETWEEN '{py_start_date}' AND '{py_end_date}'"
            )

    if filter_criteria != "":
        filter_criteria = f"AND {filter_criteria}"
    cy = query(
        f"SELECT {crit}, {expression} FROM Booked_KPIs WHERE period_reference = 'CY' {cy_flight_date} {filter_criteria} GROUP BY {group_by} ORDER BY {group_by}"
    )
    cy[0] = pd.to_datetime(cy[0], format=format_str)
    py = query(
        f"SELECT {crit}, {expression} FROM Booked_KPIs WHERE period_reference = 'PY' {py_flight_date} {filter_criteria} GROUP BY {group_by} ORDER BY {group_by}"
    )
    py[0] = pd.to_datetime(py[0], format=format_str) + pd.Timedelta(weeks=52)

    cy_trace = go.Scatter(
        x=cy[0],
        y=cy[1],
        name=f"{name} - Current Year",
        mode="lines",
    )

    py_trace = go.Scatter(
        x=py[0],
        y=py[1],
        name=f"{name} - Previous Year",
        mode="lines",
    )

    return [cy_trace, py_trace]


def table(sql_query: str, column_names: str):
    """Queries the database and displays the output to the user in tabular form.

    Args:
        sql_query (str): The SQL query to be executed. Always use Common Table Expressions (CTE) whenever possible.
        column_names (list): The column names for each column. Must be proper words/phrases.
    """
    print(column_names)
    if isinstance(column_names, str):
        if column_names == "":
            column_names = None
        else:
            column_names = (
                column_names.replace("[", "")
                .replace("]", "")
                .replace("'", "")
                .replace('"', "")
                .replace("\\", "")
            )
            if ", " in column_names:
                column_names = column_names.split(", ")
            else:
                column_names = column_names.split(",")
            for i in range(len(column_names)):
                column_names[i] = column_names[i].replace("_", " ").title()
    else:
        for i in range(len(column_names)):
            column_names[i] = (
                column_names[i]
                .replace("_", " ")
                .title()
                .replace("[", "")
                .replace("]", "")
                .replace("'", "")
                .replace('"', "")
                .replace("\\", "")
            )
    # db_credentials = request.session['db_credentials']

    sql_query = sql_query.replace("\\n", "\n").replace("\\", "")
    connection = mysql.connector.connect(
        host="sql7.freemysqlhosting.net",
        user="sql7748185",
        password="bbtqvgiWqw",
        database="sql7748185"
    )
    cursor = connection.cursor()
    query = sql_query
    # query = "WITH top_cart AS ( SELECT * FROM cart ) SELECT * FROM top_cart LIMIT 5;"
    cursor.execute(query)
    result = cursor.fetchall()

    # sqliteConnection = sqlitecloud.connect("sqlitecloud://ctqws9lknk.sqlite.cloud:8860/db.sqlite?apikey=1TBBTbRsWbzMtiEoz7MA2VQ7b0TL6JD2ZJysGFXiXpI")
    # cursor = sqliteConnection.cursor
    # cursor.execute(sql_query)
    print(result)

    record = pd.DataFrame(result, columns=column_names)

    cursor.close()
    connection.close()

    # cursor.close()
    # sqliteConnection.close()
    print(record)
    return record


def query(sql_query: str):
    """Queries the database and will provide you with access to database records. Which you can use to respond to the user in natural language.

    If the user doesn't ask you to analyze the data, just use the table function to display it.

    Args:
        sql_query (str): The SQL query to be executed. Always use Common Table Expressions (CTE) whenever possible.
    """
    if "strftime('%m'" in sql_query:
        sql_query = sql_query.replace("strftime('%m'", "strftime('%Y-%m'")

    print(sql_query)

    sql_query = sql_query.replace("\\n", "\n").replace("\\", "")
    sqliteConnection = sqlitecloud.connect("sqlitecloud://ctqws9lknk.sqlite.cloud:8860/db.sqlite?apikey=1TBBTbRsWbzMtiEoz7MA2VQ7b0TL6JD2ZJysGFXiXpI")
    cursor = sqliteConnection.cursor()

    cursor.execute(sql_query)
    record = pd.DataFrame(cursor.fetchall())
    cursor.close()
    sqliteConnection.close()

    return record


def bar(sql_query: str, x_dim: int, y_dim: int, name: str, secondary_y: bool):
    """Adds a bar trace to chart.

    Args:
        sql_query (str): The SQL query to be executed. Always use Common Table Expressions (CTE) whenever possible.
        x_dim (int): The dimension of the x-axis from sql query. (zero-indexed)
        y_dim (int): The dimension of the y-axis from sql query. (zero-indexed)
        name (str): The name of the trace.
        secondary_y (bool): Whether the y-axis is secondary.
    """
    # grouped_dim (int): The dimension across which the chart is grouped. (if not grouped return -1)
    print(
        f"bar(\n  {sql_query=},\n  {x_dim=},\n  {y_dim=},\n {name=},\n {secondary_y=}\n)"
    )

    result = query(sql_query)

    # if grouped_dim == -1:
    #     grouped_dim = None

    trace = go.Bar(
        x=result[int(x_dim)],
        y=result[int(y_dim)],
        name=name,
    )

    return trace


def line(
    sql_query: str,
    x_dim: int,
    y_dim: int,
    name: str,
    secondary_y: bool,
):
    """Adds a line trace to pre-existing chart.

    Args:
        sql_query (str): The SQL query to be executed. Always use Common Table Expressions (CTE) whenever possible.
        x_dim (int): The dimension of the x-axis from sql query. (zero-indexed)
        y_dim (int): The dimension of the y-axis from sql query. (zero-indexed)
        name (str): The name of the trace.
        secondary_y (bool): Whether the y-axis is secondary.
    """

    print(
        f"line(\n  {sql_query=},\n  {x_dim=},\n  {y_dim=},\n {name=},\n {secondary_y=}\n)"
    )

    result = query(sql_query)

    trace = go.Scatter(
        x=result[int(x_dim)],
        y=result[int(y_dim)],
        mode="lines",
        name=name,
    )

    return trace


def histogram(sql_query: str, x_dim: int, bins: int, name: str, secondary_y: bool):
    """Adds a histogram trace to pre-existing chart.

    Args:
        sql_query (str): The SQL query to be executed. Always use Common Table Expressions (CTE) whenever possible.
        x_dim (int): The dimension of the x-axis from sql query.
        bins (int): The number of bins in the histogram.
        name (str): The name of the trace.
        secondary_y (bool): Whether the y-axis is secondary.
    """

    print(
        f"histogram(\n  {sql_query=},\n  {x_dim=},\n  {bins=},\n  {name=},\n  {secondary_y=}\n)"
    )

    result = query(sql_query)

    trace = go.Histogram(x=result[int(x_dim)], nbinsx=int(bins), name=name)

    return trace

def live_fare_data(
    origin: str,
    orig_country: str,
    destination: str,
    dest_country: str,
    flight_day: int,
    flight_month: int,
    flight_year: int,
    date_mentioned: bool,
    display_table: bool = True,
    sort_by: str = "None",
    ascending: bool = True,
    cabin: str = "Y",
    filter_airline: str = "",
    filter_num_stops: int = -1,
    min_price_range: int = -1,
    max_price_range: int = -1,
    round_trip: bool = False,
    round_trip_length: int = 21,
):
    """Queries the Yatra API and displays live flight fare data to the user. Use this when the user asks for live flight fare data.

    Fare is in INR.

    Args:
        origin (str): The origin airport code.
        orig_country (str): The origin country code.
        destination (str): The destination airport code.
        dest_country (str): The destination country code.
        flight_day (int): The day of the flight. (-1 if user doesn't explicitly mention date)
        flight_month (int): The month of the flight. (-1 if user doesn't explicitly mention date)
        flight_year (int): The year of the flight. (-1 if user doesn't explicitly mention date)
        date_mentioned (bool): Whether the date was explicitly mentioned by the user.
        display_table (bool): Whether to display the data in a table. Only choose false if you need a specific row of data. (Default: True)
        sort_by (str): The column to sort the data by. (Options: "None", "Airline", "Flight No.", "Departure Time", "Stops", "Duration", "Price") (Default: "None")
        ascending (bool): Whether to sort the data in ascending order. (Default: True)
        cabin (str): The cabin class. (Options: "Y", "C", "F", "R") (Default: "Y")
        filter_airline (str): The airline to filter the data by. (Default: "")
        filter_num_stops (int): The number of stops to filter the data by. (Default: -1)
        min_price_range (int): The minimum price to filter the data by. (Default: -1)
        max_price_range (int): The maximum price to filter the data by. (Default: -1)
        round_trip (bool): Whether the flight is a round trip. Round trip is only available for international flights. (Default: False)
        round_trip_length (int): The number of days before the return flight. (Default: 21 days)
    """

    if not cabin:
        cabin = "Y"
    if not sort_by:
        sort_by = "Price"
    if not ascending:
        ascending = True
    if not filter_airline:
        filter_airline = ""
    if not filter_num_stops:
        filter_num_stops = -1
    if not min_price_range:
        min_price_range = -1
    if not max_price_range:
        max_price_range = -1
    if not round_trip:
        round_trip = False
    if round_trip_length == None:
        round_trip_length = 21

    str_flight_day = str(int(flight_day))
    if len(str_flight_day) == 1:
        str_flight_day = "0" + str_flight_day

    str_flight_month = str(int(flight_month))
    if len(str_flight_month) == 1:
        str_flight_month = "0" + str_flight_month

    flight_date = f"{str_flight_day}%2F{str_flight_month}%2F{int(flight_year)}"

    redir_cabin = (
        "Economy"
        if cabin == "Y"
        else "Business" if cabin == "C" else "First" if cabin == "F" else "Special"
    )
    redir = "int2"
    if orig_country == dest_country:
        redir = "dom2"
    if not round_trip:
        target_url = f"https://flight.yatra.com/air-search-ui/{redir}/trigger?type=O&viewName=normal&flexi=0&noOfSegments=1&origin={origin}&originCountry={orig_country}&destination={destination}&destinationCountry={dest_country}&flight_depart_date={flight_date}&ADT=1&CHD=0&INF=0&class={redir_cabin}&source=fresco-home&unqvaldesktop=1024084899884"
    else:
        if sort_by == "Stops":
            sort_by = "Duration"
        if date_mentioned:
            delta = datetime(
                year=int(flight_year), month=int(flight_month), day=int(flight_day)
            ) + timedelta(days=int(round_trip_length))
        else:
            delta = datetime.now() + timedelta(days=int(round_trip_length))
        if round_trip_length != 0:
            arrival_date = (
                f"{str(int(delta.day))}%2F{str(int(delta.month))}%2F{int(delta.year)}"
            )
        else:
            arrival_date = flight_date
        target_url = f"https://flight.yatra.com/air-search-ui/{redir}/trigger?ADT=1&CHD=0&INF=0&arrivalDate={arrival_date}&class={redir_cabin}&destination={destination}&destinationCountry={dest_country}&flexi=0&flight_depart_date={flight_date}&hb=0&noOfSegments=2&origin={origin}&originCountry={orig_country}&type=R&unique=846209747794&version=1.1&viewName=normal"
    print(f"{target_url}\n")
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Firefox(options=options)

    try_again = True
    if redir == 'int2':
        check_load_element = ".flight-loader.ovf-hidden.ng-hide"
    else:
        check_load_element = ".flight-loader.ovf-hidden.hide"
    while try_again:
        # print('here', check_load_element)
        driver.get(target_url)
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, check_load_element)
                )
            )
            try_again = False
        except TimeoutException:
            print("Timeout occurred. Retrying...")
            continue
    # Sort    
    if redir == 'int2':
        sort_element = "li.cursor-pointer.pr.white-bg.i-b.tipsy"
    else:
        sort_element = "li.fs-11.no-wrap.i-b.v-aligm-m" 
    try:
        buttons = driver.find_elements(
            By.CSS_SELECTOR, sort_element 
        )
        # print(buttons[0], 't')
        (
            buttons[1].click()
            if sort_by == "Duration"
            else buttons[2].click() if sort_by != "Price" else buttons[0].click()
        )
    except:
        return []

    counter = 0
    while counter < 100:
        counter += 1
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.01)

    if redir == "int2":
        elems = driver.find_elements(By.CLASS_NAME, "result-set")[0].find_elements(
            By.CLASS_NAME, "flightItem"
        )
    else:
        elems = driver.find_elements(By.CLASS_NAME, "flightItem")

    results = list()
    results_len = 0
    for elem in elems:
        soup = BeautifulSoup(elem.get_attribute("innerHTML"), "html.parser")

        if "banner" in elem.get_attribute("class"):
            continue

        if round_trip:
            airline = soup.find("div", class_="airline-name").findChild().text
            time_str = (
                soup.find("p", class_="time").text.replace(" ", "").split("\n")[-1]
            )
            ret_time_str = (
                soup.find_all("p", class_="time")[2]
                .text.replace(" ", "")
                .split("\n")[-1]
            )

            num_stops = (
                soup.find("div", class_="stop-cont")
                .find("div", class_="fs-11")
                .findChild()
                .text.strip()
            )
            ret_num_stops = (
                soup.find_all("div", class_="stop-cont")[1]
                .find("div", class_="fs-11")
                .findChild()
                .text.strip()
            )

            duration_str = (
                soup.find("div", class_="stop-cont")
                .find("p", class_="fs-12")
                .text.replace("h ", ":")
                .replace("m", "")
            )
            ret_duration_str = (
                soup.find_all("div", class_="stop-cont")[1]
                .find("p", class_="fs-12")
                .text.replace("h ", ":")
                .replace("m", "")
            )
            duration = f"{int(duration_str.split(':')[0]):02}h {int(duration_str.split(':')[1]):02}m"
            ret_duration = f"{int(ret_duration_str.split(':')[0]):02}h {int(ret_duration_str.split(':')[1]):02}m"

            price = (
                soup.find("div", class_="booking-section")
                .find("div", class_="fs-20")
                .text.strip("\n")
                .split("\n")[0]
                .strip()
            )
        elif soup.find("div", class_="time") == None:
            airline = soup.find("div", class_="airline-name").findChild().text
            if (
                soup.find("div", class_="airline-name").find("p", class_="fl-no")
                != None
            ):
                fl_no = (
                    soup.find("div", class_="airline-name")
                    .find("p", class_="fl-no")
                    .findChild()
                    .text
                )
            else:
                fl_no = "None"

            if soup.find("div", class_="depart-details") != None:
                time_str = (
                    soup.find("div", class_="depart-details").findChildren()[1].text
                )
            else:
                time_str = (
                    soup.find("p", class_="time").text.replace(" ", "").split("\n")[-1]
                )

            if soup.find("div", class_="stops-details") != None:
                num_stops = (
                    soup.find("div", class_="stops-details")
                    .find("div", class_="fs-12")
                    .text.strip()
                )
                duration_str = (
                    soup.find("div", class_="stops-details")
                    .findChild()
                    .text.replace("h ", ":")
                    .replace("m", "")
                )
                duration = f"{int(duration_str.split(':')[0]):02}h {int(duration_str.split(':')[1]):02}m"
            else:
                num_stops = (
                    soup.find("div", class_="stop-cont")
                    .find("div", class_="fs-11")
                    .findChild()
                    .text
                )
                duration_str = (
                    soup.find("div", class_="stop-cont")
                    .find("p", class_="fs-12")
                    .text.replace("h ", ":")
                    .replace("m", "")
                )
                duration = f"{int(duration_str.split(':')[0]):02}h {int(duration_str.split(':')[1]):02}m"

            if soup.find("p", class_="fare-price") != None:
                price = (
                    soup.find("p", class_="fare-price")
                    .get_text("\\\\\\\\")
                    .split("\\\\\\\\")[0]
                    .strip()
                )
            else:
                price = (
                    soup.find("div", class_="booking-section")
                    .find("div", class_="fs-20")
                    .text.strip("\n")
                    .split("\n")[0]
                    .strip()
                )
        else:
            arr = (
                soup.find("div", class_="time")
                .findChild()
                .get_text("\\\\\\\\")
                .split("\\\\\\\\")
            )
            airline = arr[1]
            fl_no = arr[2]
            time_str = arr[0]

            price = (
                soup.find("div", class_="fare-summary-tooltip")
                .get_text("\\\\\\\\")
                .split("\\\\\\\\")[0]
                .strip()
            )

            # STOP DETAILS
            stops = soup.find("div", class_="stop-det")
            num_stops = (
                soup.find("div", class_="stop-det")
                .find("div", class_="font-lightgrey")
                .findChild()
                .text.strip()
            )
            duration_str = (
                soup.find("div", class_="stop-det")
                .find("p", {"autom": "durationLabel"})
                .text.replace("h ", ":")
                .replace("m", "")
            )
            duration = f"{int(duration_str.split(':')[0]):02}h {int(duration_str.split(':')[1]):02}m"

        if round_trip:
            results.append(
                f"{airline} | {time_str}/{ret_time_str} | {num_stops}/{ret_num_stops} | {duration}/{ret_duration} | {price}"
            )
            results_len = 5
        elif fl_no != "None":
            results.append(
                f"{airline} | {fl_no} | {time_str} | {num_stops} | {duration} | {price}"
            )
            results_len = 6
        else:
            results.append(
                f"{airline} | {time_str} | {num_stops} | {duration} | {price}"
            )
            results_len = 5

    if not display_table:
        return results

    results_df = list()
    redir_cabin_str = redir_cabin if redir_cabin != "Special" else "Premium Economy"
    for result in results:
        results_df.append(result.split(" | ") + [redir_cabin_str])

    columns = (
        ["Airline", "Flight No.", "Time", "Stops", "Duration", "Price", "Cabin"]
        if results_len == 6
        else ["Airline", "Time", "Stops", "Duration", "Price", "Cabin"]
    )

    display_columns = (
        ["Airline", "Flight No.", "Cabin", "Time", "Stops", "Duration", "Price"]
        if results_len == 6
        else ["Airline", "Cabin", "Time", "Stops", "Duration", "Price"]
    )
    df = pd.DataFrame(results_df, columns=columns)
    df = df[display_columns]
    df["Price"] = "₹" + df["Price"]

    df["Stops"] = df["Stops"].str.replace("Non Stop", "0 Stops")
    if filter_num_stops != -1:
        df = df.loc[df["Stops"].str[0] == str(int(filter_num_stops))]
    df["Price int"] = df["Price"].str.replace("₹", "").str.replace(",", "").astype(int)
    if min_price_range != -1:
        df = df.loc[df["Price int"] >= min_price_range]
    if max_price_range != -1:
        df = df.loc[df["Price int"] <= max_price_range]
    if not round_trip:
        sort_by = sort_by if sort_by != "Price" and sort_by != "None" else "Price int"
        df = df.sort_values(by=[sort_by, "Price int"], ascending=ascending)
    elif sort_by == "Airline":
        df = df.sort_values(by=["Airline", "Price int"], ascending=ascending)
    df["Stops"] = df["Stops"].str.replace("0 Stops", "Non Stop")
    df = df.drop(columns=["Price int"])
    if filter_airline != "":
        df = df.loc[
            df["Airline"].str.lower().str.replace(" ", "")
            == (filter_airline).lower().replace(" ", "")
        ]
    df = df.reset_index().drop(columns=["index"])
    return df


def get_tools(functions):
    tools = []
    for function in functions:
        docstring = function.__doc__

        properties = dict()
        required = list()

        backslash = "\n"
        for parameter in inspect.signature(function).parameters:
            param = inspect.signature(function).parameters[parameter]
            property_name = param.name
            property_type = param.annotation.__name__

            default_value = param.default

            x = f"{property_name} ({property_type}): "
            property_description = docstring[
                docstring.find(x)
                + len(x) : docstring.find(x)
                + docstring[docstring.find(x) + len(x) :].find(backslash)
                + len(x)
            ]

            if default_value == inspect._empty:
                required.append(property_name)

            if property_type == "str":
                property_type = "string"
            elif property_type == "int":
                property_type = "integer"
            elif property_type == "bool":
                property_type = "boolean"
            else:
                raise Exception(f"Unknown type: {property_type}")

            properties[property_name] = {
                "type": property_type,
                "description": property_description,
            }

        docstring = docstring.split("Args:")[0]

        while docstring[-1] == "\n" or docstring[-1] == " ":
            docstring = docstring[:-1]

        tools.append(
            {
                "type": "function",
                "function": {
                    "name": function.__name__,
                    "description": docstring,
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                },
            }
        )
    return tools
