from decimal import Decimal
from pydantic import BaseModel, RootModel, Field

from . import constants, util


class DMSongDBDiff(BaseModel):
    level: int
    floorName: Decimal | None = None
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
    def get_level(self, songid: int, bmode: int, diff: str) -> int:
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

    def get_songs_by_level(self, level: int, bmode: int, is_sc: bool) -> list[tuple[int, str, Decimal | None, str]]:
        matching_songs = []
        for entry in self.root:
            bmode_field = f"BMode_{bmode}"
            bmode_data: DMSongDBBMode = getattr(entry.patterns, bmode_field)
            if is_sc:
                diff_data = bmode_data.SC
                if diff_data is not None and diff_data.level == level:
                    matching_songs.append((entry.songid, "SC", diff_data.floorName, entry.dlc_code))
            else:
                for diff in ["NM", "HD", "MX"]:
                    diff_data = getattr(bmode_data, diff)
                    if diff_data is not None and diff_data.level == level:
                        matching_songs.append((entry.songid, diff, diff_data.floorName, entry.dlc_code))
        return matching_songs

    def get_new_songs_sc(self, bmode: int) -> list[tuple[int, str, int, str]]:
        new_songs = []
        for entry in self.root:
            bmode_field = f"BMode_{bmode}"
            bmode_data: DMSongDBBMode = getattr(entry.patterns, bmode_field)
            diff_data = bmode_data.SC
            if diff_data is not None and util.is_new(entry.dlc_code, entry.songid):
                new_songs.append((entry.songid, "SC", diff_data.level, entry.dlc_code))
        return new_songs


class VARecord(BaseModel):
    title: int
    name: str
    dlcCode: str
    pattern: str
    level: int
    floorName: Decimal | None
    score: Decimal
    maxCombo: bool
    djpower: Decimal
    # rating: Decimal
    # updatedAt: str(date-like object) | None

class VAResponse(BaseModel):
    # success: bool
    nickname: str
    button: int
    # count: int
    records: list[VARecord]


class DMSong(BaseModel):
    songid: int
    title: str
    pattern: str # MX/SC...
    level: int
    score: Decimal
    max_combo: bool
    djpower: Decimal
    dlc_code: str

class DMBests(BaseModel):
    username: str
    bmode: int
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
        return util.cut_digits(self.total_basic_djpower_raw * constants.CONVERT_CONSTANT[self.bmode], 4)

    @property
    def total_new_djpower(self) -> Decimal:
        return util.cut_digits(self.total_new_djpower_raw * constants.CONVERT_CONSTANT[self.bmode], 4)

    @property
    def total_djpower_raw(self) -> Decimal:
        return self.total_basic_djpower_raw + self.total_new_djpower_raw

    @property
    def total_djpower(self) -> Decimal:
        ret_val = util.cut_digits(self.total_djpower_raw * constants.CONVERT_CONSTANT[self.bmode], 4)
        if ret_val > Decimal("10000.0000"):
            return Decimal("10000.0000")
        return ret_val


    def __add__(self, other: "DMBests") -> "DMBests":
        combined_basic = self.basic + other.basic
        combined_new = self.new + other.new
        return DMBests(username=self.username, bmode=self.bmode, basic=combined_basic, new=combined_new)

    def organize(self):
        self.basic.sort(key=lambda song: song.djpower, reverse=True)
        self.new.sort(key=lambda song: song.djpower, reverse=True)
        if self.basic_len > 70:
            self.basic = self.basic[:70]
        if self.new_len > 30:
            self.new = self.new[:30]


    @classmethod
    def from_VAResponse(cls, va_resp_basic: VAResponse, va_resp_new: VAResponse) -> "DMBests":
        basic_songs = []
        new_songs = []

        def __make_list(va_response: VAResponse, is_new: bool):
            for record in va_response.records:
                if (record.score is None) or (record.maxCombo is None) or (record.score < Decimal("90.00")):
                    continue
                dm_song = DMSong(
                    songid=record.title,
                    title=record.name,
                    pattern=record.pattern,
                    level=record.level,
                    score=record.score,
                    max_combo=record.maxCombo,
                    djpower=record.djpower,
                    dlc_code=record.dlcCode
                )
                if is_new:
                    new_songs.append(dm_song)
                else:
                    basic_songs.append(dm_song)

        __make_list(va_resp_basic, False)
        __make_list(va_resp_new, True)

        return cls(username=va_resp_basic.nickname, bmode=va_resp_basic.button, basic=basic_songs, new=new_songs)

    @classmethod
    def get_theoretical_bests(cls, bmode: int, song_db: DMSongDB) -> "DMBests":
        basic_songs = []
        new_songs = []

        for entry in song_db.root:
            entry_info = entry.patterns.__getattribute__(f"BMode_{bmode}").SC
            if entry_info is None:
                continue
            coeff = util.diff_coeff(entry_info.level, True)
            theoretical_power = util.djpower_pp(coeff)
            dm_song = DMSong(
                songid=entry.songid,
                title=entry.title,
                pattern="SC",
                level=entry_info.level,
                score=Decimal("100.00"),
                max_combo=True,
                djpower=theoretical_power,
                dlc_code=entry.dlc_code
            )
            if util.is_new(dm_song.dlc_code, dm_song.songid):
                new_songs.append(dm_song)
            else:
                basic_songs.append(dm_song)

        return cls(username="Max DJPower", bmode=bmode, basic=basic_songs, new=new_songs)


class DMSongSimple(BaseModel):
    songid: int
    pattern: str
    score: Decimal | None
    max_combo: bool
    dlc_code: str

class DMScorelistFloor(BaseModel):
    floor_constant: Decimal
    songs: list[DMSongSimple]

