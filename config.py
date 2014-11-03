from stores.dict_store import DictStore

instance_type_store = DictStore()
instance_store = DictStore()

from queue_manager import subscribe as sub_method
from queue_manager import send_message as send_method

subscribe = sub_method
send_message = send_method
