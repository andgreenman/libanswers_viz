import marimo

__generated_with = "0.13.7"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import pandas as pd
    import io
    import altair as alt
    from datetime import datetime
    return alt, datetime, io, pd


@app.cell
def _(mo):
    mo.md(
        r"""
    # LibAnswers Analytics Visualizer

    This Marimo notebook run as a webapp automatically adjusts heatmaps, READ level comparison charts, and more based on an uploaded LibAnswers analytics CSV file. Filters in LibAnswers analytics are replicated here, with the additional funcationality of filtering by a range of READ levels. Additionally, the smallest unit of time is a week, not a month.
    """
    )
    return


@app.cell
def _(mo):
    # creating a UI element - file upload

    file_upload = mo.ui.file(
        filetypes=[".csv"],
        label="Upload a CSV file",
        kind="button",
        multiple=False,
    )
    return (file_upload,)


@app.cell
def _(file_upload):
    file_upload
    return


@app.cell
def _(file_upload, io, pd):
    def process_file():
        if file_upload.value:
            # Get the file upload results
            file_obj = file_upload.value[0]

            # Access the content directly
            content = file_obj.contents

            # Convert to pandas DataFrame
            df = pd.read_csv(
                io.BytesIO(content)
            )  # for Excel I'd use pd.read_excel(io.BytesIO(content)) etc etc
            df = df.drop(columns=["Ticket #", "Chat #"]).fillna("None")
            df.insert(
                column="Date_time", loc=1, value=(df["Date"] + " " + df["Time"])
            )
            df["Date_time"] = pd.to_datetime(df["Date_time"])

            return df
        else:
            return "No file uploaded yet."
    return (process_file,)


@app.cell
def _(process_file):
    df = process_file()
    return (df,)


@app.cell
def _(df, mo):
    # creating simpler UI elements

    date_range = mo.ui.date_range.from_series(df["Date_time"], label=None)

    read_slider = mo.ui.range_slider(start=0, stop=6)

    read_break = mo.ui.number(start=0, stop=6, value=2)
    return date_range, read_break, read_slider


@app.cell
def _(df, mo):
    # creating metadata multiselect UI elements

    location_options = df["Location"].to_list()
    entered_by_options = df["Entered By"].to_list()
    patron_affiliation_options = df["Patron Affiliation"].to_list()
    patron_status_options = df["Patron Status"].to_list()
    communication_options = df["Communication"].to_list()
    question_type_options = df["Question Type"].to_list()
    duration_options = df["Duration"].to_list()

    # I *can't* create these repetitive widgets with a fuction, as they need to be declared by name in the form

    location = mo.ui.multiselect.from_series(
        df["Location"], value=location_options
    )
    entered_by = mo.ui.multiselect.from_series(
        df["Entered By"], value=entered_by_options
    )
    patron_affiliation = mo.ui.multiselect.from_series(
        df["Patron Affiliation"], value=patron_affiliation_options
    )
    patron_status = mo.ui.multiselect.from_series(
        df["Patron Status"], value=patron_status_options
    )
    communication = mo.ui.multiselect.from_series(
        df["Communication"], value=communication_options
    )
    question_type = mo.ui.multiselect.from_series(
        df["Question Type"], value=question_type_options
    )
    duration = mo.ui.multiselect.from_series(
        df["Duration"], value=duration_options
    )
    return (
        communication,
        duration,
        entered_by,
        location,
        patron_affiliation,
        patron_status,
        question_type,
    )


@app.cell
def _(
    communication,
    date_range,
    duration,
    entered_by,
    location,
    mo,
    patron_affiliation,
    patron_status,
    question_type,
    read_break,
    read_slider,
):
    # form replaces vstacks for calling UI elements to solve an issue where changing values out-of-order would reset other UI selections - now all values are passed at once

    form = (
        (
            mo.md(
                """
        The table and visualizations will update each time the "Submit" button is clicked.

        Choose a date range by selecting and typing over a component, or by using the calendar select.<br>{date_range} <br>
        Drag the ends to select a READ scale range to include.<br>{read_slider} <br>
        Choose a number to split up high vs low READ levels.<br>{read_break} <br>
        <br>
        {location} <br>
        {entered_by} <br>
        {patron_affiliation} <br>
        {communication} <br>
        {question_type} <br>
        {duration}
        """
            )
        )
        .batch(
            date_range=date_range,
            read_slider=read_slider,
            read_break=read_break,
            location=location,
            entered_by=entered_by,
            patron_affiliation=patron_affiliation,
            patron_status=patron_status,
            communication=communication,
            question_type=question_type,
            duration=duration,
        )
        .form()
    )
    return (form,)


