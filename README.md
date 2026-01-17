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

为了便于后期修改。首先介绍第一个界面，**控制参数**。这个界面的主要功能是调试无人机控制相关的各项参数，通过按钮点击事件发送信号。

第二个界面是**直播界面**，通过webrtc-streamer将无人机控制器端的rtsp直播流转化为mp4流，以便网页播放。

第三个界面是**信息界面**，通过与无人机遥控端构建websocket实现实时的信息接收。

第四个界面则是引申出来的**控制模式**，即用键盘来控制无人机移动，wsad用来控制移动，上下左右分别用来控制上升下降和转动。

其中还有utils中的request.js提供的方法可以利用，写出新的views功能，
## 关于无人机通信的各接口调用如下（仅作参考使用，我已实现，你可以在这个基础上优化一下代码风格）。

***Telemetry Fields（我已经将其转化为WEBSOCKET，具体的转换在src下的WebSocketServer.py文件中写完了。如果需要利用连续信息流，请查看info.vue）:***
| Field | Description |
|-------|-------------|
| `speed` | Aircraft velocity (x, y, z) |
| `heading` | Compass heading in degrees |
| `attitude` | Pitch, roll, yaw values |
| `location` | GPS coordinates and altitude |
| `gimbalAttitude` | Gimbal orientation |
| `batteryLevel` | Battery percentage |
| `satelliteCount` | GPS satellite count |
| `homeLocation` | Home point coordinates |
| `distanceToHome` | Distance to home in meters |
| `waypointReached` | Waypoint status flag |
| `isRecording` | Camera recording status |
| `flightMode` | Current flight mode (GPS, MANUAL, GO_HOME, etc.) |
| `remainingFlightTime` | Estimated flight time remaining |
| `batteryNeededToGoHome` | Battery % needed for RTH |
| `batteryNeededToLand` | Battery % needed to land |
| `timeNeededToGoHome` | Time to return home (seconds) |
| `maxRadiusCanFlyAndGoHome` | Max flyable radius (meters) |

### Control Endpoints (HTTP POST - Port 8080)

| Endpoint | Description | Parameters |
|----------|-------------|------------|
| `/send/takeoff` | Initiate takeoff | None |
| `/send/land` | Initiate landing | None |
| `/send/RTH` | Return to home | None |
| `/send/gotoWP` | Navigate to waypoint | `lat,lon,alt` |
| `/send/gotoWPwithPID` | Navigate with PID control | `lat,lon,alt,yaw` |
| `/send/gotoYaw` | Rotate to heading | `yaw_angle` |
| `/send/gotoAltitude` | Change altitude | `altitude` |
| `/send/navigateTrajectory` | Follow trajectory (Virtual Stick) | `lat,lon,alt;...;lat,lon,alt,yaw` |
| `/send/navigateTrajectoryDJINative` | DJI native waypoint mission | `lat,lon,alt;lat,lon,alt;...` |
| `/send/abort/DJIMission` | Stop DJI native mission | None |
| `/send/abortMission` | Stop and disable Virtual Stick | None |
| `/send/enableVirtualStick` | Enable Virtual Stick mode | None |
| `/send/stick` | Virtual stick input | `leftX,leftY,rightX,rightY` |
| `/send/camera/zoom` | Camera zoom control | `zoom_ratio` |
| `/send/camera/startRecording` | Start video recording | None |
| `/send/camera/stopRecording` | Stop video recording | None |
| `/send/gimbal/pitch` | Gimbal pitch control | `roll,pitch,yaw` |
| `/send/gimbal/yaw` | Gimbal yaw control | `roll,pitch,yaw` |

### Status Endpoints (HTTP GET - Port 8080)

| Endpoint | Description |
|----------|-------------|
| `/status/waypointReached` | Check if waypoint reached |
| `/status/intermediaryWaypointReached` | Check intermediary waypoint |
| `/status/yawReached` | Check if target yaw reached |
| `/status/altitudeReached` | Check if target altitude reached |
| `/status/camera/isRecording` | Check recording status |

### Legacy Telemetry Endpoints (HTTP GET - Port 8080)

These endpoints are available for backward compatibility. For continuous telemetry, use the TCP socket on port 8081.

| Endpoint | Description |
|----------|-------------|
| `/` | Connection test |
| `/aircraft/allStates` | Complete telemetry package (JSON) |
| `/aircraft/speed` | Aircraft velocity |
| `/aircraft/heading` | Compass heading |
| `/aircraft/attitude` | Pitch, roll, yaw |
| `/aircraft/location` | GPS coordinates and altitude |
| `/aircraft/gimbalAttitude` | Gimbal orientation |
| `/home/location` | Home point coordinates |


##### 2. 中英文过渡切换按钮实现。要实现可以将页面全部切换成英文和中文。