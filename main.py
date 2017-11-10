# -*- coding: utf-8 -*-
import logging

from blockchain import Blockchain
from transaction import Transaction
from messaging import Messaging

# For debug
from IPython import embed
from IPython.terminal.embed import InteractiveShellEmbed


# logging
logger = logging.getLogger("blcokchainlog")
logger.setLevel(10)
fh = logging.FileHandler('logger.log')
logger.addHandler(fh)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
fh.setFormatter(formatter)


transaction = Transaction()
blockchain = Blockchain(transaction)
message = Messaging(blockchain, transaction)

embed()
