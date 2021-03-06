from argparse import ArgumentParser
import os

from elasticsearch import Elasticsearch, helpers
from sklearn.preprocessing import OneHotEncoder

from news_iterator import NewsIterator


def get_options():
    parser = ArgumentParser()
    parser.add_argument('--es-host', dest='es_host', default='http://localhost:9200')
    parser.add_argument('--es-index', dest='es_index', default='news')
    return parser.parse_args()


def get_mapping() -> dict:
    es_mapping = {
        'mappings': {
            'properties': {
                'url': {'type': 'text'},
                'datetime': {'type': 'date'},
                'title': {
                    'type': 'text',
                    'analyzer': 'kuromoji_analyzer'
                },
                'content': {
                    'type': 'text',
                    'analyzer': 'kuromoji_analyzer'
                },
                'content_vector': {
                    'type': 'dense_vector',
                    'dims': 9
                },
                'label': {'type': 'keyword'}
            }
        },
        'settings': {
            'analysis': {
                'analyzer': {
                    'kuromoji_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'kuromoji_tokenizer'
                    }
                }
            }
        }
    }
    return es_mapping


def get_encoder(dir_path:str='text') -> OneHotEncoder:
    directories = [[path] for path in sorted(os.listdir(dir_path)) if os.path.isdir(os.path.join(dir_path, path))]
    encoder = OneHotEncoder().fit(directories)
    return encoder


def main():
    options = get_options()
    es_host = options.es_host
    es_index = options.es_index

    es_client = Elasticsearch(hosts=[es_host])

    # set index
    es_mapping = get_mapping()
    es_client.indices.create(index=es_index, body=es_mapping)

    def load_news(dir_path:str, es_index: str, encoder: OneHotEncoder):
        news_iter = NewsIterator(dir_path, encoder)
        for news in news_iter:
            yield {
                '_index': es_index,
                '_source': news.to_dict()
            }

    # bulk insert
    dir_path = 'text/*/*.txt'
    encoder = get_encoder()
    helpers.bulk(es_client, load_news(dir_path, es_index, encoder))

    print(f'the number of news: {es_client.count(index=es_index)}')
    print('setup done.')
    

if __name__ == '__main__':
    main()
