from .models import VisitorCounter
from django.utils import timezone
from datetime import date

def visitor_counter(request):
    """모든 템플릿에서 방문자 수를 사용할 수 있도록 하는 컨텍스트 프로세서"""
    try:
        today_count = VisitorCounter.get_today_count()
    except Exception:
        today_count = 0
    
    return {
        'today_visitor_count': today_count
    }
