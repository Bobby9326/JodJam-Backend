from collections import Counter
import calendar

from app.modules.memories.memory_model import Memory
from app.modules.stats.stat_repository import StatRepository
from app.modules.stats.stat_schema import MoodStats, MoodStatsResponse, YearlyMoodStatsResponse, YearlyRatingStatsResponse, OverviewResponse
from app.core.dependencies import get_current_user_id
from datetime import date as Date, timedelta


class StatService:

    def __init__(self, repo: StatRepository):
        self.repo = repo

    def get_overview(self, user_id: str, year: int) -> OverviewResponse:
        memories = self.repo.get_by_year(user_id, year)

        memory_map: dict[Date, Memory] = {m.memory_date: m for m in memories}

        streaks: list[int] = []
        dates = sorted(memory_map.keys())
        if dates:
            current_streak = 1
            for i in range(1, len(dates)):
                diff = (dates[i] - dates[i - 1]).days
                if diff == 1:
                    current_streak += 1
                else:
                    streaks.append(current_streak)
                    current_streak = 1
            streaks.append(current_streak)
        current_streak = streaks[-1] if streaks else 0
        longest_streak = max(streaks) if streaks else 0
        average_rating = sum(m.rating for m in memories) / len(memories) if memories else 0
        record_day = len(memories)

        days_in_year = 366 if calendar.isleap(year) else 365

        record_rating = round(record_day / days_in_year * 100, 2)
        return OverviewResponse(
            current_streak=current_streak,
            longest_streak=longest_streak,
            average_rating=average_rating,
            record_day=record_day,
            record_rating=record_rating,
        )

    def get_mood_stats(self, user_id: str, year: int) -> MoodStatsResponse:
        memories = self.repo.get_by_year(user_id, year)

        mood_counts: dict[str, int] = Counter(m.mood for m in memories)
        mood, count = max(mood_counts.items(), key=lambda item: item[1], default=(None, 0))

        filtered_memories = [m for m in memories if m.mood == mood]
        weekday_counts: dict[str, int] = Counter(m.memory_date.strftime("%A").lower() for m in filtered_memories)
        weekday, weekday_count = max(weekday_counts.items(), key=lambda item: item[1], default=(None, 0))

        days_in_year = 366 if calendar.isleap(year) else 365
        percentage = round(count / days_in_year * 100, 2) 

        return MoodStatsResponse(
            mood=mood,
            count=count,
            percentage=percentage,
            most_weekday=weekday,
            amount=weekday_count,
        )
    
    def get_yearly_rating_stats(self, user_id: str, year: int) -> YearlyRatingStatsResponse:
        memories = self.repo.get_by_year(user_id, year)
        month_counts: dict[str, int] = Counter(m.memory_date.strftime("%B").lower() for m in memories)
        month_avg: dict[str, float] = {month: (sum(m.rating for m in memories if m.memory_date.strftime("%B").lower() == month) / month_counts[month]) for month in month_counts}

        return YearlyRatingStatsResponse(**{month.lower(): month_avg.get(month.lower(), 0) for month in calendar.month_name if month})
    
    def get_yearly_mood_stats(self, user_id: str, year: int) -> YearlyMoodStatsResponse:
        memories = self.repo.get_by_year(user_id, year)
        mood_counts: dict[str, int] = Counter(m.mood for m in memories)
        total_days = len(memories)

        mood_stats : dict[str, MoodStats] = {mood: MoodStats(count=count, percentage=round(count / total_days * 100, 2)) for mood, count in mood_counts.items()}

        return YearlyMoodStatsResponse(**{mood: mood_stats.get(mood, MoodStats(count=0, percentage=0)) for mood in ['happy', 'sad', 'tired', 'stressed', 'excited', 'angry', 'bored', 'lonely']})



        