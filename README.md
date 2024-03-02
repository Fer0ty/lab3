# Отчёт по лабораторной работе №3

- Выполнил: Соловьев Артемий
- Группа: P33151
- Вариант: `lisp | acc | harv | mc | tick | struct | stream | port | pstr | prob5 | [4]char'

## Язык программирования

```
<expression> ::= <*-expression> | <literal> | <identifier>
<expressions> ::= <expression> | <expression> <expressions>

<multi-expression> ::= "(" <expressions> ")"

<load-by-ptr-expression> ::= "(" "@" <identifier> ")"

<if-expression> ::= "(" "if" <expression> <if-body> ")"
<if-body> ::= <expression> | <expression> <expression>

<alloc-str-expression> ::= "(" "alloc_str" <identifier> <int-literal> ")"

<set-ptr-expression> ::= "(" "set_ptr" <identifier> <expression> ")"

<set-expression> ::= "(" "set" <identifier> <expression> ")"

<loop-while-expression> ::= "(" "loop" "while" <expression> "do" <expressions> ")"

<put-char-expression> ::= "(" "put_char" <expression> ")"
<get-char-expression> ::= "(" "get_char" ")"

<let-var> ::= "(" <identifier> <expression> ")"
<let-vars> ::= <let-var> | <let-var> <let-vars>
<let-expression> ::= "(" "let" "(" <let-vars> ")" <expressions> ")"

<math-expression> ::= "(" <math-op> <expression> <expression> ")"
<math-op> ::= ">" | ">=" | "<" | "<=" | "=" | "!=" | "+" | "-" | "<<" | ">>"

<defun-expression> ::= "(" "defun" <identifier> "(" <identifiers> ")" <expressions> ")"

<func-call-expression> ::= "(" <identifier> <expressions> ")"

<identifiers> ::= <identifier> | <identifier> <identifiers>
<identifier> ::= [a-zA-Z]+

<literal> ::= <string-literal> | <int-literal> | <bool-literal>
<string-literal> ::= "\"" [a-zA-Z]+ "\""
<int-literal> ::= [0-9]+
<bool-literal> ::= "true" | "false"

