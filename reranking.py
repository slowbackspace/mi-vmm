#!/usr/bin/env python3

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import datetime
import isodate
from pprint import pprint
from geopy.distance import great_circle
from math import radians, cos, sin, asin, sqrt


# YouTube API KEY
DEVELOPER_KEY = "AIzaSyAYMg3XQ2J1trdyr5jgypW-Dbn4xufRPS0"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# great cirle distance
def great_circle_distance(lat1, lon1, lat2, lon2):
    # convert to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # count absolute differences
    dlon = abs(lon2 - lon1)
    dlat = abs(lat2 - lat1)
    arg = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    angle = 2 * asin(sqrt(arg)) 
    meters = 6367 * angle * 1000
    return meters

# min max normalization
def normalize(value, minX, maxX):
    if maxX == minX:
        return 1
    return (value-minX)/(maxX-minX)

# set min and max of 3 numbers
def find_min_max(value, act_min, act_max):
    if value < act_min:
        act_min = value
    elif value > act_max:
        act_max = value
    return act_min, act_max


# count distance between 2 videos
def video_distance(video, location, locW, views, viewsW, date, dateW, length, lengthW, minDistances, maxDistances):
    # intialise distances
    locDistanceNorm = viewsDistanceNorm = dateDistanceNorm = lengthDistanceNorm = 0

    # location distance
    if locW != 0:
        locDistance = great_circle_distance(video["location"][0],video["location"][1],location[0],location[1])
        locDistanceNorm = normalize(locDistance, minDistances["location"], maxDistances["location"])
    # views distance
    if viewsW != 0:
        viewsDistance = abs(int(video["views"]) - views)
        viewsDistanceNorm = normalize(viewsDistance, minDistances["views"], maxDistances["views"])
    # date distance
    if dateW != 0:
        dateDistance = abs(isodate.parse_datetime(video["date"]) - date).total_seconds()
        dateDistanceNorm = normalize(dateDistance, minDistances["date"], maxDistances["date"])
    # duration distance
    if lengthW != 0:
        durationSec = int(video["length"])
        lengthDistance = abs(durationSec - length)
        lengthDistanceNorm = normalize(lengthDistance, minDistances["length"], maxDistances["length"])

    return (locDistanceNorm * locW + viewsDistanceNorm * viewsW 
            + dateDistanceNorm * dateW + lengthDistanceNorm * lengthW)

def get_videos_response(youtube,keyword,location, locW):
    search_response = youtube.search().list(
        q=keyword,
        type="video",
        part="id,snippet",
        location=None if locW==0 else ",".join(map(str, location)),
        locationRadius=None if locW==0 else "1000km",
        maxResults=50
    ).execute()
    return search_response  

def set_min_max(videos, location, views, date, length, locW, viewsW, dateW, lengthW):
    # initialise min and max distances
    minDistances = {
    "location" : 0,
    "views" : 0,
    "date" : 0,
    "length" :0
    }

    maxDistances = {
    "location" : 0,
    "views" : 0,
    "date" : 0,
    "length" :0
    }

    # initialise min and max distances with distance of first video
    if locW > 0:
        minDistances["location"] = maxDistances["location"] = great_circle_distance(videos[0]["location"][0],videos[0]["location"][1],location[0],location[1])

    if viewsW > 0:
        minDistances["views"] = maxDistances["views"] = abs(int(videos[0]["views"]) - views)

    if dateW > 0:
        minDistances["date"] = maxDistances["date"] = abs(isodate.parse_datetime(videos[0]["date"]) - date).total_seconds()

    if lengthW > 0:
        durationSec = int(videos[0]["length"])
        minDistances["length"] = maxDistances["length"] = abs(durationSec - length)

    # find min and max distances
    for video in videos:
        if locW > 0:
            act_distance = great_circle_distance(video["location"][0],video["location"][1],location[0],location[1])
            minDistances["location"], maxDistances["location"] = find_min_max(act_distance, minDistances["location"], maxDistances["location"])

        if viewsW > 0:
            act_distance = abs(int(video["views"]) - views)
            minDistances["views"], maxDistances["views"] = find_min_max(act_distance, minDistances["views"], maxDistances["views"])

        if dateW > 0:
            act_distance = abs(isodate.parse_datetime(video["date"]) - date).total_seconds()
            minDistances["date"], maxDistances["date"] = find_min_max(act_distance, minDistances["date"], maxDistances["date"])

        if lengthW > 0:
            durationSec = int(video["length"])
            act_distance = abs(durationSec - length)
            minDistances["length"], maxDistances["length"] = find_min_max(act_distance, minDistances["length"], maxDistances["length"])

    return minDistances, maxDistances

def get_video(video_result, locW,i):
    location_searched = None if locW==0 else (
                            video_result["recordingDetails"]["location"].get("latitude",None),
                            video_result["recordingDetails"]["location"].get("longitude",None)
                            )
    length_searched = video_result.get("contentDetails", {}).get("duration", None)
    video = {
        "seq" : i,
        "url": "https://www.youtube.com/watch?v=" + video_result["id"],
        "title": video_result["snippet"]["title"],
        "thumbnail": video_result["snippet"]["thumbnails"]["default"]["url"],
        "location": None if location_searched==(None,None) else location_searched,
        "views": video_result.get("statistics", {}).get("viewCount", None),
        "date": video_result.get("snippet", {}).get("publishedAt", None),
        "length": None if length_searched is None else isodate.parse_duration(length_searched).total_seconds()
        }
    return video   

def search(keyword, location=None, locW=0, views=None, viewsW=0, 
           date=None, dateW=0, length=None, lengthW=0):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, 
                    developerKey=DEVELOPER_KEY)

    if location is None or location==(0,0):
        locW = 0
    if views is None:
        viewsW = 0
    if date is None:
        dateW = 0
    if length is None:
        lengthW = 0

    # search videos
    search_response = get_videos_response(youtube,keyword,location,locW)

    search_videos = []
    # Merge video ids
    for search_result in search_response.get("items", []):
        search_videos.append(search_result["id"]["videoId"])
    video_ids = ",".join(search_videos)

    # retrieve details for videos
    video_response = youtube.videos().list(
        id=video_ids,
        part="snippet,recordingDetails,statistics,contentDetails"
    ).execute()

    videos = []
    i=0
    # create dictionary of videos
    for video_result in video_response.get("items", []):
        i += 1
        video = get_video(video_result,locW,i)
        if video["location"] is None:
            locW=0
        videos.append(video)

    minDistances, maxDistances = set_min_max(videos, location, views, date, length, locW, viewsW, dateW, lengthW)

    unsorted_videos = videos.copy()
    # sort videos
    videos.sort(key=lambda video: video_distance(video, location, locW, 
                views, viewsW, date, dateW, length, lengthW, minDistances, maxDistances))

    return unsorted_videos, videos

if __name__ == "__main__":

    try:
        search(keyword="dog", views=100, viewsW=0, lengthW=1, location = (0.0001,0.00001), locW=0.5, date=datetime.datetime.now(datetime.timezone.utc), dateW=0.5)
    except HttpError as e:
        print ("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))