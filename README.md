# djiVue

This template should help get you started developing with Vue 3 in Vite.

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur) + [TypeScript Vue Plugin (Volar)](https://marketplace.visualstudio.com/items?itemName=Vue.vscode-typescript-vue-plugin).

## Customize configuration

See [Vite Configuration Reference](https://vitejs.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```


### LiveStream Setup
```bash
docker run -p 8000:8000 -it mpromonet/webrtc-streamer -n rtsp_stream -u rtsp://aaa:aaa@{rc_ip}:8554/streaming/live/1
```
this rtsp ip should be written in /src/views/LiveStream.vue replaced by ?
```
const RTSP_URL = '？'
```

### WEBRTC_STREAMER_IP
http://localhost:8000 which was supplied by docker container.

### TELEMETRY
it is supported by python script, so we get it from http://localhost:8765

# What you SHOULD DO
##### 1. beautify all the .vue files in ```/src/views``` without change the main logic communicating with the server.
就是说，这个目录下的ｖｕｅ文件都可以被修改，但是你主要修改的部分应当在布局也就是ｔｅｍｐｌａｔｅ和ｃｓｓ样式部分，而不是其中的关于与后端交互的逻辑，

为了便于后期修改。首先介绍第一个界面，控制参数。这个界面的主要功能是调试无人机控制相关的各项参数，通过按钮点击事件发送信号。

第二个界面是直播界面，通过webrtc-streamer将无人机控制器端的rtsp直播流转化为mp4流，以便网页播放。

第三个界面是信息界面，通过与无人机遥控端构建websocket实现实时的信息接收。

第四个界面则是引申出来的控制模式，即用键盘来控制无人机移动，wsad用来控制移动，上下左右分别用来控制上升下降和转动。

其中还有utils中有部分函数可以利用
##### 2. 暂时没有