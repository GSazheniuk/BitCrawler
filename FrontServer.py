import tornado.escape
import tornado.web
import tornado.ioloop
import os
import json
import SharedData
import Waiters

from tornado import gen


class RootHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        self.render("default.html", messages=[])
        pass


class GetAllIdsHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self, *args, **kwargs):
        self.write(json.dumps(SharedData.get_address_list()))
        pass


class GetDistribDataHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self, *args, **kwargs):
        # TO-DO
        self.write(json.dumps(SharedData.get_address_list()))
        pass


class GetQueueHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        res = {"queue": []}
        self.write(res)
        self.flush()

        while not self.request.connection.stream.closed():
            future = Waiters.all_waiters.subscribe_waiter(Waiters.WAIT_FOR_QUEUE)
            res = yield future

            self.write({"queue": res})
            self.flush()
            pass

        self.finish()
        pass


class FrontWatchServer:
    def __init__(self):
        self.app = tornado.web.Application(
            [
                (r"/", RootHandler),
                (r"/default.html", RootHandler),
                (r"/queue", GetQueueHandler),
                (r"/getIds", GetAllIdsHandler),
                (r"/getDistributionData", GetDistribDataHandler),
            ],
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "static"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
            debug=True,
        )
        pass

    def run(self):
        self.app.listen(9999)
        tornado.ioloop.IOLoop.current().start()
        pass
