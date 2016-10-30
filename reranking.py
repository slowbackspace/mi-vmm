#!/usr/bin/env python3

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import isodate
import geopy


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyAYMg3XQ2J1trdyr5jgypW-Dbn4xufRPS0"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_search(options):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q=options.q,
    type="video",
    location=options.location,
    locationRadius=options.location_radius,
    part="id,snippet",
    maxResults=options.max_results
  ).execute()

  search_videos = []

  # Merge video ids
  for search_result in search_response.get("items", []):
    search_videos.append(search_result["id"]["videoId"])
  video_ids = ",".join(search_videos)

  # Call the videos.list method to retrieve location details for each video.
  video_response = youtube.videos().list(
    id=video_ids,
    part='snippet, recordingDetails'
  ).execute()

  videos = []

  # Add each result to the list, and then display the list of matching videos.
  for video_result in video_response.get("items", []):
    videos.append("%s, (%s,%s)" % (video_result["snippet"]["title"],
                              video_result["recordingDetails"]["location"]["latitude"],
                              video_result["recordingDetails"]["location"]["longitude"]))

  print ("Videos:\n", "\n".join(videos), "\n")

def normalize(value, minX, maxX):
  return (value-minX)/(maxX-minX)

def video_distance(video, location, locW, views, viewsW, date, dateW, length, lengthW):
  locDistance = viewsDistance = dateDistance = lengthDistance = 0;
  if locW != 0:
    locDistance = great_circle(video["location"], location).meters();
    locDistanceNorm = normalize(locDistance, 0, 6371000)
  if viewsW != 0:
    viewsDistance = abs(video["views"] - views);
    viewsDistanceNorm = normalize(viewsDistance,0,1000000)
  if dateW !=0:
    dateDistance = abs(isodate.parse_datetime(video["date"])- isodate.parse_datetime(date)).total_seconds()
    dateDistanceNorm = normalize(dateDistance,0,31536000)
  if lengthW != 0:
    durationSec = isodate.parse_duration(video["length"]).total_seconds();
    lengthDistance = abs(durationSec - length)
    lengthDistanceNorm = normalize(lengthDistance,0,3600)

  return locDistanceNorm*locW
       + viewsDistanceNowm*viewsW
       + dateDistanceNorm*dateW
       + lengthDistanceNorm*lengthW


def search(options,keyword, location = None, locW = 0, views=None, viewsW = 0, date=None, dateW = 0, length=None, lengthW=0 ):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  if not location:
    locationString = None
  else:
    locationString = str(location[0])+','+str(location[1])
  search_response = youtube.search().list(
    q=keyword,
    type="video",
    part="id,snippet",
    location=locationString,
    locationRadius=None if not locationString else "1000km",
    maxResults=50
  ).execute()

  search_videos = []

  # Merge video ids
  for search_result in search_response.get("items", []):
    search_videos.append(search_result["id"]["videoId"])
  video_ids = ",".join(search_videos)

  part_list = []
  if not location:
    part_list.append("recordingDetails")
  if not views:
    part_list.append("statistics")
  if not date:
    part_list.append("snippet")
  if not length:
    part_list.append("contentDetails")

  partString = ",".join(part_list)

  # Call the videos.list method to retrieve location details for each video.
  video_response = youtube.videos().list(
    id=video_ids,
    part=partString
  ).execute()

  videos = []
  # Add each result to the list, and then display the list of matching videos.
  for video_result in video_response.get("items", []):
    video = {"title":video_result["snippet"]["title"],
             "location":(None,None) if locationString==None else (video_result["recordingDetails"]["location"]["latitude"],
                                                                  video_result["recordingDetails"]["location"]["longitude"]),
              "views":video_result["statistics"]["viewCount"],
              "date":video_result["snippet"]["publishedAt"],
              "length":video_result["contentDetails"]["duration"],
              "distance": 0}
    video["distance"] = video_distance (video, location, locW, views, viewsW, date, dateW, length, lengthW)
    videos.append(video)

  videos.sort(key=lambda video: video_distance(video, location, locW, views, viewsW, date, dateW, length, lengthW))
  for video in videos:
    print (video["title"]," ",video["location"]," ",video["views"]," ",video["date"]," ",video["length"], "\n" )

if __name__ == "__main__":
  argparser.add_argument("--q", help="Search term", default="Google")
  argparser.add_argument("--location", help="Location", default="37.42307,-122.08427")
  argparser.add_argument("--location-radius", help="Location radius", default="5km")
  argparser.add_argument("--max-results", help="Max results", default=25)
  args = argparser.parse_args()

  try:
    search(args, keyword="dog", location = (37.42307,-122.08427), date="2015-01-15T16:45:35.000Z", dateW=1)
  except HttpError as e:
    print ("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))