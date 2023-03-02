address = "https://www.iso.org/obp/ui/#iso:code:3166:BR"

from requests_html import HTMLSession
import pandas as pd

session = HTMLSession()

r = session.get(address)
r.html.render(timeout=10, sleep=10)

table = r.html.find('#subdivision')[0]
columns = [th.text for th in table.find(".header")]
table_content = table.find('tbody')[0]
list_2d = []
for line in table_content.find('tr'):
    list_2d.append([td.text for td in line.find('td')])
df = pd.DataFrame(list_2d, columns=columns)
df.to_csv('./data/states_iso.csv')
