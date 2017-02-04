import json
import os
import subprocess

import urllib3


def get_languages_for_line(line):
    result = line[line.rfind("[") + 1:line.rfind("]")]
    return result.replace(" ", "")


def get_url_for_line(line):
    result = line.lstrip()
    result = result[:result.index(" ")]
    return result


def download_videos(output_path):
    if output_path[-1:] == '/':
        input_file = open(output_path + 'videos.txt', 'r')
    else:
        input_file = open(output_path + '/videos.txt', 'r')
    actual_line = input_file.readline()
    i = 0
    while not actual_line == "":
        languages = get_languages_for_line(actual_line)
        url = get_url_for_line(actual_line)
        if output_path[-1:] == "/":
            path = output_path + str(i) + "/"
        else:
            path = output_path + "/" + str(i) + "/"
        if not os.path.exists(path):
            os.makedirs(path)
        command = 'youtube-dl "' + url + '" -o "' + path + 'out.%(ext)s" -x --audio-format wav --sub-lang ' + languages + ' --write-sub --convert-subs vtt'
        subprocess.call(command, shell=True)
        actual_line = input_file.readline()
        i += 1


def get_channel_id(key, username):
    http = urllib3.PoolManager()
    request = http.request('GET',
                           'https://www.googleapis.com/youtube/v3/channels?&key=' + key + '&forUsername=' + username +
                           '&part=id')

    response = json.loads(request.data.decode('utf-8'))

    channel_id = ""

    for x in range(len(response['items'])):
        if "id" in response['items'][x]:
            channel_id = response['items'][x]['id']

    return channel_id


def get_channel_videos_urls_with_token(key, channel_id, next_page_token):
    http = urllib3.PoolManager()
    request = http.request('GET',
                           'https://www.googleapis.com/youtube/v3/search?&key=' + key + '&channelId=' + channel_id +
                           '&part=snippet&order=date&maxResults=50&pageToken=' + next_page_token)
    response = json.loads(request.data.decode('utf-8'))
    actual_videos = []
    for x in range(len(response['items'])):
        if 'videoId' in response['items'][x]['id']:
            actual_videos.append('https://www.youtube.com/watch?v=' + response['items'][x]['id']['videoId'])

    next_page_token = None
    if 'nextPageToken' in response:
        next_page_token = response['nextPageToken']
    return actual_videos, next_page_token


def get_all_channel_videos(key, username):
    channel_id = get_channel_id(key, username)
    next_page_token = ''
    videos = []
    while not next_page_token is None:
        actual_videos, next_page_token = get_channel_videos_urls_with_token(key, channel_id, next_page_token)
        videos.extend(actual_videos)
    return videos


def create_input_file(output_path, key, languages):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    if output_path[-1:] == '/':
        input_file = open(output_path + 'videos.txt', 'w')
    else:
        input_file = open(output_path + '/videos.txt', 'w')

    videos = get_all_channel_videos(key, channel_name)
    for x in range(len(videos) - 1):
        input_file.write(videos[x] + " [" + languages + "]\n")
    input_file.write(videos[len(videos) - 1] + " [" + languages + "]")
    input_file.close()


if __name__ == '__main__':
    channel_name = input("Enter channel username: ")
    key = input("Enter your YouTube API key: ")
    languages = input("Enter comma separated languages: ")
    output_path = input("Enter path to output folder: ")
    create_input_file(output_path, key, languages)
    download_videos(output_path)
