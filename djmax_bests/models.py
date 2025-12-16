from pydantic import BaseModel, RootModel, Field
from decimal import Decimal
from .constants import NEW_DLC, CONVERT_CONSTANT
from . import api_handler


class VAPattern(BaseModel):
    title: int
    name: str
    # composer: str
    pattern: str
    # scFloor: str
    score: Decimal | None
    maxCombo: int | None
    djpower: Decimal
    # rating: Decimal
    # updatedAt: str(date-like object) | None
    # dlc: str
    dlcCode: str

class VAFloor(BaseModel):
    # floorNumber: int
    patterns: list[VAPattern]

class VAResponse(BaseModel):
    # success: bool
    # board: str
    # button: str
    # totalCount: int
    floors: list[VAFloor]

class DMSong(BaseModel):
    songid: int
    title: str
    pattern: str # MX/SC...
    level: int
    score: Decimal
    maxCombo: int
    djpower: Decimal

class DMBests(BaseModel):
    username: str
    bmode: str
    basic: list[DMSong]
    new: list[DMSong]

    @property
    def basic_len(self) -> int:
        return len(self.basic)

    @property
    def new_len(self) -> int:
        return len(self.new)

    @property
    def basic_min_djpower(self) -> Decimal:
        if not self.basic or self.basic_len < 70:
            return Decimal(0)
        return min(self.basic, key=lambda song: song.djpower).djpower

    @property
    def basic_max_djpower(self) -> Decimal:
        if not self.basic:
            return Decimal(0)
        return max(self.basic, key=lambda song: song.djpower).djpower

    @property
    def new_min_djpower(self) -> Decimal:
        if not self.new or self.new_len < 30:
            return Decimal(0)
        return min(self.new, key=lambda song: song.djpower).djpower

    @property
    def new_max_djpower(self) -> Decimal:
        if not self.new:
            return Decimal(0)
        return max(self.new, key=lambda song: song.djpower).djpower

    @property
    def total_basic_djpower(self) -> Decimal:
        retval = sum(song.djpower for song in self.basic)
        return retval if retval != 0 else Decimal(0)

    @property
    def total_new_djpower(self) -> Decimal:
        retval = sum(song.djpower for song in self.new)
        return retval if retval != 0 else Decimal(0)

    @property
    def total_djpower_raw(self) -> Decimal:
        return self.total_basic_djpower + self.total_new_djpower

    @property
    def total_djpower(self) -> Decimal:
        return self.total_djpower_raw * CONVERT_CONSTANT


    def __add__(self, other: "DMBests") -> "DMBests":
        combined_basic = self.basic + other.basic
        combined_new = self.new + other.new
        return DMBests(username=self.username, bmode=self.bmode, basic=combined_basic, new=combined_new)

    def justify(self):
        self.basic.sort(key=lambda song: song.djpower, reverse=True)
        self.new.sort(key=lambda song: song.djpower, reverse=True)
        if self.basic_len > 70:
            self.basic = self.basic[:70]
        if self.new_len > 30:
            self.new = self.new[:30]


    @staticmethod
    def from_VAResponse(username: str, bmode: str, va_response: VAResponse) -> "DMBests":
        song_db = api_handler.fetch_song_db()
        basic_songs = []
        new_songs = []

        for floor in va_response.floors:
            for pattern in floor.patterns:
                if (pattern.score is None) or (pattern.maxCombo is None) or (pattern.score < Decimal("90.00")):
                    continue
                level = song_db.get_level(pattern.title, bmode, pattern.pattern)
                if level is None:
                    raise ValueError(f"Level not found for songid {pattern.title}, bmode {bmode}, pattern {pattern.pattern}")
                dm_song = DMSong(
                    songid=pattern.title,
                    title=pattern.name,
                    pattern=pattern.pattern,
                    level=level,
                    score=pattern.score,
                    maxCombo=pattern.maxCombo,
                    djpower=pattern.djpower
                )
                if pattern.dlcCode in NEW_DLC:
                    new_songs.append(dm_song)
                else:
                    basic_songs.append(dm_song)

        return DMBests(username=username, bmode=bmode, basic=basic_songs, new=new_songs)

class DMSongDBDiff(BaseModel):
    level: int
    # floor: Decimal
    # rating: int

class DMSongDBBMode(BaseModel):
    NM: DMSongDBDiff | None = None
    HD: DMSongDBDiff | None = None
    MX: DMSongDBDiff | None = None
    SC: DMSongDBDiff | None = None

class DMSongDBPatterns(BaseModel):
    BMode_4: DMSongDBBMode = Field(alias="4B")
    BMode_5: DMSongDBBMode = Field(alias="5B")
    BMode_6: DMSongDBBMode = Field(alias="6B")
    BMode_8: DMSongDBBMode = Field(alias="8B")

class DMSongDBEntry(BaseModel):
    songid: int = Field(alias="title")
    patterns: DMSongDBPatterns

class DMSongDB(RootModel[list[DMSongDBEntry]]):
    def get_level(self, songid: int, bmode: str, diff: str) -> int | None:
        for entry in self.root:
            if entry.songid == songid:
                bmode_field = f"BMode_{bmode}"
                bmode_data: DMSongDBBMode = getattr(entry.patterns, bmode_field)
                diff_data: DMSongDBDiff | None = getattr(bmode_data, diff)
                if diff_data is None:
                    return None
                return diff_data.level
        return None
