# google-photos

Want to get a summary of albums (mine and shared) and a list of photos which are not in any album (mine or shared).

## Prerequisites

- Set up API access on your google account.
- Put the credentials.json file in the same directory as this script.

## Running

Just run the photo_summary.py file, it will ask you to autheticate the first time, then it will work through all your photos, figure out what is in what album, then generate a output html file (summary.html) which has the summary in it. The links to the photos not in any albums will take you directly to the photo in google photos, where you can then add it to a new album. The next time it runs it will get the metadata again so the photo will not appear in the list.

## Notes

- It doesn't know if photos are in multiple albums.
- Sometimes if the token has expired it will fail the first time it is run. Just rerun it.

## To do

- Add thumbnail images to the summary.
