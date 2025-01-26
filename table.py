from http.server import HTTPServer, BaseHTTPRequestHandler
import json


class Leaderboard:
    """ hello """
    score_table = {}

    def set_score(self, name, score):
        self.score_table[name] = score


    def get_sorted_Scores(self, count, sort_order='descending'):

        if sort_order == 'ascending':
            sorted_table = dict(sorted(self.score_table.items(), key=lambda item: item[1]))
        elif sort_order == 'descending':
            sorted_table = dict(sorted(self.score_table.items(), key=lambda item: item[1], reverse=True))
        else:
            print("Invalid sort order. Use 'ascending' or 'descending'.")
            return

        return list(sorted_table.items())[:count]

    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.score_table, file)

    def load_from_file(self, filename):

        try:
            with open(filename, 'r') as file:
                self.score_table = json.load(file)
        except FileNotFoundError:
            self.score_table = {}


the_leaderboard = Leaderboard()
the_leaderboard.load_from_file("leaderboard.json")


class Handler(BaseHTTPRequestHandler):
    def do_POST (self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        name, score = self.path.split('/')[1:]

        self.wfile.write(bytes("POST request for {}".format(self.path)  , 'utf-8'))
        the_leaderboard.set_score(name, int(score))
        the_leaderboard.save_to_file("leaderboard.json")
    def do_GET(self):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            Output = ''
            for score in the_leaderboard.get_sorted_Scores(10, 'descending'):
                Output += f"<tr> <td> {score[0]} </td> <td> {score[1]} </td> </tr>"
            self.wfile.write(bytes(f"<table> {Output} </table>", 'utf-8'))



http_server = HTTPServer(('', 8080), Handler)
http_server.serve_forever()


while True:
    user_input = input("Enter a command ('add', 'show', or 'exit'): ").lower()

    if user_input == 'exit':
        break
    elif user_input == 'add':
        try:
            name = input("Enter a name: ")
            score = int(input("Enter a score: "))
            the_leaderboard.set_score(name, score)
        except ValueError:
            print("Please enter a valid number.")
    elif user_input == 'show':
        try:
            amount = int(input("How many pairs do you want to display? "))
            sort_order = input("Enter sort order ('ascending' or 'descending'): ").lower()

            print(the_leaderboard.get_sorted_Scores(amount, sort_order))
        except ValueError:
            print("Please enter a valid number for the amount.")
    else:
        print("Invalid command. Please use 'add', 'show', or 'exit'.")