class DMScorelist(BaseModel):
    username: str
    bmode: int
    is_sc: bool
    level: int
    floors: list[DMScorelistFloor]

    @property
    def avg_score(self) -> Decimal:
        if not self.floors:
            return Decimal(0)
        score_sum = Decimal(0)
        count = 0
        for floor in self.floors:
            for entry in floor.songs:
                if entry.score is not None and entry.score > Decimal(0):
                    score_sum += entry.score
                    count += 1
        if count == 0:
            return Decimal(0)
        return util.cut_digits(score_sum / count, 2)

    @property
    def completion_rate(self) -> Decimal:
        if not self.floors:
            return Decimal(0)
        score_sum = Decimal(0)
        count = 0
        for floor in self.floors:
            for entry in floor.songs:
                score_sum += entry.score if entry.score is not None else Decimal(0)
                count += 1
        if count == 0:
            return Decimal(0)
        return util.cut_digits(score_sum / count, 2)

    @property
    def count_patterns(self) -> dict[str, int]:
        pattern_count: dict[str, int] = {}
        for floor in self.floors:
            for entry in floor.songs:
                if entry.pattern in pattern_count:
                    pattern_count[entry.pattern] += 1
                else:
                    pattern_count[entry.pattern] = 1
        return pattern_count

    @property
    def count_99_97(self) -> tuple[int, int]:
        count_99 = 0
        count_97 = 0
        for floor in self.floors:
            for entry in floor.songs:
                if entry.score is None:
                    continue
                if entry.score >= Decimal("99.00"):
                    count_99 += 1
                elif entry.score >= Decimal("97.00"):
                    count_97 += 1
        return count_99, count_97

    @property
    def count_mc_pp(self) -> tuple[int, int]:
        count_mc = 0
        count_pp = 0
        for floor in self.floors:
            for entry in floor.songs:
                if entry.max_combo is None or entry.score is None:
                    continue
                if entry.score == Decimal("100.00"):
                    count_pp += 1
                elif entry.max_combo:
                    count_mc += 1
        return count_mc, count_pp


    def organize(self):
        self.floors.sort(key=lambda floor: floor.floor_constant, reverse=True)
        for floor in self.floors:
            floor.songs.sort(key=lambda entry: entry.score if entry.score is not None else Decimal(0), reverse=True)


    @classmethod
    def from_VAResponse(cls, is_sc: bool, level: int, song_db: DMSongDB, va_response: VAResponse) -> "DMScorelist":
        floors: list[DMScorelistFloor] = []
        all_patterns = song_db.get_songs_by_level(level, va_response.button, is_sc)

        for pattern in va_response.records:
            floor_constant = pattern.floorName if pattern.floorName is not None else Decimal(0)
            if not is_sc:
                floor_constant = Decimal(int(floor_constant))
            dm_song_simple = DMSongSimple(
                songid=pattern.title,
                pattern=pattern.pattern,
                score=pattern.score,
                max_combo=pattern.maxCombo,
                dlc_code=pattern.dlcCode
            )
            for _floor in floors:
                if _floor.floor_constant == floor_constant:
                    _floor.songs.append(dm_song_simple)
                    break
            else:
                new_floor = DMScorelistFloor(
                    floor_constant=floor_constant,
                    songs=[dm_song_simple]
                )
                floors.append(new_floor)

            all_patterns.remove((pattern.title, pattern.pattern, pattern.floorName, pattern.dlcCode))

        for pattern in all_patterns:
            floor_constant = pattern[2] if pattern[2] is not None else Decimal(0)
            if not is_sc:
                floor_constant = Decimal(int(floor_constant))
            dm_song_simple = DMSongSimple(
                songid=pattern[0],
                pattern=pattern[1],
                score=None,
                max_combo=False,
                dlc_code=pattern[3]
            )
            for _floor in floors:
                if _floor.floor_constant == floor_constant:
                    _floor.songs.append(dm_song_simple)
                    break
            else:
                new_floor = DMScorelistFloor(
                    floor_constant=floor_constant,
                    songs=[dm_song_simple]
                )
                floors.append(new_floor)

        return cls(username=va_response.nickname, bmode=va_response.button, is_sc=is_sc, level=level, floors=floors)

    @classmethod
    def from_VAResponse_new(cls, song_db: DMSongDB, va_response: VAResponse) -> "DMScorelist":
        floors: list[DMScorelistFloor] = []
        all_patterns = song_db.get_new_songs_sc(va_response.button)

        for pattern in va_response.records:
            floor_constant = pattern.level
            dm_song_simple = DMSongSimple(
                songid=pattern.title,
                pattern=pattern.pattern,
                score=pattern.score,
                max_combo=pattern.maxCombo,
                dlc_code=pattern.dlcCode
            )
            for _floor in floors:
                if _floor.floor_constant == floor_constant:
                    _floor.songs.append(dm_song_simple)
                    break
            else:
                new_floor = DMScorelistFloor(
                    floor_constant=Decimal(floor_constant),
                    songs=[dm_song_simple]
                )
                floors.append(new_floor)

            all_patterns.remove((pattern.title, pattern.pattern, pattern.level, pattern.dlcCode))

        for pattern in all_patterns:
            floor_constant = pattern[2]
            dm_song_simple = DMSongSimple(
                songid=pattern[0],
                pattern=pattern[1],
                score=None,
                max_combo=False,
                dlc_code=pattern[3]
            )
            for _floor in floors:
                if _floor.floor_constant == floor_constant:
                    _floor.songs.append(dm_song_simple)
                    break
            else:
                new_floor = DMScorelistFloor(
                    floor_constant=Decimal(floor_constant),
                    songs=[dm_song_simple]
                )
                floors.append(new_floor)

        return cls(username=va_response.nickname, bmode=va_response.button, is_sc=False, level=0, floors=floors)
