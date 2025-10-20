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