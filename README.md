# google-photos

Olly Butters

Get a list of albums (mine and shared) with the count of photos in each. Also get a list of photos which are not in any album (mine or shared), with a link to them so they can be added to an album.

## Prerequisites

- Set up API access on your google account.
- Put the credentials.json file in the same directory as this script.

## Authentication

This code is set up to use the google-photos-api library. It needs to be set up in the developers console - [https://console.developers.google.com/](https://console.developers.google.com/). You need the credentials.json file which can be downloaded from the Credentials page in the developers console. The credentials.json file should be placed in the same directory as this script, but it is secret, so don't share it.

It uses OAuth2 for authentication.

## Running

Just run the photo_summary.py file, it will ask you to autheticate the first time, then it will work through all your photos, figure out what is in what album, then generate a output html file (summary.html) which has the summary in it. The links to the photos not in any albums will take you directly to the photo in google photos, where you can then add it to a new album. The next time it runs it will get all the metadata again so the photos you've added to albums will not appear in the list.

## Notes

- It doesn't know if photos are in multiple albums.
- Sometimes if the token has expired it will fail the first time it is run. Just rerun it.

## Useful links

- https://developers.google.com/photos/library/guides/overview?hl=en_GB
- https://developers.google.com/photos/library/reference/rest?hl=en_GB

## To do

- Add flag to my albums to show if they are shared.
