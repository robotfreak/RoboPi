import RPi.GPIO as GPIO
import time
import os

# Pin 26 als Ausgang deklarieren
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(26, GPIO.OUT)

while True:
	# PWM mit 50Hz an Pin 26 starten
	Servo = GPIO.PWM(26, 50)

	# Richtungseingabe
	Eingabe = raw_input("Bitte treffen Sie Ihre Wahl: ") 

	# Richtung "Rechts"
	if(Eingabe == "r"):

		# Schrittweite eingeben
		Schritte = raw_input("Schrittweite: ") 
		print Schritte, "Schritte nach Rechts"
	
		# PWM mit 10% Dutycycle (2ms) generieren
		Servo.start(10)
		for Counter in range(int(Schritte)):
			time.sleep(0.01)
	
		# PWM stoppen
		Servo.stop()

	# Mittelstellung einnehmen
	elif(Eingabe == "m"):
		Servo.start(7)
		print "Drehung in die Mitte"
		time.sleep(1) 
		Servo.stop()
	
	# Richtung "Links"
	elif(Eingabe == "l"):
	
		# Schrittweite eingeben
		Schritte = raw_input("Schrittweite: ") 
		print Schritte, "Schritte nach Links"
		
		# PWM mit 5% Dutycycle (1ms) generieren
		Servo.start(5)
		for Counter in range(int(Schritte)):
			time.sleep(0.01)
		
		# PWM stoppen
		Servo.stop()
	
	# Programm beenden
	elif(Eingabe == "q"):
		print "Programm wird beendet......"
		os._exit(1)
		Servo.stop()
		GPIO.cleanup()
		
	# Ungueltige Eingabe
	else:
		print "Ungueltige Eingabe!"

