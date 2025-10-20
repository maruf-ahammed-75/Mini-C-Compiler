/* Test 2: Advanced Control Flow and Expressions
   Focus: Complex nested structures and edge cases */

// Test 1: Multiple nested loops
int outer;
int inner;
int result;

outer = 0;
while (outer < 3) {
    inner = 0;
    while (inner < 3) {
        result = outer * 10 + inner;
        print(result);
        inner = inner + 1;
    }
    outer = outer + 1;
}

// Test 2: Complex conditional nesting
int score;
score = 85;

if (score >= 90) {
    print(1);
} else {
    if (score >= 80) {
        print(2);
        if (score >= 85) {
            print(3);
        }
    } else {
        if (score >= 70) {
            print(4);
        } else {
            print(5);
        }
    }
}

// Test 3: Multiple operators in single expression
int val1;
int val2;
int val3;
int final;

val1 = 10;
val2 = 5;
val3 = 2;

final = val1 + val2 * val3 - val3;  // 10 + 10 - 2 = 18
print(final);

final = (val1 + val2) * (val3 - 1); // 15 * 1 = 15
print(final);

final = val1 / val2 + val3 * val3;  // 2 + 4 = 6
print(final);

// Test 4: All comparison operators
int num1;
int num2;

num1 = 10;
num2 = 10;

if (num1 == num2) {
    print(100);
}

if (num1 != num2) {
    print(200);
} else {
    print(201);
}

num2 = 5;

if (num1 > num2) {
    print(300);
}

if (num1 >= num2) {
    print(400);
}

if (num2 < num1) {
    print(500);
}

if (num2 <= num1) {
    print(600);
}

// Test 5: Loop with conditional break pattern
int countdown;
countdown = 10;

while (countdown > 0) {
    if (countdown == 5) {
        print(999);
    }
    print(countdown);
    countdown = countdown - 1;
}

// Test 6: Scope testing with same variable names
int temp;
temp = 100;
print(temp);

if (temp > 50) {
    int temp;
    temp = 50;
    print(temp);
    
    if (temp < 100) {
        int temp;
        temp = 25;
        print(temp);
    }
}

print(temp);

// Test 7: Multiple sequential blocks
int block;
block = 1;

if (block == 1) {
    int local;
    local = 10;
    print(local);
}

if (block == 1) {
    int local;
    local = 20;
    print(local);
}

if (block == 1) {
    int local;
    local = 30;
    print(local);
}

// Test 8: Float arithmetic
float pi;
float radius;
float circumference;
float area;

pi = 3.14159;
radius = 7.5;

circumference = 2.0 * pi * radius;
area = pi * radius * radius;

print(circumference);
print(area);

// Test 9: Mixed int and float operations
int intVal;
float floatVal;
float mixedResult;

intVal = 10;
floatVal = 3.5;
mixedResult = floatVal * intVal;  // Type conversion
print(mixedResult);

// Test 10: Modulo with different values
int dividend;
int divisor;
int remainder;

dividend = 17;
divisor = 5;
remainder = dividend % divisor;
print(remainder);

dividend = 100;
divisor = 7;
remainder = dividend % divisor;
print(remainder);

// Test 11: Expression precedence testing
int expr;
expr = 2 + 3 * 4;           // 14
print(expr);

expr = (2 + 3) * 4;         // 20
print(expr);

expr = 10 - 6 / 2;          // 7
print(expr);

expr = (10 - 6) / 2;        // 2
print(expr);

expr = 5 * 4 - 3 * 2;       // 14
print(expr);

// Test 12: Chained comparisons simulation
int check;
check = 15;

if (check > 10) {
    if (check < 20) {
        print(777);
    }
}

// Test 13: Loop counter patterns
int pattern;
pattern = 0;

while (pattern < 10) {
    if (pattern % 2 == 0) {
        print(pattern);
    }
    pattern = pattern + 1;
}

// Test 14: Negative number handling
int positive;
int negative;
int zero;

positive = 42;
negative = 0 - 42;
zero = 0;

print(positive);
print(negative);
print(zero);

// Test 15: Complex nested scope with calculations
int global;
global = 1000;

while (global > 0) {
    int level1;
    level1 = global / 10;
    
    if (level1 > 50) {
        int level2;
        level2 = level1 / 2;
        
        while (level2 > 10) {
            int level3;
            level3 = level2 - 5;
            print(level3);
            level2 = 0;
        }
    }
    
    global = 0;
}