# Tests
This directory is for tests by Docoker-compose.

## Enviroment
- docker 17.12.0
- docker-compose 1.18.0

## How to run tests
In root directory of this repository.
'''
docker-compose build
docker-compose run
'''

Each tests file in this directory run as docker containor.
How run is see '''Dockerfile''' and '''docker-compose.yml''' in root directory of this repository.

## Files
Pair test files is run as one of tests.
- Get Old Block and Resolv
    - test_node1.py:Old Block receive
    - test_node2.py:Old Block send
- Get Orphan Block and Resolv
    - test_node3.py:Orphan Block receive
    - test_node4.py:Orphan Block send
- Get Orphan and Conflict Block and Resolv
    - test_node5.py:Orphan and Conflict Block receive
    - test_node6.py:Orphan and Conflict Block send
