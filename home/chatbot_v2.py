from functions import *
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from openai import OpenAI
import streamlit as st
import json, os
import traceback
import mysql.connector
from mysql.connector import Error

def send_message(message,thread_from_previous_page=None,assistant_from_previous_page=None):
        
    MODEL="gpt-4o"
    os.environ['OPENAI_API_KEY']='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'
    client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    assistant = client.beta.assistants.create(
    name="Data Analyst for Air India",
    instructions=open("./utils/system-instructions.txt", "r").read(),
    tools=get_tools([
        year_over_year,
        table,
        query,
        create_chart,
        show_chart,
        bar,
        line,
        histogram,
        live_fare_data,
    ]),
    model=MODEL,
    )
    ass_ID=assistant.id
    st.set_page_config(layout="wide")

    def load_model():
        client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        assistant = client.beta.assistants.retrieve(ass_ID)
        thread = client.beta.threads.create()

        return client, assistant, thread


    def load_tokens():
        tokens = 0
        return tokens

    client, assistant, thread = load_model()
    figure = make_subplots(specs=[[{"secondary_y": True}]])
    traces = list()
    secondary_ys = list()
    task_list = list()
    request_tokens = 0

    print(f"\n\033[1mUSER:\033[0m\n{message}\033[1m\n\nSYSTEM:\033[0m")
    usage_data = None
    if thread_from_previous_page != None :
        thread.id = thread_from_previous_page
        assistant.id = assistant_from_previous_page
    try:
        # Check if there are any active runs
        active_runs = client.beta.threads.runs.list(thread_id=thread.id)
        active_run = [run for run in active_runs.data if run.status != "completed"]

        if active_run:
            # Only cancel if the run is expired or still active
            if active_run[0].status == "active" or active_run[0].status not in ["expired", "failed", "cancelled"]:
                client.beta.threads.runs.cancel(thread_id=thread.id, run_id=active_run[0].id)
                print(f"Active run {active_run[0].id} has been cancelled.")
                
                # Optionally, wait a few seconds to ensure the run has been cancelled
                time.sleep(2)
            else:
                print(f"Run {active_run[0].id} is not in an active or expired state, skipping cancellation.")
        else:
            print("No active runs found.")
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message,
        )
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

        output = None
        while run.status != "completed":
            if run.status == "requires_action":
                tool_outputs = list()
                for tool in run.required_action.submit_tool_outputs.tool_calls:
                    args = json.loads(tool.function.arguments)
                    output_str = ""
                    created = False
                    plotted = False
                    shown = False

                    if tool.function.name == "create_chart":
                        output_str = "Chart created."
                        task_list.append("Creating chart...")

                        # global figure, traces
                        figure, traces = create_chart(
                            title=args["title"],
                            x_label=args["x_label"],
                            y_label=args["y_label"],
                            secondary_y_label=args.get("secondary_y_label", None),
                            
                        )

                        created = True
                    elif tool.function.name == "table_and_chat":
                        print("table and chart")
                        result = table_and_chat(
                                sql_query=args["sql_query"],
                                column_names=args["column_names"],
                        )
                    elif tool.function.name == "line":
                        print(
                            f"line(sql_query={args['sql_query']}, x_dim={args['x_dim']}, y_dim={args['y_dim']}, name={args['name']}, secondary_y={args['secondary_y']})"
                        )
                        output_str = "Line added to chart."
                        plotted = True

                        result = line(
                            sql_query=args["sql_query"],
                            x_dim=args["x_dim"],
                            y_dim=args["y_dim"],
                            name=args["name"],
                            secondary_y=args["secondary_y"],
                                thread_from_previous_page = thread_from_previous_page
                            
                        )

                        traces.append(result)
                        secondary_ys.append(args["secondary_y"])
                        task_list.append("Adding line...")
                    elif tool.function.name == "bar":
                        print(
                            f"bar(\n  sql_query={args['sql_query']},\n  x_dim={args['x_dim']},\n  y_dim={args['y_dim']},\n  name={args['name']},\n  secondary_y={args['secondary_y']}\n)"
                        )
                        output_str = "Bar added to chart."
                        plotted = True

                        result = bar(
                            sql_query=args["sql_query"],
                            x_dim=args["x_dim"],
                            y_dim=args["y_dim"],
                            name=args["name"],
                            secondary_y=args["secondary_y"],
                                thread_from_previous_page = thread_from_previous_page

                        )

                        traces.append(result)
                        secondary_ys.append(args["secondary_y"])
                        task_list.append("Adding bar...")
                    elif tool.function.name == "year_over_year":
                        print(
                            f"year_over_year(expression={args['expression']}, name={args['name']}, secondary_y={args['secondary_y']}, frequency={args.get('frequency', 'daily')}, start_date={args.get('start_date', '')}, end_date={args.get('end_date', '')}, filter_criteria={args.get('filter_criteria', '')})"
                        )
                        output_str = "Year comparison lines added to chart."
                        plotted = True

                        result = year_over_year(
                            expression=args["expression"],
                            name=args["name"],
                            secondary_y=args["secondary_y"],
                            frequency=args.get("frequency", "daily"),
                            start_date=args.get("start_date", ""),
                            end_date=args.get("end_date", ""),
                            filter_criteria=args.get("filter_criteria", ""),
                        )

                        traces.append(result[0])
                        traces.append(result[1])
                        secondary_ys.append(args["secondary_y"])
                        task_list.append("Adding line...")
                        task_list.append("Adding line...")
                    elif tool.function.name == "histogram":
                        print(
                            f"histogram({args['sql_query']}, {args['x_dim']}, {args['bins']}, {args['name']}, {args['secondary_y']})"
                        )
                        output_str = "Histogram added to chart."
                        plotted = True

                        result = histogram(
                            sql_query=args["sql_query"],
                            x_dim=args["x_dim"],
                            name=args["name"],
                            bins=args["bins"],
                            secondary_y=args["secondary_y"],
                                thread_from_previous_page = thread_from_previous_page

                        )

                        traces.append(result)
                        secondary_ys.append(args["secondary_y"])
                        task_list.append("Adding histogram...")
                    elif tool.function.name == "show_chart":
                        print(f"show_chart(message={args['message']})")
                        output_str = "Chart shown."
                        shown = True

                        figure.add_traces(traces, secondary_ys=secondary_ys)
                        figure.update_layout(barmode="group")

                        task_list.append("Done!")

                        output = "chart", usage_data, figure
                    elif tool.function.name == "live_fare_data":
                        print(
                            f"live_fare_data(origin={args['origin']}, orig_country={args['orig_country']}, destination={args['destination']}, dest_country={args['dest_country']}, date_mentioned={args['date_mentioned']}, flight_day={args['flight_day']}, flight_month={args['flight_month']}, flight_year={args['flight_year']}, round_trip={args.get('round_trip', False)}, round_trip_length={args.get('round_trip_length', 21)}, display_table={args.get('display_table', True)}, sort_by={args.get('sort_by', 'None')}, ascending={args.get('ascending', True)}, cabin={args.get('cabin', 'Y')}, filter_airline={args.get('filter_airline', '')}, filter_num_stops={args.get('filter_num_stops', -1)}, min_price_range={args.get('min_price_range', -1)}, max_price_range={args.get('max_price_range', -1)})"
                        )
                        output_str = "Fetching live data..."
                        task_list.append("Fetching live data...")

                        if not args["date_mentioned"]:
                            args["flight_day"] = datetime.now().day
                            args["flight_month"] = datetime.now().month
                            args["flight_year"] = datetime.now().year

                        flight_date = datetime(
                            day=int(args["flight_day"]),
                            month=int(args["flight_month"]),
                            year=int(args["flight_year"]),
                            hour=23,
                            minute=59,
                            second=59,
                        )

                        if (
                            args["orig_country"] == "IN"
                            and args["dest_country"] == "IN"
                            and args.get("round_trip", False)
                            or args["orig_country"] == "India"
                            and args["dest_country"] == "India"
                            and args.get("round_trip", False)
                        ):
                            task_list.append("Error...")
                            output_str = "You cannot get round trip live fares for domestic flights."

                        if datetime.now() > flight_date:
                            task_list.append("Need more information...")
                            output_str = f"Incorrect flight date. The provided date must be on or after today, {datetime.now().strftime('%b %-d, %Y')}. Use the current date and user's information."

                        task_list.append("Fetching live data...")

                        result = live_fare_data(
                            origin=args["origin"],
                            orig_country=args["orig_country"],
                            destination=args["destination"],
                            dest_country=args["dest_country"],
                            flight_day=args["flight_day"],
                            flight_month=args["flight_month"],
                            flight_year=args["flight_year"],
                            date_mentioned=args["date_mentioned"],
                            display_table=args.get("display_table", True),
                            sort_by=args.get("sort_by", "None"),
                            ascending=args.get("ascending", True),
                            cabin=args.get("cabin", "Y"),
                            filter_airline=args.get("filter_airline", ""),
                            filter_num_stops=args.get("filter_num_stops", -1),
                            min_price_range=args.get("min_price_range", -1),
                            max_price_range=args.get("max_price_range", -1),
                            round_trip=args.get("round_trip", False),
                            round_trip_length=args.get("round_trip_length", 21),
                        )
                        print('done scrapping', result)
                        if not isinstance(result, list) and result.empty:
                            output_str = "No flights found for the given criteria."

                        if args.get("display_table", True):
                            task_list.append("Creating table...")
                            output = "query", usage_data, result

                        task_list.append("Analyzing data...")
                        output_str = "List the following flights:\n" + "\n".join(result)
                    elif tool.function.name == "table":
                        print(
                            f"table(sql_query={args['sql_query']}, column_names={args['column_names']},thread_from_previous_page)"
                        )
                        output_str = "Table created."
                        task_list.append("Creating table...")
                        output = (
                            "query",
                            usage_data,
                            table(
                                sql_query=args["sql_query"],
                                column_names=args["column_names"],
                                thread_from_previous_page = thread_from_previous_page
                            ),
                           
                        )
                    elif tool.function.name == "query":
                        task_list.append("Querying database...")
                        print(f"query(sql_query={args['sql_query']})")

                        result = query(
                            
                            sql_query=args["sql_query"],
                            thread_from_previous_page= thread_from_previous_page
                        )

                        task_list.append("Analyzing data...")
                        output_str = result.to_string()
                    else:
                        print(f"Unknown function: {tool.function.name}")

                    tool_outputs.append(
                        {
                            "tool_call_id": tool.id,
                            "output": output_str,
                        }
                    )
                if created and not shown:
                    for to in tool_outputs:
                        to["output"] = (
                            "ERROR: You must call every function in parallel, including create_chart and show_chart. Try again."
                        )
                elif created and shown and not plotted:
                    for to in tool_outputs:
                        to["output"] = (
                            "ERROR: You have plotted an empty chart. Try again."
                        )

                try:
                    run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=tool_outputs,
                    )
                    print("Tool outputs submitted successfully.")
                except Exception as e:
                    print("Failed to submit tool outputs:", e)

        if output is None:
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            for message in enumerate(reversed(messages.data)):
                print(message[1].content[0].text.value)
            return "text", usage_data, list(messages)[0].content[0].text.value
        else:
            return output

    except Exception as e:
        traceback.print_exc()
        task_list.append(f"{type(e).__name__}: {str(e)}")
        message = f"{type(e).__name__}: {str(e)}"
        print(f"{type(e).__name__}: {str(e)}")
    return "error", usage_data, "The query is invalid. Please try a different one."

