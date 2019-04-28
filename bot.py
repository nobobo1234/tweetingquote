# -*- coding: utf8 -*-

# Importing every package 
from twython import Twython
import requests
import feedparser
from PIL import ImageFont, Image, ImageDraw
import yaml
import io

# Open config
config = yaml.load(open("./config.yml", "r"), Loader=yaml.FullLoader)

# Connect to api
api = Twython(
	config["consumer_key"],
	config["consumer_secret"],
	config["access_token"],
	config["access_token_secret"])

# Getting data from Quote of the Day api
data = feedparser.parse("https://www.brainyquote.com/link/quotebr.rss")
author = data["entries"][0]["title"]
quote = f"{data['entries'][0]['summary']} ~ {author}"
link = data["entries"][0]["link"]

with requests.Session() as s:
	r = s.get("https://api.unsplash.com/photos/random?query=nature",
								headers={"Authorization": f"Client-ID {config['unsplash_client_id']}"})
	data = r.json()
	photographer = f"{data['user']['links']['html']}?utm_source=Daily%20Quote&utm_medium=referral"
	unsplash_website = "https://unsplash.com/?utm_source=Daily%20Quote&utm_medium=referral"
	download_location = data["links"]["download_location"]
	download_link = s.get(download_location,
						headers={"Authorization": f"Client-ID {config['unsplash_client_id']}"})
	download_link_data = download_link.json()
	print(download_link_data)
	r = s.get(f"{download_link_data['url']}&w=1080", stream=True)
	if r.status_code == 200:
		i = io.BytesIO()
		for chunk in r:
			i.write(chunk)
		i.seek(0)

# Making image
font = ImageFont.truetype("arial.ttf", 30)

image = Image.open(i).convert("RGBA")
text = Image.new("RGBA", image.size, color=(0, 0, 0, 0))
draw = ImageDraw.Draw(image)
text_draw = ImageDraw.Draw(text)

quote_lines = ""
for i in quote.split(" "):
	if text_draw.textsize(quote_lines.split("\n")[-1], font=font)[0] > image.width/2:
		quote_lines += "\n"
	quote_lines += i + " "

# Adding rectangle and quote text
padding = 10
w, h = draw.textsize(quote_lines, font=font)
x, y = ((image.width-w)/2, (image.height-h)/2)
text_draw.rectangle([(x-padding, y-padding), (x+w+padding, y+h+padding)], fill=(0, 0, 0, 127))
text_draw.text((x, y), quote_lines, font=font, align="center")

final = Image.alpha_composite(image, text)
final.save('quote.png')

with open('quote.png', 'rb') as media:
	response = api.upload_media(media=media)
	api.update_status(media_ids=[response["media_id"]],
					status=f"Hello, here's my daily tweet #quote by {author}. Quote by: {link}. Photo by {photographer} on {unsplash_website}")
