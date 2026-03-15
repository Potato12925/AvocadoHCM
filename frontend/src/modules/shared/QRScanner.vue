<script setup>
import { ref, nextTick, onBeforeUnmount } from 'vue'
import jsQR from 'jsqr'

defineProps({
  disabled: {
    type: Boolean,
    default: false
  }
})

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

defineExpose({
  startScanner,
  stopScanner
})
</script>

<template>
  <div>

    <!-- Scan Button -->
    <button
      type="button"
      @click="startScanner"
      :disabled="disabled"
      class="px-[18px] py-[10px] rounded-[10px] font-semibold
             bg-[#86c06b] text-[#14532d]
             hover:bg-[#6fb457]
             disabled:opacity-60 disabled:cursor-not-allowed"
    >
      📷
    </button>

    <!-- Scanner -->
    <transition
      enter-active-class="transition-opacity duration-200"
      leave-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isScanning"
        class="fixed inset-0 bg-black/60 flex justify-center items-center z-[9999]"
      >

        <!-- Modal -->
        <div
          class="w-[340px] max-w-[90%] bg-white rounded-[16px] p-4
                 shadow-[0_20px_50px_rgba(0,0,0,0.3)]"
        >

          <!-- Header -->
          <div class="flex justify-between items-center mb-3">

            <div class="font-semibold text-[#14532d]">
              Quét mã QR
            </div>

            <button
              type="button"
              @click="stopScanner"
              class="w-[28px] h-[28px] rounded-full bg-red-500 text-white"
            >
              ✕
            </button>

          </div>

          <!-- Body -->
          <div>

            <div class="relative">
              <video
                ref="videoRef"
                class="w-full rounded-[12px]"
                autoplay
                muted
                playsinline
              ></video>
            </div>

            <div class="mt-[10px] text-[14px] text-gray-600">
              {{ status }}
            </div>

            <div
              v-if="errorMsg"
              class="mt-[8px] text-[13px] text-red-600"
            >
              {{ errorMsg }}
            </div>

          </div>

          <!-- Footer -->
          <button
            type="button"
            @click="stopScanner"
            class="mt-[12px] w-full py-[8px] rounded-[8px]
                   bg-gray-600 text-white hover:bg-gray-700"
          >
            Tắt camera
          </button>

        </div>

      </div>
    </transition>

  </div>
</template>