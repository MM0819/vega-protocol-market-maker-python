from gql import gql, Client
from gql.transport.websockets import WebsocketsTransport


class VegaGraphQLClient:
    def __init__(self, graphql_url: str):
        self.gql_url = graphql_url
