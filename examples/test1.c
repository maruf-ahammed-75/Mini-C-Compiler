/* Test file for Mini C Compiler
   This file demonstrates various language features */

// Variable declarations and basic arithmetic
int x;
int y;
int sum;
int diff;
int product;

x = 15;
y = 5;

// Basic arithmetic operations
sum = x + y;        // 20
diff = x - y;       // 10
product = x * y;    // 75
print(sum);
print(diff);
print(product);

// Conditional statements
if (x > y) {
    int temp;
    temp = x - y;
    print(temp);
}

if (x == y) {
    print(0);
} else {
    print(1);
}

// Nested conditions
if (x > 10) {
    if (y < 10) {
        int result;
        result = x + y;
        print(result);
    }
}

// While loop
int counter;
counter = 0;
while (counter < 5) {
    print(counter);
    counter = counter + 1;
}

// Loop with scope
int i;
i = 0;
while (i < 3) {
    int squared;
    squared = i * i;
    print(squared);
    i = i + 1;
}

// Complex expressions
int a;
int b;
int c;
a = 10;
b = 20;
c = a + b * 2;      // 50
print(c);
c = (a + b) * 2;    // 60
print(c);

// Comparison operators
if (a < b) {
    print(1);
}

if (a <= b) {
    print(2);
}

if (a != b) {
    print(3);
}

if (a >= 5) {
    print(4);
}

// Floating point operations
float pi;
float radius;
float area;

pi = 3.14;
radius = 5.0;
area = pi * radius * radius;
print(area);

// Modulo operation
int num;
int mod;
num = 17;
mod = num % 5;      // 2
print(mod);

// Multiple scopes
int outer;
outer = 100;

if (outer > 50) {
    int inner;
    inner = outer / 2;
    print(inner);
    
    while (inner > 0) {
        int nested;
        nested = inner - 10;
        print(nested);
        inner = 0;
    }
}

print(outer);