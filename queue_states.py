#! /usr/bin/python3

import requests
from bs4 import BeautifulSoup
import os


def rigi_queue_state():
    url = 'https://www2.hu-berlin.de/chemie/ag_theochem/Resources/status.html'
    # Make a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        rigi_info = html_to_nodeinfo(response)
        return rigi_info
    else:
        print("Failed to fetch the webpage for queue state. Status code:", response.status_code) 
        exit()

def html_to_nodeinfo(url_resp):
    # Parse the HTML content using BeautifulSoup
    html_object = BeautifulSoup(url_resp.text, 'html.parser').body.get_text(" ").strip()

    # Initialize an empty list to store extracted information
    html_object_list = []

    # Iterate through the parsed HTML text with a step of 12 characters
    for m in range(0, len(html_object), 12):
        # Check if the substring "Currently" is present in the current segment
        if "Currently" in html_object[m:m + 12]:
            # Iterate through the text starting from the position after "Currently"
            for n in range(m + 12, len(html_object), 4):
                # Check if the substring "cpu" is present in the current segment
                if "cpu" in html_object[n:n + 6]:
                    # Extract and append the relevant portion to the list
                    html_object_list.append(html_object[n + html_object[n:n + 6].index("cp"):n + 17])
                # Check if the substring "Name" is present, and exit the loop if found
                if "Name" in html_object[n:n + 12]:
                    break
            # Exit the outer loop if "Name" is found
            break

    # Initialize an empty list to store CPU information
    cpu_list = [('#Cores', 'Free', 'Queued')]

    # Iterate through the extracted HTML object list
    for k in html_object_list:
        # Check if the first part of the split string is not in the specified list
        if k.split(" ")[0] not in ['cpu-12', 'cpu-14', 'cpu-44', 'cpu-48']:
            continue  # Skip to the next iteration if not in the specified list
        # Append a list containing relevant information to the CPU list
        cpu_list.append((k.split(" ")[0], k.split(" ")[1], k.split(" ")[3]))

    # Return the final CPU list
    return cpu_list

def liverpool_queue_state():
    os.system("ssh -o LogLevel=QUIET lege@liverpool -t 'squeue' > this_is_a_very_very_veriiii_temporary_file.tmp")
    n = 0
    with open("this_is_a_very_very_veriiii_temporary_file.tmp", "r") as file:
        for line in file:
            n += 1
    
    if n-2 >= 14:
        free_nodes = 0
        queued_calcs = n-16
    elif n-2 < 14:
        free_nodes = 14-(n-2)
        queued_calcs = 0

    liverpool_info_obj = ('liverpool', str(free_nodes), str(queued_calcs))
    os.system("rm this_is_a_very_very_veriiii_temporary_file.tmp")
    return liverpool_info_obj

def all_queue_state():
    all_states = rigi_queue_state()
    all_states.append(liverpool_queue_state())
    return all_states

def main():
    print("this is a lib")

if __name__ == "__main__":
	main()

#print(all_queue_state())