st.title("ChatBot")
st.markdown(
    """<style>
        /* Text */
        .st-bf, .st-al {
            background-color: #383a47;
        }

        /* background */
        .st-au {
            color: #d4d5dd;
        }
        .stMarkdown > div > p > code {
            display: none;
        }
    </style>""",
    unsafe_allow_html=True,
)
if "messages" not in st.session_state:
    st.session_state.messages = []
    tokens = 0
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": "Hello! How can I help you today?",
            "type": "text",
            "tokens": tokens,
            "total_tokens": tokens,
            "TOTAL_TOKENS": 0,
        }
    )

for message in st.session_state.messages[1:]:
    col1, col2 = st.columns([7.5, 1.5])
    with col1:
        with st.chat_message(message["role"]):
            if message["type"] == "chart":
                st.plotly_chart(message["content"])
            elif message["type"] == "query":
                st.dataframe(message["content"], use_container_width=True)
            elif message["type"] == "error":
                st.error(
                    message["content"].replace("\n", "\n  "),
                )
            else:
                st.markdown(
                    message["content"].replace("\n", "<br>").replace("<br>*", "\n*"),
                    unsafe_allow_html=True,
                )
    with col2:
        if message["role"] == "assistant":
            task_list_str = "<br>".join(message["task_list"])
            st.markdown(
                f"<div style='width: fit-content; margin-left: auto; margin-right: 10px; margin-top: 9px; padding: 10px 15px; background-color: #1A1C24; color: #b8b9c7; border-radius: 5px'>{message['tokens']} token{'s' if message['tokens'] != 1 else ''}</div><div style='margin-left: auto; margin-right: 10px; margin-top: 10px; margin-bottom: 10px; color: #b8b9c7; text-align:right'>{task_list_str}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='position: relative'><div style='position: absolute; right: 10px; top: 26px; padding: 10px 15px; background-color: #1A1C24; color: #b8b9c7; border-radius: 5px'>{message['tokens']} token{'s' if message['tokens'] != 1 else ''}</div></div>",
                unsafe_allow_html=True,
            )

