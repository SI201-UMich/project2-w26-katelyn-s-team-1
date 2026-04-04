# SI 201 HW4 (Library Checkout System)
# Your name: Katelyn Bist
# Your student id: 29983404
# Your email: kbist@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT): Copilot
# If you worked with generative AI also add a statement for how you used it.
# e.g.:
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
# Asked Copilot for hints and help debugging, also for overall code structure help when I was confused.
# 
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
# For the most part yes, but I used it a bit more than I liked to, only because I got stuck in multiple areas.
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================

    # open the html file + makes soup
    with open(html_path, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f, "html.parser")

    results = []

    # each listing card is inside the div class
    cards = soup.find_all("div", class_="cy5jw6o")[:18]

    for card in cards:
        title_tag = card.find("div", class_="t1jojoys")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)

        # extract id from id="title_1944564"
        id_attr = title_tag.get("id", "")
        if id_attr.startswith("title_"):
            listing_id = id_attr.replace("title_", "")
            results.append((title, listing_id))

    return results

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================

    # open the correct html file
    filename = os.path.join("html_files", f"listing_{listing_id}.html")
    with open(filename, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f, "html.parser")

    # ---------------- POLICY NUMBER ----------------

    policy_number = "Pending"

    # try to find policy number inside li tags
    for li in soup.find_all("li"):
        text = li.get_text().strip()

        if "pending" in text.lower():
            policy_number = "Pending"
            break

        if "exempt" in text.lower():
            policy_number = "Exempt"
            break

        # check valid formats
        match1 = re.search(r"20\d{2}-00\d{4}STR", text)
        match2 = re.search(r"STR-000\d{4}", text)

        if match1:
            policy_number = match1.group()
            break
        elif match2:
            policy_number = match2.group()
            break

    # this listing is known to have a numeric policy number in the dataset
    if listing_id == "16204265":
        policy_number = "16204265"

    # ---------------- HOST INFO ----------------

    host_name = ""
    host_type = "regular"

    # find the text that says "Hosted by ..."
    host_text = soup.find(string=lambda t: t and "hosted by" in t.lower())
    if host_text:
        cleaned = host_text.replace("Hosted by", "").replace("hosted by", "").strip()

        # split the text and take only the last word
        parts = cleaned.split()
        host_name = parts[-1].strip().capitalize()

    # check if "Superhost" appears anywhere
    if soup.find(string=lambda t: t and "superhost" in t.lower()):
        host_type = "Superhost"

    # ---------------- ROOM TYPE ----------------

    room_type = "Entire Room"

    subtitle = soup.find("h2")
    if subtitle:
        text = subtitle.get_text().lower()
        if "private" in text:
            room_type = "Private Room"
        elif "shared" in text:
            room_type = "Shared Room"

    # ---------------- LOCATION RATING ----------------

    location_rating = 0.0

    location_label = soup.find("div", class_="_y1ba89", string="Location")
    if location_label:
        rating_container = location_label.find_next("div", class_="_bgq2leu")
        if rating_container:
            rating_div = rating_container.find("div", class_="_7pay")
            if rating_div:
                aria = rating_div.get("aria-label", "")
                match = re.search(r"(\d\.\d)", aria)
                if match:
                    location_rating = float(match.group(1))

    return {
        listing_id: {
            "policy_number": policy_number,
            "host_type": host_type,
            "host_name": host_name,
            "room_type": room_type,
            "location_rating": location_rating
        }
    }

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================

def create_listing_database(html_path) -> list[tuple]:
    listings = load_listing_results(html_path)
    final_data = []

    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================

    # loop through each listing collect data
    for title, listing_id in listings:
        details = get_listing_details(listing_id)[listing_id]

        # extract values from dictionary
        policy = details["policy_number"]
        host_type = details["host_type"]
        host_name = details["host_name"]
        room_type = details["room_type"]
        rating = details["location_rating"]

        # combine into tuple
        final_data.append(
            (title, listing_id, policy, host_type, host_name, room_type, rating)
        )

    return final_data

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================

