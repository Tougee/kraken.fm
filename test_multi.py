from threading import Thread
import urllib.parse
import http.server
import socketserver
import re
from pathlib import Path
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from random import randint
import uuid
import time

count = 16
exit_max = 2
room_name = "test"

chrome_options = Options()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
browser = Chrome(chrome_options = chrome_options)

pattern = re.compile('.png|.jpg|.jpeg|.js|.css|.ico|.gif|.svg', re.IGNORECASE)

def run_server(port):
    Thread(target=server_on_port, args=(port,)).start()

def server_on_port(port):
    httpd = ThreadingHTTPServer(('0.0.0.0', port), Handler)
    httpd.serve_forever()

class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        url_parts = urllib.parse.urlparse(self.path)
        request_file_path = Path(url_parts.path.strip("/"))

        ext = request_file_path.suffix
        if not request_file_path.is_file() and not pattern.match(ext):
            self.path = 'index.html'

        return http.server.SimpleHTTPRequestHandler.do_GET(self)


def main():
    for i in range(count):
        print("Starting server... {}".format(8000 + i))
        run_server(8000 + i)

    for i in range(count):
        port = 8000 + i
        print("Opening browser... {}".format(port))
        if i > 0:
            browser.switch_to.new_window()
        browser.get("http://localhost:{}?room={}".format(port, room_name))
        uid = uuid.uuid4()
        browser.execute_script('return localStorage.setItem("uid", "{}");'.format(uid))
        browser.execute_script('return localStorage.setItem("{}:{}", "user-{}");'.format(room_name, uid, i))
        browser.refresh()

    last_index_list = []
    while True:
        if (len(last_index_list) != 0):
            for i in range(len(last_index_list)):
                index = last_index_list[i]
                browser.switch_to.window(browser.window_handles[index])
                browser.get("http://localhost:{}?room={}".format(8000 + index, room_name))
                print("{} joined".format(8000 + index))

        last_index_list.clear() 

        time.sleep(5)

        for i in range(count):
            browser.switch_to.window(browser.window_handles[i])
            try:
                list = browser.execute_script('return list')
                inbound = browser.execute_script('return inbound')
                state = browser.execute_script('return state')
                print("{} list: {}, inbound: {}, state: {}".format(i, list, inbound, state))
            except:
                pass
        print("===========================")

        ignoreExit = randint(0, 10) < 9
        if ignoreExit:
            continue

        exit_count = randint(0, exit_max)
        for i in range(exit_count):
            index = randint(0, count - 1)
            if index in last_index_list:
                continue

            last_index_list.append(index)

            browser.switch_to.window(browser.window_handles[index])
            browser.get("about:blank")

            print("{} exit".format(8000 + index))


        time.sleep(5)


if __name__ == '__main__':
    main()