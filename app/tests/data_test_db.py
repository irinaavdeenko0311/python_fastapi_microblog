from datetime import datetime

from database import models

users = [models.User(name=name) for name in ("Irina", "Alex", "Olga", "John")]

api_keys = [
    models.UserApiKey(api_key="test", user_id=1),
    models.UserApiKey(api_key="test2", user_id=3),
    models.UserApiKey(api_key="test3", user_id=4),
    models.UserApiKey(api_key="test4", user_id=2),
]

follows = [
    models.Follow(follower_user_id=1, following_user_id=2),
    models.Follow(follower_user_id=1, following_user_id=3),
    models.Follow(follower_user_id=2, following_user_id=1),
    models.Follow(follower_user_id=2, following_user_id=3),
    models.Follow(follower_user_id=3, following_user_id=2),
    models.Follow(follower_user_id=4, following_user_id=1),
]

tweets = [
    models.Tweet(content="tweet1", date_time=datetime.now(), author_id=2),
    models.Tweet(content="tweet2", date_time=datetime.now(), author_id=3),
    models.Tweet(content="tweet3", date_time=datetime.now(), author_id=3),
    models.Tweet(content="tweet4", date_time=datetime.now(), author_id=1),
    models.Tweet(content="tweet5", date_time=datetime.now(), author_id=4),
]

attachments = [
    models.Attachment(link="link1", tweet_id=1),
    models.Attachment(link="link2", tweet_id=1),
    models.Attachment(link="link3", tweet_id=2),
]

likes = [
    models.Like(tweet_id=3, user_id=1),
    models.Like(tweet_id=4, user_id=1),
    models.Like(tweet_id=1, user_id=2),
    models.Like(tweet_id=4, user_id=2),
    models.Like(tweet_id=2, user_id=3),
]

DATA_TEST_DB = users + api_keys + follows + tweets + attachments + likes
