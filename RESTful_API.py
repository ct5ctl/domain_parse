import flask
from flask_restful import Api, Resource

import Dynamicity
import Resolvability
import Urls
import Usability
from Config import time_ping_max

import os
import sys


path = os.path.dirname(sys.path[0])
print(path)
if path and path not in sys.path:
    sys.path.append(path)

app = flask.Flask(__name__)
api = Api(app)  # application的主要入口


# REST类：可解析性判断
class cls_Resolvability(Resource):  # rest的api的类必须继承Resource类！！
    def post(self):
        # 以json格式提交域名，返回值(json)：域名，ip，可解析性
        request_json = flask.request.get_json(force=True)
        resolvability, ip = Resolvability.api_judge_resolvability(request_json["Domain"])
        return flask.jsonify(Domain=request_json["Domain"], Resolvability=resolvability, IP=ip)


# REST类：可用性判断
class cls_Usability(Resource):
    def post(self):
        # 以json格式提交域名，返回值(json)：域名，固定ip集，动态性，周期性，周期
        request_json = flask.request.get_json(force=True)
        back_json = Usability.api_judge_usability(request_json["Domain"], time_max=time_ping_max)
        return flask.jsonify(Domain=back_json["Domain"], IP=back_json["IP set"][0],
                             Parsability=back_json["Parsability"], Usability=back_json["Usability"])


# REST类：动态性判断
class cls_Dynamicity(Resource):
    def post(self):
        # 以json格式提交域名，解析动态性后将结构保存到本地json文件中，返回值(json)：域名，固定ip集，动态性，周期性，周期
        request_json = flask.request.get_json(force=True)
        back_json = Dynamicity.api_judge_dynamicity(request_json["Domain"])
        return back_json

    def get(self):
        # 对url文件中所有域名进行解析
        back_json = Dynamicity.api_judge_dynamicity_all()
        return back_json


# REST类：获得所有待解析的url
class cls_url(Resource):
    def get(self):
        back_json = Urls.get_all_urls()
        return back_json

    def post(self):
        # 以json格式提交域名，返回值:成功/失败
        request_json = flask.request.get_json(force=True)
        back_json = Urls.add_url(request_json["Domain"])
        return back_json

    def delete(self):
        # 以json格式提交要删除的域名，返回值:成功/失败
        request_json = flask.request.get_json(force=True)
        back_json = Urls.del_url(request_json["Domain"])
        return back_json


# REST类：获得所有域名的所有信息
class cls_info(Resource):
    def get(self):
        back_json = Urls.get_all_info()
        return back_json

    def delete(self):
        # json格式传入若干个域名，将本地文件中对应的解析结果删除
        request_json = flask.request.get_json(force=True)
        back_json = Urls.delete_info(request_json)
        return back_json


# 给RESTful_API添加资源和设置路由
api.add_resource(cls_Resolvability, "/api/resolvavility")  # [可解析性]解析
api.add_resource(cls_Usability, "/api/usability")  # [可用性]解析
api.add_resource(cls_Dynamicity, "/api/dynamicity")  # [动态性]、[周期性]解析
api.add_resource(cls_url, "/api/url")  # 对本地url增删查
api.add_resource(cls_info, "/api/all_info")  # 对解析结果的删查

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9000)
