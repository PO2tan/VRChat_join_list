#----------------------------------------------------------------------------------
#  import
#----------------------------------------------------------------------------------
import PySimpleGUI as sg
import datetime
#[注意]pybluez2を使用
import bluetooth
import threading

#----------------------------------------------------------------------------------
#  各種設定
#----------------------------------------------------------------------------------
BACK_GROUND_COLOR = "#101010"
MAX_PLAYER_LIST_NUM = 10
FONT_SIZE = 25

#----------------------------------------------------------------------------------
#  ユーザ登録
#----------------------------------------------------------------------------------
player_device_list = [
	#"device_addr, device_name, player_name"
	["**:**:**:**:**:**", "device_name", "PO2tan"]
]

#----------------------------------------------------------------------------------
#  クラスの定義
#----------------------------------------------------------------------------------
class player:
	def __init__(self, date, join_left, player_name):
		self.date = date
		self.join_left = join_left
		self.player_name = player_name

#----------------------------------------------------------------------------------
#  グローバル変数の定義
#----------------------------------------------------------------------------------
player_list = []
player_num = 0
ble_device_log = 0
player_join_left_flag = False
task_end_flag = False

#----------------------------------------------------------------------------------
#  GUIレイアウト
#----------------------------------------------------------------------------------
gui_layout = [
    [[
		sg.Text("", key = "-time-", background_color = BACK_GROUND_COLOR),
		sg.Text("// 0 players", key = "-player_num-", background_color = BACK_GROUND_COLOR)

	]],
	[sg.HorizontalSeparator(color = "#FFFFFF")],
	[
		[
			sg.Text("", key = "-player_join_log_" + str(key) + "_a-", background_color = BACK_GROUND_COLOR),
			sg.Text("", key = "-player_join_log_" + str(key) + "_b-", background_color = BACK_GROUND_COLOR),
			sg.Text("", key = "-player_join_log_" + str(key) + "_c-", background_color = BACK_GROUND_COLOR)
		]
		for key in range(MAX_PLAYER_LIST_NUM)
	]
]

window = sg.Window("join_log", gui_layout, background_color = BACK_GROUND_COLOR, location = (0, 0), resizable = True, font=("None", FONT_SIZE))

#----------------------------------------------------------------------------------
#  GUI処理関数
#----------------------------------------------------------------------------------
def gui_process():
	global player_join_left_flag
	global task_end_flag
	global player_num

	while True:
		#描画
		#valuesも必要なようです
		event, values = window.read(timeout = 50, timeout_key = "-timeout-")
		dt_now = datetime.datetime.now()			#現在時間を取得

		if event == sg.WIN_CLOSED:
			task_end_flag = True
			break
		elif event == "-timeout-":
			window["-time-"].update(dt_now.strftime("%Y-%m-%d %H:%M:%S"))

		#---
		if player_join_left_flag == True:
			player_list_len = len(player_list)
			if(player_list_len > MAX_PLAYER_LIST_NUM):
				player_list.pop(0)

			for key in range(MAX_PLAYER_LIST_NUM):
				if key > player_list_len - 1:
					break

				if player_list[key].join_left == "[join]":
					color = "#00DC00"
				else:
					color = "#E10000"

				window["-player_num-"].update("// " + str(player_num) + " players")
				window["-player_join_log_" + str(key) + "_a-"].update(player_list[key].date)
				window["-player_join_log_" + str(key) + "_b-"].update(player_list[key].join_left, text_color = color)
				window["-player_join_log_" + str(key) + "_c-"].update(player_list[key].player_name)
				player_join_left_flag = False
		#---

#----------------------------------------------------------------------------------
#  ble処理関数
#----------------------------------------------------------------------------------
def ble_device_scan():
	global player_join_left_flag
	global task_end_flag
	global ble_device_log
	global player_num

	while True:
		if task_end_flag == True:
			break

		device = bluetooth.discover_devices(lookup_names=True)
		device_diff = set(ble_device_log) ^ set(device)				#オブジェクトをlistに変換し、内容を比較(接続された時)

		if len(ble_device_log) < len(device):	#接続されたデバイスがある場合
			for addr, name in device_diff:
				for player_device_addr, player_device_name, player_name in player_device_list:
					if(addr == player_device_addr and name == player_device_name):
						player_join_left(True)

		elif len(ble_device_log) > len(device):	#切断されたデバイスがある場合
			for addr, name in device_diff:
				for player_device_addr, player_device_name, player_name in player_device_list:
					if(addr == player_device_addr and name == player_device_name):
						player_join_left(False)
				
		ble_device_log = device


#----------------------------------------------------------------------------------
#  プレイヤー追加関数
#----------------------------------------------------------------------------------
def player_join_left(player_join):
	global player_join_left_flag
	global player_num
	dt_now = datetime.datetime.now()			#現在時間を取得

	if player_join == True:
		player_list.append(player(dt_now.strftime("%H:%M:%S"), "[join]", player_name))
		player_num += 1
	else:
		player_list.append(player(dt_now.strftime("%H:%M:%S"), "[leave]", player_name))
		player_num -= 1

	player_join_left_flag = True


#----------------------------------------------------------------------------------
#  MAIN
#----------------------------------------------------------------------------------
if __name__ == "__main__":
	thread = threading.Thread(target=gui_process)
	thread.start()

	ble_device_log = bluetooth.discover_devices(lookup_names=True)
	for addr, name in ble_device_log:
		for player_device_addr, player_device_name, player_name in player_device_list:
			if(addr == player_device_addr and name == player_device_name):
				player_join_left(True)

	thread = threading.Thread(target=ble_device_scan)
	thread.start()
	print(">>>起動完了")