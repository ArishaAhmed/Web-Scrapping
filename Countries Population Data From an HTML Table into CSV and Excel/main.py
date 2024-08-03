import requests
from bs4 import BeautifulSoup
import pandas as pd

url  = "https://www.worldometers.info/world-population/population-by-country/"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

rows = soup.find('table',{'id':'example2'}).find('tbody').find_all('tr')

# print(len(rows))
#print(rows)

Countries_list=[]

for row in rows:
    dict = {}
    dict["Country"] = row.find_all('td')[1].text
    dict["Population"] = row.find_all('td')[2].text.replace(',','')

    Countries_list.append(dict)

print(Countries_list)

df = pd.DataFrame(Countries_list)
df.to_excel('Coutries_Population.xlsx',index = False)
df.to_csv('Coutries_Population.csv', index = False)

########################## Printing all the columns without mentioning column names ####################################



import requests
from bs4 import BeautifulSoup
import pandas as pd

url  = "https://www.worldometers.info/world-population/population-by-country/"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Find the table
table = soup.find('table',{'id':'example2'})

# Extract the headers
headers = [header.text.strip() for header in table.find('thead').find_all('th')]

# Extract the rows
rows = table.find('tbody').find_all('tr')

# Initialize a list to hold the data
data = []

# Iterate over the rows
for row in rows:
    # Extract the columns
    cols = [col.text.strip().replace(',', '') for col in row.find_all('td')]
    # Append the row data to the data list
    data.append(cols)

# Create a DataFrame from the data
df = pd.DataFrame(data, columns=headers)

# Save the DataFrame to an Excel file
df.to_excel('Countries_Population.xlsx', index=False)
# Save the DataFrame to a CSV file
df.to_csv('Countries_Population.csv', index=False)

print("Data has been scraped and saved to 'Countries_Population.xlsx' and 'Countries_Population.csv'")

