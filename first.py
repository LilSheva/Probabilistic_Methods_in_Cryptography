# -*- coding: utf-8 -*-
import copy
import random
import itertools
import math
import numpy as np

size = 6

def fft_step(f, size, step, i):
	j = 0
	while (j < 2**size):
		if ((j // 2**step) % 2):
			f[i][j] = f[i][j] ^ f[i][j - 2**(step)]
		j = j + 1

def jegalkin(func, size):
	f = [[func[i][j] for j in range (2**size)] for i in range(size)] # копирование листа чтоб начальный не менять
	for i in range(size):
		for step in range(size):
			fft_step(f, size, step, i)
	return f



sbox = [i for i in range(2**size)]

random.shuffle(sbox)

#sbox = [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2]

functions = [[0 for i in range(2**size)] for i in range(size)]

for i in range(len(sbox)):
	for j in range(size):
		functions[j][i] = (sbox[i]//(2**j)) % 2 # просто записываем в лист значения булевых функций, не оптимально но я ногу пинал на питоне булевых операции реализовывать

weight = [0 for i in range(size)]

for i in range(size):
	for j in range(2**size):
		weight[i] = weight[i] + functions[i][j]

jeg = jegalkin(functions, size)

tmp = jegalkin(jeg, size)

fictiv = [[0 for i in range(size)] for i in range(size)]

for i in range(size):
	for j in range(size):
		tmp = 0
		for k in range(2**size):
			tmp = tmp + ( jeg[i][k] if (k//(2**j)) % 2 else 0 )
		fictiv[i][j] = 1 if tmp else 0

#тут начинается вывод
print('подстановка')
print(sbox)
print('функции')
for i in range(size):
	print(functions[i])
print('веса')
print(weight)
print('преобладание')
bias = [1 - w / (2**(size-1)) for w in weight]
print(bias)
print('многочлены жегалкина')
for i in range(size):
	string = ""
	for j in range(2**size):
		if (jeg[i][j]):
			str = " "
			for k in range(size):
				str += f"x({k})*" if j//(2**k)%2 else ""
			string += str[:-1] + " " + "^"
	print(string[:-2])
print('фиктивность (0 значит она фиктивна, 1 - существенна)')
print(fictiv)

print('--------------------')

# начинаем вторую лабу

class Tree:
	def __init__(self, vec):
		self.vectors = vec.copy()
		self.parent = self
		self.c = []
	def next_step(self, func):
		self.zero = Tree([])
		self.one = Tree([])
		self.zero.parent = self
		self.one.parent = self
		self.zero.c = self.c + [0]
		self.one.c = self.c + [1]
		for i in self.vectors:
			j = i[-(size-1):]
			sum = 0
			for k in range(len(j)):
				sum = sum + j[k] * (2**(size-k-1))
			if (func[sum]):
				self.one.vectors.append(i + [0])
			else:
				self.zero.vectors.append(i + [0])
			sum = sum + 1
			if (func[sum]):
				self.one.vectors.append(i + [1])
			else:
				self.zero.vectors.append(i + [1])

vec = itertools.product([0, 1], repeat = size)
v = [list(i) for i in vec]
t = Tree(v)
zapret = [0 for i in range(size)]
for k in range(len(functions)):
	tmp = [t]
	min = math.inf
	next = []
	count = 0
	while(1):
		for i in tmp:
			i.next_step(functions[k])
			if (len(i.one.vectors) == min):
				next.append(i.one)
			if (len(i.zero.vectors) == min):
				next.append(i.zero)
			if (len(i.one.vectors) < min):
				min = len(i.one.vectors)
				next = [i.one]
			if (len(i.zero.vectors) < min):
				min = len(i.zero.vectors)
				next = [i.zero]
		if (min == 0):
			break
		tmp = next.copy()
		next = []
		count = count + 1
		if (min == 2**(size) and count > size*4):
			zapret[k] = -1
			break
	for i in tmp:
		i.next_step(functions[k])
		if (len(i.one.vectors) == 0):
			zapret[k] = i.one.c
		if (len(i.zero.vectors) == 0):
			zapret[k] = i.zero.c

#начинаем вывод
print('запреты')
for i in zapret:
	print(i)
print('-------')
#начинаем третью лабу

def wa_step(f, size, step, i):
	j = 0
	while (j < 2**size):
		if ((j // 2**step) % 2):
			f[i][j], f[i][j - 2**(step)] = -f[i][j] + f[i][j - 2**(step)], f[i][j] + f[i][j - 2**(step)]
		j = j + 1

def wolsh_adamar(func, size):
	f = copy.deepcopy(func) # копирование листа чтоб начальный не менять
	for i in range(size):
		for step in range(size):
			wa_step(f, size, step, i)
	return f

f_coefs = wolsh_adamar(functions, size) # вызов бпф

for i in range(len(f_coefs)):
	for j in range(len(f_coefs[i])):
		f_coefs[i][j] = f_coefs[i][j] / (2**size) #коррекция результата для получения коэффициентов фурье

wa = copy.deepcopy(f_coefs) # из ранее полученных коэффициентов строим следующие

for i in range(len(wa)):
	for j in range(len(wa[i])):
		wa[i][j] = (1 - 2 * wa[i][j]) if (j == 0) else (-2 * wa[i][j]) # корректирум для получения коэффициентов уолша адамара

st_struct = copy.deepcopy(wa) # из ранне полученный коэффициентов строим следующие

for i in range(len(st_struct)): #
	for j in range(len(st_struct[i])):
		st_struct[i][j] = st_struct[i][j] * 2**(size-1) # корректируем для коэффициентов стат структуры

kor_imun = [[1 for i in range(size)] for i in range(size)]

for j in range(len(wa)):
	for vector in v:
		index = 0
		for i in range(len(vector)):
			index += 2**(size - i - 1) * vector[i]
		if (wa[j][index] != 0):
			kor_imun[j][sum(vector) - 1] = 0

for i in range(size):
	for j in range(size):
		if (kor_imun[i][j] == 0):
			kor_imun[i] = j
			break

# только тут мы получаем корреляционную имунность

lin_pribl = [[] for i in range(size)]

for i in range(len(st_struct)):
	max_abs = max(abs(x) for x in st_struct[i])
	for j in range(len(st_struct[i])):
		if (abs(st_struct[i][j]) == max_abs):
			lin_pribl[i].append(v[j]) # добавляем еще 1 линейную функцию приближенную к данной

bent = [1 for i in range(size)]

for i in range(len(wa)):
	for j in range(len(wa[i])):
		if (abs(wa[i][j]) != abs(wa[i][0])):
			bent[i] = 0
			break

auto_cor = [[0 for i in range(2**size)] for i in range(size)]

for i in range(size):
	for j in range(2**size):
		for k in range(2**size):
			auto_cor[i][j] += (-1)**(functions[i][k] ^ functions[i][j ^ k])
		auto_cor[i][j] /= 2**size

# начинаем вывод
print('кореляционная имунность и эластичность')
for i in kor_imun: # и кореляционная имунность и эластичность
	print(i)

print('статструктура')
for i in st_struct:
	print(i)

print('линейные приближения')
for i in lin_pribl:
	print(i)

print("автокореляция")
for i in auto_cor:
	print(i)

print("бентность")
print(bent)

# ==========================================
# ЛАБОРАТОРНАЯ РАБОТА №4: Комбинирующий генератор и криптоанализ
# ==========================================
print('\n--------------------')
print('=== Лабораторная работа №4 ===')

import time

class LFSR:
    def __init__(self, length, taps, init_state):
        self.length = length
        self.taps = taps
        self.state = list(init_state)
        
    def step(self):
        fb = 0
        for tap in self.taps:
            fb ^= self.state[tap]
        out = self.state[-1]
        self.state = [fb] + self.state[:-1]
        return out

def generate_m_sequence(length, taps, init_state, count):
    s = 0
    for i, b in enumerate(init_state):
        s |= (b << i)
        
    seq = [0] * count
    mask = (1 << length) - 1
    
    for i in range(count):
        fb = 0
        for tap in taps:
            fb ^= (s >> tap)
        fb &= 1
        seq[i] = (s >> (length - 1)) & 1
        s = ((s << 1) & mask) | fb
        
    return seq

def solve_gf2_system(matrix, vector, num_vars):
    rows = []
    for eq, val in zip(matrix, vector):
        row = [(eq >> i) & 1 for i in range(num_vars)] + [val]
        rows.append(row)
        
    num_eqs = len(rows)
    
    h = 0  # pivot row
    k = 0  # pivot col
    while h < num_eqs and k < num_vars:
        pivot = -1
        for i in range(h, num_eqs):
            if rows[i][k] == 1:
                pivot = i
                break
        if pivot == -1:
            k += 1
            continue
            
        rows[h], rows[pivot] = rows[pivot], rows[h]
        
        for i in range(num_eqs):
            if i != h and rows[i][k] == 1:
                for j in range(k, num_vars + 1):
                    rows[i][j] ^= rows[h][j]
        h += 1
        k += 1
        
    solution = [0] * num_vars
    for i in range(num_eqs):
        leading_col = -1
        for j in range(num_vars):
            if rows[i][j] == 1:
                leading_col = j
                break
        if leading_col == -1:
            if rows[i][num_vars] != 0:
                return None  # Inconsistent
        else:
            solution[leading_col] = rows[i][num_vars]
            
    return solution

def run_lab4():
    # LFSR parameters
    L1, taps1 = 17, [16, 2]
    L2, taps2 = 22, [21, 0]
    L3, taps3 = 25, [24, 2]
    
    # Secret Key (Initial States, non-zero) - use independent local generator
    rng = random.Random(42)
    key1 = [rng.randint(0, 1) for _ in range(L1)]
    key2 = [rng.randint(0, 1) for _ in range(L2)]
    key3 = [rng.randint(0, 1) for _ in range(L3)]
    
    if sum(key1) == 0: key1[0] = 1
    if sum(key2) == 0: key2[0] = 1
    if sum(key3) == 0: key3[0] = 1
    
    print(f"Секретный ключ LFSR 1 (17 бит): {key1}")
    print(f"Секретный ключ LFSR 2 (22 бит): {key2}")
    print(f"Секретный ключ LFSR 3 (25 бит): {key3}")
    print(f"Суммарная длина ключа: {L1 + L2 + L3} бит (>= 64 бит)")
    
    # Keystream generation
    n_bits = 200  # Number of observed keystream bits
    
    lfsr1 = LFSR(L1, taps1, key1)
    lfsr2 = LFSR(L2, taps2, key2)
    lfsr3 = LFSR(L3, taps3, key3)
    
    keystream = []
    x1_seq = []
    x2_seq = []
    
    for _ in range(n_bits):
        bit1 = lfsr1.step()
        bit2 = lfsr2.step()
        bit3 = lfsr3.step()
        x1_seq.append(bit1)
        x2_seq.append(bit2)
        # Combining function: f(x1, x2, x3) = x1*x2 ^ x1*x3 ^ x2*x3
        gamma = (bit1 & bit2) ^ (bit1 & bit3) ^ (bit2 & bit3)
        keystream.append(gamma)
        
    print(f"Сгенерировано {n_bits} бит наблюдаемой гаммы.")
    
    # Convert keystream to integer for fast bitwise comparisons
    gamma_int = 0
    for b in keystream:
        gamma_int = (gamma_int << 1) | b
        
    # ==========================================
    # Phase 1: Attack on LFSR 1
    # ==========================================
    print("\n--- Фаза 1: Атака на LFSR 1 (длина 17) ---")
    start = time.time()
    
    period1 = (1 << L1) - 1
    ref_init1 = [0] * (L1 - 1) + [1]
    seq1 = generate_m_sequence(L1, taps1, ref_init1, period1 + n_bits)
    
    mask1 = (1 << n_bits) - 1
    window = 0
    for b in seq1[:n_bits]:
        window = (window << 1) | b
        
    correct_offset1 = -1
    min_mismatches = n_bits
    
    for offset in range(period1):
        mismatches = (window ^ gamma_int).bit_count()
        if mismatches < min_mismatches:
            min_mismatches = mismatches
            correct_offset1 = offset
            
        if offset + n_bits < len(seq1):
            window = ((window << 1) & mask1) | seq1[offset + n_bits]
            
    recovered_key1 = seq1[correct_offset1 : correct_offset1 + L1][::-1]
    duration1 = time.time() - start
    print(f"LFSR 1 восстановлен за {duration1:.4f} сек!")
    print(f"Восстановленное состояние: {recovered_key1}")
    print(f"Совпадение: {recovered_key1 == key1}")
    
    # ==========================================
    # Phase 2: Attack on LFSR 2
    # ==========================================
    print("\n--- Фаза 2: Атака на LFSR 2 (длина 22) ---")
    start = time.time()
    
    period2 = (1 << L2) - 1
    ref_init2 = [0] * (L2 - 1) + [1]
    seq2 = generate_m_sequence(L2, taps2, ref_init2, period2 + n_bits)
    
    window = 0
    for b in seq2[:n_bits]:
        window = (window << 1) | b
        
    correct_offset2 = -1
    min_mismatches = n_bits
    
    for offset in range(period2):
        mismatches = (window ^ gamma_int).bit_count()
        if mismatches < min_mismatches:
            min_mismatches = mismatches
            correct_offset2 = offset
            
        if offset + n_bits < len(seq2):
            window = ((window << 1) & mask1) | seq2[offset + n_bits]
            
    recovered_key2 = seq2[correct_offset2 : correct_offset2 + L2][::-1]
    duration2 = time.time() - start
    print(f"LFSR 2 восстановлен за {duration2:.4f} сек!")
    print(f"Восстановленное состояние: {recovered_key2}")
    print(f"Совпадение: {recovered_key2 == key2}")
    
    # ==========================================
    # Phase 3: Algebraic recovery of LFSR 3
    # ==========================================
    print("\n--- Фаза 3: Алгебраическое восстановление LFSR 3 (длина 25) ---")
    start = time.time()
    
    r_lfsr1 = LFSR(L1, taps1, recovered_key1)
    r_lfsr2 = LFSR(L2, taps2, recovered_key2)
    rec_x1 = [r_lfsr1.step() for _ in range(n_bits)]
    rec_x2 = [r_lfsr2.step() for _ in range(n_bits)]
    
    state_eqs = [1 << i for i in range(L3)]
    
    equations = []
    vector = []
    
    for t in range(n_bits):
        out_eq = state_eqs[-1]
        
        fb_eq = 0
        for tap in taps3:
            fb_eq ^= state_eqs[tap]
        state_eqs = [fb_eq] + state_eqs[:-1]
        
        x1_val = rec_x1[t]
        x2_val = rec_x2[t]
        if (x1_val ^ x2_val) == 1:
            target_val = keystream[t] ^ (x1_val & x2_val)
            equations.append(out_eq)
            vector.append(target_val)
            
    sol = solve_gf2_system(equations, vector, L3)
    
    solved = sol is not None
    recovered_key3 = sol
                
    duration3 = time.time() - start
    if solved:
        print(f"LFSR 3 восстановлен за {duration3:.4f} сек!")
        print(f"Восстановленное состояние: {recovered_key3}")
        print(f"Совпадение: {recovered_key3 == key3}")
    else:
        print("Не удалось решить систему уравнений для LFSR 3.")
        
    print("\n==========================================")
    print("Итоги атаки:")
    print(f"LFSR 1: {'Успешно' if recovered_key1 == key1 else 'Ошибка'} ({duration1:.4f}s)")
    print(f"LFSR 2: {'Успешно' if recovered_key2 == key2 else 'Ошибка'} ({duration2:.4f}s)")
    print(f"LFSR 3: {'Успешно' if recovered_key3 == key3 else 'Ошибка'} ({duration3:.4f}s)")
    print(f"Общее время подбора: {duration1 + duration2 + duration3:.4f} секунд!")
    print("==========================================")

run_lab4()

