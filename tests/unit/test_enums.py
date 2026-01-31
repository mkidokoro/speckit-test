from src.models.enums import AlertType, AlertState, UserType, CallStatus

def test_alert_type_values():
    assert AlertType.FIRE.value == 'FIRE'
    assert AlertType.SECURITY.value == 'SECURITY'

def test_alert_state_values():
    assert AlertState.PENDING.value == 'PENDING'
    assert AlertState.DISPLAYED.value == 'DISPLAYED'

def test_user_type():
    assert UserType.RESIDENT.value == 'RESIDENT'
    assert UserType.GUEST.value == 'GUEST'

def test_call_status():
    assert CallStatus.RINGING.value == 'RINGING'
    assert CallStatus.CONNECTED.value == 'CONNECTED'
