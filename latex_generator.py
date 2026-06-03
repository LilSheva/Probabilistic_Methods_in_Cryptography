import argparse
import random
import itertools
import math
import copy

class LatexDocument:
    def __init__(self, verbosity='mid'):
        self.verbosity = verbosity
        self.content = []
        self.add_preamble()

    def add_preamble(self):
        preamble = r"""\documentclass[14pt, a4paper]{extarticle}
\usepackage[utf8]{inputenc}
\usepackage[russian]{babel}
\usepackage{amsmath, amsfonts, amssymb}
\usepackage[left=30mm, right=15mm, top=20mm, bottom=20mm]{geometry}
\usepackage{setspace}
\onehalfspacing
\usepackage{indentfirst}
\usepackage{graphicx}
\usepackage{longtable}

\begin{document}

\begin{titlepage}
\begin{center}
    \textbf{Министерство науки и высшего образования Российской Федерации}\\
    \textbf{НАЗВАНИЕ ВАШЕГО ВУЗА}\\
    \vspace{2cm}
    \textbf{Факультет (ваша кафедра)}\\
    \vspace{4cm}
    {\Large \textbf{КУРСОВАЯ РАБОТА}}\\
    \vspace{0.5cm}
    по дисциплине «Вероятностные методы в криптографии»\\
    \vspace{4cm}
\end{center}
\begin{flushright}
    \textbf{Выполнил:}\\
    Студент(ка) группы ХХХ\\
    Фамилия И. О.\\
    \vspace{1cm}
    \textbf{Проверил:}\\
    Должность, Фамилия И. О.
\end{flushright}
\vfill
\begin{center}
    Город -- 2026
\end{center}
\end{titlepage}

\tableofcontents
\newpage
"""
        self.content.append(preamble)

    def add_section(self, title):
        self.content.append(f"\\section{{{title}}}\n")

    def add_subsection(self, title):
        self.content.append(f"\\subsection{{{title}}}\n")

    def add_text(self, text):
        self.content.append(f"{text}\n")
        
    def add_math(self, expr):
        self.content.append(f"\\[ {expr} \\]\n")

    def add_list(self, items):
        self.content.append("\\begin{itemize}")
        for item in items:
            self.content.append(f"    \\item {item}")
        self.content.append("\\end{itemize}\n")

    def finish(self, filename='coursework.tex'):
        self.content.append("\\end{document}")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.content))
        print(f"File {filename} successfully generated!")

