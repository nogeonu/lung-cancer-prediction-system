from django.utils.deprecation import MiddlewareMixin
from .models import VisitorCounter
import logging

logger = logging.getLogger(__name__)

class VisitorCounterMiddleware(MiddlewareMixin):
    """방문자 카운터 미들웨어"""
    
    def process_request(self, request):
        """요청 처리 시 방문자 수 증가"""
        try:
            # 특정 경로는 제외 (정적 파일, API 등)
            excluded_paths = [
                '/static/',
                '/media/',
                '/admin/',
                '/favicon.ico',
                '/robots.txt',
            ]
            
            # 제외 경로가 아닌 경우에만 카운트
            if not any(request.path.startswith(path) for path in excluded_paths):
                # 세션을 사용하여 같은 사용자의 중복 카운트 방지
                if not request.session.get('visited_today', False):
                    VisitorCounter.increment_today()
                    request.session['visited_today'] = True
                    # 세션 만료 시간을 자정까지로 설정
                    request.session.set_expiry(86400)  # 24시간
                    
        except Exception as e:
            # 방문자 카운터 오류가 전체 서비스에 영향을 주지 않도록 로그만 남김
            logger.error(f"Visitor counter error: {e}")
        
        return None