if prompt := st.chat_input("How can I help you 👋?"):
    col1, col2 = st.columns([7.5, 1.5])
    tokens = 0
    with col1:
        with st.chat_message("user"):
            st.markdown(prompt)
    with col2:
        st.markdown(
            f"<div style='position: relative'><div style='position: absolute; right: 10px; top: 26px; padding: 10px 15px; background-color: #1A1C24; color: #b8b9c7; border-radius: 5px'>{tokens} token{'s' if tokens != 1 else ''}</div></div>",
            unsafe_allow_html=True,
        )
    if len(st.session_state.messages) > 0:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
                "type": "text",
                "tokens": tokens,
                "total_tokens": tokens + st.session_state.messages[-1]["total_tokens"],
            }
        )
    print('this is prompt', prompt)
    message_type, usage_data, response = send_message(prompt)
    print(message_type, usage_data, response)

    col1, col2 = st.columns([7.5, 1.5])
    with col1:
        with st.chat_message("assistant"):
            if message_type == "chart":
                st.plotly_chart(response)
            elif message_type == "query":
                st.dataframe(response, use_container_width=True)
            elif message_type == "error":
                st.error(
                    response.replace("\n", "<br>").replace("<br>*", "\n*"),
                )
            else:
                st.markdown(
                    response.replace("\n", "<br>").replace("<br>*", "\n*"),
                    unsafe_allow_html=True,
                )
    tokens = 0
    with col2:
        task_list_str = "<br>".join(task_list)
        st.markdown(
            f"<div style='width: fit-content; margin-left: auto; margin-right: 10px; margin-top: 9px; padding: 10px 15px; background-color: #1A1C24; color: #b8b9c7; border-radius: 5px'>{tokens} token{'s' if tokens != 1 else ''}</div><div style='margin-left: auto; margin-right: 10px; margin-top: 10px; margin-bottom: 20px; color: #b8b9c7; text-align:right'>{task_list_str}</div>",
            unsafe_allow_html=True,
        )
    st.session_state.messages[0]["TOTAL_TOKENS"] += request_tokens
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
            "type": message_type,
            "tokens": tokens,
            "total_tokens": 0,  # usage_data.total_token_count,
            "task_list": task_list,
        }
    )
