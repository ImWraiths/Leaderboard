



table = {}


while True:

    user_input = input("Enter a name and a score or write exit to stop: ")

    if user_input.lower() == 'exit':
        break



    name, number = user_input.split()

    table[name] = int(number)



sorted_table = dict(sorted(table.items(), key=lambda item: item[1], reverse=True))



print(sorted_table)
