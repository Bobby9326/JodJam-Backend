from pydantic import BaseModel



class MoodStats(BaseModel):
    count: int
    percentage: float

class OverviewResponse(BaseModel):
    current_streak: int
    longest_streak: int
    average_rating: float
    record_day: int
    record_rating: float

class MoodStatsResponse(BaseModel):
    mood: str
    count: int
    percentage: float
    most_weekday: str
    amount: int

class YearlyRatingStatsResponse(BaseModel):
    january: float
    february: float
    march: float
    april: float
    may: float
    june: float
    july: float
    august: float
    september: float
    october: float
    november: float
    december: float

class YearlyMoodStatsResponse(BaseModel):
    happy: MoodStats
    sad: MoodStats
    tired: MoodStats
    stressed: MoodStats
    excited: MoodStats
    angry: MoodStats
    bored: MoodStats
    lonely: MoodStats
    
