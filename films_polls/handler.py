def chunks(lst, count):
    for i in range(0,len(lst),3):
        yield lst[i:i+3]