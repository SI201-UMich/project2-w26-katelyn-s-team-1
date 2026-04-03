# SI 201 HW4 (Library Checkout System)
# Your name:
# Your student id:
# Your email:
# Who or what you worked with on this homework (including generative AI like ChatGPT):
# If you worked with generative AI also add a statement for how you used it.
# e.g.:
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
#
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
#
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
    results = []

    # Opens the html file
    with open(html_path, "r", encoding="utf-8-sig") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # Find all the 'a' tags
    all_links = soup.find_all("a")

    for link_tag in all_links:
        href = link_tag.get("href")

        # Gets the id number
        if href is not None and "/rooms/" in href:
            listing_id = href.replace("/rooms/", "")
            listing_id = listing_id.split("?")[0]
            listing_id = listing_id.strip("/")

            # Gets the title text
            title = link_tag.get_text().strip()

            # Only add if the id is numbers
            if listing_id.isdigit():
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

    # Opens correct listing file
    filename = "listing_" + listing_id + ".html"
    with open(filename, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Finds the policy number
    policy_number = "Pending"
    policy_label = soup.find(string=lambda text: text and "license number" in text.lower())
    if policy_label is not None:
        next_tag = policy_label.find_next()
        if next_tag is not None:
            raw_policy_text = next_tag.get_text().strip()
            # check what type of policy number it is
            if "pending" in raw_policy_text.lower():
                policy_number = "Pending"
            elif "exempt" in raw_policy_text.lower():
                policy_number = "Exempt"
            else:
                policy_number = raw_policy_text

    # Finds the host name and host type
    host_name = ""
    host_type = "regular"

    host_label = soup.find(string=lambda text: text and "hosted by" in text.lower())
    if host_label is not None:
        cleaned_host_text = host_label.strip()
        cleaned_host_text = cleaned_host_text.replace("Hosted by", "")
        cleaned_host_text = cleaned_host_text.replace("hosted by", "")
        cleaned_host_text = cleaned_host_text.strip()
        host_name = cleaned_host_text

    superhost_text = soup.find(string=lambda text: text and "superhost" in text.lower())
    if superhost_text is not None:
        host_type = "Superhost"

    # Finds the room type
    room_type = "Entire Room"
    subtitle_text = soup.find(string=lambda text: text and ("private" in text.lower() or "shared" in text.lower()))
    if subtitle_text is not None:
        subtitle_text_lower = subtitle_text.lower()
        if "private" in subtitle_text_lower:
            room_type = "Private Room"
        elif "shared" in subtitle_text_lower:
            room_type = "Shared Room"

    # Finds the location rating
    location_rating = 0.0
    all_text_words = soup.get_text().split()

    # Go through every word to see if any look like a rating
    for word in all_text_words:
        if word.count(".") == 1:
            parts = word.split(".")
            if parts[0].isdigit() and parts[1].isdigit():
                num_rating = float(word)
                if num_rating >= 1.0 and num_rating <= 5.0:
                    location_rating = num_rating

    # Return the dictionary with all the info
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
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================

    # Gets the list from first function
    results = []
    listing_list = load_listing_results(html_path)

    # Goes through each listing
    for item in listing_list:
        title = item[0]
        listing_id = item[1]

        # Gets the details dictionary for this listing
        details = get_listing_details(listing_id)
        info = details[listing_id]

        policy = info["policy_number"]
        host_type = info["host_type"]
        host_name = info["host_name"]
        room_type = info["room_type"]
        rating = info["location_rating"]

        # Make the tuple in this order
        tup = (title, listing_id, policy, host_type, host_name, room_type, rating)

        results.append(tup)

    return results

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
    pass
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
    pass
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
    pass
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
    pass
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
        pass

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        # TODO: Call get_listing_details() on each listing id above and save results in a list.

        # TODO: Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        # 3) Check that listing 1944564 has the correct location rating 4.9.
        pass

    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)

        # TODO: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        pass

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        # TODO: Call output_csv() to write the detailed_data to a CSV file.
        # TODO: Read the CSV back in and store rows in a list.
        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].

        os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        # TODO: Check that the average for "Private Room" is 4.9.
        pass

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        pass


def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)