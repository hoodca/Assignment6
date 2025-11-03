# Assignment6
Features
Parses CSV files without using csv or other external libraries.

Dynamically maps CSV headers to attributes using a custom State class.

Handles inconsistent row lengths and performs basic type inference (int, float, string).

Groups data by state code and allows interactive exploration.

Offers a simple command-line interface to view data per state or list all available states.

File Structure
State class: Maps CSV headers to object attributes and converts string values to appropriate types.

parse_csv_line(line): Custom CSV parser that handles quoted fields and escaped quotes.

Notes
The script assumes the CSV has a header row.

It attempts to convert numeric strings to int or float, and leaves certain fields as strings (e.g., state, fips, hash).

It avoids using any external libraries for maximum portability.
