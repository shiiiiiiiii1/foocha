#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import serial
import json

# from sakuraio.hardware.rpi import SakuraIOSMBus
# sakuraio = SakuraIOSMBus()
# import struct

#デバイスの指定
DEV = '/dev/ttyUSB0'

#緯度、経度の分数表記⇒度数表記への変換関数
def convert(x):
    result = (float(x[0:-7])+(float(x[-7:])/60))
    return result

def get_str(x):
  result = ""
  if (x[2] == "A") and (x[2] != ""):
    result += "state:"+"ok "
  elif (x[2] == "V") and (x[2] != ""):
    result += "state:"+"alert "
  else:
    result += "state:"+"no data "
  if x[7] != "":
    result += 'speed:'+ '%.1f' % (float(x[7])*1.852) + "km/h "
  else:
    result += "speed:"+"no data "
  if (x[4] == "N")  and ( x[4] != "" ):
    result += "north latitude:" + '%.4f' % convert(x[3]) +' '
  elif (x[4] == "S")  and ( x[4] != "" ):
    result += "south latitude:" + '%.4f' % convert(x[3]) +' '
  else:
    result += "latitude:"+"no data "
  if (x[6] == "E") and ( x[6] != ""):
    result += "east longitude:" + '%.4f' % convert(x[5]) +' '
  elif (x[6] == "W") and ( x[6] != ""):
    result += "west longitude" + '%.4f' % convert(x[5]) +' '
  else:
    result += "logitude:"+"no data "
  return result

#チェックサムの検証
def checksum_verify(c_sum,data):
  c_data = '0x00'
  for i in range(1,len(data)-3):
    c_data = hex(int(c_data,16) ^ int(hex(ord(data[i])),16))
  if int(c_sum,16) == int(c_data,16):
    return True
  else:
    return False

def get_LatLng(s):
  s_split = s.split(',')
  lat = [s_split[3], s_split[4]]
  lat[0] = float(lat[0]) * 0.01
  lng = [s_split[5], s_split[6]]
  lng[0] = float(lng[0]) * 0.01
  if (lat[1] == 'S'):
    lat[0] *= -1
  if (lng[1] == 'W'):
    lng[0] *= -1
  jsonLatLng = {
    'lat': lat[0],
    'lng': lng[0]
  }
  return jsonLatLng

def change_LatLng(s, b):
  if (b == 0):
    if (len(str(s)) == 10):
      length = str(s)[:-1]
      s = float(length)
    s = -1 * s
  binary = struct.pack('>d', s)
  unsigned_long = struct.unpack('>Q', binary)[0]
  binary_number_2 = bin(unsigned_long)
  val = binary_number_2.lstrip('0b')
  if len(val) < 64:
    val = val.rjust(64, '0')
  data = []
  l = 64
  for i in range(0, 8):
    l2 = l - 8
    data.append(val[l2:l])
    data[i] = int(data[i], 2)
    l = l2
  return data


#メインループ
#GPRMCの値のみ処理、その値の要素の数が13未満でうまく取得出来ていない場合は処理しない
try:
  #シリアルの取得
  sr = serial.Serial(DEV, 4800)
  while 1:
    #改行コードは除外
    tmp = sr.readline().rstrip()
    tmp = tmp.decode('utf-8')
    #チェックサムの確認
    if checksum_verify(tmp[-2:],tmp):
      tmp2 = tmp.split(",")
      #GPRMCのみ処理
      if (tmp2[0] == '$GPRMC'):
        line = get_str(tmp2)
        print("OK:", tmp)
        lat_lng = get_LatLng(tmp)
        print(lat_lng)
        jsonLatLng = json.dumps(lat_lng)
        with open('LatLng.json', 'w') as f:
          f.write(jsonLatLng)
        # lat = change_LatLng(lat_lng[0], lat_lng[1])
        # lng = change_LatLng(lat_lng[2], lat_lng[3])
        # sakuraio.send_immediate_raw(0, "d", lat)
        # sakuraio.send_immediate_raw(1, "d", lng)
        time.sleep(1.0)
    else:
      print('NG:', tmp)
finally:
  tmp = serial.Serial(DEV, 4800).readline().rstrip()
  print(tmp)
  print('serial_close')
  sr.close()



