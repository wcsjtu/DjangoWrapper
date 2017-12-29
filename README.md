# 使用说明

## 基本功能

&nbsp;&nbsp;&nbsp;&nbsp;对Django框架(version 1.10.1)进行了一次包装, 增加了一些功能、约定以及能让业务写起来更加爽的wrapper。 下面详细讲这些功能的使用方法。

## 约定

- 所有view的uri必须以特定的包含特定的前缀如`/api/users/info`、 `/api/users/my/detail`, 以便nginx能分开代理. 

- 所有view的uri第二层必须是该view所在的app的名字, 比如说, `/api/users/info`、 `/api/users/my/detail`对应的view都位于`users` app中, 但是`/api/flow/def` 则位于`flow` app中

- app间严格独立, 不能存在import关系。 各项目数据库也严格独立, 必须单独使用一个database

这些约定是我写死在wrapper内部的, 用户在写uri时, 不用去管什么app名啊, 前缀名啊。 平时怎写就怎么写。

## 使用

### router

山寨flask的写法, 自己造了个`router`修饰器, 用法与flask的`route`一致. 比如说下面的代码。比flask那个更强大的是, 它可以修饰类。

```python
from common import router
@router(r"^/login$", loginRequired=True)    #请注意, uri中是没有api, app的
def login(request):
    blabla

from common import http
@router(r"/index$", permRequired="sudo")
class Index(http.ViewBase):
    def get(self, request):
        pass
    def post(self, request):
        pass
```

有几个常用参数。其他参数可以考router函数的定义。

```python
loginRequired: bool #被修饰的view是否需要登录
permRequired: str   #被修饰的view是否需要某种权限。用户的权限表存在session中, 
                    #key在settings.py文件中可以配置。
```

### loginRequired/permRequired

两个修饰器, 让你从繁琐的登录判断、权限控制中解脱出来。 这两个修饰器, 只能修饰函数或者方法, 不能修饰类。 这几个修饰器都可以叠加使用啊, 比如说

```python
from common import http, router,\
    loginRequired, permRequired

@router(r"^/login")
@router(r"^/myss/login")
def login(request):
    pass

@router(r"/index$")
class Index(http.ViewBase):
    @loginRequired
    def get(self, request):
        pass

    @permRequired("sudo")
    def post(self, request):
        pass

```

这个特性可以用于`REST`设计中, 控制某类`method`的权限问题。

## HTTP接口

这里使用`json`协议, 我们约定的接口一般格式是。所有的接口, 除了发生HTTP异常的, 都会按这种格式返回数据。

```json
{"err_code": integer, "data": blabla}
```

为了让业务写起来更爽, 有几点设计.

### 错误码文件

有一个专门的文件, 用来放错误码的定义, 文件为json格式, 内容为两大块

- 错误码
- 错误码提示

比如说

```json
[
    {
        "OK": 0,
        "NO_LOGIN": -1000
    },
    {
        "0": "操作成功",
        "-1000": "用户尚未登录"
    }
]
```

服务在启动时, 会自动把文件内容, 加载到`common.err_code`模块中, 比如说`common.err_code.OK`就等于0。 前端在打包时, 也会把该错误码打包进去, 这样前后端只需要传输错误码, 而不用传输提示了, 隐蔽性更好。

### ErrorResp

光有错误码还不够爽, 为了更爽的使用, 在`common.http`模块中, 定义了一个`ErrorResp`异常类, 你可以在任何地方抛出这个异常, 只要它不被未知的`except Exception:`捕获到就行了

```python
class ErrorResp(Exception):

    TIPS = _load_errno()

    def __init__(self, err_no, tips=None):
        self.errno = err_no
        if not tips:
            tips = self.TIPS.get(err_no,
                             "unknown error with code %d" % err_no)
        super(ErrorResp, self).__init__(tips)

    def __iter__(self):
        return iter([("err_code", self.errno), ("data", None)])
```

