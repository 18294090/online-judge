h = 0
m = float(input())
n = int(input())
for i in range(1, n+1):
    if i == 1:
        h += m
    else:
        h += m*2
    m /= 2
print(h)
