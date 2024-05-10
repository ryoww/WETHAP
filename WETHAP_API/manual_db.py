import datetime

from managers import infos_manager, sender_manager, manual_infos_manager

# infos_manager.init_table()
# infos_manager.delete_table()
# infos_manager.create_table()
# infos_manager.insert("テスト", str(datetime.date.today()), str(datetime.datetime.now()), 0, 0.0, 0.0, 0.0, "晴れ")
# infos_manager.update(1, "更新", str(datetime.date.today()), str(datetime.datetime.now()), 1, 1.0, 1.0, 1.0, "雨")
# print(infos_manager.get_rows(lab_id="テスト", row_limit=3))
print(infos_manager.preview_data())

# sender_manager.init_table()
print(sender_manager.get_all())

# manual_infos_manager.init_table()
