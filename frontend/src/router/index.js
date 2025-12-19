import { createRouter, createWebHistory } from 'vue-router';
import ImportsManagement from '../components/ImportsManagement.vue';
import ProductsManagement from '../components/ProductsManagement.vue';
import OrdersManagement from '../components/OrdersManagement.vue';
import SoldManagement from '../components/SoldManagement.vue';
import ExpensesManagement from '../components/ExpensesManagement.vue';

const routes = [
  { path: '/', redirect: '/import' },
  { path: '/import', name: 'imports', component: ImportsManagement },
  { path: '/product', name: 'products', component: ProductsManagement },
  { path: '/order', name: 'orders', component: OrdersManagement },
  { path: '/sold', name: 'sold', component: SoldManagement },
  { path: '/expense', name: 'expenses', component: ExpensesManagement },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
