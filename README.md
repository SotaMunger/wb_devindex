# World_Bank_Development_Index

This repository encompasses all code and data sets used to build a full stack data visualization application entitled 'Economics of Food Insecurity' exploring economic conditions that create food insecurity for the residents of low-income countries.  The application features a PostgreSQL back-end and a Plotly Dash front-end.  Data sets were downloaded from the World Development Index and Global Economic Prospect data collections of the World Bank Databank then programmatically cleaned, organized, and loaded into PostGreSQL relational tables using Python code.  The dashboard consists of four pages - a landing page explaining the purpose of the dashboard and three data exploration pages, each presenting one economic aspect that creates food insecurity for low income countries - inflation, dependence on food imports, and lack of prospects for economic growth.

See the live dashboard at https://wb-devindex.onrender.com.

Elements included in this repository include:

1. /ETL/load_data.py - Code written to extract data from the World Bank Databank .zip files, separate large .csv data files into constituent files each pertaining to only one economic indicator (i.e. inflation, food imports, etc.), and load data into PostGreSQL tables via a psycopg2 library-mediated database connection.

Each table contained the following columns:

    1. country_code (primary key) - The three letter iso3 country abbreviation
    2. income_group - The income group to which the country belongs: Low income, Upper middle income, Lower middle income, High income
    3. country_name - The name of the country
    4. series_name - The World Bank title for the economic indicator covered by the table
    5. yr1960 to yr2021 - Indicator data for the country in that given year (the dashboard explores only data starting from the year 2000 because records were sparse for some indicators before that year) 

2. /assets/ - Files that encoded the appearance and style of the dashboard (style.css) and the images found in the dashboard (globe1.png, income-map.png)

3. /components/navbar.py - File that encoded the functionality of the navigation bar found atop each page of the dashboard

4. /data/ - Data files that were downloaded from the World Bank Databank and processed through the ETL/load_data.py code.  All files were downloaded from the World Bank Databank between Feb 7, 2023 and April 2, 2023 and reflect the state of the data held in the databank between those dates

5. /pages/ - Code written to encode the layout, database query commands, and functioning of the interactive components and graphs found on each of the pages linked in the navigation bar

6. app.py - File that creates the Dash app framework under which the dashboard functions

7. index.py - File that encodes the navigational layout of the dashboard

8. requirements - Description of the library versions in the conda environment in which the app was built