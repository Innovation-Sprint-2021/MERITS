import sys
import requests
import json

import csv
import os

'''
url = 'https://prereview.org/api/v2/preprints?limit=1'
url = 'https://prereview.org/api/v2/preprints/doi-10.1101/2021.03.04.433973v1'
url = 'https://prereview.org/api/v2/preprints/doi-10.1101-2021.09.09.459577/full-reviews'
'''
url = 'https://prereview.org/api/v2/preprints/'
headers = {"Accept": "application/json","Content-Type": "application/json"}

doi = "doi-10.1101-2021.07.28.21260814"	#Random DOI that contains a couple of rapid reviews


input_data = []


def save_json(name,data):
	file_name = str(name)+".txt"
	with open(file_name, 'w+') as outfile:
		json.dump(data, outfile)


def create_directory(name):
	if not os.path.exists(name):
		os.makedirs(name)


'''
Function to prepare the doi for the curl request
Not sure how they modify DOIs for their API, seems like they only replace "/" by "-", but there might be other things.
'''
def prepare_doi_string(input_doi):

	#We need to find and replace "/" by "-"
	input_doi = input_doi.replace("/", "-")
	#If we only needed to replace the fist one, we just use this line instead.
	#input_doi = input_doi.replace("/", "-",1)

	doi = "doi-"+input_doi
	arxiv = "arxiv-"+input_doi
	

	return [doi,arxiv]


def read_command_line_input():
	if len(sys.argv) <= 1:
		print("You need to provide an argument to the program. A list of dois in a csv")
		return -1
	else:
		return sys.argv[1]

def parse_command_line(input):
	global input_data 
	if ".csv" in input:
		print("CSV Input provided")
		with open(input, newline='') as csvfile:
			reader = csv.reader(csvfile)
			for row in reader:
				input_data.append(row[0])
	else:
		print("You need to provide an argument to the program. The path of the csv containing DOIs")
		input_data = -1


def process_request(request_return,doi):
	create_directory(str(doi))
	dir_name="./"+str(doi)
	os.chdir(dir_name)
	request_return = json.loads(request_return.text)
	if "data" in request_return:
		data = request_return["data"][0]
		if "rapidReviews" in data:
			rreviews = data["rapidReviews"]
			i = 0
			for rr in rreviews:
				i+=1
				json_object = json.dumps(rr, indent = 4) 
				save_json(i,json_object)
				print("Rapid Review:")
				print(rr)
				print("-----------")
				print()
			os.chdir("../")


def send_request(doi):
	#First we create a directory for that DOI
	final_url = url+doi[0]
	print(final_url)
	r = requests.get(final_url, headers=headers)
	print(r.status_code)
	if r.status_code == 200:
		process_request(r,doi[0])
	elif r.status_code == 404: #document not found, we try arxiv instead
		final_url = url+doi[1]
		r = requests.get(final_url, headers=headers)
		if r.status_code == 200:
			process_request(r,doi[1])


command_line = read_command_line_input()
if command_line != -1:
	parse_command_line(command_line)
	if command_line!=-1:
		print(len(input_data))
		for doi in input_data:
			doi = prepare_doi_string(doi)
			send_request(doi)