@app.cell
def _(form):
    form
    return


@app.cell
def _(mo):
    mo.md(r"""# Date/Time stats""")
    return


@app.cell
def _(datetime, form):
    start_date = form.value["date_range"][0]
    end_date = form.value["date_range"][1]

    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    date_string = (
        f"{start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}"
    )

    read_min = form.value["read_slider"][0]
    read_max = form.value["read_slider"][1]

    read_break_level = form.value["read_break"]
    return (
        date_string,
        end_datetime,
        read_break_level,
        read_max,
        read_min,
        start_datetime,
    )


@app.cell
def _(
    df,
    end_datetime,
    form,
    read_break_level,
    read_max,
    read_min,
    start_datetime,
):
    # main filtering logic responds to form entries

    filtered_df = df.copy()

    filtered_df = filtered_df[
        (df["Date_time"] >= start_datetime) & (df["Date_time"] <= end_datetime)
    ]

    filtered_df = filtered_df[(df["READ"] >= read_min) & (df["READ"] <= read_max)]

    filtered_df["READ group"] = filtered_df["READ"].apply(
        lambda x: f"Low (0-{read_break_level - 1})"
        if x < read_break_level
        else f"High ({read_break_level} -6)"
    )

    # filtering from the multiselects could be a function, but it's easy to keep everything in this cell

    filtered_df = filtered_df[filtered_df["Location"].isin(form.value["location"])]
    filtered_df = filtered_df[
        filtered_df["Entered By"].isin(form.value["entered_by"])
    ]
    filtered_df = filtered_df[
        filtered_df["Patron Affiliation"].isin(form.value["patron_affiliation"])
    ]
    filtered_df = filtered_df[
        filtered_df["Patron Status"].isin(form.value["patron_status"])
    ]
    filtered_df = filtered_df[
        filtered_df["Communication"].isin(form.value["communication"])
    ]
    filtered_df = filtered_df[
        filtered_df["Question Type"].isin(form.value["question_type"])
    ]
    filtered_df = filtered_df[filtered_df["Duration"].isin(form.value["duration"])]

    # data transformations for plotting - not sure how many are still in use?

    date_time_pos = list(filtered_df.columns).index("Date_time")

    filtered_df.insert(
        date_time_pos + 1, "month", filtered_df["Date_time"].dt.month_name()
    )
    filtered_df.insert(date_time_pos + 2, "day", filtered_df["Date_time"].dt.day)
    filtered_df.insert(date_time_pos + 3, "hour", filtered_df["Date_time"].dt.hour)
    filtered_df.insert(
        date_time_pos + 4, "day_of_week", filtered_df["Date_time"].dt.day_name()
    )
    filtered_df.insert(
        date_time_pos + 5,
        "yearweek",
        filtered_df["Date_time"].dt.to_period("W").apply(lambda r: r.start_time),
    )
    return (filtered_df,)


@app.cell
def _(filtered_df, mo):
    display_df = filtered_df.drop(
        columns=["Date_time", "Id", "yearweek", "hour", "Date"]
    )

    mo.ui.table(display_df, page_size=15)
    return


@app.cell
def _(mo):
    # creating a UI element - show/hide LibAnswers plots

    switch = mo.ui.switch()
    return (switch,)


@app.cell
def _():
    days_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    months_order = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    return days_order, months_order


