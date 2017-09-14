def publish(server_name):
    import redis
    redis_session1 = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)
    ps = redis_session1.pubsub()
    ps.subscribe(['servername'])
    redis_session1.publish('servername', server_name)