# Supplemental Data Visualizations for Chapman Reference

This project visualizes Chapman University Libraries reference transaction data in several ways supplementary to the visualization capabilities of LibAnswers analytics. Upload a .CSV file exported from LibAnswers analytics' "Export Transactions" option to use the notebook.

All cleaning, filtering, and visualization code is contained in the [Marimo notebook](https://marimo.io/), a next-gen pure Python notebook, which can be run as an interactive web app to allow for convenient data exploration. See https://andgreenman.github.io/libanswers_viz/ for most recent webapp build.

-----
Considerations for non-Chapman reuse: several column filters are hardcoded, and may break if your data does not have those columns. For example, if you don't use READ levels in your reference logging, several of the visualizations will be pointless, but you can easily edit these parts of the code out if desired. I do intend on minimizing hardcoding as much as possible to support reuse by anyone using LibAnswers analytics in future updates.
