import datetime

from managers import infos_manager, sender_manager

# infos_manager.init_table()
# infos_manager.delete_table()
# infos_manager.create_table()
# infos_manager.insert("テスト", str(datetime.date.today()), 0.0, 0.0, 0.0, 0.0, "晴れ")
# infos_manager.update(10, "更新", str(datetime.date.today()), 1.0, 1.0, 1.0, 1.0, "雨")
print(infos_manager.preview_data())


# sender_manager.init_table()
sender_manager.update(before_labID="T4教室", after_labID="高野家")
print(sender_manager.get_all())
