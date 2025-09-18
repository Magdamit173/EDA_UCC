from flask import Flask, render_template, request
import pandas as pd
import os
from datetime import datetime
import math

app = Flask(__name__, template_folder="templates", static_folder="static", static_url_path="/")

# Load and merge CSVs
csv_path = "csv/"
csv_files = [f for f in os.listdir(csv_path) if f.endswith(".csv")]
df_list = [pd.read_csv(os.path.join(csv_path, f)) for f in csv_files] if csv_files else []
df = pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()

# Chart config
plot_config = {
    "quantity_ordered": "bar",
    "total_sales": "bar",
    "average_order_value": "line",
    "total_order_value": "line"
}

group_options = ["Product", "Date", "Time", "Month", "Week", "Day", "Hour", "City"]
chart_types = ["bar", "line", "scatter", "area", "pie", "doughnut", "radar", "polarArea"]

def preprocess_data(df):
    if df.empty:
        return df
    d = df.copy()
    d["Quantity Ordered"] = pd.to_numeric(d.get("Quantity Ordered"), errors="coerce")
    d["Price Each"] = pd.to_numeric(d.get("Price Each"), errors="coerce")
    d["Sales"] = d["Price Each"] * d["Quantity Ordered"]
    d["Order Value"] = d["Sales"] / d["Quantity Ordered"]
    d["Order Date"] = pd.to_datetime(d.get("Order Date"), format="%m/%d/%y %H:%M", errors="coerce")
    d["Date"] = d["Order Date"].dt.date
    d["Time"] = d["Order Date"].dt.time
    d["Month"] = d["Order Date"].dt.month
    d["Week"] = d["Order Date"].dt.isocalendar().week
    d["Day"] = d["Order Date"].dt.day
    d["Hour"] = d["Order Date"].dt.hour
    if "Purchase Address" in d.columns:
        parts = d["Purchase Address"].astype(str).str.split(",", expand=True)
        d["City"] = parts[1].str.strip() if parts.shape[1] > 1 else None
    else:
        d["City"] = None
    return d

def compute_grouped(df, group_by):
    out = {}
    if df.empty or group_by not in df.columns:
        return {
            "quantity_ordered": {"x": [], "y": []},
            "total_sales": {"x": [], "y": []},
            "average_order_value": {"x": [], "y": []},
            "total_order_value": {"x": [], "y": []}
        }

    q = df.groupby(group_by, as_index=False)["Quantity Ordered"].sum().sort_values(by=group_by)
    out["quantity_ordered"] = {"x": q[group_by].astype(str).tolist(), "y": q["Quantity Ordered"].fillna(0).tolist()}

    s = df.groupby(group_by, as_index=False)["Sales"].sum().sort_values(by=group_by)
    out["total_sales"] = {"x": s[group_by].astype(str).tolist(), "y": s["Sales"].fillna(0).tolist()}

    a = df.groupby(group_by, as_index=False)["Order Value"].mean().sort_values(by=group_by)
    out["average_order_value"] = {"x": a[group_by].astype(str).tolist(), "y": a["Order Value"].fillna(0).tolist()}

    t = df.groupby(group_by, as_index=False)["Order Value"].sum().sort_values(by=group_by)
    out["total_order_value"] = {"x": t[group_by].astype(str).tolist(), "y": t["Order Value"].fillna(0).tolist()}

    return out

@app.route("/", methods=["GET", "POST"])
def index():
    cooked = preprocess_data(df)

    selected_group = request.form.get("grouping_dimension", "Hour")
    product_label = request.form.get("product_label", "").strip()
    current_page = int(request.args.get("page", 1))
    rows_per_page = 20

    data_scope = "All Products"
    scoped_df = cooked
    if product_label:
        if "Product" in cooked.columns:
            scoped_df = cooked[cooked["Product"].astype(str).str.contains(product_label, case=False, na=False)]
            data_scope = product_label if not scoped_df.empty else f"No match for '{product_label}'"
        else:
            scoped_df = cooked.iloc[0:0]
            data_scope = "No Product column"

    chart_data = compute_grouped(scoped_df, selected_group)

    total_rows = len(scoped_df)
    total_pages = math.ceil(total_rows / rows_per_page)
    start = (current_page - 1) * rows_per_page
    end = start + rows_per_page
    paged_df = scoped_df.iloc[start:end]

    table_html = paged_df.to_html(classes="data-table", index=False) if not paged_df.empty else "<p>No data to display.</p>"

    return render_template(
        "index.html",
        current_year=datetime.now().year,
        group_options=group_options,
        selected_group=selected_group,
        product_label=product_label,
        data_scope=data_scope,
        chart_data=chart_data,
        plot_config=plot_config,
        chart_types=chart_types,
        summary_table=table_html,
        total_pages=total_pages,
        current_page=current_page
    )

if __name__ == "__main__":
    app.run(debug=True)
