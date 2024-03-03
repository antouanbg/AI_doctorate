# Примерен код за дисертацията ми - https://anguelov.blogspot.com/2024/03/blog-post.html
# който би следвало да показва алгоритъм за фомиране на път с невронна мрежа на Хопфийлд

import  math
import numpy as np
from pymongo import MongoClient
import urllib.parse
import dns.resolver

dns.resolver.default_resolver=dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers=['8.8.8.8']

# space = 0 # матрица с индексите/номерата на работните пространства
#unit_id = 0 # идентификатор на агента
M = 10# вертикален размер на мрежата (ред)
N = 10 # хоризонтален размер на мрежата (колона)
#start_point = 91 # индекс на стартовата клетка (където се намира агента)
#target_point = 56 # индекс на целевата клетка (цел)
start = (0, 0) # # матричен индекс на началната клетка
k=1     # коефициент на усилване
actf_type='linear'  # избор linear или tanh тип функция активация
target = (5, 5)     # матричен индекс на целевата клетка (ред, колона) / (row, col)
dw = (1/(math.sqrt(2)))*k # тегло на връзката по диагонал * 1/2
sw = 1*k #тегло на възката по права
scw = 0*k #тегло на връзката към самия себе си неврон
#smoothing = 0 # включване/изключване на функцията за "изглаждане" на траекторията
#smooth = sw - dw # коефициент на "изглаждане" на траекторията
E = [[0]*N for i in range(M)] # начално състояние на НМ (E e невронна матрица/карта)
obst = [[[3], [0]],
	    [[3], [1]],
        [[3], [2]],
        [[3], [3]],
        [[3], [4]],
		[[3], [5]]] # списък с координати на препрядствията в E [col, row]
track =    [[[3], [0]],
	        [[3], [1]],
            [[3], [2]],
            [[3], [3]],
            [[3], [4]],
		    [[3], [5]]] # списък с координати на следите в E [col, row]

domain = (dw, sw, dw, sw, scw, sw, dw, sw, dw) # списък на клетките в малкото пространство F
obstacle = -1    #значение на препятствието в началото, после става Е = 0;

col = start[1]     # колона с текущите позиции
row = start[0]
gradient = [0] * 8      # Буфер за градиентите
sum_gradient = 0
recalculate = False # променлива за необходимостта от преизчисляване на траекторията
cur_direction = 0 # начално направление (на 12ч.)
username = urllib.parse.quote_plus('antouan')
password = urllib.parse.quote_plus('boriss150')
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
#client =  MongoClient('mongodb+srv://%s:%s@phd.sb35c.mongodb.net/PhD?retryWrites=true&w=majority' % (username, password))

#db = client['PhD']



def set_obstacles(self):    #функция + I (при препядствие Е = 0, а при следа трябва да натежи с коефц.)
    if self == - 1:
        ar = np.array (obst, dtype=int)
        for i in range(len(ar)):
            row = ar[i, 0]    # малко сметки да превърнем координатите в цели числа за Е
            col = ar[i, 1]
            print(int(col), int (row))   #col, row, 0.0 е в май горе, най-ляво
            E[int(col)][int(row)]= -1  # Use ar as a source of indices, to assign 1

    #print(np.matrix(obst))
   # arr_obst = [[0]*len (obst) for i in xrange(obst [len (obst)])
    # obsticles = np.reshape(arr_obst, (N, M))  # списък с координатите на предпрядствията;

def get_normw(curY, curX):  # функция за изчисляване на теглата
    wesumm = 0
    wsumm = 0
    wcount = 0      #Разглеждаме всеки съседен неврон
    #print('функция: изчисляване на теглата')
    for y in range((curY - 1), (curY + 1 + 1)):
        for x in range((curX - 1), (curX + 1 + 1)):     # ако координатите на тествания неврон не излизат извън работната зона и не падат върху препядтвие
            if x >= 0 and y >= 0 and x < N and y < M:
                if E[y][x] != -1:
                    #print (E[y][x], wcount, wsumm, wesumm, domain[wcount], y, x)
                    wesumm += E[y][x] * domain[wcount]
                    wsumm += domain[wcount]
            wcount += 1
    return wesumm / wsumm


def act_function(x):   # калкулация на функцията за активиране на неврон в зависимост от линейна или нелинейна
    if actf_type == 'linear':
        #print('x:', x)
        if x<=0:
            x=0
        elif x > 1:
            x=1
    elif actf_type == 'tanh':
        x = (math.exp(2*x) - 1) / (math.exp(2*x) + 1)
        if x > 1:
            x=1
    #print('x:', x)
    return x

# Построяване на невронната карта
def net_activation(actf_type):
    cycles = 0 # брояч на цикъла на активиране
    cycles_max = (N * M) ** 2 # максимално допустимо кол-во цикли на активация
    if len(obst) > 0:
        set_obstacles (-1) # установяане "-1" за "изключване" на невроно-препятствие
    E[target[0]][target[1]] = 1 # установяване на активирания неврон
    m=1 #стъпка
    n=1
    while E[start[0]][start[1]] < 1e-15:
        print('цикли:', cycles)
        for y in range((target[0] - m), (target[0] + m + 1)):
            for x in range((target[1] - n), (target[1] + n + 1)):

                if x >= 0 and y >= 0 and x < N and y < M:
                    if E[y][x] == 1:
                        E[y][x] = 1
                    elif E[y][x] != -1:      # при -1 има препрядствие! => да се отрази
                        E[y][x] = act_function(get_normw(y, x))
                        #print(E[y][x])
                    #if len(obst) > 0:
                        #set_obstacles(0)
                if m < M:
                    m += 1
                if n < N:
                    n += 1

        cycles += 1
        print(np.round(E, 3))    #даните от матрицата закръгляваме до 3ти знак след десетичната
        if cycles > cycles_max:
            break
    #print (E[start[0]][start[1]])
    #if len(obst) > 0:
        #set_obstacles(0)           # формиране на крайния изходен сигнал "net_output" (нулиране на предпрядствията)
    print(" number of activation cycles: " + str(cycles))

#start1 = act_function(x)
test = net_activation (actf_type)
#print (get_normw(y, x))
#print(np.round (E, 3))