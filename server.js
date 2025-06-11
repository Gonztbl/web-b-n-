// Import các thư viện cần thiết
const express = require('express');
const path = require('path');

// Tạo một ứng dụng Express
const app = express();

// Render sẽ tự động gán PORT qua biến môi trường
const port = process.env.PORT || 3000;

// Cấu hình để Express phục vụ các file tĩnh từ thư mục gốc của dự án
// __dirname là biến toàn cục trong Node.js, trỏ đến thư mục chứa file server.js đang chạy
app.use(express.static(path.join(__dirname, '')));

// Route để xử lý yêu cầu đến trang chủ
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Khởi động server và lắng nghe ở port đã định
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});