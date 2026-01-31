import importlib
mods = [
    'src.models.enums',
    'src.core.asyncio_manager',
    'src.core.priority_queue',
    'src.services.alert_processor',
    'src.main',
]
for m in mods:
    try:
        importlib.import_module(m)
        print('OK', m)
    except Exception as e:
        print('ERR', m, repr(e))
