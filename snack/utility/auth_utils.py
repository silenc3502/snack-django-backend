from redis_cache.service.redis_cache_service_impl import RedisCacheServiceImpl
from board.entity.board import Board

def is_authorized_user(board: Board, token: str) -> tuple[bool, int, str]:
    redisService = RedisCacheServiceImpl.getInstance()
    account_id = redisService.getValueByKey(token)

    if not account_id:
        return False, 401, "로그인 인증이 필요합니다."

    if not board or not board.author or not board.author.account:
        return False, 404, "게시글 또는 작성자 정보를 찾을 수 없습니다."

    if str(account_id) == str(board.author.account.id):
        return True, 200, "인증 성공"

    return False, 403, "작성자와 일치하지 않습니다."