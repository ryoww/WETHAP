import datetime

from managers import infos_manager, sender_manager

# infos_manager.init_table()
# infos_manager.delete_table()
# infos_manager.create_table()
# infos_manager.insert("テスト", str(datetime.date.today()), str(datetime.datetime.now()), 0, 0.0, 0.0, 0.0, "晴れ")
# infos_manager.update(1, "更新", str(datetime.date.today()), str(datetime.datetime.now()), 1, 1.0, 1.0, 1.0, "雨")
print(infos_manager.preview_data())


# sender_manager.init_table()
sender_manager.change_lab_id(before_lab_id="T4教室", after_lab_id="高野家")
print(sender_manager.get_all())
