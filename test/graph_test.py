import json

import pytest

from scraper.graph.actor import Actor
from scraper.graph.entity_type import EntityType
from scraper.graph.graph import Graph
from scraper.graph.movie import Movie


@pytest.fixture
def elements():
    graph = Graph()
    actor1 = Actor(name='Actor 1', url='http://actor1.com', age=10)
    actor2 = Actor(name='Actor 2', url='http://actor2.com', age=12)
    movie1 = Movie(name='Movie 1', url='http://movie1.com', total_grossing=100,
                   year=2019)
    movie2 = Movie(name='Movie 2', url='http://movie2.com', total_grossing=500,
                   year=2018)
    movie3 = Movie(name='Movie 3', url='http://movie3.com', total_grossing=100,
                   year=2018)
    graph.add_node(actor1)
    graph.add_node(actor2)
    graph.add_node(movie1)
    graph.add_node(movie2)
    graph.add_node(movie3)
    graph.add_relationship(movie1.node_id, actor1.node_id).weight = 0.1
    graph.add_relationship(movie2.node_id, actor2.node_id).weight = 0.2
    graph.add_relationship(movie1.node_id, actor2.node_id).weight = 0.3
    return graph, actor1, actor2, movie1, movie2, movie3


def test_graph_size(elements):
    graph = elements[0]
    assert 5 == len(graph.nodes)
    assert 3 == len(graph.edges)


def test_relationship(elements):
    _, actor1, actor2, movie1, movie2, movie3 = elements
    assert 1 == len(actor1.get_edges())
    assert 2 == len(actor2.get_edges())
    assert movie1 in actor1.get_edges()[0].ends
    assert actor1 in actor1.get_edges()[0].ends
    assert 0.1 == actor1.get_edges()[0].weight
    assert actor1.has_peer(movie1)
    assert movie1.has_peer(actor1)
    assert movie1.has_peer(actor2)
    assert movie2.has_peer(actor2)
    assert not movie1.has_peer(movie2)
    assert not actor1.has_peer(actor2)
    assert not movie2.has_peer(actor1)
    assert movie1 != movie2
    assert movie1 == movie1


def test_grossing(elements):
    _, actor1, actor2, movie1, movie2, movie3 = elements
    assert 10 == actor1.grossing
    assert 130 == actor2.grossing


def test_add_duplicate_node(elements):
    graph = elements[0]
    movie = Movie(name='Movie n', url='http://movie1.com', total_grossing=100,
                  year=9102)
    assert not graph.add_node(movie)


def test_add_duplicate_relationship(elements):
    graph, actor1, actor2, movie1, movie2, movie3 = elements
    assert graph.add_relationship(actor1.node_id, movie1.node_id) is None


def test_query_nodes(elements):
    graph, actor1, actor2, movie1, movie2, movie3 = elements
    movies_18 = graph.query_nodes({'year': 2018, 'type': EntityType.MOVIE})
    assert 2 == len(movies_18)
    movies_18 = graph.query_nodes({'year': 2018})
    assert 2 == len(movies_18)
    assert movie3 in movies_18
    assert movie2 in movies_18

    actors = graph.query_nodes({'type': EntityType.ACTOR})
    assert 2 == len(actors)
    assert actor1 in actors
    assert actor2 in actors


def test_serialize(elements):
    graph, actor1, actor2, movie1, movie2, movie3 = elements
    json_str = graph.serialize()
    json_dict = json.loads(json_str)
    assert 'nodes' in json_dict
    assert 'edges' in json_dict
    graph_loaded = Graph()
    graph_loaded.deserialize(json_str)
    assert graph_loaded.serialize() == graph.serialize()
    assert actor1 in graph_loaded.query_nodes({'type': EntityType.ACTOR})


def test_serialize_failed(elements):
    graph, actor1, actor2, movie1, movie2, movie3 = elements
    json_str = graph.serialize()
    json_dict = json.loads(json_str)
    json_dict['nodes'][0]['doesn\'t exist'] = 1
    graph_loaded = Graph()
    assert not graph_loaded.deserialize(json.dumps(json_dict))

    graph_loaded = Graph()
    json_str = graph.serialize()
    json_dict = json.loads(json_str)
    # Invalid id
    for node in json_dict['nodes']:
        node['node_id'] = 0
    assert not graph_loaded.deserialize(json.dumps(json_dict))

    graph_loaded = Graph()
    json_str = graph.serialize()
    json_dict = json.loads(json_str)
    # Duplicate edge
    json_dict['edges'].append({'ends': [3, 1], 'weight': 0.1})
    assert not graph_loaded.deserialize(json.dumps(json_dict))
