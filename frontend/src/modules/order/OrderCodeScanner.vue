<template>
  <transition name="fade">
    <div v-if="isScanning" class="scanner-overlay">
      <div class="scanner-modal" :class="{ 'scanner-modal--compact': isScanning }">
        <div class="scanner-header">
          <div class="scanner-title">Quét mã vận đơn (QR)</div>
          <button type="button" class="scanner-close" @click="emitStop">✕</button>
        </div>
        <div class="scanner-body">
          <div class="scanner-content">
            <video ref="videoRef" class="scanner-video" autoplay muted playsinline></video>
            <div class="scanner-status">{{ scannerStatus || 'Đang quét...' }}</div>
            <div v-if="scannerError" class="scanner-error">{{ scannerError }}</div>
          </div>
        </div>
        <div class="scanner-footer">
          <button type="button" class="btn-secondary" @click="emitStop">Tắt camera</button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  isScanning: Boolean,
  scannerStatus: String,
  scannerError: String,
  videoRef: Object,
});

const emit = defineEmits([
  'stop',
]);

const emitStop = () => {
  emit('stop');
};
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.scanner-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 16px;
  z-index: 2000;
}

.scanner-modal {
  background: #fff;
  width: 100%;
  max-width: 520px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.scanner-modal--compact {
  max-width: 360px;
}

.scanner-modal--compact .scanner-body {
  padding: 12px;
}

.scanner-modal--compact .scanner-video {
  aspect-ratio: 4 / 3;
}

.scanner-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
}

.scanner-title {
  font-weight: 700;
  color: #14532d;
}

.scanner-close {
  border: none;
  background: transparent;
  font-size: 18px;
  cursor: pointer;
}

.scanner-body {
  padding: 16px;
}

.scanner-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.scanner-video {
  width: 100%;
  aspect-ratio: 3 / 4;
  background: #0f172a;
  border-radius: 12px;
  object-fit: cover;
}

.scanner-status {
  font-size: 14px;
  color: #374151;
  text-align: center;
}

.scanner-error {
  margin-top: 6px;
  padding: 10px 12px;
  border-radius: 8px;
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
  font-size: 13px;
  text-align: center;
}

.scanner-footer {
  display: flex;
  justify-content: flex-end;
  padding: 12px 16px;
  border-top: 1px solid #e5e7eb;
}

.btn-secondary {
  padding: 12px 16px;
  background: #f3f4f6;
  border: 1px solid #ddd;
  color: #555;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-secondary:hover:not(:disabled) {
  background: #e5e7eb;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
