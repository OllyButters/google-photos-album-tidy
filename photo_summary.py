#!/usr/bin/env python3

import datetime
import os.path
import pickle
import pprint
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Needs credentials.json from google before running

# My photos can be in:
# 1) One or more of my albums
# 2) One or more of someone elses shared albums
# 3) No album

# This script gets the IDs of ALL of my photos and checks to see if it is in AT LEAST ONE album.
# If it's not then it outputs an HTML file with links to each.

scopes = ['https://www.googleapis.com/auth/photoslibrary.readonly']

credentials = None

# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        credentials = pickle.load(token)

# If there are no (valid) credentials available, let the user log in.
if not credentials or not credentials.valid:
    if os.path.exists('token.pickle'):
        os.remove('token.pickle')

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', scopes)
        credentials = flow.run_local_server(port=0)

    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(credentials, token)

google_photos = build('photoslibrary', 'v1', credentials=credentials)
# google_photos = build('photoslibrary', 'v2', credentials=credentials, static_discovery=False)


########################################################################################
# Get list of all my albums
my_albums = []        # List of dicts with metadata about each album in it.
my_albums_ids = []    # List of IDs of my albums
my_albums_titles = []
nextpagetoken = None

print("Getting metadata about my albums...")
while nextpagetoken != '':
    # print("\nNumber of items processed:" + str(len(my_albums)))

    # dict with albums : list of dicts
    results = google_photos.albums().list(pageSize=50, pageToken=nextpagetoken).execute()
    my_albums.extend(results['albums'])
    nextpagetoken = results.get('nextPageToken', '')

# pprint.pprint(my_albums)

print(str(len(my_albums)) + " my albums found.\n")

for this_album in my_albums:
    my_albums_ids.append(this_album['id'])
    my_albums_titles.append(this_album['title'])
    # print(this_album['title'] + " / " + this_album['id'])


##################################################################
# Get list of all shared albums
shared_albums = []        # List of dicts with all metadata
shared_albums_ids = []    # List of IDs
shared_albums_titles = []

print("Getting metadata about shared albums...")
nextpagetoken = None

while nextpagetoken != '':
    # print("\n\nNumber of items processed:" + str(len(shared_albums)))

    # dict with sharedAlbums : list of dicts
    results = google_photos.sharedAlbums().list(pageSize=50, pageToken=nextpagetoken).execute()
    shared_albums.extend(results['sharedAlbums'])
    nextpagetoken = results.get('nextPageToken', '')

# pprint.pprint(shared_albums)

print(str(len(shared_albums)) + " shared albums found.\n")

for this_album in shared_albums:
    # A title is not always present
    try:
        # print(this_album)
        shared_albums_ids.append(this_album['id'])
        shared_albums_titles.append(this_album['title'])
        # print(this_album['title'] + " / " + this_album['id'])
    except:
        pass

# print("\n\nShared minus mine. (Albums shared with me.)")
# print(list(set(shared_albums_titles) - set(my_albums_titles)))

# print("\n\nMine minus shared. (My albums which are not shared with anyone.)")
# print(list(set(my_albums_titles) - set(shared_albums_titles)))


# List of all unique albums
all_albums_ids = list(set(my_albums_ids + shared_albums_ids))


########################################################################################
# Get all my photos
all_my_photos = []      # List of dicts with all metadata
all_my_photos_ids = []  # List of IDs
nextpagetoken = None
status_counter = 0

print("Getting metadata about my photos...")
while nextpagetoken != '':
    status_counter += 1
    if status_counter % 100 == 0:
        print("\n" + str(status_counter) + " albums processed.")

    results = google_photos.mediaItems().list(pageSize=100, pageToken=nextpagetoken).execute()
    all_my_photos += results.get('mediaItems', [])
    nextpagetoken = results.get('nextPageToken', '')

# pprint.pprint(all_my_photos)

for this_photo in all_my_photos:
    all_my_photos_ids.append(this_photo['id'])

print(str(len(all_my_photos_ids)) + " my photos.")
print(str(len(set(all_my_photos_ids))) + " unique my photos.")

# https://developers.google.com/photos/library/reference/rest


########################################################################################
# Get list of all my photos in all albums (mine and shared)
all_photos_in_all_albums = []
all_photos_in_all_albums_ids = []
status_counter = 0

