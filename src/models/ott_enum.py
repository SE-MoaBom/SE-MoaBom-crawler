class OTTPlatformMeta(type):
    def __iter__(cls):
        for key in cls._DATA.keys():
            yield getattr(cls, key)


class OTTPlatform(metaclass=OTTPlatformMeta):
    _DATA = {
        "NETFLIX": (
            "넷플릭스",
            5500,
            "https://static.kinolights.com/icon/btn_squircle_netflix.png",
        ),
        "TVING": (
            "티빙",
            5500,
            "https://static.kinolights.com/icon/btn_squircle_tving.png",
        ),
        "COUPANG_PLAY": (
            "쿠팡플레이",
            7890,
            "https://static.kinolights.com/icon/btn_squircle_coupangplay.png",
        ),
        "WAVVE": (
            "웨이브",
            5500,
            "https://static.kinolights.com/icon/btn_squircle_wavve.png",
        ),
        "DISNEY_PLUS": (
            "디즈니+",
            9900,
            "https://static.kinolights.com/icon/btn_squircle_disneyplus.png",
        ),
        "WATCHA": (
            "왓챠",
            7900,
            "https://static.kinolights.com/icon/btn_squircle_watcha.png",
        ),
        "LAFTEL": (
            "라프텔",
            4900,
            "https://static.kinolights.com/icon/btn_squircle_laftel.png",
        ),
        "U_PLUS_MOBILE_TV": (
            "U+모바일tv",
            6490,
            "https://static.kinolights.com/icon/btn_squircle_lguplus.png",
        ),
        "AMAZON_PRIME_VIDEO": (
            "아마존 프라임 비디오",
            5500,
            "https://static.kinolights.com/icon/btn_squircle_amazon.png",
        ),
        "CINEFOX": (
            "씨네폭스",
            9900,
            "https://static.kinolights.com/icon/btn_squircle_cinefox.png",
        ),
    }

    def __init__(self, name, price, logo_url):
        self.name = name
        self.price = price
        self.logo_url = logo_url

    @property
    def value(self):
        return self.name

    def __repr__(self):
        return f"<OTTPlatform: {self.name}>"

    @classmethod
    def from_korean(cls, name: str):
        if not name:
            return None

        clean_name = name.replace("\u200b", "").strip()

        for key in cls._DATA.keys():
            instance = getattr(cls, key)
            if instance.name == clean_name:
                return instance

        return None


for key, (name, price, url) in OTTPlatform._DATA.items():
    setattr(OTTPlatform, key, OTTPlatform(name, price, url))
