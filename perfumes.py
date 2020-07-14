from selenium import webdriver
import time
import re
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
import csv

# Windows users need to specify the path to chrome driver you just downloaded.
# You need to unzip the zipfile first and move the .exe file to any folder you want.
# driver = webdriver.Chrome(r'path\to\the\chromedriver.exe')
driver = webdriver.Chrome()
# Go to the page that we want to scrape
driver.get("https://www.sephora.com/beauty/best-selling-perfume")
#driver.get("https://www.sephora.com/shop/clean-skin-care")

csv_file = open('products.csv', 'w', encoding='utf-8', newline='')
writer = csv.writer(csv_file)

SCROLL_PAUSE_TIME = 0.5

while True:

    # Get scroll height
	### This is the difference. Moving this *inside* the loop
	### means that it checks if scrollTo is still scrolling 
	last_height = driver.execute_script("return document.body.scrollHeight")

	# Scroll down to bottom
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

	# Wait to load page
	time.sleep(SCROLL_PAUSE_TIME)

	# Calculate new scroll height and compare with last scroll height
	new_height = driver.execute_script("return document.body.scrollHeight")
	if new_height == last_height:

	    # try again (can be removed)
	    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

	    # Wait to load page
	    time.sleep(SCROLL_PAUSE_TIME)

	    # Calculate new scroll height and compare with last scroll height
	    new_height = driver.execute_script("return document.body.scrollHeight")

	    # check if the page height has remained the same
	    if new_height == last_height:
	        # if so, you are done
	        break
	    # if not, move on to the next loop
	    else:
	        last_height = new_height
	        continue

num = 1
links = [link.get_attribute('href') for link in driver.find_elements_by_xpath('//a[@class="css-ix8km1"]')]
#links = ["https://www.sephora.com/product/legend-spirit-eau-de-toilette-P405416?icid2=bestsellersfragrance_skugrid_ufe:p405416:product"]
for link in links:
	driver.get(link)
	product_dict = {}



	perf_name = driver.find_element_by_xpath('//span[@class="css-0"]').text
	brand = driver.find_element_by_xpath('//span[@class="css-euydo4"]').text
	price = float(driver.find_element_by_xpath('//span[@data-at="price"]').text.strip('$'))
	#reviews
	try:
		reviews = driver.find_element_by_xpath('//span[@class="css-2rg6q7"]').text.strip(' reviews')
		if 'K' in reviews:
			reviews = float(reviews.replace('K',''))*1000
	except:
		reviews = ''
	#loves
	try:
		loves = driver.find_element_by_xpath('//span[@data-at="product_love_count"]').text
		if 'K' in loves:
			loves = int(float(loves.replace('K', ''))*1000)
	except:
		loves = ''

	#ratings
	try:
		ratings = float(driver.find_element_by_xpath('//div[@class="css-ychh9y"]').get_attribute('aria-label').strip(' stars'))
	except:
		ratings = ''

	product_dict['num'] = num
	product_dict['perf_name'] = perf_name
	product_dict['brand'] = brand
	product_dict['price'] = price
	product_dict['reviews'] = reviews
	product_dict['loves'] = loves
	product_dict['ratings'] = ratings
	

	full_description = driver.find_element_by_xpath('//div[@class="css-pz80c5"]').text
	description = full_description.split('\n\n')
	r2 = re.compile('.*Notes.*', re.DOTALL)
	r = re.compile('(.*Fragrance Family:.*)|(.*Scent Type:.*)|(.*Key Notes:.*)')

	if r.match(full_description):
		description = [line.split(':')[1].strip('\n').strip() for line in description if r.match(line)]
		product_dict['frag_family'] = description[0]
		product_dict['scent_type'] = description[1]
		product_dict['key_notes'] = description[2]
	elif r2.match(full_description):
		description = [line.split(':')[1].strip('Style').strip('\n').strip('.') for line in description if r2.match(line)]
		product_dict['frag_family'] = ''
		product_dict['scent_type'] = ''
		product_dict['key_notes'] = description[0]
	else:
		product_dict['frag_family'] = ''
		product_dict['scent_type'] = ''
		product_dict['key_notes'] = ''

	if num == 1: 
		writer.writerow(product_dict.keys())
	writer.writerow(product_dict.values())
	num += 1


