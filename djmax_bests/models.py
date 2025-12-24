from pydantic import BaseModel, RootModel, Field
from decimal import Decimal, ROUND_FLOOR
from . import constants, api_handler, util


def cut_digits(num: Decimal, digit: int) -> Decimal:
    return num.quantize(Decimal(f'0.{"0" * (digit - 1)}1'), rounding=ROUND_FLOOR)


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
    max_combo: int
    djpower: Decimal
    dlc_code: str

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
    def total_basic_djpower_raw(self) -> Decimal:
        retval = sum(song.djpower for song in self.basic)
        return retval if retval != 0 else Decimal(0)

    @property
    def total_new_djpower_raw(self) -> Decimal:
        retval = sum(song.djpower for song in self.new)
        return retval if retval != 0 else Decimal(0)

    @property
    def total_basic_djpower(self) -> Decimal:
        return self.total_basic_djpower_raw * constants.CONVERT_CONSTANT[self.bmode]

    @property
    def total_new_djpower(self) -> Decimal:
        return self.total_new_djpower_raw * constants.CONVERT_CONSTANT[self.bmode]

    @property
    def total_djpower_raw(self) -> Decimal:
        return self.total_basic_djpower_raw + self.total_new_djpower_raw

    @property
    def total_djpower(self) -> Decimal:
        return self.total_basic_djpower + self.total_new_djpower


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


    @classmethod
    def from_VAResponse(cls, username: str, bmode: str, va_response: VAResponse) -> "DMBests":
        song_db = api_handler.fetch_song_db()
        basic_songs = []
        new_songs = []

        for floor in va_response.floors:
            for pattern in floor.patterns:
                if (pattern.score is None) or (pattern.maxCombo is None) or (pattern.score < Decimal("90.00")):
                    continue
                level = song_db.get_level(pattern.title, bmode, pattern.pattern)
                dm_song = DMSong(
                    songid=pattern.title,
                    title=pattern.name,
                    pattern=pattern.pattern,
                    level=level,
                    score=pattern.score,
                    max_combo=pattern.maxCombo,
                    djpower=pattern.djpower,
                    dlc_code=pattern.dlcCode
                )
                if util.is_new(dm_song.dlc_code, dm_song.songid):
                    new_songs.append(dm_song)
                else:
                    basic_songs.append(dm_song)

        return cls(username=username, bmode=bmode, basic=basic_songs, new=new_songs)

class DMSongSimple(BaseModel):
    songid: int
    pattern: str
    score: Decimal | None
    max_combo: int
    dlc_code: str

class DMScorelist(BaseModel):
    username: str
    bmode: str
    is_sc: bool
    level: int
    scores: list[DMSongSimple]

    @property
    def is_diff_unified(self) -> bool:
        return all(song.pattern == self.scores[0].pattern for song in self.scores)

    @property
    def avg_score(self) -> Decimal:
        if not self.scores:
            return Decimal(0)
        score_sum = Decimal(0)
        count = 0
        for song in self.scores:
            if song.score is not None and song.score > Decimal(0):
                score_sum += song.score
                count += 1
        if count == 0:
            return Decimal(0)
        return cut_digits(score_sum / count, 2)

    @property
    def completion_rate(self) -> Decimal:
        if not self.scores:
            return Decimal(0)
        score_sum = Decimal(0)
        count = 0
        for song in self.scores:
            score_sum += song.score if song.score is not None else Decimal(0)
            count += 1
        if count == 0:
            return Decimal(0)
        return cut_digits(score_sum / count, 2)

    @classmethod
    def from_VAResponse(cls, username: str, bmode: str, is_sc: bool, level: int, va_response: VAResponse) -> "DMScorelist":
        song_db = api_handler.fetch_song_db()
        scores = []

        for floor in va_response.floors:
            for pattern in floor.patterns:
                _level = song_db.get_level(pattern.title, bmode, pattern.pattern)
                if _level != level:
                    continue
                dm_song_simple = DMSongSimple(
                    songid=pattern.title,
                    pattern=pattern.pattern,
                    score=pattern.score,
                    max_combo=pattern.maxCombo if pattern.maxCombo is not None else 0,
                    dlc_code=pattern.dlcCode
                )
                scores.append(dm_song_simple)

        return cls(username=username, bmode=bmode, is_sc=is_sc, level=level, scores=scores)

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
    title: str = Field(alias="name")
    dlc_code: str = Field(alias="dlcCode")
    patterns: DMSongDBPatterns

class DMSongDB(RootModel[list[DMSongDBEntry]]):
    def get_level(self, songid: int, bmode: str, diff: str) -> int:
        for entry in self.root:
            if entry.songid == songid:
                bmode_field = f"BMode_{bmode}"
                bmode_data: DMSongDBBMode = getattr(entry.patterns, bmode_field)
                diff_data: DMSongDBDiff = getattr(bmode_data, diff)
                return diff_data.level
        raise ValueError(f"Song ID {songid} with BMode {bmode} and diff {diff} not found in DB.")

    def get_title(self, songid: int) -> str:
        for entry in self.root:
            if entry.songid == songid:
                return entry.title
        raise ValueError(f"Song ID {songid} not found in DB.")
