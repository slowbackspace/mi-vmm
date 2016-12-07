#!/usr/bin/env python3

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import datetime
import isodate
from pprint import pprint
from geopy.distance import great_circle
from math import radians, cos, sin, asin, sqrt


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyAYMg3XQ2J1trdyr5jgypW-Dbn4xufRPS0"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

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


def normalize(value, minX, maxX):
    if maxX = minX:
        return 1
    return (value-minX)/(maxX-minX)

def find_min_max(value, act_min, act_max):
    if value < act_min:
        act_min = value
    elif value > act_max:
        act_max = value
    return act_min, act_max


def video_distance(video, location, locW, views, viewsW, date, dateW, length, lengthW, minDistances, maxDistances):
    locDistanceNorm = viewsDistanceNorm = dateDistanceNorm = lengthDistanceNorm = 0
    if locW != 0:
        locDistance = great_circle_distance(video["location"][0],video["location"][1],location[0],location[1])
        locDistanceNorm = normalize(locDistance, minDistances["location"], maxDistances["location"])
    if viewsW != 0:
        viewsDistance = abs(int(video["views"]) - views)
        viewsDistanceNorm = normalize(viewsDistance, minDistances["views"], maxDistances["views"])
    if dateW != 0:
        dateDistance = abs(isodate.parse_datetime(video["date"]) - date).total_seconds()
        dateDistanceNorm = normalize(dateDistance, minDistances["date"], maxDistances["date"])
    if lengthW != 0:
        durationSec = isodate.parse_duration(video["length"]).total_seconds()
        lengthDistance = abs(durationSec - length)
        lengthDistanceNorm = normalize(lengthDistance, minDistances["length"], maxDistances["length"])

    return (locDistanceNorm * locW + viewsDistanceNorm * viewsW 
            + dateDistanceNorm * dateW + lengthDistanceNorm * lengthW)


def search(keyword, location=None, locW=0, views=None, viewsW=0, 
           date=None, dateW=0, length=None, lengthW=0):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, 
                    developerKey=DEVELOPER_KEY)

    # Call the search.list method to retrieve results matching the specified
    # query term.
    search_response = youtube.search().list(
        q=keyword,
        type="video",
        part="id,snippet",
        location=None if not location else ",".join(map(str, location)),
        locationRadius=None if not location else "1000km",
        maxResults=50
    ).execute()

    search_videos = []
    print(type(search_response))
    # Merge video ids
    for search_result in search_response.get("items", []):
        search_videos.append(search_result["id"]["videoId"])
    video_ids = ",".join(search_videos)

    part_list = ["snippet"]
    if location:
        part_list.append("recordingDetails")
    if views:
        part_list.append("statistics")
    if length:
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
        location_searched = None if not location else (
                            video_result["recordingDetails"]["location"]["latitude"],
                            video_result["recordingDetails"]["location"]["longitude"]
                            )
        video = {
            "title": video_result["snippet"]["title"],
            "thumbnail": video_result["snippet"]["thumbnails"]["default"]["url"],
            "location": location_searched,
            "views": video_result.get("statistics", {}).get("viewCount", None),
            "date": video_result.get("snippet", {}).get("publishedAt", None),
            "length": video_result.get("contentDetails", {}).get("duration", None)
            }
        videos.append(video)

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

    if locW > 0:
        minDistances["location"] = maxDistances["location"] = great_circle_distance(videos[0]["location"][0],videos[0]["location"][1],location[0],location[1])

    if viewsW > 0:
        minDistances["views"] = maxDistances["views"] = abs(int(videos[0]["views"]) - views)

    if dateW > 0:
        minDistances["date"] = maxDistances["date"] = abs(isodate.parse_datetime(videos[0]["date"]) - date).total_seconds()

    if lengthW > 0:
        durationSec = isodate.parse_duration(videos[0]["length"]).total_seconds()
        minDistances["length"] = maxDistances["length"] = abs(durationSec - length)

    for video in videos:
        if locW > 0:
            act_distance = great_circle_distance(video["location"][0],video["location"][1],location[0],location[1])
            minDistances["location"], maxDistances["location"] = find_min_max(act_distance, minDistances["location"], maxDistances["location"])

        if viewsW > 0:
            act_distance = abs(int(video["views"]) - views)
            print(act_distance)
            minDistances["views"], maxDistances["views"] = find_min_max(act_distance, minDistances["views"], maxDistances["views"])

        if dateW > 0:
            act_distance = abs(isodate.parse_datetime(video["date"]) - date).total_seconds()
            minDistances["date"], maxDistances["date"] = find_min_max(act_distance, minDistances["date"], maxDistances["date"])

        if lengthW > 0:
            durationSec = isodate.parse_duration(video["length"]).total_seconds()
            act_distance = abs(durationSec - length)
            minDistances["length"], maxDistances["length"] = find_min_max(act_distance, minDistances["length"], maxDistances["length"])



    unsorted_videos = videos.copy()
    videos.sort(key=lambda video: video_distance(video, location, locW, 
                views, viewsW, date, dateW, length, lengthW, minDistances, maxDistances))

    for video in unsorted_videos:
        print(video)
    print ("\n\n\n\n")
    for video in videos:
        pprint(video)

    return unsorted_videos, videos

if __name__ == "__main__":

    try:
        search(keyword="dog", length=10, lengthW=0.5, views=100, viewsW=0.5, location = (37.42307,-122.08427), locW=0.5, date=datetime.datetime.now(datetime.timezone.utc), dateW=0.5)
    except HttpError as e:
        print ("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))