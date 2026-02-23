import lgpio
import time

out = 23

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, out)


while(True):
	lgpio.gpio_write(h, out, 1)
	print("on")
	time.sleep(1)

	lgpio.gpio_write(h, out, 0)
	print("off")
	time.sleep(1)
