// 单向 WebRTC 接收端（Browser）
// 无人机 = offer 方
// 浏览器 = answer 方

export class WebRTCReceiver {
  constructor(videoEl, signalUrl) {
    this.videoEl = videoEl
    this.signalUrl = signalUrl
    this.pc = null
    this.ws = null
  }

  start() {
    this._initSignal()
  }

  stop() {
    if (this.pc) {
      this.pc.close()
      this.pc = null
    }
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  _initPeer() {
    this.pc = new RTCPeerConnection({
      iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
    })

    // 接收无人机视频
    this.pc.ontrack = (e) => {
      console.log('[WebRTC] 收到视频流')
      this.videoEl.srcObject = e.streams[0]
    }

    this.pc.onicecandidate = (e) => {
      if (e.candidate) {
        this._send({
          type: 'candidate',
          candidate: e.candidate
        })
      }
    }
  }

  _initSignal() {
    this.ws = new WebSocket(this.signalUrl)

    this.ws.onopen = () => {
      console.log('[WebRTC] 信令连接成功')
    }

    this.ws.onmessage = async (evt) => {
      const msg = JSON.parse(evt.data)

      switch (msg.type) {
        case 'offer':
          await this._handleOffer(msg.sdp)
          break

        case 'candidate':
          this.pc && this.pc.addIceCandidate(msg.candidate)
          break
      }
    }
  }

  async _handleOffer(sdp) {
    if (!this.pc) this._initPeer()

    await this.pc.setRemoteDescription({
      type: 'offer',
      sdp
    })

    const answer = await this.pc.createAnswer()
    await this.pc.setLocalDescription(answer)

    this._send({
      type: 'answer',
      sdp: answer.sdp
    })
  }

  _send(msg) {
    this.ws && this.ws.send(JSON.stringify(msg))
  }
}
