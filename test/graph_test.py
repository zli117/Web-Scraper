import pytest

from scraper.graph.actor import Actor
from scraper.graph.graph import Graph
from scraper.graph.movie import Movie


@pytest.fixture
def relationship():
    graph = Graph()
    actor1 = Actor(name='Actor 1', url='http://actor1.com', age=10)
    actor2 = Actor(name='Actor 2', url='http://actor2.com', age=12)
    movie1 = Movie(name='Movie 1', url='http://movie1.com', total_grossing=100,
                   year=2019)
    movie2 = Movie(name='Movie 2', url='http://movie2.com', total_grossing=500,
                   year=2018)
    graph.add_node(actor1)
    graph.add_node(actor2)
    graph.add_node(movie1)
    graph.add_node(movie2)
    graph.add_relationship(movie1.node_id, actor1.node_id).weight = 0.1
    graph.add_relationship(movie2.node_id, actor2.node_id).weight = 0.2
    graph.add_relationship(movie1.node_id, actor2.node_id).weight = 0.3
    return graph, actor1, actor2, movie1, movie2


@pytest.fixture
def graph(relationship):
    return relationship[0]


def test_graph_size(graph):
    assert 4 == len(graph.nodes)
    assert 3 == len(graph.edges)


def test_relationship(relationship):
    _, actor1, actor2, movie1, movie2 = relationship
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


def test_grossing(relationship):
    _, actor1, actor2, movie1, movie2 = relationship
    assert 10 == actor1.grossing
    assert 130 == actor2.grossing


def test_add_duplicate_node(graph):
    movie = Movie(name='Movie n', url='http://movie1.com', total_grossing=100,
                  year=9102)
    assert not graph.add_node(movie)


def test_add_duplicate_relationship(relationship):
    graph, actor1, actor2, movie1, movie2 = relationship
    assert graph.add_relationship(actor1.node_id, movie1.node_id) is None
