# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game
value = 0
guessAmount = 0
pwmLED = 0
pwmBuzzer = 0
guessAttempts = 0

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
eeprom = ES2EEPROMUtils.ES2EEPROM()


# Print the game banner
def welcome():
    eeprom.clear(256)
    eeprom.populate_mock_scores()
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")

# Print the game menu
def menu():
    global end_of_game
    global value
    

    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        end_of_game = False
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")

    
def millis(): #get system time in milliseconds
    return round(time.time() * 1000)

def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    to_print = count if(count<3) else 3
    for i in range(to_print):
        byte = 4*i
        name = raw_data[byte] + raw_data[byte+1] + raw_data[byte+2]
        print(i+1, "- ", name, "took", ord(raw_data[byte+3]), "guesses")
    pass
    menu()
    

# Setup Pins
def setup():
    # Setup board mode
    GPIO.setmode(GPIO.BOARD)
    # Setup regular GPIO
    GPIO.setup(btn_increase, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(btn_submit, GPIO.IN, pull_up_down = GPIO.PUD_UP)

    GPIO.setup(LED_value[0], GPIO.OUT)
    GPIO.output(LED_value[0], 0)
    GPIO.setup(LED_value[1], GPIO.OUT)
    GPIO.output(LED_value[1], 0)
    GPIO.setup(LED_value[2], GPIO.OUT)
    GPIO.output(LED_value[1], 0)
    # Setup PWM channels
    GPIO.setup(LED_accuracy, GPIO.OUT)
    global pwmLED
    pwmLED = GPIO.PWM(LED_accuracy, 1000)
    pwmLED.start(0)

    #buzzer
    global pwmBuzzer
    GPIO.setup(buzzer, GPIO.OUT)
    pwmBuzzer = GPIO.PWM(buzzer, 0.5)
    pwmBuzzer.start(0.1)
    
    # Setup debouncing and callbacks
    GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback = btn_increase_pressed, bouncetime = 500)
    GPIO.add_event_detect(btn_submit, GPIO.FALLING, callback = btn_guess_pressed, bouncetime = 500)



# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = int(eeprom.read_byte(0))
    # Get the scores
    scores = eeprom.read_block(1, 4*score_count)
    # convert the codes back to ascii
    for i in range(0, 4*score_count):
        scores[i] = chr(scores[i])
    # return back the results
    return score_count, scores


# Save high scores
def save_scores(name, score):
    # fetch scores
    score_count, raw_data = fetch_scores()
    # include new score
    raw_data.append(name[0])
    raw_data.append(name[1])
    raw_data.append(name[2])
    raw_data.append(chr(score))
    # update total amount of scores
    score_count += 1
    # sort
    #sort list of score values
    score_values = []
    for i in range(0,score_count):
        score_values.append(raw_data[4*i + 3])

    score_values.sort()
    #populate scores list based on score values
    scores = []
    for j in range(score_count):
        a = j*4
        index = score_values.index(raw_data[a+3])
        b = 4*index
        score_values[index] = None
        scores.insert(b, raw_data[a])
        scores.insert(b+1, raw_data[a+1])
        scores.insert(b+2, raw_data[a+2])
        scores.insert(b+3, raw_data[a+3])
    # write new scores
    eeprom.write_byte(0, score_count)

    register = 4
    for k in range(score_count*4):
        eeprom.write_byte(register, ord(scores[k]))
        register += 1
    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    
    global guessAmount
    guessAmountBin = bin(guessAmount)
    guessAmount = guessAmount + 1

    # can only guess up to 7
    if guessAmount > 7:
        guessAmount = 0

    guessAmountBinStr = str(guessAmountBin)
    slicedStr =  guessAmountBinStr[2:]
    reverseStr = slicedStr[::-1]
    strLED = reverseStr.ljust(3, "0")

    # Increase the value shown on the LEDs

    if (strLED[0] == '1'):
        GPIO.output(LED_value[0], GPIO.HIGH)
    else:
        GPIO.output(LED_value[0], GPIO.LOW)

    if (strLED[1] == '1'):
        GPIO.output(LED_value[1], GPIO.HIGH)

    else:
        GPIO.output(LED_value[1], GPIO.LOW)

    if (strLED[2] == '1'):
        GPIO.output(LED_value[2], GPIO.HIGH)

    else:
        GPIO.output(LED_value[2], GPIO.LOW)

    accuracy_leds()
    trigger_buzzer()
    pass


# Guess button
def btn_guess_pressed(channel):
    global guessAmount
    global guessAttempts
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    time_held = time.time()
    while GPIO.input(btn_submit) == 0:
        pass
    
    button_time = time.time() - time_held

    if button_time > 2:
        GPIO.cleanup()
        end_of_game = True
        menu()
        pass

    
    else:
        guessAttempts += 1
        # if exact guess
        if guessAmount == value:
            # - Disable LEDs and Buzzer
            pwmLED.stop() 
            pwmBuzzer.stop()
             # - tell the user and prompt them for a name
            print("Congrats, you have guessed correctly!")
            name = input("Please enter your name (3 letters):")
            # save new score
            save_scores(name, guessAttempts)
            end_of_game = True
            GPIO.cleanup()
            menu()
        else:
            print("Sorry, incorrect. Please try again.")
            trigger_buzzer()
            accuracy_leds()
    



# LED Brightness
def accuracy_leds():
    global value
    global pwmLED
    correctness = 0.00
    if guessAmount > value:
        correctness = ((8-guessAmount)/(8-value))*100
    elif guessAmount < value:
        correctness = (guessAmount/value)*100
    elif guessAmount == value:
        correctness = 100
    pwmLED.ChangeDutyCycle(correctness)        
    

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    if abs(guessAmount - value) == 3:
        pwmBuzzer.ChangeFrequency(1)
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    if abs(guessAmount - value) == 2:
        pwmBuzzer.ChangeFrequency(2)
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    if abs(guessAmount - value) == 1:
        pwmBuzzer.ChangeFrequency(4)
    pass


if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
