import { createRouter, createWebHistory } from 'vue-router';
import ImportsManagement from '@/modules/import/ImportsManagement.vue';
import ProductsManagement from '@/modules/product/ProductsManagement.vue';
import OrdersManagement from '@/modules/order/OrdersManagement.vue';
import SoldManagement from '@/modules/sold/SoldManagement.vue';
import ExpensesManagement from '@/modules/expense/ExpensesManagement.vue';

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
