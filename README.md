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