def fft_step(f, size, step, i):
    j = 0
    while (j < 2**size):
        if ((j // 2**step) % 2):
            f[i][j] = f[i][j] ^ f[i][j - 2**(step)]
        j = j + 1

def jegalkin(func, size):
    f = [[func[i][j] for j in range(2**size)] for i in range(size)]
    for i in range(size):
        for step in range(size):
            fft_step(f, size, step, i)
    return f

def wa_step(f, size, step, i):
    j = 0
    while (j < 2**size):
        if ((j // 2**step) % 2):
            f[i][j], f[i][j - 2**(step)] = -f[i][j] + f[i][j - 2**(step)], f[i][j] + f[i][j - 2**(step)]
        j = j + 1

def wolsh_adamar(func, size):
    f = copy.deepcopy(func)
    for i in range(size):
        for step in range(size):
            wa_step(f, size, step, i)
    return f

class Tree:
    def __init__(self, vec, size):
        self.vectors = vec.copy()
        self.parent = self
        self.c = []
        self.size = size
    def next_step(self, func):
        self.zero = Tree([], self.size)
        self.one = Tree([], self.size)
        self.zero.parent = self
        self.one.parent = self
        self.zero.c = self.c + [0]
        self.one.c = self.c + [1]
        for i in self.vectors:
            j = i[-(self.size-1):]
            sum_val = 0
            for k in range(len(j)):
                sum_val += j[k] * (2**(self.size-k-1))
            if (func[sum_val]):
                self.one.vectors.append(i + [0])
            else:
                self.zero.vectors.append(i + [0])
            sum_val += 1
            if (func[sum_val]):
                self.one.vectors.append(i + [1])
            else:
                self.zero.vectors.append(i + [1])

def run_lab1(doc, size, sbox, functions, weight, jeg, fictiv):
    doc.add_text(r"\newpage")
    doc.add_section("Лабораторная работа №1")
    doc.add_text(r"\textbf{Задание:}")
    doc.add_list([
        r"Генерируем $g \in V_6 \to V_6$ случ.",
        r"Построить векторы значений для $f_k, k \in \overline{1,6}$ координатных функций $g$.",
        r"$||f_k||$ - ? $k \in \overline{1,6}$.",
        r"Найти мн-н Жегалкина для $f_k, k \in \overline{1,6}$.",
        r"Опр-ть фиктивные переменные для $f_k, k \in \overline{1,6}$."
    ])
    
    if doc.verbosity in ['mid', 'max']:
        doc.add_subsection("Генерация подстановки")
        if doc.verbosity == 'max':
            doc.add_text(r"В криптографии S-блоки (подстановки) играют ключевую роль в обеспечении нелинейности алгоритмов симметричного шифрования. В качестве подстановки $g: V_n \to V_n$ используется случайно сгенерированная биекция (перестановка чисел от $0$ до $2^n-1$).")
        doc.add_text(f"Сгенерирована следующая случайная подстановка ($n={size}$):")
        doc.add_text(f"$S = [{', '.join(map(str, sbox))}]$")
        
        doc.add_subsection("Координатные функции и их вес")
        if doc.verbosity == 'max':
            doc.add_text(r"Координатные функции $f_1, \dots, f_6$ строятся путем перевода каждого значения подстановки в двоичную систему счисления. То есть, $g(x) = (f_1(x), f_2(x), \dots, f_n(x))$.")
            doc.add_text(r"Вес (норма) булевой функции $||f_k||$ — это количество единиц в её векторе значений. Строго говоря, $||f|| = \sum_{x \in V_n} f(x)$. Знание веса позволяет судить о сбалансированности функции.")
    
    for i in range(size):
        if doc.verbosity == 'max':
            func_str = ''.join(map(str, functions[i]))
            doc.add_math(f"f_{i+1} = ({func_str})")
        doc.add_math(f"||f_{i+1}|| = {weight[i]}")

    if doc.verbosity in ['mid', 'max']:
        doc.add_subsection("Многочлены Жегалкина и фиктивные переменные")
        if doc.verbosity == 'max':
            doc.add_text(r"Любая булева функция может быть однозначно представлена в виде многочлена Жегалкина (алгебраической нормальной формы, АНФ).")
            doc.add_text(r"\textbf{Теорема Жегалкина:} Всякая булева функция $f$ единственным образом представима в виде полинома над полем GF(2): $f(x_1, \dots, x_n) = \bigoplus_{I \subseteq \{1,\dots,n\}} a_I \prod_{i \in I} x_i$.")
            doc.add_text(r"Для быстрого вычисления коэффициентов $a_I$ используется алгоритм быстрого преобразования Жегалкина (БПЖ), или преобразование Мёбиуса, имеющий сложность $O(n 2^n)$.")
            doc.add_text(r"Переменная $x_i$ называется \textbf{фиктивной}, если она не входит ни в один моном многочлена Жегалкина, то есть изменение значения этой переменной не влияет на результат функции.")
    
    for i in range(size):
        poly = []
        for j in range(2**size):
            if jeg[i][j]:
                term = []
                for k in range(size):
                    if j // (2**k) % 2:
                        term.append(f"x_{k+1}")
                poly.append("".join(term) if term else "1")
        poly_str = r" \oplus ".join(poly) if poly else "0"
        doc.add_math(f"g_{i+1}(x) = {poly_str}")
        
        fic_vars = [f"x_{j+1}" for j in range(size) if fictiv[i][j] == 0]
        if fic_vars:
            doc.add_text(f"Фиктивные переменные для $f_{i+1}$: ${', '.join(fic_vars)}$")
        else:
            doc.add_text(f"Для $f_{i+1}$ фиктивных переменных нет.")

def run_lab2(doc, size, functions, weight, zapret):
    doc.add_text(r"\newpage")
    doc.add_section("Лабораторная работа №2")
    doc.add_text(r"\textbf{Задание:}")
    doc.add_list([
        r"Для $f_k, k \in \overline{1,3}$ найти преобладание $\delta(f_k)$",
        r"Проверить, явл-ся ли $f_k$ - сильноравновероятной",
        r"Проверить, $f_k$ имеет запреты? Если да, то построить запрет."
    ])
    
    if doc.verbosity in ['mid', 'max']:
        doc.add_subsection("Преобладание нулей над единицами")
        if doc.verbosity == 'max':
            doc.add_text(r"Преобладание нулей над единицами (bias, $\delta(f)$) характеризует отклонение функции от абсолютно случайной (сбалансированной).")
            doc.add_text(r"Определяется по формуле $\delta(f) = 1 - \frac{||f||}{2^{n-1}}$. Если функция идеально сбалансирована, её вес $||f|| = 2^{n-1}$, и преобладание $\delta(f) = 0$.")
            
    bias = [1 - w / (2**(size-1)) for w in weight]
    for i in range(size):
        doc.add_math(f"\\delta(f_{i+1}) = {bias[i]}")
        
    if doc.verbosity in ['mid', 'max']:
        doc.add_subsection("Запреты")
        if doc.verbosity == 'max':
            doc.add_text(r"\textbf{Определение:} Булева функция $f$ называется \textbf{сильно равновероятной}, если в генерируемой ею последовательности $z_i = f(s_i)$ при случайном выборе начального состояния отсутствуют \textit{запреты} (невозможные битовые комбинации).")
            doc.add_text(r"Запрет — это подпоследовательность бит, вероятность появления которой равна нулю. Наличие запретов является серьезной уязвимостью генератора ПСЧ, так как позволяет криптоаналитику отбраковывать неверные предположения о ключе.")
            doc.add_text(r"Для поиска запретов мы строим дерево возможных продолжений последовательности, отслеживая все достижимые внутренние состояния автомата. Поиск прекращается при обнаружении комбинации, множество состояний для которой становится пустым.")
            doc.add_text("Поскольку для каждой функции удалось найти запрет, ни одна из них не является сильно равновероятной.")
    else:
        doc.add_text("Функции не являются сильно равновероятными, так как имеют запреты:")
        
    for i in range(size):
        if zapret[i] == -1:
            doc.add_text(f"Для $f_{i+1}$ запрет не найден за разумное время (длина $>$ {size*4}).")
        else:
            doc.add_text(f"Запрет для $f_{i+1}$: {zapret[i]} (длина {len(zapret[i])})")

def run_lab3(doc, size, functions, st_struct, lin_pribl, auto_cor, bent, kor_imun):
    doc.add_text(r"\newpage")
    doc.add_section("Лабораторная работа №3")
    doc.add_text(r"\textbf{Задание:}")
    doc.add_list([
        r"Построение спектра коорд. функц. $f_i$ (векторы коэф. $\Delta_f^u$)",
        r"Найти наилучшее лин. приближ. для $f_i$",
        r"Построить автокорреляционную ф-ию для $f_i$",
        r"Явл-ся ли $f_i$ - бент-функцией",
        r"Найти все $k$ при которых $f_i$ к.и. порядка $k$ и $k$-устойчивые"
    ])
    
    if doc.verbosity in ['mid', 'max']:
        doc.add_subsection("Спектр стат. структуры и наилучшие линейные приближения")
        if doc.verbosity == 'max':
            doc.add_text(r"Коэффициенты Уолша-Адамара для функции $f$ определяются как $W_f(\vec{u}) = \frac{1}{2^n} \sum_{x \in V_n} (-1)^{f(x) \oplus \langle \vec{u}, x \rangle}$.")
            doc.add_text(r"Коэффициенты статистической структуры $\Delta_f(\vec{u})$ связаны с ними напрямую: $\Delta_f(\vec{u}) = 2^{n-1} W_f(\vec{u})$.")
            doc.add_text(r"Поиск максимального по модулю коэффициента $|\Delta_f(\vec{u})|$ означает поиск наилучшего линейного приближения функции $f(x)$ линейной функцией $L_{\vec{u}}(x) = \langle \vec{u}, x \rangle$. Это является математической основой \textbf{линейного криптоанализа}.")
            
    for i in range(size):
        max_delta = max(abs(x) for x in st_struct[i])
        doc.add_text(f"Максимальный коэффициент $|\\Delta_f|$ для $f_{i+1}$ равен {max_delta}.")
        for u in lin_pribl[i]:
            terms = [f"x_{k+1}" for k in range(size) if u[k]]
            eq = r" \oplus ".join(terms) if terms else "0"
            doc.add_math(f"\\vec{{u}} = {u} \\implies {eq}")
            
    if doc.verbosity in ['mid', 'max']:
        doc.add_subsection("Автокорреляция и бент-свойства")
        if doc.verbosity == 'max':
            doc.add_text(r"Автокорреляционная функция $r_f(\vec{a}) = \frac{1}{2^n} \sum_{x} (-1)^{f(x) \oplus f(x \oplus \vec{a})}$ показывает меру зависимости значений функции при сдвиге аргумента. Низкая автокорреляция важна для противодействия дифференциальному криптоанализу.")
            doc.add_text(r"\textbf{Определение:} Функция $f$ называется \textbf{бент-функцией}, если коэффициенты её преобразования Уолша-Адамара постоянны по модулю для всех $\vec{u}$ ($|W_f(\vec{u})| = 2^{-n/2}$). Бент-функции обладают максимальной нелинейностью и существуют только при четном $n$.")
            
    for i in range(size):
        b = "является" if bent[i] else "не является"
        doc.add_text(f"Функция $f_{i+1}$ {b} бент-функцией.")
        
    if doc.verbosity in ['mid', 'max']:
        doc.add_subsection("Корреляционная иммунность и эластичность")
        if doc.verbosity == 'max':
            doc.add_text(r"\textbf{Определение:} Функция называется корреляционно-иммунной порядка $k$, если она статистически независима от любого подмножества из $k$ входных переменных. Эквивалентно: $\forall \vec{u}, 1 \le ||\vec{u}|| \le k \implies W_f(\vec{u}) = 0$.")
            doc.add_text(r"\textbf{Определение:} Эластичной называется сбалансированная ($W_f(\vec{0}) = 0$) функция с корреляционной иммунностью порядка $k$.")
            doc.add_text(r"\textbf{Теорема (Неравенство Зигенталера):} Если функция $f$ от $n$ переменных корреляционно-иммунна порядка $k$, то её алгебраическая степень $d \le n - k$. Если $f$ еще и сбалансирована (эластична) при $k < n-1$, то $d \le n - k - 1$.")
            
    for i in range(size):
        order = kor_imun[i] if isinstance(kor_imun[i], int) else 0
        doc.add_text(f"Функция $f_{i+1}$ имеет порядок корреляционной иммунности и эластичности $k = {order}.")

def solve_gf2_system(matrix, vector, num_vars):
    rows = []
    for eq, val in zip(matrix, vector):
        row = [(eq >> i) & 1 for i in range(num_vars)] + [val]
        rows.append(row)
        
    num_eqs = len(rows)
    h = 0
    k = 0
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
                return None
        else:
            solution[leading_col] = rows[i][num_vars]
    return solution

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

def run_lab4(doc):
    doc.add_text(r"\newpage")
    doc.add_section("Лабораторная работа №4")
    doc.add_text(r"\textbf{Задание:}")
    doc.add_list([
        r"Реализовать алгоритм шифрования с длиной ключа $\ge 64$ бит.",
        r"Описать атаку (рассчитать параметры) на ключ.",
        r"В соответствии с выбранной атакой подготовить гамму.",
        r"Найти ключ (Корреляционная атака)."
    ])
    
    L1, taps1 = 17, [16, 2]
    L2, taps2 = 22, [21, 0]
    L3, taps3 = 25, [24, 2]
    
    rng = random.Random(42)
    key1 = [rng.randint(0, 1) for _ in range(L1)]
    key2 = [rng.randint(0, 1) for _ in range(L2)]
    key3 = [rng.randint(0, 1) for _ in range(L3)]
    
    if sum(key1) == 0: key1[0] = 1
    if sum(key2) == 0: key2[0] = 1
    if sum(key3) == 0: key3[0] = 1
    
    n_bits = 200
    lfsr1 = LFSR(L1, taps1, key1)
    lfsr2 = LFSR(L2, taps2, key2)
    lfsr3 = LFSR(L3, taps3, key3)
    
    keystream = []
    for _ in range(n_bits):
        bit1 = lfsr1.step()
        bit2 = lfsr2.step()
        bit3 = lfsr3.step()
        gamma = (bit1 & bit2) ^ (bit1 & bit3) ^ (bit2 & bit3)
        keystream.append(gamma)
        
    gamma_int = 0
    for b in keystream:
        gamma_int = (gamma_int << 1) | b
        
    if doc.verbosity in ['mid', 'max']:
        doc.add_subsection("Схема генератора")
        if doc.verbosity == 'max':
            doc.add_text(r"Линейный регистр сдвига с обратной связью (LFSR) — классический блок потоковых шифров. Однако использование одного LFSR абсолютно уязвимо (алгоритм Берлекэмпа-Мэсси). Поэтому применяется комбинирующий генератор из нескольких регистров и нелинейной функции $f(x_1, \dots, x_m)$.")
            doc.add_text(r"В нашей модели используются 3 регистра длин $L_1 = 17, L_2 = 22, L_3 = 25$. Комбинирующая функция (мажоритарная): $f(x_1, x_2, x_3) = x_1 x_2 \oplus x_1 x_3 \oplus x_2 x_3$.")
            doc.add_text(r"Атака Зигенталера (корреляционная атака) применима, если $P(f(x_1,\dots,x_m) = x_i) \neq 0.5$. Для нашей $f$ вероятность совпадения $P(f = x_i) = 0.75$, поэтому атака возможна на все три регистра по отдельности.")
        doc.add_text(f"Суммарная длина ключа: ${L1 + L2 + L3}$ бит.")
        doc.add_text(f"Сгенерирована перехваченная гамма длиной ${n_bits}$ бит.")
        
    if doc.verbosity == 'max':
        doc.add_subsection("Корреляционная атака")
        doc.add_text(r"Определим длину перехватываемой гаммы $N$, необходимую для успешной атаки. Согласно \textbf{лемме Неймана-Пирсона}, $N \approx \left(\frac{3 \sqrt{p(1-p)}}{\varepsilon}\right)^2$, где $p = 0.75, \varepsilon = p - 0.5 = 0.25$.")
        doc.add_text(r"Для надежности возьмем вероятность ошибки $P_{error} < 0.01$, откуда получаем, что $N$ должно быть не менее $186$ бит. Мы используем гамму $N=200$ бит.")
        doc.add_text(r"\textbf{Алгоритм решения (метод скользящего окна):} Мы генерируем полные последовательности для LFSR 1 и LFSR 2 (M-последовательности длины $2^{L}-1$) и сравниваем каждое ''окно'' длины $N$ с перехваченной гаммой, подсчитывая количество несовпадений (расстояние Хэмминга). Минимальное количество несовпадений дает нам правильный сдвиг и, как следствие, начальное заполнение (ключ).")
        
    # Phase 1
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
    doc.add_text(f"LFSR 1 восстановлен: {recovered_key1}. Совпадает с истинным ключом: {recovered_key1 == key1}.")

    # Phase 2
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
    doc.add_text(f"LFSR 2 восстановлен: {recovered_key2}. Совпадает с истинным ключом: {recovered_key2 == key2}.")

    if doc.verbosity == 'max':
        doc.add_subsection("Алгебраическая атака")
        doc.add_text(r"Поскольку регистры 1 и 2 полностью восстановлены, мы знаем последовательности $x_1(t)$ и $x_2(t)$. Для нахождения ключа к регистру 3 (длина 25) мы можем эффективно использовать \textbf{алгебраическую атаку}.")
        doc.add_text(r"В те моменты времени $t$, когда $x_1(t) \neq x_2(t)$, мажоритарная функция $f$ работает как прозрачный повторитель: $f(x_1, x_2, x_3) = x_3$. Следовательно, в эти моменты выход генератора $z(t) = x_3(t)$.")
        doc.add_text(r"Состояние LFSR 3 в любой момент $t$ линейно зависит от его начального состояния $\vec{s}_0$. Таким образом, мы составляем систему линейных уравнений $A \cdot \vec{s}_0 = \vec{b}$ над полем GF(2) и решаем её методом Гаусса. Это требует всего $L_3 = 25$ подходящих битов гаммы, что делает атаку мгновенной.")

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
    doc.add_text(f"LFSR 3 алгебраически восстановлен: {sol}. Совпадает с истинным: {sol == key3}.")

def main():
    parser = argparse.ArgumentParser(description="Coursework LaTeX Generator")
    parser.add_argument('--verbosity', choices=['min', 'mid', 'max'], default='max', help="Уровень детализации отчета")
    args = parser.parse_args()

    print(f"Starting LaTeX generation with verbosity: {args.verbosity}")
    doc = LatexDocument(verbosity=args.verbosity)
    
    # ------------------ PRE-COMPUTE MATH CORE (LAB 1-3) ------------------
    size = 6
    sbox = list(range(2**size))
    random.seed(42)  # For deterministic LaTeX output
    random.shuffle(sbox)
    
    functions = [[0 for _ in range(2**size)] for _ in range(size)]
    for i in range(len(sbox)):
        for j in range(size):
            functions[j][i] = (sbox[i]//(2**j)) % 2
            
    weight = [sum(functions[i]) for i in range(size)]
    jeg = jegalkin(functions, size)
    
    fictiv = [[0 for _ in range(size)] for _ in range(size)]
    for i in range(size):
        for j in range(size):
            tmp = sum(jeg[i][k] for k in range(2**size) if (k//(2**j)) % 2)
            fictiv[i][j] = 1 if tmp else 0

    vec = itertools.product([0, 1], repeat=size)
    v = [list(i) for i in vec]
    
    zapret = [0 for _ in range(size)]
    for k in range(len(functions)):
        t = Tree(v, size)
        tmp_nodes = [t]
        min_len = math.inf
        next_nodes = []
        count = 0
        while True:
            for node in tmp_nodes:
                node.next_step(functions[k])
                if len(node.one.vectors) == min_len:
                    next_nodes.append(node.one)
                if len(node.zero.vectors) == min_len:
                    next_nodes.append(node.zero)
                if len(node.one.vectors) < min_len:
                    min_len = len(node.one.vectors)
                    next_nodes = [node.one]
                if len(node.zero.vectors) < min_len:
                    min_len = len(node.zero.vectors)
                    next_nodes = [node.zero]
            if min_len == 0:
                break
            tmp_nodes = next_nodes.copy()
            next_nodes = []
            count += 1
            if count > size*4:
                zapret[k] = -1
                break
        if zapret[k] != -1:
            for node in tmp_nodes:
                node.next_step(functions[k])
                if len(node.one.vectors) == 0:
                    zapret[k] = node.one.c
                    break
                if len(node.zero.vectors) == 0:
                    zapret[k] = node.zero.c
                    break
                    
    f_coefs = wolsh_adamar(functions, size)
    for i in range(len(f_coefs)):
        for j in range(len(f_coefs[i])):
            f_coefs[i][j] = f_coefs[i][j] / (2**size)
            
    wa = copy.deepcopy(f_coefs)
    for i in range(len(wa)):
        for j in range(len(wa[i])):
            wa[i][j] = (1 - 2 * wa[i][j]) if (j == 0) else (-2 * wa[i][j])
            
    st_struct = copy.deepcopy(wa)
    for i in range(len(st_struct)):
        for j in range(len(st_struct[i])):
            st_struct[i][j] = st_struct[i][j] * 2**(size-1)
            
    kor_imun = [[1 for _ in range(size)] for _ in range(size)]
    for j in range(len(wa)):
        for vector in v:
            index = sum(2**(size - i - 1) * vector[i] for i in range(len(vector)))
            if wa[j][index] != 0:
                kor_imun[j][sum(vector) - 1] = 0
    for i in range(size):
        for j in range(size):
            if kor_imun[i][j] == 0:
                kor_imun[i] = j
                break
                
    lin_pribl = [[] for _ in range(size)]
    for i in range(len(st_struct)):
        max_abs = max(abs(x) for x in st_struct[i])
        for j in range(len(st_struct[i])):
            if abs(st_struct[i][j]) == max_abs:
                lin_pribl[i].append(v[j])
                
    bent = [1 for _ in range(size)]
    for i in range(len(wa)):
        for j in range(len(wa[i])):
            if abs(wa[i][j]) != abs(wa[i][0]):
                bent[i] = 0
                break
                
    auto_cor = [[0 for _ in range(2**size)] for _ in range(size)]
    for i in range(size):
        for j in range(2**size):
            for k in range(2**size):
                auto_cor[i][j] += (-1)**(functions[i][k] ^ functions[i][j ^ k])
            auto_cor[i][j] /= 2**size

    # ------------------ BUILD LATEX ------------------
    run_lab1(doc, size, sbox, functions, weight, jeg, fictiv)
    run_lab2(doc, size, functions, weight, zapret)
    run_lab3(doc, size, functions, st_struct, lin_pribl, auto_cor, bent, kor_imun)
    run_lab4(doc)
    
    doc.finish()

if __name__ == "__main__":
    main()
