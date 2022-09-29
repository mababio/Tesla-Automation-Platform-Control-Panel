import time

val = 10
while val != 0:
    print('mike --->')
    time.sleep(2)
    val -= 2
    if val == 2:
        print('works')
        break
else:
    print('esle this')
