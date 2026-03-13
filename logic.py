from itertools import combinations
from constants import DAYS

class ScheduleGenerator:
    def __init__(self, all_courses, target_credits, empty_days, max_gap, max_results=50):
        # max_results: 너무 많은 결과가 나오면 멈추기 위한 안전 장치
        self.all_courses = all_courses
        self.target_credits = target_credits
        self.empty_days = set(empty_days)
        self.max_gap = max_gap
        self.max_results = max_results

    def generate(self):
        fixed_courses = [c for c in self.all_courses if c.is_fixed]
        optional_courses = [c for c in self.all_courses if not c.is_fixed]
        
        valid_schedules = []
        
        if self.has_conflict(fixed_courses) or not self.check_empty_days(fixed_courses):
            return []

        current_credits = sum(c.credits for c in fixed_courses)
        needed_credits = self.target_credits - current_credits
        
        # 조합 탐색
        for r in range(len(optional_courses) + 1):
            for combo in combinations(optional_courses, r):
                
                # [안전 장치] 찾은 결과가 제한 개수를 넘으면 즉시 중단
                if len(valid_schedules) >= self.max_results:
                    return valid_schedules

                combo_list = list(combo)
                
                if sum(c.credits for c in combo_list) != needed_credits:
                    continue
                
                full_schedule = fixed_courses + combo_list
                
                if (not self.has_conflict(full_schedule) and 
                    self.check_empty_days(full_schedule) and 
                    self.check_max_gap(full_schedule)):
                    
                    valid_schedules.append(full_schedule)
                        
        return valid_schedules

    def has_conflict(self, courses):
        occupied = set()
        for course in courses:
            for p in course.get_periods():
                slot = (course.day, p)
                if slot in occupied:
                    return True
                occupied.add(slot)
        return False

    def check_empty_days(self, courses):
        for course in courses:
            if course.day in self.empty_days:
                return False
        return True

    def check_max_gap(self, courses):
        day_periods = {day: [] for day in DAYS}
        
        for course in courses:
            if course.day in day_periods:
                day_periods[course.day].extend(course.get_periods())
        
        for day in DAYS:
            periods = sorted(list(set(day_periods[day])))
            if len(periods) < 2:
                continue
            
            for i in range(len(periods) - 1):
                gap = periods[i+1] - periods[i] - 1
                if gap > self.max_gap:
                    return False
        return True