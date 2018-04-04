# -*- coding: utf8 -*-

# Importing every package 
from twython import Twython
import requests
import json
from PIL import ImageFont, Image, ImageDraw
import textwrap
from datetime import datetime
from pytz import timezone
import calendar
import yaml

# Setup times
tz = timezone('EST')
now = datetime.now(tz)
date = now.strftime('%Y-%m-%d')
time = now.strftime('%H:%M:%S')

# Open config
config = yaml.load(open('./config.yml', 'r'))

# Connect to api
api = Twython(config['consumer_key'],config['consumer_secret'],config['access_token'],config['access_token_secret'])

# Getting data from Quote of the Day api
r = requests.get('http://api.theysaidso.com/qod.json')
d=r.json()


def text2png(text, fullpath, linkback, color = "#000", bgcolor = "#FFF", fontfullpath = None, fontsize = 20, leftpadding = 3, rightpadding = 3, width = 200):
	NEWLINE_REPLACEMENT_STRING = ' ' + u'\uFFFD' + ' '

	# Add copyright
	fontlinkback = ImageFont.truetype('arial.ttf', 8)
	linkbackx = fontlinkback.getsize(linkback)[0]
	linkback_height = fontlinkback.getsize(linkback)[1]

	# load font
	font = ImageFont.load_default() if fontfullpath == None else ImageFont.truetype(fontfullpath, fontsize)
	text = text.replace('\n', NEWLINE_REPLACEMENT_STRING)

	lines = []
	line = u""

	# Print text to image
	for word in text.split():
		if word == u'\uFFFD':
			lines.append(line[1:])
			line = u""
			lines.append( u"" )
		elif font.getsize( line + ' ' + word )[0] <= (width - rightpadding - leftpadding):
			line += ' ' + word
		else: #start a new line
			lines.append( line[1:] ) #slice the white space in the begining of the line
			line = u""

			line += ' ' + word #for now, assume no word alone can exceed the line width

	if len(line) != 0:
		lines.append( line[1:] ) #add the last line

	line_height = font.getsize(text)[1]
	img_height = line_height * (len(lines) + 1)

	img = Image.new("RGBA", (width, img_height), bgcolor)
	draw = ImageDraw.Draw(img)

	y = 0
	for line in lines:
		draw.text( (leftpadding, y), line, color, font=font)
		y += line_height

	# add linkback at the bottom
	draw.text( (width - linkbackx, img_height - linkback_height), linkback, color, font=fontlinkback)

	img.save(fullpath)

# Prepare the image data
copyright = d['contents']['copyright']
def hastagconverter(array):
	for i in range(len(array)):
		array[i] = ''.join(('#', array[i]))
	myString = " ".join(array)
	return myString
text=d['contents']['quotes'][0]['quote']
author = d['contents']['quotes'][0]['author']
imgtext = text + " ~ " + author
if "'" in text:
	text=d['contents']['quotes'][0]['quote'].replace("'", "")
hashtags = d['contents']['quotes'][0]['tags']
hasht = hastagconverter(hashtags)

# Run the image drawing function
text2png(text=imgtext, fullpath='test.png', fontfullpath="arial.ttf", linkback=copyright)

# Open image and upload image to twitter
photo = open('test.png', 'rb')
response = api.upload_media(media=photo)

# Upload to twitter
api.update_status(media_ids=[response['media_id']], status="Hello, here's my daily tweet #quote. It's " + calendar.day_name[now.weekday()] + " " + hasht)
