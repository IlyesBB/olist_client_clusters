address = "https://bra.postcodebase.com/fr"
class_states = "view view-region2-text view-id-region2_text view-display-id-block view-dom-id-fb5b0df2f7c500d4f11f1ffb23931ce2"
field_content_class = "field-content"
class_states = class_states.replace(' ', '.')
import asyncio

from requests_html import HTMLSession, AsyncHTMLSession
import pandas as pd




async def get_response(address):
    session = AsyncHTMLSession()
    r = await session.get(address)
    await r.html.arender()
    return r

response = asyncio.run(get_response(address))
table = response.html.find(".%s" % class_states, first=True)
content = table.find(".%s" %  field_content_class)
content = [c.find('a', first=True) for c in content]
print(content)


print()

