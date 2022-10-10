def sum(a, b):
    if getattr(sum, 'has_run', False):
        print('no')
        return
    sum.has_run = True

    return a + b

sum(1,2)
sum(2,2)
sum(2,2)