@app.cell
def _(filtered_df, months_order, pd):
    daily_counts = (
        filtered_df.groupby("day_of_week").size().reset_index(name="count")
    )

    # this transform is more complex because groupby("month") doesn't account for years
    monthly_counts = (
        filtered_df.set_index("Date_time")
        .to_period("M")
        .groupby("Date_time")
        .size()
        .reset_index(name="count")
    )

    # the groupby makes it not a dt object and thus ruins the plot unless I re-dt it
    monthly_counts["Date_time"] = monthly_counts["Date_time"].dt.to_timestamp()

    calendar_data = (
        filtered_df.groupby(["Date", "month", "day", "day_of_week"])
        .size()
        .reset_index(name="count")
    )

    calendar_data["Date"] = pd.to_datetime(calendar_data["Date"])

    calendar_data["month"] = pd.Categorical(
        calendar_data["month"], categories=months_order, ordered=True
    )
    return calendar_data, daily_counts, monthly_counts


@app.cell
def _(alt, daily_counts, date_string, days_order):
    day_bars = (
        (
            alt.Chart(daily_counts)
            .mark_bar()
            .encode(
                x=alt.X(
                    "day_of_week:O",
                    title=None,
                    sort=days_order,
                    axis=alt.Axis(labelAngle=0),
                ),
                y=alt.Y("count", title="Transactions"),
            )
        )
        .properties(
            title=alt.Title("Daily sums", subtitle=date_string, anchor="start"),
            width=700,
            height=300,
        )
        .configure_axis(labelFontSize=15, titleFontSize=18)
        .configure_title(fontSize=25, subtitleFontSize=18)
    )
    return (day_bars,)


@app.cell
def _(alt, date_string, monthly_counts):
    month_bars = (
        (
            alt.Chart(monthly_counts)
            .mark_bar()
            .encode(
                x=alt.X(
                    "yearmonth(Date_time):O",
                    title=None,
                    axis=alt.Axis(labelAngle=0),
                ),
                y=alt.Y("count", title="Transactions"),
            )
        )
        .properties(
            title=alt.Title("Monthly sums", subtitle=date_string, anchor="start"),
            width=700,
            height=300,
        )
        .configure_axis(labelFontSize=15, titleFontSize=18)
        .configure_title(fontSize=25, subtitleFontSize=18)
    )
    return (month_bars,)


@app.cell
def _(day_bars, mo, month_bars, switch):
    mo.vstack(
        [
            mo.md(
                "Toggle to add plots replicating the Monthly and Daily breakdowns in LibAnswers analytics."
            ),
            switch,
            *(
                [mo.ui.altair_chart(day_bars), mo.ui.altair_chart(month_bars)]
                if switch.value
                else ["Not displaying LibAnswers-style charts."]
            ),
        ]
    )
    return


@app.cell
def _(alt, calendar_data, date_string, mo):
    weekly_totals = (
        alt.Chart(calendar_data)
        .mark_line()
        .encode(
            x=alt.X("yearweek(Date):O", title=None),
            y=alt.Y("sum(count):Q", title="Transactions"),
            tooltip=[
                alt.Tooltip("yearweek(Date):O", title="Week"),
                alt.Tooltip("sum(count):Q", title="Total"),
            ],
        )
        .properties(
            title=alt.Title("Weekly sums", subtitle=date_string, anchor="start"),
            width=700,
            height=300,
        )
        .configure_axis(labelFontSize=15, titleFontSize=18)
        .configure_title(fontSize=25, subtitleFontSize=18)
    )

    mo.ui.altair_chart(weekly_totals)

    # I'd love to do the interactive plot + table thing here but mo.vstack([chart, mo.ui.table(chart.value)]) doesn't work if I use Altair transforms in the plot, which I'm doing throughout this notebook
    return


@app.cell
def _(mo):
    mo.md(r"""# Heatmaps""")
    return


