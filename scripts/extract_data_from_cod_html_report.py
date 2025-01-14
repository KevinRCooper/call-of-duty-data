import os
from bs4 import BeautifulSoup
import pandas as pd

def load_html_from_data_dir(file_name, root_dir="data"):
    # Loads an HTML file from the specified root directory.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(script_dir, root_dir, file_name)
    if not os.path.exists(html_path):
        raise FileNotFoundError(f"HTML file '{file_name}' not found in '{root_dir}' directory.")
    with open(html_path, "r", encoding="utf-8") as file:
        return BeautifulSoup(file, "html.parser")

def extract_table_from_html(soup, target_h2_text):
    # Extracts the table following the <h2> with the specified text.
    target_h2 = soup.find("h2", string=target_h2_text)
    if not target_h2:
        print(f"<h2> with text '{target_h2_text}' not found.")
        return None

    next_sibling = target_h2.find_next_sibling()
    if next_sibling and next_sibling.name == "table":
        rows = next_sibling.find_all("tr")
        table_data = [
            [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
            for row in rows
        ]
        return table_data
    else:
        print(f"No table found immediately after <h2> with text '{target_h2_text}'.")
        return None

def save_table_to_csv(table_data, output_file):
    # Saves the extracted table data to a CSV file.
    if not table_data:
        print("No table data to export.")
        return

    # Convert the table data to a DataFrame
    df = pd.DataFrame(table_data[1:], columns=table_data[0])  # First row as header
    df.to_csv(output_file, index=False)
    print(f"The table has been exported to {output_file}")

def main():
    # Configuration
    html_file_name = "Account.html"
    target_h2_text = "Multiplayer Match Data (reverse chronological)"
    output_csv_name = "multiplayer_match_data.csv"

    try:
        # Load the HTML content
        soup = load_html_from_data_dir(html_file_name)

        # Extract the table data
        table_data = extract_table_from_html(soup, target_h2_text)

        # Save the table data to a CSV file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_csv_path = os.path.join(script_dir, output_csv_name)
        save_table_to_csv(table_data, output_csv_path)

    except FileNotFoundError as e:
        print(e)

if __name__ == "__main__":
    main()
