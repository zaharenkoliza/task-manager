import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  vus: 50,
  duration: '3m',
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export default function () {
  const res = http.get(`${BASE_URL}/api/tasks`);
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(0.1);
}
