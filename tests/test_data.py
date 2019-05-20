# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import elasticsearch.exceptions as elasticexceptions
import elasticsearch_dsl as es


class DataDocType(es.Document):
    """Elasticsearch test model"""
    first_name = es.Keyword()
    last_name = es.Keyword()
    city = es.Text()
    skills = es.Keyword()
    birthday = es.Date()
    is_active = es.Boolean()
    score = es.Integer()
    location = es.GeoPoint()
    description = es.Text()


    class Index:
        name = 'test'


def create_test_index():
    """Initialize test index"""
    DataDocType.init()


DATA = [
    {
        '_index': 'test',
        '_type': 'doc',
        '_id': '1',
        '_source': {
            'first_name': 'Zofia',
            'last_name': 'Marie',
            'city': 'Warsaw',
            'skills': ['python', 'sql', 'js'],
            'birthday': '1985-03-17T12:20:09',
            'is_active': True,
            'score': 100,
            "location": {
                "lon": -8.2177734375, "lat": 43.16512263158296   # Spain
            },
            'description': """
                He had made one careless blunder though, because he had skimped
                a bit on his preparatory research.
            """
        },
    },
    {
        '_index': 'test',
        '_type': 'doc',
        '_id': '2',
        '_source': {
            'first_name': 'Callisto',
            'last_name': 'Alexandra',
            'city': 'San Jose',
            'skills': ['java', 'c#', 'sql'],
            'birthday': '1990-02-07T15:22:09',
            'is_active': True,
            'score': 200,
            "location": {
                "lon": -2.2412109375, "lat": 42.98857645832184  # Spain
            },
            'description': """
                The information he had gathered had led him to choose the name
                Ford Prefect as being nicely inconspicuous.
            """
        },
    },
    {
        '_index': 'test',
        '_type': 'doc',
        '_id': '3',
        '_source': {
            'first_name': 'Samantha',
            'last_name': 'Arundhati',
            'city': 'Manila',
            'skills': ['html', 'js', 'css'],
            'birthday': '1987-05-27T16:08:02',
            'is_active': False,
            'score': 100,
            "location": {
                "lon": 2.96630859375, "lat": 42.147114459220994  # Spain
            },
            'description': """
                He struck most of the friends he had made on Earth as an
                eccentric, but a harmless one – an unruly boozer with some
                oddish habits.
            """
        },
    },
    {
        '_index': 'test',
        '_type': 'doc',
        '_id': '4',
        '_source': {
            'first_name': 'Crocetta',
            'last_name': 'Florette',
            'city': 'Rome',
            'skills': ['python', 'go', 'sql', 'django'],
            'birthday': '1991-04-07T16:38:29',
            'is_active': True,
            'score': 450,
            "location": {
                "lon": -3.40576171875, "lat": 37.16031654673677  # Spain
            },
            'description': """
                Thereafter, staggering semi-paralytic down the night streets he
                would of ten ask passing policemen if they knew the way to
                Betelgeuse.
            """
        },
    },
    {
        '_index': 'test',
        '_type': 'doc',
        '_id': '5',
        '_source': {
            'first_name': 'Akhmad',
            'last_name': 'Farouk',
            'city': 'Ottawa',
            'skills': ['python', 'flask', 'django'],
            'birthday': '1992-01-21T12:18:09',
            'is_active': True,
            'score': 10,
            'location': {
                "lon": -121.9921875, "lat": 46.6795944656402  # USA
            },
            'description': """
                Ford Prefect was desperate that any flying saucer at all would
                arrive soon because fifteen years was a long time to get
                stranded anywhere, particularly somewhere as mindboggingly dull
                as the Earth.
            """
        },
    },
    {
        '_index': 'test',
        '_type': 'doc',
        '_id': '6',
        '_source': {
            'first_name': 'Rohan',
            'last_name': 'Dand',
            'city': 'Ottawa',
            'skills': ['ruby', 'ror', 'sql'],
            'birthday': '1991-09-07T11:20:29',
            'is_active': False,
            'score': 1000,
            'location': {
                "lon": -74.35546875, "lat": 40.111688665595956  # USA
            },
            'description': """
                Ford wished that a flying saucer would arrive soon because he
                knew how to flag flying saucers down and get lifts from them.
            """
        },
    },
    {
        '_index': 'test',
        '_type': 'doc',
        '_id': '7',
        '_source': {
            'first_name': 'Odell',
            'last_name': 'Leonidas',
            'city': 'Rome',
            'skills': ['angular', 'react', 'css'],
            'birthday': '1993-09-20T16:20:08',
            'is_active': True,
            'score': 500,
            'location': {
                "lon": -80.244140625, "lat": 25.928407032694118  # USA
            },
            'description': """
                He knew how to see the Marvels of the Universe for less than
                thirty Altairan dollars a day.
            """
        },
    },
    {
        '_index': 'test',
        '_type': 'doc',
        '_id': '8',
        '_source': {
            'first_name': 'Markus',
            'last_name': 'Emmeline',
            'city': 'Ottawa',
            'skills': ['php', 'html'],
            'birthday': '1991-04-26T16:48:03',
            'is_active': False,
            'score': 600,
            'location': {
                "lon": 131.044921875, "lat": -12.983147716796566 # Australian
            },
            'description': """
                In fact, Ford Prefect was a roving researcher for that wholly
                remarkable book The Hitchhiker’s Guide to the Galaxy.
            """
        },
    },
    {
        '_index': 'test',
        '_type': 'doc',
        '_id': '9',
        '_source': {
            'first_name': 'Gabriel',
            'last_name': 'Sara',
            'city': 'Baku',
            'skills': ['js', 'css', 'html', 'sql'],
            'birthday': '1988-08-27T16:18:29',
            'is_active': True,
            'score': 100,
            'location': {
                "lon": 138.955078125, "lat": -34.161818161230386  # Australian
            },
            'description': """
                Human beings are great adaptors, and by lunchtime life in the
                environs of Arthur’s house had settled into a steady routine.
            """
        },
    },
    {
        '_index': 'test',
        '_type': 'doc',
        '_id': '10',
        '_source': {
            'first_name': 'Merilyn',
            'last_name': 'Barrie',
            'city': 'Rabat',
            'skills': ['python', 'sql'],
            'birthday': '1992-03-11T11:28:09',
            'is_active': False,
            'score': 600,
            'location': {
                "lon": 121.322021484375, "lat": 24.986058021167594  # Taiwan
            },
            'description': """
                Arthur looked up and squinting into the sun was startled to see
                Ford Prefect standing above him.
            """
        },
    },
    {
        '_index': 'test',
        '_type': 'doc',
        '_id': '11',
        '_source': {
            'first_name': 'Sunil',
            'last_name': 'Allan',
            'city': 'Lima',
            'skills': ['java', 'android'],
            'birthday': '1991-05-20T17:28:32',
            'is_active': True,
            'score': 900,
            'location': {
                "lon": 120.38818359375, "lat": 23.815500848699656  # Taiwan
            },
            'description': """
                Then suddenly he squatted down beside Arthur.
            """
        },
    },
    {
        '_index': 'test',
        '_type': 'doc',
        '_id': '12',
        '_source': {
            'first_name': 'Navin',
            'last_name': 'Mladen',
            'city': 'Doha',
            'skills': ['swift', 'c'],
            'birthday': '1990-04-23T16:48:09',
            'is_active': True,
            'score': 10,
            'location': {
                "lon": 121.44287109374999, "lat": 23.71495350699027  # Taiwan
            },
            'description': """
                Ford stared at Arthur, and Arthur was astonished to find that
                his will was beginning to weaken.
            """
        },
    },
    {
        '_index': 'test',
        '_type': 'doc',
        '_id': '13',
        '_source': {
            'first_name': 'Helga',
            'last_name': 'Terell',
            'city': 'Oslo',
            'skills': ['c++', 'c#'],
            'birthday': '1989-01-20T06:18:02',
            'is_active': True,
            'score': 200,
            'location': {
                "lon": 120.78369140624999, "lat":22.268764039073968  # Taiwan
            },
            'description': """
                Two contestants would sit either side of a table, with a glass
                in front of each of them.
            """
        },
    },
    {
        '_index': 'test',
        '_type': 'doc',
        '_id': '14',
        '_source': {
            'first_name': 'Lynsey',
            'last_name': 'Brynja',
            'city': 'Oslo',
            'skills': ['c++', 'java'],
            'birthday': '1984-07-21T12:18:29',
            'is_active': True,
            'score': 100,
            'location': {
                "lon": 120.95947265624999, "lat": 23.83560098662095  # Taiwan
            },
            'description': """
                The game was not unlike the Earth game called Indian Wrestling,
                and was played like this.
            """
        },
    },
]


class TestCreateIndex:

    def setup_method(self):
        pass

    def test_index(self):
        """Initialize test index"""
        DataDocType.init()
        index = es.Index("test")

        try:
            index.delete()
        except elasticexceptions.NotFoundError:
            assert False