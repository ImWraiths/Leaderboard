import cgi
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse as urlparse  # For parsing POST data


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
            return []

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

        if self.path == '/':

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = urlparse.parse_qs(post_data)

            name = parsed_data.get("name", [""])[0]
            score = parsed_data.get("score", [""])[0]

            if name and score.isdigit():
                the_leaderboard.set_score(name, int(score))
                the_leaderboard.save_to_file("leaderboard.json")

        if self.path == '/table-fileupload':
            content_length = int(self.headers['Content-Length'])
            # post_body = self.rfile.read(content_length).decode('utf-8')
            header = cgi.parse_header(self.headers['Content-Type'])[1]
            header['boundary'] = header['boundary'].encode('utf-8')
            post_body = cgi.parse_multipart(self.rfile, header)
            print(post_body)
            # print(self.rfile.read())
            # post_data = self.rfile.read(content_length).decode('utf-8')

            scores = json.loads(post_body['filename'][0].decode('utf-8'))
            print(scores)

            for name, score in scores:
                the_leaderboard.set_score(name, score)

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def do_GET(self):
        if self.path == '/download-sorted-scores':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Content-Disposition',
                             'attachment; filename="sorted_scores.json"')
            self.end_headers()

            self.wfile.write(json.dumps(the_leaderboard.get_sorted_Scores(100, 'descending')).encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            html = """
            <html>
            <head><title>Leaderboard</title></head>
            <body>
                <h1>Submit Your Score</h1>
                <form method="POST" action="/">
                    <label for="name">Name:</label>
                    <input type="text" id="name" name="name" required><br><br>
                    <label for="score">Score:</label>
                    <input type="number" id="score" name="score" required><br><br>
                    <input type="submit" value="Submit">
                </form>

                <h2>Leaderboard</h2>
                <table border="1">
                    <tr><th>Name</th><th>Score</th></tr>
            """

            sorted_scores = the_leaderboard.get_sorted_Scores(100, 'descending')
            if sorted_scores:
                min_score = sorted_scores[-1][1]
                max_score = sorted_scores[0][1]
                score_range = max_score - min_score if max_score != min_score else 1

                for name, score in sorted_scores:
                    ratio = (score - min_score) / score_range
                    hue = int(120 * ratio)
                    color = f"hsl({hue}, 100%, 50%)"
                    html += f'<tr style="background-color: {color}"><td>{name}</td><td>{score}</td></tr>'
            else:
                html += "<tr><td colspan='2'>No scores yet.</td></tr>"

            html += """
                </table>
                <br>
                <a href="/download-sorted-scores"><button type="button">Download Leaderboard</button></a>
                <form action="/table-fileupload" method="post" enctype="multipart/form-data">
                    <input type="file" id="myFile" name="filename">
                    <input type="submit" value="Upload">
                </form>
            </body>
            </html>
            """

            self.wfile.write(html.encode("utf-8"))


http_server = HTTPServer(('', 8080), Handler)
http_server.serve_forever()
