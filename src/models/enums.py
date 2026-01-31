"""列挙型定義
日本語コメント: 警報タイプ等の定義を格納します
"""
from enum import Enum

class AlertType(Enum):
    FIRE = 'FIRE'
    SECURITY = 'SECURITY'

class AlertState(Enum):
    PENDING = 'PENDING'
    DISPLAYED = 'DISPLAYED'
    CLEARED = 'CLEARED'

class UserType(Enum):
    RESIDENT = 'RESIDENT'
    GUEST = 'GUEST'

class CallStatus(Enum):
    RINGING = 'RINGING'
    CONNECTED = 'CONNECTED'
    HELD = 'HELD'
    ENDED = 'ENDED'
