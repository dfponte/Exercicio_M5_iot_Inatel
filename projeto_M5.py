import spidev
import time
from libsoc import gpio
from gpio_96boards import GPIO
from dweet import Dweet

GPIO_CS = GPIO.gpio_id('GPIO_CS')
Sgas = GPIO.gpio_id('GPIO_A')
ASom = GPIO.gpio_id('GPIO_C')
Lampada = GPIO.gpio_id('GPIO_E')

pins = ((GPIO_CS, 'out'), (ASom, 'out'), (Lampada, 'out'),(Sgas, 'in'),)

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 10000
spi.mode = 0b00
spi.bits_per_word = 8

system_status = 1

dweet = Dweet()


def readDigital(gpio):
	digital = [0,0,0]
	digital[0] = gpio.digital_read(Lampada)
	digital[1] = gpio.digital_read(ASom)
        digital[2] = gpio.digital_read(Sgas)
        #digital[2] = 1
	return digital

def writeDigital(gpio, digital):
	write = digital
	gpio.digital_write(Lampada, write[0])
	gpio.digital_write(ASom, write[1])
	return digital


def readvolGas(gpio):

	gpio.digital_write(GPIO_CS, GPIO.HIGH)
	time.sleep(0.0002)
	gpio.digital_write(GPIO_CS, GPIO.LOW)
	r = spi.xfer2([0x01, 0xA0, 0x00])
	gpio.digital_write(GPIO_CS, GPIO.HIGH)

	adcout = (r[1] << 8) & 0b1100000000
	adcout = adcout | (r[2] & 0xff)
	adc_volGas = (adcout*100)/1023



       
	#if adc_temp > 27:
		#gpio.digital_write(Ar, GPIO.HIGH)
	#else:
		#gpio.digital_write(Ar, GPIO.LOW)
	
	return adc_volGas

def readLumi(gpio):

	gpio.digital_write(GPIO_CS, GPIO.HIGH)
	time.sleep(0.0002)
	gpio.digital_write(GPIO_CS, GPIO.LOW)
	r = spi.xfer2([0x01, 0x80, 0x00])
	gpio.digital_write(GPIO_CS, GPIO.HIGH)

	adcout = (r[1] << 8) & 0b1100000000
	adcout = adcout | (r[2] & 0xff)
	
	#if adcout < 100:
		#gpio.digital_write(Lampada, GPIO.HIGH)
	#else:
		#gpio.digital_write(Lampada, GPIO.LOW)

	return adcout

#def readDweet():


if __name__=='__main__':
	with GPIO(pins) as gpio:
		while True:
			digital = [0,0,0]
			resposta = dweet.latest_dweet(name="projeto_final")
			digital[0] =  resposta['with'][0]['content']['Lampada']
			digital[1] =  resposta['with'][0]['content']['ASom']
			writeDigital(gpio, digital)
			volGas = readvolGas(gpio)
			Lumi = readLumi(gpio)
			digital = readDigital(gpio)
                        if digital[2]==1:
		               gpio.digital_write(ASom, GPIO.HIGH)
                               digital[1] = gpio.digital_read(ASom)
	              
                        else:
		               gpio.digital_write(ASom, GPIO.LOW)
                               digital[1] = gpio.digital_read(ASom)

                        if Lumi < 200:
		               gpio.digital_write(Lampada, GPIO.HIGH)
                               digital[0] = gpio.digital_read(Lampada)
                        else:
		            gpio.digital_write(Lampada, GPIO.LOW)
                            digital[0] = gpio.digital_read(Lampada)




			print "VolGas: %3.1f\nLumi: %d\nLamp: %d\nASom: %d\nSgas: %d" %(volGas, Lumi,
                        digital[0], digital[1],digital[2])
			dweet.dweet_by_name(name="projeto_final", data={"Lampada":digital[0],
                         "ASom": digital[1], "Sgas": digital[1],"Volume_Gas":volGas, "Luminosidade": Lumi})

			time.sleep(10)
