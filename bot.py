# -*- coding: utf8 -*-

# Importing every package 
from twython import Twython
import requests
import feedparser
from PIL import ImageFont, Image, ImageDraw
import yaml

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

background_request = requests.get("https://api.unsplash.com/photos/random?query=nature",
								headers={"Authorization": f"Client-ID {config['unsplash_client_id']}"})
background_data = background_request.json()
background_image = background_data["urls"]["raw"] + "&w=1080"
r = requests.get(background_image, stream=True)
if r.status_code == 200:
	with open("scenery.png", "wb") as f:
		for chunk in r:
			f.write(chunk)

# Making image
font = ImageFont.truetype("arial.ttf", 30)

image = Image.open("scenery.png").convert("RGBA")
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
final.save("image.png")

photo = open("image.png", "rb")
response = api.upload_media(media=photo)
api.update_status(media_ids=[response["media_id"]],
				status=f"Hello, here's my daily tweet #quote by {author}. {link}")