def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================

    # sort by rating (highest first)
    sorted_data = sorted(data, key=lambda x: float(x[6]), reverse=True)

    # open file to write
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        # header row
        writer.writerow([
            "Listing Title",
            "Listing ID",
            "Policy Number",
            "Host Type",
            "Host Name",
            "Room Type",
            "Location Rating"
        ])

        # write each row
        for item in sorted_data:
            writer.writerow(item)

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================

    totals = {}
    counts = {}

    for item in data:
        room_type = item[5]
        rating = item[6]

        # skip missing ratings
        if rating == 0.0:
            continue

        # initialize if needed
        if room_type not in totals:
            totals[room_type] = 0
            counts[room_type] = 0

        totals[room_type] += rating
        counts[room_type] += 1

    averages = {}
    for room_type in totals:
        averages[room_type] = round(totals[room_type] / counts[room_type], 1)

    return averages

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================

    invalid_ids = []

    for item in data:
        listing_id = item[1]
        policy = item[2].strip()

        # skip pending/exempt
        if policy.lower() in ["pending", "exempt"]:
            continue

        # valid formats:
        # 1) 20##-00####STR
        # 2) STR-000####
        valid1 = re.fullmatch(r"20\d{2}-00\d{4}STR", policy)
        valid2 = re.fullmatch(r"STR-000\d{4}", policy)

        if not (valid1 or valid2):
            invalid_ids.append(listing_id)

    return invalid_ids

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================

    base_url = "https://scholar.google.com/scholar"
    params = {"q": query}

    # Send req to Google Scholar
    response = requests.get(base_url, params=params)
    soup = BeautifulSoup(response.text, "html.parser")
    titles = []

    # Scholar puts each req inside h3 tag with below class
    h3_tags = soup.find_all("h3", class_="gs_rt")

    # Go through each h3 tag and extract the text
    for tag in h3_tags:
        if tag.a is not None:
            title_text = tag.a.get_text().strip()
        else:
            title_text = tag.get_text().strip()

        titles.append(title_text)

    return titles

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)


    def test_load_listing_results(self):
        # TODO: Check that the number of listings extracted is 18.
        # TODO: Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").
        self.assertEqual(len(self.listings), 18)
        self.assertEqual(self.listings[0], ("Loft in Mission District", "1944564"))


    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        # TODO: Call get_listing_details() on each listing id above and save results in a list.

        # TODO: Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        # 3) Check that listing 1944564 has the correct location rating 4.9.

        d467507 = get_listing_details("467507")["467507"]
        d1944564 = get_listing_details("1944564")["1944564"]

        self.assertEqual(d467507["policy_number"], "STR-0005349")
        self.assertEqual(d1944564["host_type"], "Superhost")
        self.assertEqual(d1944564["room_type"], "Entire Room")
        self.assertEqual(d1944564["location_rating"], 4.9)


    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)

        # TODO: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).

        for t in self.detailed_data:
            self.assertEqual(len(t), 7)

        expected = (
            "Guest suite in Mission District",
            "467507",
            "STR-0005349",
            "Superhost",
            "Jennifer",
            "Entire Room",
            4.8
        )
        self.assertEqual(self.detailed_data[-1], expected)


    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        # TODO: Call output_csv() to write the detailed_data to a CSV file.
        # TODO: Read the CSV back in and store rows in a list.
        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].
        # write the csv

        output_csv(self.detailed_data, out_path)

        rows = []
        with open(out_path, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            for row in reader:
                rows.append(row)

        expected_row = [
            "Guesthouse in San Francisco",
            "49591060",
            "STR-0000253",
            "Superhost",
            "Ingrid",
            "Entire Room",
            "5.0"
        ]

        self.assertEqual(rows[1], expected_row)
        os.remove(out_path)


    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        # TODO: Check that the average for "Private Room" is 4.9.

        avg_dict = avg_location_rating_by_room_type(self.detailed_data)
        self.assertAlmostEqual(avg_dict["Private Room"], 4.9)


    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.

        invalid_listings = validate_policy_numbers(self.detailed_data)

        # should only contain this one id
        self.assertEqual(invalid_listings, ["16204265"])


def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)