<template>
  <div class="qr-wrapper">
    <button class="scan-btn" @click="startScanner">
      📷
    </button>

    <transition name="fade">
      <div v-if="isScanning" class="scanner-overlay">
        <div class="scanner-modal">
          <div class="scanner-header">
            <div class="scanner-title">Quét mã QR</div>
            <button class="scanner-close" @click="stopScanner">✕</button>
          </div>

          <div class="scanner-body">
            <div class="video-wrapper">
              <video
                ref="videoRef"
                class="scanner-video"
                autoplay
                muted
                playsinline
              ></video>
            </div>

            <div class="scanner-status">
              {{ status }}
            </div>

            <div v-if="errorMsg" class="scanner-error">
              {{ errorMsg }}
            </div>
          </div>

          <div class="scanner-footer">
            <button class="btn-secondary" @click="stopScanner">
              Tắt camera
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, nextTick, onBeforeUnmount } from 'vue'
import jsQR from 'jsqr'

const emit = defineEmits(['update:text','scanned'])

const isScanning = ref(false)
const videoRef = ref(null)

const status = ref('')
const errorMsg = ref('')

let stream = null
let canvas = null
let ctx = null
let scanHandle = null

const VIDEO_CONSTRAINTS = {
  video: {
    facingMode: 'environment'
  }
}

async function startScanner() {
  if (isScanning.value) return

  errorMsg.value = ''
  status.value = 'Đang mở camera...'
  isScanning.value = true
  await nextTick()

  try {
    stream = await navigator.mediaDevices.getUserMedia(VIDEO_CONSTRAINTS)
    const video = videoRef.value
    if (!video) throw new Error('Không tìm thấy video')

    video.srcObject = stream
    await video.play()

    canvas = document.createElement('canvas')
    ctx = canvas.getContext('2d')

    status.value = 'Đưa mã QR vào khung hình...'
    scanFrame()
  } catch (err) {
    errorMsg.value = err.message || 'Không mở được camera'
    stopScanner()
  }
}

function scanFrame() {
  if (!videoRef.value || !ctx) return

  const video = videoRef.value
  const width = video.videoWidth
  const height = video.videoHeight

  if (!width || !height) {
    scanHandle = requestAnimationFrame(scanFrame)
    return
  }

  canvas.width = width
  canvas.height = height

  ctx.drawImage(video, 0, 0, width, height)
  const imageData = ctx.getImageData(0, 0, width, height)

  const result = jsQR(imageData.data, width, height)

  if (result?.data) {
    emit('update:text', result.data)
    emit('scanned')
    stopScanner()
    return
  }

  scanHandle = requestAnimationFrame(scanFrame)
}

function stopScanner() {
  if (scanHandle) {
    cancelAnimationFrame(scanHandle)
    scanHandle = null
  }

  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }

  isScanning.value = false
}

onBeforeUnmount(() => {
  stopScanner()
})
</script>

<style scoped>
.scan-btn {
  padding: 10px 18px;
  background: #86c06b;
  color: #14532d;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
}

.scan-btn:hover {
  background: #6fb457;
}

/* Overlay */
.scanner-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

/* Modal */
.scanner-modal {
  width: 340px;
  max-width: 90%;
  background: white;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.3);
}

.scanner-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.scanner-title {
  font-weight: 600;
  color: #14532d;
}

.scanner-close {
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  cursor: pointer;
}

.video-wrapper {
  position: relative;
}

.scanner-video {
  width: 100%;
  border-radius: 12px;
}

.scanner-status {
  margin-top: 10px;
  font-size: 14px;
  color: #4b5563;
}

.scanner-error {
  margin-top: 8px;
  color: #dc2626;
  font-size: 13px;
}

.btn-secondary {
  margin-top: 12px;
  width: 100%;
  padding: 8px;
  background: #4b5563;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}
</style>