@app.cell
def _(days_order, filtered_df, months_order, pd):
    # filter for day-of-week/hour heatmap
    heatmap_days_data = (
        filtered_df.groupby(["day_of_week", "hour"])
        .size()
        .reset_index(name="count")
    )

    heatmap_days_data["day_of_week"] = pd.Categorical(
        heatmap_days_data["day_of_week"], categories=days_order, ordered=True
    )

    heatmap_days_data = heatmap_days_data.sort_values("day_of_week")

    # filter for week/day-of-week heatmap
    heatmap_calendar_data = (
        filtered_df.groupby(["month", "day"]).size().reset_index(name="count")
    )

    heatmap_calendar_data["month"] = pd.Categorical(
        heatmap_calendar_data["month"], categories=months_order, ordered=True
    )
    heatmap_calendar_data = heatmap_calendar_data.sort_values(["month", "day"])
    return (heatmap_days_data,)


@app.cell
def _(alt, date_string, days_order, heatmap_days_data, mo):
    heatmap_days = (
        (
            alt.Chart(heatmap_days_data)
            .mark_rect()
            .encode(
                x=alt.X(
                    "day_of_week:O",
                    title=None,
                    sort=days_order,
                    axis=alt.Axis(labelAngle=0),
                ),  # if I don't declare the sort it starts on Friday?
                # the labelAngle=0 keeps the labels horizontal, use -45 for tilt, etc
                y=alt.Y("hour:O", title="Hour"),
                color=alt.Color("count:Q", scale=alt.Scale(scheme="viridis")),
                tooltip=["day_of_week", "hour", "count"],
            )
            .properties(
                title=alt.Title(
                    "Daily/Hourly Distribution Heatmap",
                    subtitle=date_string,
                    anchor="start",
                ),
                width=700,
                height=400,
                spacing=5,
            )
            .configure_scale(
                bandPaddingInner=0.05
            )  # whitespace between cells for readability
        )
        .configure_axis(labelFontSize=15, titleFontSize=18)
        .configure_title(fontSize=25, subtitleFontSize=18)
        .configure_legend(titleFontSize=18, labelFontSize=15)
    )

    mo.ui.altair_chart(heatmap_days)
    return


@app.cell
def _(alt, calendar_data, date_string, days_order, mo):
    heatmap_calendar = (
        (
            alt.Chart(calendar_data)
            .mark_rect()
            .encode(
                x=alt.X(
                    "day_of_week:O",
                    title=None,
                    sort=days_order,
                    axis=alt.Axis(labelAngle=0),
                ),
                y=alt.Y(
                    "yearweek(Date):O",
                    title=None,
                ),
                color=alt.Color(
                    "count:Q",
                    scale=alt.Scale(scheme="viridis"),
                    legend=alt.Legend(title="Count"),
                ),
                tooltip=["Date:T", "count:Q"],
            )
            .properties(
                title=alt.Title(
                    "Weekly/Daily Distribution Heatmap",
                    subtitle=date_string,
                    anchor="start",
                ),
                width=700,
                height=400,
                spacing=5,
            )
            .configure_scale(
                bandPaddingInner=0.05
            )  # whitespace between cells for readability
        )
        .configure_axis(labelFontSize=15, titleFontSize=18)
        .configure_title(fontSize=25, subtitleFontSize=18)
        .configure_legend(titleFontSize=18, labelFontSize=15)
    )

    mo.ui.altair_chart(heatmap_calendar)
    return


@app.cell
def _(mo):
    mo.md(r"""# READ level trends""")
    return


@app.cell
def _(filtered_df, pd):
    # simple filter for READ-by-question bar plot
    read_questions = (
        filtered_df.groupby(["Question Type", "READ group"])
        .size()
        .reset_index(name="count")
    )

    # get unique weeks and READ_group combinations
    all_weeks = filtered_df["yearweek"].drop_duplicates()
    all_read_groups = filtered_df["READ group"].drop_duplicates()
    full_index = pd.MultiIndex.from_product(
        [all_weeks, all_read_groups], names=["yearweek", "READ group"]
    )
    full_df = pd.DataFrame(index=full_index).reset_index()

    # get weekly counts
    counts_df = (
        filtered_df.groupby(["yearweek", "READ group"])
        .size()
        .reset_index(name="count")
    )

    # merge togther and fill missing values with zeroes
    merged_df = pd.merge(
        full_df, counts_df, on=["yearweek", "READ group"], how="left"
    ).fillna(0)
    merged_df["count"] = merged_df["count"].astype(int)
    # this df just holds weeks and their READ counts to do acurate line plots where zero counts aren't skipped by the line
    return all_weeks, merged_df, read_questions


