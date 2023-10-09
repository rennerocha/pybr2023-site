#!/usr/bin/env python
import os
import pathlib
import requests
import json
from dotenv import dotenv_values
from markdownify import markdownify
from textwrap import dedent


def string_parser(string):
    return (
        string.lower()
        .replace("- ", "")
        .replace(", ", "-")
        .replace(" ", "-")
        .replace("ç", "c")
        .replace("á", "a")
        .replace("ã", "a")
        .replace("é", "e")
        .replace("ê", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("õ", "o")
        .replace("ú", "u")
        .replace("ñ", "n")
        .replace("ü", "u")
        .replace(".", "-dot-")
        .replace("/", "-")
        .replace("!", "")
        .replace("?", "")
        .replace("(", "")
        .replace(")", "")
        .replace("[", "")
        .replace("]", "")
        .replace("{", "")
        .replace("}", "")
        .replace("=", "")
        .replace("+", "")
        .replace("*", "")
        .replace("&", "")
        .replace("#", "")
        .replace("$", "")
        .replace("%", "-por-cento-")
        .replace("'", "")
        .replace(":", "")
        .replace("--", "-")
        .replace("_", "-")
    )


class GetDataFromServer():
    def __init__(self):
        self.app_path = str(pathlib.Path().resolve())
        self.env = self.__load_token_from_file()
        self.token = self.env.get('PRETALX_TOKEN') or ''
        self.api_url = self.env.get('API_URL') or ''
        self.headers = self.__get_headers()
        self.talks = self.__get_talks() or None
        self.short_tutorials = self.__get_short_tutorials() or None

    def __load_token_from_file(self):
        """Load the API token from .env file on the root path"""
        if (os.path.isfile('{}/.env'.format(self.app_path))):
            return {
                **dotenv_values('{}/.env'.format(self.app_path))
            }
        else:
            return '{}'

    def __get_headers(self):
        """Create the api headers"""
        return {
            'accept': 'application/json',
            'Authorization': str(self.token),
        }

    def __get_talks(self):
        """Get all confirmed talks from server"""
        url = '{}?state=confirmed&submission_type=2858&limit=100'.format(
            self.api_url)
        response = requests.get(url, headers=self.headers)
        return response.content

    def __get_short_tutorials(self):
        """Get all confirmed tutorials from server"""
        url = '{}?state=confirmed&submission_type=2860&limit=100'.format(
            self.api_url)
        response = requests.get(url, headers=self.headers)
        return response.content


class CreateMDContent():
    """Create a new MD content for each talk or tutorial"""

    def __init__(self, data=None, post_type=str):
        self.app_path = str(pathlib.Path().resolve())
        self.data = data
        self.post_type = post_type

    def create_content(self):
        json_data = json.loads(self.data)
        for talks in json_data['results']:
            talk = {
                'title': talks['title'],
                'abstract': talks['abstract'],
                'track': talks['track'],
                'duration': talks['duration'],
                'speakers': [],
            }

            for speaker in talks['speakers']:
                talk['speakers'].append({
                    'name': speaker['name'] or '',
                    'biography': speaker['biography'] or '',
                    'avatar': speaker['avatar'] or '',
                })

            self.create_file(content=talk)

    def create_file(self, content):
        """Create the file for the content"""
        content_path = ''

        if self.post_type == 'palestras':
            content_path = '{}/content/palestras'.format(self.app_path)
            if not os.path.exists(content_path):
                os.mkdir(content_path)
        if self.post_type == 'tutoriais':
            content_path = '{}/content/tutoriais'.format(self.app_path)
            if not os.path.exists(content_path):
                os.mkdir(content_path)

        file_name = string_parser(content.get('title'))
        with open('{}/{}.md'.format(content_path, file_name), "w") as f:
            content = dedent(
                "---\n"
                + 'Title: '
                + content.get('title')
                + '\n'
                + 'Date: 2023-12-03 10:20'
                + '\n'
                + 'Description: '
                + content.get('abstract').replace('\r\n', '<br/>')
                + '\n'
                + 'Slug: '
                + string_parser(content.get('title'))
                + '\n'
                + 'Duration: '
                + str(content.get('duration'))
                + '\n'
                + 'Speakers: ' +
                '|'.join(x.get('name')
                         for x in content.get('speakers'))
                + '\n'
                + 'Speakers_biography: ' +
                '|'.join(x.get('biography').replace('\r\n', '<br/>')
                         for x in content.get('speakers'))
                + '\n'
                + 'Speakers_avatar: ' +
                '|'.join(x.get('avatar')
                         for x in content.get('speakers'))
                + '\n\n'
                + "---\n"
                + "\n"
                + markdownify(content.get('abstract'))
            )
            f.write(content)
            f.close()
            print("File created:" + file_name)


def generate_content():
    server = GetDataFromServer()
    CreateMDContent(server.talks, 'palestras').create_content()
    CreateMDContent(server.short_tutorials, 'tutoriais').create_content()


if __name__ == '__main__':
    generate_content()
