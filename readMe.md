📊 Data Visualization Dashboard

A modular dashboard built for Week 7 Data Analysis Project, visualizing sales trends and product metrics using datasets from Kaggle. Currently in development—expect chart upgrades, tooltip logic, and seasonal annotations soon.

---

📁 Project Status

⚠️ Work in progress  
🔍 Data sourced from Kaggle  
🧪 Chart logic refactored for responsiveness  
📦 Histogram removed due to Chart.js limitations

---

📌 Features

- Dynamic chart rendering (bar, line, pie, etc.)  
- Grouping by Product, Date, Hour, City, and more  
- Searchable, paginated data table  
- Chart type selector per metric  
- Preprocessed metrics: Quantity Ordered, Total Sales, Average Order Value, Total Order Value

---

📚 Datasets Used

- 💻 https://www.kaggle.com/datasets/juanmerinobermejo/laptops-price-dataset  
- 🛒 https://www.kaggle.com/datasets/sinjoysaha/sales-analysis-dataset

---

🛠️ Development Notes

To avoid data rate limit errors in Jupyter Lab:

jupyter lab --ServerApp.iopub_data_rate_limit=10000000
