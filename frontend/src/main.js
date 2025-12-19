import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

createApp(App).use(router).mount('#app')

// Dev-only: trace window.print() and optionally block Ctrl+P for debugging
if (import.meta && import.meta.env && import.meta.env.DEV) {
  try {
    const params = new URLSearchParams(window.location.search);
    const shouldBlock = params.get('blockPrint') === '1' || params.has('blockPrint');

    if (typeof window.print === 'function') {
      const origPrint = window.print.bind(window);
      window.print = (...args) => {
        // Will show stack to locate the caller
        console.trace('window.print called');
        return origPrint(...args);
      };
    }

    window.addEventListener('beforeprint', () => console.log('beforeprint event'));
    window.addEventListener('afterprint', () => console.log('afterprint event'));

    if (shouldBlock) {
      document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && (e.key === 'p' || e.key === 'P')) {
          e.preventDefault();
          console.log('Blocked Ctrl+P (debug)');
        }
      });
    }
  } catch (e) {
    // ignore debug wiring errors
  }
}
