import time
from redis import Redis
from flask import current_app

redis = None


class FakeRedis:
  """Redis mock used for testing."""
  def __init__(self):
    self.v = {}
    self.last_key = None

  def pipeline(self):
    return self

  def incr(self, key):
    if self.v.get(key, None) is None:
      self.v[key] = 0
    self.v[key] += 1
    self.last_key = key

  def expireat(self, key, exp_time):
    pass

  def execute(self):
    return [self.v[self.last_key]]


class RateLimit:
  expiration_window = 10

  def __init__(self, key_prefix, limit, per):
    global redis
    if redis is None and current_app.config['USE_RATE_LIMITS']:
      if current_app.config['TESTING']:
        redis = FakeRedis()
      else:  # pragma: no cover
        redis_host = current_app.config.get("REDIS_HOST", "localhost")
        redis_port = current_app.config.get("REDIS_PORT", 6379)
        redis_db = current_app.config.get("REDIS_DB", 0)
        redis = Redis(host=redis_host, port=redis_port, db=redis_db)

    self.reset = (int(time.time()) // per) * per + per
    self.key = key_prefix + str(self.reset)
    self.limit = limit
    self.per = per
    p = redis.pipeline()
    p.incr(self.key)
    p.expireat(self.key, self.reset + self.expiration_window)
    self.current = min(p.execute()[0], limit)

  @property
  def remaining(self):
    return self.limit - self.current

  @property
  def over_limit(self):
    return self.current >= self.limit