<macro> :: "#include " .+ <EOL>
```
- `let` - создать переменные на стеке, которые будут видимы внутри тела данного выражения, возвращает то - что вернуло последнее выражение в теле.
- `get_char` - выражение возвращает число от 0 до 255, которое представляет собой следующий полученный символ из потока ввода, где 0 обозначает конец потока.
- `put_char` - помещает значение полученное в теле выражения в поток вывода
- `set` - установить для переменной значение, полученное из тела выражения
- `set_ptr` - установить по указателю для переменной значение, полученное из тела выражения
- `loop while ... do` - повторное выполняет действие в теле выражения, пока условие не станет равным 0
- `@`- возвращает значение, полученное по указателю
    - Если просто указать идентификатор, то будет загрузка по значению
- `defun` - позволяет определить функцию, работает только в глобальном скоупе, чтобы внутри выражений других не было определение функций
- `alloc_str` - позволяет аллоцировать статический строковой буфер, оптимизируя так, чтобы 4 символа помещались в одно машинное слово, работает только в глобальном скоупе
- `math-expression` - выполняет математическое действие и возвращает результат, для вычисления сначала вычисляется правый операнд, который затем добавляется на стек, после чего вычисляется левый операнд и производится математическая операция. Для операций сравнения результат 1 или 0
- `if` - если выражение в условии отличается от 0, то возвращает первое выражение в теле, иначе второе выражение или 0, если второе выражение отсутствует
- вызов функции - помещает адрес возврата и все аргументы по очереди на стек, затем переход на адрес функции
- числовой литерал - сразу возвращает число
- строковой литерал - все строковые литералы в программе статически выделены в памяти, возвращается адрес этого литерала
- булевый литерал - становится числом 1 или 0

Память для строковых литералов, строковых буферов выделяется статически и их видимость глобальная. Локальные переменные создаются с помощью `let` и хранятся на стеке.

## Организация памяти
По варианту используется гарвардская архитектура, поэтому память инструкций и память данных разделена.

Память инструкций представляет собой список объектов, которые описывают инструкции. 

Память данных - линейное адресное пространство, где одно машинное слово - 32 бит. В коде реализуется словарем, чтобы не хранить все нули между началом памяти и вершиной стека.

- Константы не описаны, так как в языке они отсутствуют
- Числовые литералы загружаются в аккумулятор, когда они встречаются
- Строковые литералы статически выделены в порядке очереди в начале памяти данных, и когда они встречаются, используется их адрес в памяти. Одинаковые строковые литералы будут переиспользоваться. В одном машинном слове хранятся 4 символа.
- Булевые литералы превращаются в числовые, где 1 - true, а 0 - false
- Строковые буферы также статически выделяются в памяти данных при компиляции, изначально заполнены нулями, при их встрече используется адрес начала буффера.
- При использовании выражения `let` созданные переменные будут помещены на стек, и их область видимости ограничена выражением `let`
- В памяти инструкций функции хранятся по очереди в начале памяти, основная программа будет расположена после всех функций



## Система команд
**Особенности процессора:**
- Машинное слово - 32 бит, знаковое
- Доступ к памяти данных осуществляется по адресу, который указан в инструкции
- Ввод-вывод осуществляется через регистр IO Port
- AC (Аккумулятор) - для бинарных и унарных операций
- Поток управления 
  - CMP - позволяет установить флаги 
  - Инструкции по флагам будут изменять PC

**Пример кодирования инструкции:**
```json
{
    "instructions": [
            {
                "instr_index": 0,
                "op_code": "LD",
                "operand_type": "immediate",
                "operand": 0,
                "comment": "load literal 0"
            }
    ]
}
```
 `instr_index` - номер инструкции в скомпилированной программе
- `op_code` - инструкция
- `operand_type` - тип операнда 
    - `no_operand` - для отладки, но по факту тоже `immediate`
    - `immediate` - загрузка числа
    - `address` - загрузка по адресу
    - `pointer_address` - косвенная загрузка по адресу в ячейке памяти
    - `stack_offset` - загрузить с вершины стека по номеру
    - `pointer_stack_offset` - косвенно по ячейки в стеке
- `operand` - число/адрес/номер в стеке
### Набор инструкций:
<Инструкция> M: M будет использоваться как адрес

<Инструкция> O: будет произведено чтение из памяти по адресу O
  - **Math operations**
    - ADD O
    - SUB O
    - AND O
    - OR  O
    - SHL O
    - SHR O
  - **Memory access**
    - LD O
    - ST M 
  - **Stack manipulation**
    - PUSH 
    - POP 
  - **Branching** 
    - CMP O 
    - JZ  M 
    - JNZ M 
    - JA  M 
    - JAE M 
    - JB  M 
    - JBE M 
    - JMP M 
  - **Machine control**
    - HLT - остановка (установка флага HLT в CU)

В качестве первого источника данных и хранения результата операции используется аккумулятор.
Второй операнд указывается в инструкции (O или M).

## Транслятор

Состав транслятора:
- [lexer.py](lab3%2Fcompiler%2Flexer.py)- разбивает поток символов на токены, проверяет на простые ошибки (например, незакрытые скобки)
- [ast.py](lab3%2Fcompiler%2Fast.py)- использует тонки для построения абстрактного синтаксического дерева, проверяет на соответсвие синтаксису
- [backend.py](lab3%2Fcompiler%2Fbackend.py)- использует AST для упаковки программы. В программе есть все необходимые инструкции, статически выделенные данные в память

```bash
$ poetry install
$ poetry shell
$ python -m lab3.compiler <input_file> <output_file>
```
## Модель процессора
### Data Path
![proc_model.png](resources%2Fproc_model.png)

Сигналы (реализуются в микрокомандах [microcode.json](lab3%2Fmachine%2Fmicrocode.json), [microcode.py](lab3%2Fmachine%2Fmicrocode.py)) на схеме отображены голубыми линиями:
- latch_[регистр] - открыть вентиль для записи в регистр
- write_io_latch - открыть вентиль для записи в регистр ввода-вывода
- write_data_latch - открыть вентиль для записи в память данных, в ячейку, указанную в AR
- data_io_sel:
  - 0: дальше пойдут данные из памяти данных
  - 1: дальше пойдут данные из IO Port'а
- dr_mux:
  - 0: в DR будут направлены данные из АЛУ
  - 1: в DR будут направлены данные из (памяти данных или IO Port'а)
- pc_to_br:
  - 0: в BR будут направлены данных из АЛУ
  - 1: в BR будут направленны данные из PC
- alu_lop_sel: - выбор левого операнда АЛУ
  - 11: 0
  - 00: AC
  - 01: BR
  - 10: IR
- alu_rop_sel: - выбор правого операнда АЛУ
  - 11: 0
  - 00: DR
  - 01: AR
  - 10: SP
- alu_op: - выбор операции АЛУ
  - ADD 
  - SUB 
  - AND 
  - OR 
  - SHL 
  - SHR 
  - INC
  - DEC
  - NOT 

Данные подключения к Control Unit (оранжевые линии)Ж
- op_code
- operand
- operand_type
- Флаги:
  - N: Число на выходе АЛУ отрицательное (31 бит "1")
  - Z: Значение на выходе АЛУ нулевое
  - C: Был перенос в 32 бит

### Control Unit
![control_unit.png](resources%2Fcontrol_unit.png)

Два вида микрокоманд:
- Управляющие - отправляют сигналы
- Ветвления - переход на микро-инструкцию, если результат функции логического И для 9 операндов "1".
Есть специальный вид команды, где игнорируются все остальные биты и происходит ветвление по результату декодера `OP_CODE`

**Микрокоманды:**
```
0 IR <- INSTR_MEMORY (start)
1 BR <- PC 
2 PC <- AluLopSel.SEL_BR AluOp.INC AluRopSel.SEL_ZERO 
3 JUMP TO DECODE(OP_CODE) IF OP_CODE IN ['PUSH', 'POP', 'HLT'] 
4 JUMP TO 9 IF OPERNAD_TYPE IN ['pointer_address'] 
5 JUMP TO 12 IF OPERNAD_TYPE IN ['stack_offset', 'pointer_stack_offset'] 
6 DR <- AluLopSel.SEL_IR AluOp.ADD AluRopSel.SEL_ZERO (fetch_immediate_or_no_operand_or_address)
7 JUMP TO 16 IF OPERNAD_TYPE IN ['address'] 
8 JUMP TO 17 IF 
9 AR <- AluLopSel.SEL_IR AluOp.ADD AluRopSel.SEL_ZERO (fetch_pointer_address)
10 DR <- DataIoMuxSel.SEL_DATA 
11 JUMP TO 16 IF 
12 DR <- AluLopSel.SEL_IR AluOp.ADD AluRopSel.SEL_SP (fetch_stack_offset)
13 JUMP TO 16 IF OPERNAD_TYPE IN ['stack_offset'] 
14 AR <- AluLopSel.SEL_ZERO AluOp.ADD AluRopSel.SEL_DR 
15 DR <- DataIoMuxSel.SEL_DATA 
16 AR <- AluLopSel.SEL_ZERO AluOp.ADD AluRopSel.SEL_DR (fetch_operand)
17 JUMP TO DECODE(OP_CODE) IF OP_CODE IN ['JZ', 'JNZ', 'JB', 'JBE', 'JA', 'JAE', 'JMP', 'ST'] (execute)
18 JUMP TO 23 IF OPERNAD_TYPE IN ['immediate', 'no_operand'] 
19 JUMP TO 22 IF OPERNAD_TYPE IN ['address'] OPERAND = 52 
20 DR <- DataIoMuxSel.SEL_DATA 
21 JUMP TO 23 IF 
22 DR <- DataIoMuxSel.SEL_IO (fetch_from_io)
23 JUMP TO DECODE(OP_CODE) IF (execute2)
24 AC <- AluLopSel.SEL_ZERO AluOp.ADD AluRopSel.SEL_DR (OpCode.LD)
25 JUMP TO 67 IF 
26 JUMP TO 29 IF OPERNAD_TYPE IN ['address'] OPERAND = 69 (OpCode.ST)
27 DATA <- AluLopSel.SEL_AC AluOp.ADD AluRopSel.SEL_ZERO 
28 JUMP TO 67 IF 
29 IO <- AluLopSel.SEL_AC AluOp.ADD AluRopSel.SEL_ZERO (st_to_io)
30 JUMP TO 67 IF 
31 BR <- AluLopSel.SEL_AC AluOp.ADD AluRopSel.SEL_DR PS <- NZC(AluLopSel.SEL_AC AluOp.ADD AluRopSel.SEL_DR) (OpCode.ADD)
32 JUMP TO 42 IF 
33 BR <- AluLopSel.SEL_AC AluOp.SUB AluRopSel.SEL_DR PS <- NZC(AluLopSel.SEL_AC AluOp.SUB AluRopSel.SEL_DR) (OpCode.SUB)
34 JUMP TO 42 IF 
35 BR <- AluLopSel.SEL_AC AluOp.AND AluRopSel.SEL_DR PS <- NZC(AluLopSel.SEL_AC AluOp.AND AluRopSel.SEL_DR) (OpCode.AND)
36 JUMP TO 42 IF 
37 BR <- AluLopSel.SEL_AC AluOp.OR AluRopSel.SEL_DR PS <- NZC(AluLopSel.SEL_AC AluOp.OR AluRopSel.SEL_DR) (OpCode.OR)
38 JUMP TO 42 IF 
39 BR <- AluLopSel.SEL_AC AluOp.SHL AluRopSel.SEL_DR PS <- NZC(AluLopSel.SEL_AC AluOp.SHL AluRopSel.SEL_DR) (OpCode.SHL)
40 JUMP TO 42 IF 
41 BR <- AluLopSel.SEL_AC AluOp.SHR AluRopSel.SEL_DR PS <- NZC(AluLopSel.SEL_AC AluOp.SHR AluRopSel.SEL_DR) (OpCode.SHR)
42 AC <- AluLopSel.SEL_BR AluOp.ADD AluRopSel.SEL_ZERO (math_end)
43 JUMP TO 67 IF 
44 BR <- AluLopSel.SEL_ZERO AluOp.DEC AluRopSel.SEL_SP (OpCode.PUSH)
45 AR <- AluLopSel.SEL_BR AluOp.ADD AluRopSel.SEL_ZERO SP <- AluLopSel.SEL_BR AluOp.ADD AluRopSel.SEL_ZERO 
46 DATA <- AluLopSel.SEL_AC AluOp.ADD AluRopSel.SEL_ZERO 
47 JUMP TO 67 IF 
48 BR <- AluLopSel.SEL_ZERO AluOp.ADD AluRopSel.SEL_SP (OpCode.POP)
49 SP <- AluLopSel.SEL_BR AluOp.INC AluRopSel.SEL_ZERO 
50 JUMP TO 67 IF 
51 HLT (OpCode.HLT)
52 JUMP TO 67 IF 
53 PS <- NZC(AluLopSel.SEL_AC AluOp.SUB AluRopSel.SEL_DR) (OpCode.CMP)
54 JUMP TO 67 IF 
55 JUMP TO 66 IF Z = True (OpCode.JZ)
56 JUMP TO 67 IF 
57 JUMP TO 66 IF Z = False (OpCode.JNZ)
58 JUMP TO 67 IF 
59 JUMP TO 66 IF N = False (OpCode.JAE)
60 JUMP TO 66 IF N = False Z = False (OpCode.JA)
61 JUMP TO 67 IF 
62 JUMP TO 67 IF 
63 JUMP TO 66 IF N = True (OpCode.JBE)
64 JUMP TO 66 IF N = True Z = False (OpCode.JB)
65 JUMP TO 67 IF 
66 PC <- AluLopSel.SEL_ZERO AluOp.ADD AluRopSel.SEL_DR (OpCode.JMP)
67 JUMP TO 0 IF (end)
```
Можно получить, запустив:
```bash
$ poetry install
$ poetry shell
$ poetry run python -m lab3.machine <input_file> [<input_stream>] [--show-statistics, --logs]
```
### Тестирование

Этап golden тестирования CI "CI".

**Вывод**

Программа должна вывести `Hello World!`:  [hello.yml](tests%2Fgolden_tests%2Fhello.yml)

**Ввод-вывод**

Программа должна вывести введенную строку: [cat.yml](tests%2Fgolden_tests%2Fcat.yml), [hello_user_name.yml](tests%2Fgolden_tests%2Fhello_user_name.yml)

**Задача**
[Программа](examples%2Feuler_problem_5.lisq) должна вывести `23`

**Тесты на компонент АЛУ [test_alu.py](tests%2Fmachine%2Ftest_alu.py)**

Запуск тестов
```bash
$ poetry install
$ poetry shell
$ make test-cov # make test чтобы запускать без вычисления покрытия тестами
```
Пример использования и журнал работы `cat`:
```
poetry install
poetry shell
make
poetry run python -m lab3.compiler examples/hello.lisq output/examples/hello.json
poetry run python -m lab3.compiler examples/euler_problem_1.lisq output/examples/euler_problem_5.json
poetry run python -m lab3.compiler examples/hello_user_name.lisq output/examples/hello_user_name.json
poetry run python -m lab3.compiler examples/cat.lisq output/examples/cat.json
poetry run python -m lab3.machine output/examples/cat.json foo --show-statistics --logs
```
Логи: [cat.yml](tests%2Fgolden_tests%2Fcat.yml)

Покрытие тестами:
```
tests/test_golden.py::test_golden[golden_tests/euler_problem_5.yml] PASSED                                                                                                                    [  8%]
tests/test_golden.py::test_golden[golden_tests/cat.yml] PASSED                                                                                                                                [ 16%]
tests/test_golden.py::test_golden[golden_tests/hello.yml] PASSED                                                                                                                              [ 25%]
tests/test_golden.py::test_golden[golden_tests/hello_user_name.yml] PASSED                                                                                                                    [ 33%]
tests/machine/test_alu.py::test_compliment[0-0] PASSED                                                                                                                                        [ 41%]
tests/machine/test_alu.py::test_compliment[1-4294967295] PASSED                                                                                                                               [ 50%]
tests/machine/test_alu.py::test_compliment[52-4294967244] PASSED                                                                                                                              [ 58%]
tests/machine/test_alu.py::test_alu_addition PASSED                                                                                                                                           [ 66%]
tests/machine/test_alu.py::test_alu_add_zero PASSED                                                                                                                                           [ 75%]
tests/machine/test_alu.py::test_alu_overflow_add PASSED                                                                                                                                       [ 83%]
tests/machine/test_alu.py::test_alu_above_or_equals PASSED                                                                                                                                    [ 91%]
tests/machine/test_alu.py::test_alu_below PASSED                                                                                                                                              [100%]

---------- coverage: platform darwin, python 3.11.5-final-0 ----------
Name                             Stmts   Miss  Cover
----------------------------------------------------
lab3/common/instructions.py         58      0   100%
lab3/compiler/__init__.py           16      0   100%
lab3/compiler/ast.py               441     88    80%
lab3/compiler/backend.py           214     12    94%
lab3/compiler/lexer.py              88      8    91%
lab3/compiler/preprocessing.py       8      0   100%
lab3/machine/__init__.py            23      3    87%
lab3/machine/common.py              22      0   100%
lab3/machine/components.py         155     12    92%
lab3/machine/control_unit.py        35      1    97%
lab3/machine/datapath.py            64      1    98%
lab3/machine/microcode.py          197      9    95%
----------------------------------------------------
TOTAL                             1321    134    90%

Required test coverage of 70% reached. Total coverage: 89.86%

======================================================================================== 12 passed in 41.04s ========================================================================================
```
