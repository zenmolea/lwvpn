
**构建程序**
```shell
cmake .
make
```
**引用lwvpn包**
```python
import lwvpn
```
调用run函数
```python
lwvpn.run(args)
```
args为字符串数组，第一个变量为空，“”
```python
args=["","client", "vpn.key", "170.106.178.152", "1959"]
```
示例可见 (test.py)