print("\nGetting metadata about photos from all albums...")
for this_album_id in all_albums_ids:
    # print("\n\n##############################")
    # print(this_album_id)

    # Search for the photos that have this albumId
    try:
        nextpagetoken = None

        while nextpagetoken != '':
            status_counter += 1
            if status_counter % 500 == 0:
                print("\n" + str(status_counter) + " albums processed.")

            results = google_photos.mediaItems().search(body={"albumId": this_album_id, "pageToken": nextpagetoken, "pageSize": 100}).execute()
            # pprint.pprint(results)
            these_photos = results.get('mediaItems', [])
            nextpagetoken = results.get('nextPageToken', '')

            all_photos_in_all_albums.extend(results['mediaItems'])

    except:
        print("\nWARNING: No album for ID: " + this_album_id)

print(str(len(all_photos_in_all_albums)) + " photos in all albums\n\n")

for this_photo in all_photos_in_all_albums:
    try:
        all_photos_in_all_albums_ids.append(this_photo["id"])
    except:
        pass


# Calculate the difference between all my photos and all photos in all albums
photos_not_in_albums_ids = list(set(all_my_photos_ids) - set(all_photos_in_all_albums_ids))

uncategorised = []
for this_photo in photos_not_in_albums_ids:
    uncategorised.extend([element for element in all_my_photos if element['id'] == this_photo])

print(str(len(uncategorised)) + " photos not in any albums.")


# Make an HTML page with a summary of albums
with open('summary.html', 'w') as html:
    html.write("<html><head></head><body>")

    html.write("Updated: " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + "<br/>")

    html.write(str(len(all_my_photos_ids)) + " my photos.<br/>")
    html.write(str(len(set(all_my_photos_ids))) + " unique my photos.<br/>")

    html.write(str(len(my_albums)) + " my albums found.<br/>")
    html.write(str(len(shared_albums)) + " shared albums found.<br/>")

    html.write(str(len(all_photos_in_all_albums)) + " all photos in all albums (mine and shared).<br/>")
    html.write(str(len(uncategorised)) + " my photos not in any albums (mine or shared).<br/>")

    # My albums
    html.write("<h1>My albums</h1>")
    html.write("<table>")
    photo_count = 0

    html.write("<tr><th>Album name</th><th>Number of photos</th></tr>")
    for this_album in sorted([item for item in my_albums if 'title' in item.keys()], key=lambda item: item['title']):
        photo_count += int(this_album['mediaItemsCount'])
        html.write("<tr><td>" + this_album['title'] + "</td><td>" + this_album['mediaItemsCount'] + "</td></tr>")

    html.write("<tr><td></td><td><strong>" + str(photo_count) + "</strong></td></tr>")
    html.write("<table>")

    # Shared albums
    html.write("<h1>Shared albums</h1>")
    html.write("<table>")
    photo_count = 0
    # pprint.pprint(shared_albums)

    html.write("<tr><th>Album name</th><th>Number of photos</th></tr>")
    for this_album in sorted([item for item in shared_albums if 'title' in item.keys()], key=lambda item: item['title']):
        try:
            photo_count += int(this_album['mediaItemsCount'])
            html.write("<tr><td>" + this_album['title'] + "</td><td>" + this_album['mediaItemsCount'] + "</td></tr>")
        except:
            pass
    html.write("<tr><td></td><td><strong>" + str(photo_count) + "</strong></td></tr>")
    html.write("<table>")

    html.write("<h1>Photos not in any album</h1>")
    html.write("<table>")

    # Photos not in any album
    for this_photo in sorted([item for item in uncategorised if 'baseUrl' in item.keys()], key=lambda item: item['mediaMetadata']['creationTime'], reverse=True):
        try:
            html.write('<tr><td><a href="' + this_photo['productUrl'] + '" target="_blank">' + this_photo['filename'] + '</a></td>')
            html.write('<td>' + this_photo['mediaMetadata']['creationTime'] + '</td>')
            html.write('<td><a href="' + this_photo['productUrl'] + '" target="_blank"><img src=\"' + this_photo['baseUrl'] + '=w150-h150\" height=\"150px\"/></a></td></tr>')
        except:
            pass

    html.write("</table>")

    html.write("</body></html>")
