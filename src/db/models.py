from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    ForeignKey,
    Text,
    UniqueConstraint,
    TIMESTAMP,
    BigInteger,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class UserModel(Base):
    __tablename__ = "User"

    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False)

    subscribes = relationship("SubscribeModel", back_populates="user")
    wishlists = relationship("WishlistModel", back_populates="user")


class OTTModel(Base):
    __tablename__ = "OTT"

    ott_id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)
    logo_url = Column(String(255), nullable=False)

    subscribes = relationship("SubscribeModel", back_populates="ott")
    availabilities = relationship("AvailabilityModel", back_populates="ott")


class SubscribeModel(Base):
    __tablename__ = "Subscribe"

    subscribe_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("User.user_id"), nullable=False)
    ott_id = Column(BigInteger, ForeignKey("OTT.ott_id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)

    user = relationship("UserModel", back_populates="subscribes")
    ott = relationship("OTTModel", back_populates="subscribes")


class ProgramModel(Base):
    __tablename__ = "Program"

    program_id = Column(BigInteger, primary_key=True, autoincrement=True)
    crawling_id = Column(BigInteger, unique=True, nullable=False)
    title = Column(String(100), nullable=False)
    genre = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    thumbnail_url = Column(String(255), nullable=False)
    backdrop_url = Column(String(255), nullable=True)
    running_time = Column(Integer, nullable=True)
    ranking = Column(Integer, nullable=True)
    updated_at = Column(
        TIMESTAMP, nullable=False, default=func.now(), onupdate=func.now()
    )

    availabilities = relationship(
        "AvailabilityModel", back_populates="program", cascade="all, delete-orphan"
    )
    wishlists = relationship("WishlistModel", back_populates="program")


class AvailabilityModel(Base):
    __tablename__ = "Program_Availability"

    availability_id = Column(BigInteger, primary_key=True, autoincrement=True)
    program_id = Column(BigInteger, ForeignKey("Program.program_id"), nullable=False)
    ott_id = Column(BigInteger, ForeignKey("OTT.ott_id"), nullable=False)
    url = Column(String(255), nullable=False)
    release_date = Column(Date, nullable=True)
    expire_date = Column(Date, nullable=True)
    updated_at = Column(
        TIMESTAMP, nullable=False, default=func.now(), onupdate=func.now()
    )

    program = relationship("ProgramModel", back_populates="availabilities")
    ott = relationship("OTTModel", back_populates="availabilities")

    __table_args__ = (UniqueConstraint("program_id", "ott_id", name="uix_program_ott"),)


class WishlistModel(Base):
    __tablename__ = "Wishlist"

    wishlist_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("User.user_id"), nullable=False)
    program_id = Column(BigInteger, ForeignKey("Program.program_id"), nullable=False)

    user = relationship("UserModel", back_populates="wishlists")
    program = relationship("ProgramModel", back_populates="wishlists")

    # filepath: /Users/mingyu/SE-MoaBom-crawler/src/db/models.py


from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    ForeignKey,
    Text,
    UniqueConstraint,
    TIMESTAMP,
    BigInteger,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class UserModel(Base):
    __tablename__ = "User"

    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False)

    subscribes = relationship("SubscribeModel", back_populates="user")
    wishlists = relationship("WishlistModel", back_populates="user")


class OTTModel(Base):
    __tablename__ = "OTT"

    ott_id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)
    logo_url = Column(String(255), nullable=False)

    subscribes = relationship("SubscribeModel", back_populates="ott")
    availabilities = relationship("AvailabilityModel", back_populates="ott")


class SubscribeModel(Base):
    __tablename__ = "Subscribe"

    subscribe_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("User.user_id"), nullable=False)
    ott_id = Column(BigInteger, ForeignKey("OTT.ott_id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)

    user = relationship("UserModel", back_populates="subscribes")
    ott = relationship("OTTModel", back_populates="subscribes")


class ProgramModel(Base):
    __tablename__ = "Program"

    program_id = Column(BigInteger, primary_key=True, autoincrement=True)
    crawling_id = Column(BigInteger, unique=True, nullable=False)
    title = Column(String(100), nullable=False)
    genre = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    thumbnail_url = Column(String(255), nullable=False)
    backdrop_url = Column(String(255), nullable=True)
    running_time = Column(Integer, nullable=True)
    ranking = Column(Integer, nullable=True)
    updated_at = Column(
        TIMESTAMP, nullable=False, default=func.now(), onupdate=func.now()
    )

    availabilities = relationship(
        "AvailabilityModel", back_populates="program", cascade="all, delete-orphan"
    )
    wishlists = relationship("WishlistModel", back_populates="program")


class AvailabilityModel(Base):
    __tablename__ = "Program_Availability"

    availability_id = Column(BigInteger, primary_key=True, autoincrement=True)
    program_id = Column(BigInteger, ForeignKey("Program.program_id"), nullable=False)
    ott_id = Column(BigInteger, ForeignKey("OTT.ott_id"), nullable=False)
    url = Column(String(255), nullable=False)
    release_date = Column(Date, nullable=True)
    expire_date = Column(Date, nullable=True)
    updated_at = Column(
        TIMESTAMP, nullable=False, default=func.now(), onupdate=func.now()
    )

    program = relationship("ProgramModel", back_populates="availabilities")
    ott = relationship("OTTModel", back_populates="availabilities")

    __table_args__ = (UniqueConstraint("program_id", "ott_id", name="uix_program_ott"),)


class WishlistModel(Base):
    __tablename__ = "Wishlist"

    wishlist_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("User.user_id"), nullable=False)
    program_id = Column(BigInteger, ForeignKey("Program.program_id"), nullable=False)

    user = relationship("UserModel", back_populates="wishlists")
    program = relationship("ProgramModel", back_populates="wishlists")

    __table_args__ = (
        UniqueConstraint("user_id", "program_id", name="uix_user_program"),
    )