@app.cell
def _(alt, date_string, filtered_df, mo):
    read_compare_bar = (
        alt.Chart(filtered_df)
        .mark_bar()
        .encode(
            x=alt.X("yearweek(Date_time):T", title="Week"),
            y=alt.Y("count():Q", title="Number of Transactions"),
            color=alt.Color("READ group:N", title="READ Level Group"),
            tooltip=[
                alt.Tooltip("yearweek(Date_time):T", title="Week"),
                alt.Tooltip("READ group:N", title="READ Group"),
                alt.Tooltip("count():Q", title="Count"),
            ],
        )
        .properties(
            title=alt.Title(
                "Weekly READ Level Trends", subtitle=date_string, anchor="start"
            ),
            width=700,
            height=400,
            spacing=5,
        )
        .encode(
            x=alt.X("yearweek(Date_time):T", title="Week"),
            xOffset="READ group:N",  # somehow this is what I need for side-by-side grouping
        )
        .configure_axis(labelFontSize=15, titleFontSize=18)
        .configure_title(fontSize=25, subtitleFontSize=18)
        .configure_legend(
            titleFontSize=18,
            labelFontSize=15,
            strokeColor="gray",
            fillColor="#EEEEEE",
            padding=10,
            cornerRadius=10,
        )
    )

    # add , orient="top-right" to configure.legend to move it inside the plot

    mo.ui.altair_chart(read_compare_bar)
    return


@app.cell
def _(alt, date_string, merged_df, mo):
    read_compare_line = (
        alt.Chart(merged_df)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "yearweek(yearweek):T", title="Week"
            ),  # wrapping in Altair's yearweek for label consistency
            y=alt.Y(
                "count:Q",
                title="Number of Transactions",  # , scale=alt.Scale(domain=[0, 140]) if topping out
            ),
            color=alt.Color("READ group:N", title="READ Level Group"),
            tooltip=[
                alt.Tooltip("yearweek:T", title="Week"),
                alt.Tooltip("READ group:N", title="READ Group"),
                alt.Tooltip("count:Q", title="Count"),
            ],
        )
        .properties(
            title=alt.Title(
                "Weekly READ Level Trends", subtitle=date_string, anchor="start"
            ),
            width=700,
            height=400,
            spacing=5,
        )
        .configure_axis(labelFontSize=15, titleFontSize=18)
        .configure_title(fontSize=25, subtitleFontSize=18)
        .configure_legend(
            titleFontSize=18,
            labelFontSize=15,
            strokeColor="gray",
            fillColor="#EEEEEE",
            padding=10,
            cornerRadius=10,
        )
    )

    # add , orient="top-right" to configure.legend to move it inside the plot

    mo.ui.altair_chart(read_compare_line)
    return


@app.cell
def _(alt, date_string, mo, read_questions):
    read_questiontype_bar = (
        alt.Chart(read_questions)
        .mark_bar()
        .encode(
            y=alt.Y("Question Type:N", title=None),
            x=alt.X("count:Q", title="Number of Questions"),
            color=alt.Color("READ group:N", title="READ Level Group"),
            yOffset="READ group:N",  # this creates side-by-side bars like xOffset did for the Weekly READ level plot
            tooltip=[
                alt.Tooltip("Question Type:N", title="Question Type"),
                alt.Tooltip("READ group:N", title="READ Level"),
                alt.Tooltip("count:Q", title="Count"),
            ],
        )
        .properties(
            title=alt.Title(
                "READ levels by question type",
                subtitle=date_string,
                anchor="start",
            ),
            width=700,
            height=400,
            spacing=5,
        )
        .configure_axis(labelFontSize=15, titleFontSize=18)
        .configure_title(fontSize=25, subtitleFontSize=18)
        .configure_legend(
            titleFontSize=18,
            labelFontSize=15,
            strokeColor="gray",
            fillColor="#EEEEEE",
            padding=10,
            cornerRadius=10,
        )
    )

    # add , orient="top-right" to configure.legend to move it inside the plot

    mo.ui.altair_chart(read_questiontype_bar)
    return


