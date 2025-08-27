from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
from datetime import datetime

app = Flask(__name__, template_folder="templates", static_folder="static", static_url_path="/")

# Load and merge all CSVs
csv_path = "csv/"
csv_files = [f for f in os.listdir(csv_path) if f.endswith(".csv")]
df_list = [pd.read_csv(os.path.join(csv_path, f)) for f in csv_files]
df = pd.concat(df_list, ignore_index=True)
cooked_df = None

plot_config = {
    "quantity_ordered": "bar",
    "total_sales": "bar",
    "average_price": "line",
    "average_order_value": "scatter",
    "total_order_value": "line"
}

group_options = ["Product", "Date", "Time", "Month", "Week", "Day", "Hour", "City"]
ROWS_PER_PAGE = 25

def preprocess_data(df):
    df["Quantity Ordered"] = pd.to_numeric(df["Quantity Ordered"], errors="coerce")
    df["Price Each"] = pd.to_numeric(df["Price Each"], errors="coerce")
    df["Sales"] = df["Price Each"] * df["Quantity Ordered"]
    df["Order Value"] = df["Sales"] / df["Quantity Ordered"]
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%y %H:%M", errors="coerce")
    df["Date"] = df["Order Date"].dt.date
    df["Time"] = df["Order Date"].dt.time
    df["Month"] = df["Order Date"].dt.month
    df["Week"] = df["Order Date"].dt.isocalendar().week
    df["Day"] = df["Order Date"].dt.day
    df["Hour"] = df["Order Date"].dt.hour
    df["City"] = df["Purchase Address"].str.split(",", expand=True)[1]
    return df

def generate_charts(df, group_by, label, plot_config=None):
    charts = {}
    group_key = f"grouped_by_{group_by.lower()}"
    label_key = f"for_{label.lower().replace(' ', '_')}"
    plot_types = plot_config if plot_config else plot_config

    def get_plot_func(metric):
        return {
            "bar": px.bar,
            "line": px.line,
            "scatter": px.scatter
        }.get(plot_types.get(metric, "bar"), px.bar)

    # Quantity Ordered
    quantity = df.groupby(group_by, as_index=False)["Quantity Ordered"].sum()
    fig_quantity = get_plot_func("quantity_ordered")(
        quantity,
        x=group_by,
        y="Quantity Ordered",
        title=f"{label} • Quantity Ordered • Grouped by {group_by}"
    )
    charts[f"quantity_ordered_{group_key}_{label_key}"] = pio.to_html(fig_quantity, full_html=False)

    # Total Sales
    sales = df.groupby(group_by, as_index=False)["Sales"].sum()
    fig_sales = get_plot_func("total_sales")(
        sales,
        x=group_by,
        y="Sales",
        title=f"{label} • Total Sales • Grouped by {group_by}"
    )
    charts[f"total_sales_{group_key}_{label_key}"] = pio.to_html(fig_sales, full_html=False)

    # Average Price (only if grouped by Product)
    if group_by == "Product":
        price = df.groupby(group_by, as_index=False)["Price Each"].mean()
        fig_price = get_plot_func("average_price")(
            price,
            x=group_by,
            y="Price Each",
            title=f"{label} • Average Price • Grouped by {group_by}"
        )
        charts[f"average_price_{group_key}_{label_key}"] = pio.to_html(fig_price, full_html=False)
    else:
        # Average Order Value with Std Dev
        avg = df.groupby(group_by)["Order Value"].agg(["mean", "std"]).reset_index()
        fig_avg = get_plot_func("average_order_value")(
            avg,
            x=group_by,
            y="mean",
            hover_data={"std": True},
            title=f"{label} • Average Order Value ± Std Dev • Grouped by {group_by}"
        )
        charts[f"average_order_value_{group_key}_{label_key}"] = pio.to_html(fig_avg, full_html=False)

        # Total Order Value
        total = df.groupby(group_by, as_index=False)["Order Value"].sum()
        fig_total = get_plot_func("total_order_value")(
            total,
            x=group_by,
            y="Order Value",
            title=f"{label} • Total Order Value • Grouped by {group_by}"
        )
        charts[f"total_order_value_{group_key}_{label_key}"] = pio.to_html(fig_total, full_html=False)

    return charts

def paginate_dataframe(df, page, rows_per_page=ROWS_PER_PAGE):
    start = (page - 1) * rows_per_page
    end = start + rows_per_page
    total_pages = (len(df) + rows_per_page - 1) // rows_per_page
    return df.iloc[start:end], total_pages

@app.route("/", methods=["GET", "POST"])
def index():
    global cooked_df
    cooked_df = preprocess_data(df)

    selected_group = request.form.get("grouping_dimension", "Hour")
    product_label = request.form.get("product_label", "").strip()
    page = int(request.args.get("page", 1))

    # Overview Charts: always All Products
    overview_charts = generate_charts(cooked_df, selected_group, "All Products", plot_config)

    # Filtered Charts: only if product label is provided
    filtered_charts = {}
    if product_label:
        filtered_df = cooked_df[cooked_df["Product"].str.contains(product_label, case=False, na=False)]
        if not filtered_df.empty:
            filtered_charts = generate_charts(filtered_df, selected_group, product_label, plot_config)

    # Paginated Table
    paginated_df, total_pages = paginate_dataframe(cooked_df, page)
    table_html = paginated_df.to_html(classes="data-table", index=False)

    return render_template("index.html",
        chart_htmls=filtered_charts,
        overview_htmls=overview_charts,
        summary_table=table_html,
        group_options=group_options,
        selected_group=selected_group,
        current_year=datetime.now().year,
        current_page=page,
        total_pages=total_pages
    )

if __name__ == "__main__":
    app.run(debug=True)
