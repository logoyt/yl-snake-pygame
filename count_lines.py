files = [
    'config',
    'entities',
    'main',
    'utility'
]

total = 0
for file in files:
    count = 0
    with open(f'{file}.py') as f:
        for line in f:
            if line.strip():
                if not line.strip().startswith('#'):
                    count += 1
    print(file, count)
    total += count
print(f'{total=}')

'''
config 6
entities 155
main 85
utility 86
total=332
'''
