from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.orm.decl_api import DeclarativeMeta, registry

mapper_registry = registry()


class Base(metaclass=DeclarativeMeta):
    __abstract__ = True
    registry = mapper_registry
    metadata = mapper_registry.metadata
    __init__ = mapper_registry.constructor


class User(Base):
    """Модель, описывающая пользователя."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)

    # на кого он подписан:
    followings = relationship(
        "Follow", primaryjoin="User.id==Follow.follower_user_id", lazy="selectin"
    )
    # кто на него подписан:
    followers = relationship(
        "Follow", primaryjoin="User.id==Follow.following_user_id", lazy="selectin"
    )
    tweets = relationship(
        "Tweet", back_populates="author", cascade="all, delete", lazy="selectin"
    )


class UserApiKey(Base):
    """Модель, описывающая api-key пользователя."""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True)
    api_key = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship(
        "User", primaryjoin="UserApiKey.user_id==User.id", lazy="selectin"
    )


class Follow(Base):
    """Модель, описывающая подписки."""

    __tablename__ = "follows"

    id = Column(Integer, primary_key=True)
    follower_user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    following_user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    __table_args__ = (UniqueConstraint("follower_user_id", "following_user_id"),)


class Tweet(Base):
    """Модель, описывающая твит."""

    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    date_time = Column(DateTime, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    author = relationship(
        "User", primaryjoin="Tweet.author_id==User.id", lazy="selectin"
    )
    attachments = relationship(
        "Attachment", primaryjoin="Tweet.id==Attachment.tweet_id", lazy="selectin"
    )
    likes = relationship("Like", primaryjoin="Tweet.id==Like.tweet_id", lazy="selectin")


class Attachment(Base):
    """Модель, описывающая файл, приложенный к твиту."""

    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True)
    link = Column(String(100), nullable=False)
    tweet_id = Column(Integer, ForeignKey("tweets.id", ondelete="SET NULL"))


class Like(Base):
    """Модель, описывающая лайки твита."""

    __tablename__ = "likes"

    id = Column(Integer, primary_key=True)
    tweet_id = Column(
        Integer, ForeignKey("tweets.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    user = relationship("User", primaryjoin="Like.user_id==User.id", lazy="selectin")
    __table_args__ = (UniqueConstraint("tweet_id", "user_id"),)
