import time
import smbus


class Si7020(object):
	CMD_READ_TEMP_HOLD = 0xe3
	CMD_READ_HUM_HOLD = 0xe5
	CMD_READ_TEMP_NOHOLD = 0xf3
	CMD_READ_HUM_NOHOLD = 0xf5
	CMD_WRITE_USER_REG = 0xe6
	CMD_READ_USER_REG = 0xe7
	CMD_SOFT_RESET= 0xfe

	def __init__(self, address=0x40, bus=1, offset_temp=0, offset_humid=0):
		self.bus = smbus.SMBus(bus)
		self.address = address
		self.offset_temp = offset_temp
		self.offset_humid = offset_humid

	def reset(self):
		self.bus.write_byte(self.address, self.CMD_SOFT_RESET)
		time.sleep(.02)

	def get_temp(self):
		self.bus.write_byte(self.address, self.CMD_READ_TEMP_NOHOLD)
		time.sleep(.02)
		raw_temp = (self.bus.read_byte(self.address) << 8) + self.bus.read_byte(self.address)
		self.bus.read_byte(self.address)  # CRC
		return -46.85 + self.offset_temp + (175.72 * (raw_temp / float(2 ** 16)))

	def get_rel_humidity(self):
		self.bus.write_byte(self.address, self.CMD_READ_HUM_NOHOLD)
		time.sleep(.02)
		raw_hum = (self.bus.read_byte(self.address) << 8) + self.bus.read_byte(self.address)
		self.bus.read_byte(self.address)  # CRC
		return -6 + self.offset_humid + (125 * (raw_hum / float(2 ** 16)))


if __name__ == '__main__':
	sensor = Si7020()
	sensor.reset()
	print(time.time(), sensor.get_temp(), sensor.get_rel_humidity())