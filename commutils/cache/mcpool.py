import functools
from commutils.log import log as logging
from commutils.cache import _memcache_pool

LOG = logging.getLogger(__name__)


# Helper to ease backend refactoring
class ClientProxy(object):
    def __init__(self, client_pool):
        self.client_pool = client_pool

    def _run_method(self, __name, *args, **kwargs):
        with self.client_pool.acquire() as client:
            return getattr(client, __name)(*args, **kwargs)

    def __getattr__(self, name):
        return functools.partial(self._run_method, name)


class PooledMemcachedBackend():
    def __init__(self, url, arguments={}):
        self.client_pool = _memcache_pool.MemcacheClientPool(
            url,
            # arguments for memcache.Client
            arguments={
                'dead_retry': arguments.get('dead_retry', 5 * 60),
                'socket_timeout': arguments.get('socket_timeout', 3),
            },
            # arguments for memcache pool
            maxsize=arguments.get('pool_maxsize', 10),
            unused_timeout=arguments.get('pool_unused_timeout', 60),
            conn_get_timeout=arguments.get('pool_connection_get_timeout', 10),
        )

    @property
    def client(self):
        # get a memcache connection from pool and call memcache client's method
        return ClientProxy(self.client_pool)