这个异常, 会被我写的一个中间件捕获到, 把它格式化成我们约定的`json`格式, 然后丢弃掉。 这个玩意相当有用, 可以让你从恶心的层层返回值中恶心出来. 这得益于python的异常处理机制——异常会沿着堆栈冒泡, 直到有人接收它。 

## settings.py

### Django原生配置项

&nbsp;&nbsp;&nbsp;&nbsp; 这部分不讲, 有兴趣看Django官方文档

### 我定义的配置项


#### host函数

&nbsp;&nbsp;&nbsp;&nbsp;这个函数返回当前web服务的host信息, 比如说`http://localhost:8080`, 可以根据环境变量, 来实现开发/部署共用代码, 比如说

```python
import platform
    if platform.system() == "Windows":
        return "http://localhost"
    if os.environ.get("USER", "unkown") == "online":
        return "http://192.168.1.100"
    else:
        return "http://localhost"
```

#### LOGIN_KEY

&nbsp;&nbsp;&nbsp;&nbsp;用于判断用户是否登录的key, 可以是任意值

#### ENABLE_WEBSOCKET

&nbsp;&nbsp;&nbsp;&nbsp;是否开启内置的websocket功能, 注意, **如果开启该功能, 则需要额外安装`ws4redis`和`redis`两个库**。 建议websocket服务用tornado替代

#### ENABLE_CELERY

&nbsp;&nbsp;&nbsp;&nbsp;是否开启celery功能. 注意, **如果开启该功能, 则需要额外安装`celery`和`dill`, `django_celery_beat`三个库**。 celery会提供吊炸天的异步、定时功能, 按需使用。

#### WEBSOCKET_URL

&nbsp;&nbsp;&nbsp;&nbsp;标识websocket服务的url前缀, 比如说`/ws/`, 则所有以`/ws/`开头的url, 都会转到websocket服务.

#### BACKEND_URL_PREFIX

&nbsp;&nbsp;&nbsp;&nbsp;由于前后端分离, 现在后台只是一个api服务器, 为了让nginx能够分开代理前后端的服务, 需要一个前缀标识来区分。 比如说`api`, 则所有以`/api`开头的请求, 都会被nginx转发至Django进程。

#### BROKER_URL

&nbsp;&nbsp;&nbsp;&nbsp;celery broker的配置, 用于放置celery的任务队列, 我用的是redis, 则这里配置应该是`'redis://localhost:6379/1'`

#### CELERY_RESULT_BACKEND

&nbsp;&nbsp;&nbsp;&nbsp;用于放置celery的结果队列, 我用的是redis, 则这里配置应该是`'redis://localhost:6379/1'`

#### CELERY_ACCEPT_CONTENT

&nbsp;&nbsp;&nbsp;&nbsp;celery能够处理的序列化对象, 默认是`'application/json'`, 为了让celery能够处理序列化之后的函数, 增加了`dill`类型, 则这里的配置应该是`['application/json', 'dill']`

#### CELERY_TASK_SERIALIZER

&nbsp;&nbsp;&nbsp;&nbsp;celery的序列化方式, 默认是`json'`, 为了让celery能够序列化函数, 增加了`dill`类型, 则这里的配置应该是`'dill'`

#### CELERY_RESULT_SERIALIZER

&nbsp;&nbsp;&nbsp;&nbsp;同上

#### CELERY_TASK

&nbsp;&nbsp;&nbsp;&nbsp;我写的wrapper内部使用的变量, 用户无需知道用途, 但是不能删, 删了必定报错

#### ROUTER_FILES

&nbsp;&nbsp;&nbsp;&nbsp;我写的wrapper内部使用的变量, 用户无需知道用途, 但是不能删, 删了必定报错

#### ERRNO_FILE

&nbsp;&nbsp;&nbsp;&nbsp;错误码所在的文件的路径, 比如说`"./common/errno.json"`

#### PERM_TABLE_NAME

&nbsp;&nbsp;&nbsp;&nbsp;session中, 存储用户权限的key, 这个与permRequired修饰器有关. 你可以无视掉这个参数, 如果你要自己重新实现这个修饰器的话

