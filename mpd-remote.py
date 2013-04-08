#!/usr/bin/env python3

from quick2wire.gpio import pins, In, Out, Falling
import select
import mpd
import time

button_play = pins.pin(4, direction=In, interupt=Falling) # 23
led_green = pins.pin(1, direction=Out) # 18
led_red = pins.pin(6, direction=Out) # 25

client = mpd.MPDClient()

def update_led_status(client, led):
  status = client.status()
  value = 0
  if (status['state'] == "play"):
    value = 1
  led.value = value

def toggle_player_state(client):
  status = client.status()
  if (status['state'] == "play"):
      client.pause(1)
  elif (status['state'] == "stop"):
      client.play()
  else: # pause
      client.pause(0)

def blink_led(led):
  for i in range(0, 5):
    led.value = 1
    time.sleep(1)
    led.value = 0
    time.sleep(1)

def mpd_connect(client, led):
  try:
    client.connect("localhost", 6600)
    #client.password()
  except IOError as e:
    print("cannot connect to mpd")
    blink_led(led)
    mpd_connect(client, led)

with button_play, led_green, led_red:
  mpd_connect(client, led_red)

  update_led_status(client, led_green)

  client.send_idle('player')

  epoll = select.epoll()
  epoll.register(button_play, select.EPOLLIN|select.EPOLLET)
  epoll.register(client, select.EPOLLIN)

  while True:
    events = epoll.poll()
    for fileno, event in events:
      # MPD changed state
      if (fileno == client.fileno()):
        client.fetch_idle()
        if ('player' in changed):
          update_led_status(client, led_green)
      # The button has changed state
      elif (fileno == button_play.fileno()):
        client._pending = []
        client.noidle()
        client._read_line()
        if (button_play.value == 1):
            toggle_player_state(client)
      else:
          print('unknown fileno', fileno, event)
      client.send_idle('player')
