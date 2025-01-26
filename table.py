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
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        name, score = self.path.split('/')[1:]

        self.wfile.write(bytes("POST request for {}".format(self.path), 'utf-8'))
        the_leaderboard.set_score(name, int(score))
        the_leaderboard.save_to_file("leaderboard.json")
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        sorted_scores = the_leaderboard.get_sorted_Scores(10, 'descending')
        if not sorted_scores:  # Exit if there are no scores
            self.wfile.write(bytes("<p>No scores to display.</p>", 'utf-8'))
            return

        min_score = sorted_scores[-1][1]
        max_score = sorted_scores[0][1]
        score_range = max_score - min_score if max_score != min_score else 1

        Output = ''
        for name, score in sorted_scores:
            ratio = (score - min_score) / score_range


            hue = int(120 * ratio)
            saturation = 100
            lightness = 50
            color = f"hsl({hue}, {saturation}%, {lightness}%)"

            Output += f'<tr style="background-color: {color}"> <td>{name}</td> <td>{score}</td> </tr>'

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



