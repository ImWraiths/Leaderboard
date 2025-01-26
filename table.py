import cgi
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse as urlparse
from datetime import datetime


class Leaderboard:
    """hello"""
    score_table = {}

    def set_score(self, name, score, timestamp=None, ):
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.score_table[name] = {'score': score, 'timestamp': current_time}

    def get_sorted_Scores(self, count, sort_order='descending'):
        if sort_order in ['ascending', 'descending']:
            reverse_order = sort_order == 'descending'
            sorted_table = sorted(
                self.score_table.items(),
                key=lambda item: item[1]['score'],
                reverse=reverse_order
            )

            return [(name, data['score'], data['timestamp']) for name, data in sorted_table[:count]]
        else:
            print("Invalid sort order. Use 'ascending' or 'descending'.")
            return []

    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.score_table, file)

    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as file:
                self.score_table = json.load(file)
        except FileNotFoundError:
            self.score_table = {}

    def clear_leaderboard(self, filename):
        self.score_table = {}
        self.save_to_file(filename)


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

        if self.path == '/reset-leaderboard':
            the_leaderboard.clear_leaderboard("leaderboard.json")
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()

        if self.path == '/table-fileupload':
            try:
                content_length = int(self.headers['Content-Length'])
                header = cgi.parse_header(self.headers['Content-Type'])[1]
                header['boundary'] = header['boundary'].encode('utf-8')
                post_body = cgi.parse_multipart(self.rfile, header)

                scores = json.loads(post_body['filename'][0].decode('utf-8'))

                for score_entry in scores:
                    name = score_entry[0]
                    score = score_entry[1]
                    if len(score_entry) > 2:
                        timestamp = score_entry[2]
                    else:
                        timestamp = None
                    the_leaderboard.set_score(name, score, timestamp)

                the_leaderboard.save_to_file("leaderboard.json")
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()
            except:
                pass

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
            <!-- Latest compiled and minified CSS -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css" integrity="sha384-HSMxcRTRxnN+Bdg0JdbxYKrThecOKuH5zCYotlSAcp1+c8xmyTe9GYg1l9a69psu" crossorigin="anonymous">

<!-- Optional theme -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap-theme.min.css" integrity="sha384-6pzBo3FDv/PJ8r2KRkGHifhEocL+1X2rVCTTkUfGk7/0pbek5mMa1upzvWbrUbOZ" crossorigin="anonymous">

<!-- Latest compiled and minified JavaScript -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/js/bootstrap.min.js" integrity="sha384-aJ21OjlMXNL5UyIl/XNwTMqvzeRMZH2w8c5cRVpzpU8Y5bApTppSuUkhZXN0VxHd" crossorigin="anonymous"></script>
<style>
tr th{margin-bottom:1em;}
tr{padding-left: 1em; background-color: #f2f2f2; vertical-align: middle;}
</style>
            <head><title>Leaderboard</title></head>
            <body style="margin:2em">
                <h1>Submit Your Score</h1>
                <form method="POST" action="/">
                    <label for="name">Name:</label>
                    <input type="text" id="name" name="name" required><br><br>
                    <label for="score">Score:</label>
                    <input type="number" id="score" name="score" required><br><br>
                    <input type="submit" value="Submit">
                </form>
                <form method="POST" action="/reset-leaderboard" style="margin-top: 1em;"><button type="submit" class="btn btn-danger">Clear Leaderboard</button>
</form>

                <h2>Leaderboard</h2>

                <table border="0">
                    <tr style="margin-bottom:1ex;"><th >Name</th><th style="padding-right:1ex;">Score</th><th style="padding-right:1ex;">Last Edited</th><th style="padding-left:2em;width:10em">bar</th></tr>
            """

            sorted_scores = the_leaderboard.get_sorted_Scores(100, 'descending')
            if sorted_scores:
                min_score = sorted_scores[-1][1]
                max_score = sorted_scores[0][1]
                score_range = max_score - min_score if max_score != min_score else 1

                for name, score, timestamp in sorted_scores:
                    ratio = (score - min_score) / score_range
                    hue = int(120 * ratio)
                    color = f"hsl({hue}, 100%, 80%)"

                    html += f'<tr style=""><td>{name}</td><td>{score}</td><td>{timestamp}</td><td style="">      <div class="progress">        <div class="progress-bar" role="progressbar" aria-valuenow="{score}" aria-valuemin="0" aria-valuemax="{max_score}" style="background-color: {color}; width: {score * 100 / max_score}%;"><span class="sr-only">60% Complete</span></div>      </div></td></tr>'
            else:
                html += "<tr><td colspan='3'>No scores yet.</td></tr>"

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