@app.cell
def _(mo):
    mo.md(r"""# Location""")
    return


@app.cell
def _(all_weeks, filtered_df, pd):
    # simple filter for READ-by-location bar graph
    location_read_data = (
        filtered_df.groupby(["Location", "READ group"])
        .size()
        .reset_index(name="count")
    )

    # reusing how I did this for READ-by-week
    # get unique locations (reusing all_weeks from earlier)
    all_locations = filtered_df["Location"].drop_duplicates()

    location_index = pd.MultiIndex.from_product(
        [all_weeks, all_locations],
        names=["yearweek", "Location"],
    )
    location_full_df = pd.DataFrame(index=location_index).reset_index()

    # get weekly counts by location
    location_week_data = (
        filtered_df.groupby(["yearweek", "Location"])
        .size()
        .reset_index(name="count")
    )

    # merge together and fill missing values with zeroes
    location_df = pd.merge(
        location_full_df,
        location_week_data,
        on=["yearweek", "Location"],
        how="left",
    ).fillna(0)
    location_df["count"] = location_df["count"].astype(int)
    return location_df, location_read_data


@app.cell
def _(alt, date_string, location_read_data, mo):
    location_read = (
        (
            alt.Chart(location_read_data)
            .mark_bar()
            .encode(
                y=alt.Y("Location:N", title=None),
                x=alt.X("count:Q"),
                color=alt.Color("READ group:N", title="READ Level Group"),
                yOffset="READ group:N",  # this creates side-by-side bars like xOffset did for the Weekly READ level plot
                tooltip=[
                    alt.Tooltip("Location:N", title="Location"),
                    alt.Tooltip("READ group:N", title="READ Level"),
                    alt.Tooltip("count:Q", title="Count"),
                ],
            )
            .properties(
                title=alt.Title(
                    "READ levels by question location",
                    subtitle=date_string,
                    anchor="start",
                ),
                width=700,
                height=400,
                spacing=5,
            )
            .configure_axis(labelFontSize=15, titleFontSize=18)
            .configure_title(fontSize=25, subtitleFontSize=18)
            .configure_legend(
                titleFontSize=18,
                labelFontSize=15,
                strokeColor="gray",
                fillColor="#EEEEEE",
                padding=10,
                cornerRadius=10,
            )
        )
        .properties(
            title=alt.Title(
                "READ Level counts by Location",
                subtitle=date_string,
                anchor="start",
            ),
            width=700,
            height=400,
            spacing=5,
        )
        .configure_axis(labelFontSize=15, titleFontSize=18)
        .configure_title(fontSize=25, subtitleFontSize=18)
        .configure_legend(
            titleFontSize=18,
            labelFontSize=15,
            strokeColor="gray",
            fillColor="#EEEEEE",
            padding=10,
            cornerRadius=10,
        )
    )

    # add , orient="top-right" to configure.legend to move it inside the plot

    mo.ui.altair_chart(location_read)
    return


@app.cell
def _(alt, date_string, location_df, mo):
    location_compare_line = (
        (
            alt.Chart(location_df)
            .mark_line(point=True)
            .encode(
                x=alt.X(
                    "yearweek(yearweek):T", title="Week"
                ),  # wrapping in Altair's yearweek for label consistency
                y=alt.Y(
                    "count:Q",
                    title="Number of Transactions",
                ),
                color=alt.Color("Location:N"),
            )
        )
        .properties(
            title=alt.Title(
                "Weekly Location Trends", subtitle=date_string, anchor="start"
            ),
            width=700,
            height=400,
            spacing=5,
        )
        .configure_axis(labelFontSize=15, titleFontSize=18)
        .configure_title(fontSize=25, subtitleFontSize=18)
        .configure_legend(
            titleFontSize=18,
            labelFontSize=15,
            strokeColor="gray",
            fillColor="#EEEEEE",
            padding=10,
            cornerRadius=10,
        )
    )

    mo.ui.altair_chart(location_compare_line)
    return


if __name__ == "__main__":
    app.run()
