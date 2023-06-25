import time
import continuous_threading

def foo(i):
    return True,""

retornos = []
for i in range(3):
    retornos.append(foo(i))

time.sleep(0)
print(retornos[1])