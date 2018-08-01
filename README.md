# Tiny Http Server

## 简介

基于 socket 实现的静态 http 服务器

## 使用

异步方式：

```bash
$ python -m tinyhttp.async # or python -m tinyhttp
```

多线程方式：

```bash
$ python -m tinyhttp.thread
```

默认会开启 6789 端口，可指定端口：

```bash
$ python -m tinyhttp 6666
```