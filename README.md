# face-uart
2020年10月11日 16点55分
```
//所有命令返回 
<[cmd]:ok
//或者
<[cmd]:data
```

## 基础命令
### 1 snapshot
快照并保存到指定路径 文件默认后缀名.pgm
```
>snapshot:[path]

example:
>snapshot:/photo/[userNumber]/[sn]
```

### 2 lbp
指定文件夹生成lbp数据 并保存到指定路径
```
>lbp:[srcpath]->[distpath]

example:
>lbp:/photo/xxx->/lbp/xxx
```

### 3 ls
获取指定目录下的文件和文件夹
```
>ls:[path]

example:
>ls:/photo/xxx
```
### 4 rm
删除指定文件或文件夹
```
>rm:[path]

example:
>rm:/lbp
```

### 5 check 
进入人脸检测状态 指定时间间隔 阈值  
返回匹配到的用户编码 或者空
```
//开始
>check:[interval] [threshold]
>break
``` 

### 5 checkinfo
进入人脸检测状态返回详细详细 指定时间间隔 阈值   
返回匹配到的用户编码 以及各个模型匹配的详细结果
```
>checkinfo:[interval] [threshold]
>break
``` 


## 应用命令
### 1 shutter
给指定用户拍照
```
>shutter:[userNumber]
``` 

### 2 generate
生成指定用户特征值
```
>generate:[userNumber]
```

### 3 users
获取生成特征值的用户列表
```
>users
```

### 4 remove
移除用户特征值和图片
```
>remove:[userNumber]
```

### 5 clearall
移除所有用户特征值和图片
```
>clearall
```

## 流程示例

```

>shutter:111
>generate:111
>shutter:a22
>generate:a22
>users
>check:300 5

//...

>break

```



## data log

| THRESHOLD | FILTER_OUTLIERS | result | f1 | f1 |
| :-- | :-- | :-- | :-- | :-- |
| 95 | False |  |  |  |
| 5  | False |  |  |  |
| 95 | True  |  |  |  |
| 5  | True  |  |  |  |

### idea
1. 采集 跳过前3张
2. 用平均最小值判断
