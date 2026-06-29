

Shop Bán Sữa - Nền tảng E-commerce Django Toàn diện

![alt text](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)


![alt text](https://img.shields.io/badge/Django-5.2-green?style=for-the-badge&logo=django)


![alt text](https://img.shields.io/badge/PostgreSQL-14-blue?style=for-the-badge&logo=postgresql)


![alt text](https://img.shields.io/badge/Bootstrap-4.4-purple?style=for-the-badge&logo=bootstrap)


![alt text](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

Một dự án thương mại điện tử đầy đủ chức năng được xây dựng trên nền tảng Django, mô phỏng một cửa hàng bán các sản phẩm từ sữa. Dự án tích hợp các công nghệ hiện đại như Trợ lý AI (Google Gemini) và Cổng thanh toán tự động (PayOS) để mang lại trải nghiệm mua sắm thông minh và tiện lợi.

🌐 Tiếng Việt | English (Placeholders for language switching)
🎯 Giới thiệu dự án

Shop Bán Sữa không chỉ là một trang web bán hàng thông thường. Đây là một hệ thống e-commerce hoàn chỉnh, được thiết kế để trình diễn các kỹ năng phát triển web với Django, từ các chức năng cơ bản đến các tích hợp nâng cao. Dự án phù hợp cho các nhà phát triển muốn tìm hiểu về Django, các doanh nghiệp nhỏ muốn xây dựng một cửa hàng trực tuyến, hoặc bất kỳ ai quan tâm đến việc tích hợp AI và thanh toán vào ứng dụng web.

<br>

✨ Tính năng nổi bật

Dự án được trang bị nhiều tính năng mạnh mẽ để phục vụ cả người dùng và quản trị viên:

Dành cho Người dùng (Khách hàng)

✅ Trợ lý AI Thông minh (Google Gemini & RAG): Tích hợp chatbot cho phép khách hàng hỏi đáp về sản phẩm. Chatbot sử dụng kỹ thuật Retrieval-Augmented Generation (RAG) để cung cấp câu trả lời chính xác dựa trên dữ liệu sản phẩm thực tế trong CSDL.

✅ Tích hợp Cổng thanh toán PayOS (VietQR): Cho phép khách hàng thanh toán an toàn và nhanh chóng qua mã QR của các ngân hàng Việt Nam. Hệ thống tự động xác nhận đơn hàng qua Webhook.

✅ Quản lý Tài khoản: Đăng ký, đăng nhập, quên mật khẩu và quản lý thông tin cá nhân.

✅ Trải nghiệm Mua sắm Mượt mà:

Duyệt, tìm kiếm và lọc sản phẩm theo tên, tình trạng còn hàng, giá cả.

Xem chi tiết thông tin, hình ảnh và mô tả sản phẩm.

Hệ thống giỏ hàng động, tự động cập nhật khi kho hàng thay đổi.

✅ Quản lý Đơn hàng: Theo dõi trạng thái đơn hàng (Chờ xử lý, Đã xác nhận, Đang giao,...) và xem lại lịch sử mua hàng.

✅ Đánh giá Sản phẩm: Người dùng có thể viết đánh giá (rating & comment) cho các sản phẩm trong những đơn hàng đã được giao thành công.

Dành cho Quản trị viên (Admin)

✅ Bảng điều khiển Trực quan: Giao diện quản lý thân thiện để giám sát và vận hành cửa hàng.

✅ Quản lý Sản phẩm Toàn diện (CRUD): Thêm, sửa, xóa sản phẩm một cách dễ dàng.

✅ Quản lý Đơn hàng Chuyên sâu:

Xem tất cả đơn hàng của khách hàng.

Lọc đơn hàng theo trạng thái.

Thay đổi trạng thái đơn hàng (Xác nhận, Xử lý, Gửi hàng, Giao hàng).

✅ Phân quyền Rõ ràng: Quyền hạn của admin được tách biệt hoàn toàn với người dùng thông thường.

<br>
📊 Sơ đồ Use Case & Luồng hoạt động
Các sơ đồ dưới đây mô tả trực quan các tương tác giữa người dùng (actors) và hệ thống, thể hiện rõ ràng các chức năng chính.
1. Sơ đồ Use Case cho Khách và Khách hàng
Sơ đồ này thể hiện các hành động của một người dùng chưa đăng nhập (Khách) và một người dùng đã đăng nhập (Khách hàng). Khách hàng kế thừa toàn bộ quyền của Khách và có thêm các chức năng riêng.
Generated mermaid
graph TD
    subgraph "Hệ thống Shop Bán Sữa"
        UC1(Xem trang chủ &<br>sản phẩm nổi bật)
        UC2(Xem danh sách sản phẩm)
        UC3(Tìm kiếm & Lọc sản phẩm)
        UC4(Xem chi tiết sản phẩm)
        UC5(Tương tác Chatbot AI)
        UC6(Đăng ký tài khoản)
        UC7(Đăng nhập)
        UC8(Quản lý giỏ hàng<br>Thêm/Xóa/Xem)
        UC9(Tiến hành thanh toán)
        UC10(Thanh toán COD)
        UC11(Thanh toán PayOS/VietQR)
        UC12(Xem lịch sử &<br>chi tiết đơn hàng)
        UC13(Hủy đơn hàng)
        UC14(Viết đánh giá sản phẩm)
        UC15(Đăng xuất)
    end

    Khach(Khách)
    KH(Khách hàng)

    %% Kế thừa: Khách hàng có thể làm mọi việc của Khách
    KH --|> Khach

    %% Các hành động của Khách
    Khach --> UC1
    Khach --> UC2
    Khach --> UC3
    Khach --> UC4
    Khach --> UC5
    Khach --> UC6
    Khach --> UC7

    %% Các hành động riêng của Khách hàng
    KH --> UC8
    KH --> UC9
    KH --> UC12
    KH --> UC13
    KH --> UC14
    KH --> UC15

    %% Mối quan hệ giữa các use case
    UC9 -- <<include>> --> UC10
    UC9 -- <<include>> --> UC11
    UC14 -- <<extend>> --> UC12
Use code with caution.
Mermaid
Phân tích chi tiết:
Actor: Khách (Guest)
Có thể duyệt xem sản phẩm, tìm kiếm, lọc và xem chi tiết.
Có thể tương tác với Chatbot AI để được tư vấn.
Có thể đăng ký tài khoản mới hoặc đăng nhập vào tài khoản đã có.
Actor: Khách hàng (Customer)
Kế thừa tất cả các quyền của Khách.
Quản lý giỏ hàng: Thêm sản phẩm, xem giỏ hàng và xóa sản phẩm.
Thanh toán: Thực hiện quy trình thanh toán, lựa chọn giữa COD hoặc thanh toán online qua PayOS.
Quản lý đơn hàng: Xem lại lịch sử các đơn đã đặt, theo dõi trạng thái và hủy đơn hàng (nếu đơn hàng đang ở trạng thái cho phép).
Viết đánh giá: Để lại nhận xét và xếp hạng cho các sản phẩm đã mua (chỉ khi đơn hàng đã được giao thành công).
2. Sơ đồ Use Case cho Quản trị viên (Admin)
Sơ đồ này tập trung vào các chức năng quản lý và vận hành hệ thống dành riêng cho Quản trị viên.
Generated mermaid
graph TD
    subgraph "Hệ thống Quản trị"
        A_UC1(Đăng nhập)
        A_UC2(Quản lý Sản phẩm)
        A_UC3(Quản lý Đơn hàng)
        A_UC4(Xem chi tiết<br>đơn hàng bất kỳ)
        A_UC5(Lọc đơn hàng<br>theo trạng thái)
        A_UC6(Thay đổi<br>trạng thái đơn hàng)

        subgraph "CRUD Sản phẩm"
            A_UC2_1(Thêm sản phẩm mới)
            A_UC2_2(Sửa thông tin sản phẩm)
            A_UC2_3(Xóa sản phẩm)
        end
    end

    Admin(Quản trị viên)

    Admin --> A_UC1
    Admin --> A_UC2
    Admin --> A_UC3

    A_UC2 -- <<include>> --> A_UC2_1
    A_UC2 -- <<include>> --> A_UC2_2
    A_UC2 -- <<include>> --> A_UC2_3

    A_UC3 -- <<include>> --> A_UC4
    A_UC3 -- <<include>> --> A_UC5
    A_UC3 -- <<include>> --> A_UC6
Use code with caution.
Mermaid
Phân tích chi tiết:
Actor: Quản trị viên (Admin)
Quản lý Sản phẩm (CRUD): Có toàn quyền thêm mới, cập nhật thông tin (tên, giá, mô tả, ảnh, số lượng kho) và xóa sản phẩm khỏi hệ thống.
Quản lý Đơn hàng:
Xem toàn bộ đơn hàng từ tất cả khách hàng.
Lọc đơn hàng theo các trạng thái khác nhau để tiện xử lý (ví dụ: chỉ xem các đơn Confirmed).
Cập nhật trạng thái của đơn hàng theo quy trình nghiệp vụ: Confirmed -> Processing -> Shipped -> Delivered.
Có thể chủ động hủy đơn hàng của khách nếu cần thiết.
📸 Demo & Hình ảnh

![Screenshot 2025-07-06 161157](https://github.com/user-attachments/assets/f0b17e36-c7ba-4373-bffa-b72abec44f05)

![Screenshot 2025-07-06 161211](https://github.com/user-attachments/assets/257980a7-65cc-41c3-9b40-dbdfe2f995d6)
![Screenshot 2025-07-06 161215](https://github.com/user-attachments/assets/e12d2115-3c80-495f-acc4-5c26ed1671a1)
![Screenshot 2025-07-06 161220](https://github.com/user-attachments/assets/aab1f23f-1c83-4af6-b4f4-584b184e70ad)
![Screenshot 2025-07-06 161230](https://github.com/user-attachments/assets/f1627333-94bd-4597-afe3-96ce4ff9bf79)
![Screenshot 2025-07-06 161241](https://github.com/user-attachments/assets/eb955284-4a38-4ab4-8add-b97a8eba1ef2)
![Screenshot 2025-07-06 161252](https://github.com/user-attachments/assets/2386c83c-1df3-428c-a572-8c1f749ff6ef)
![Screenshot 2025-07-06 161303](https://github.com/user-attachments/assets/e29ebf78-554d-4bfd-82f8-0b7341ef6e09)
![Screenshot 2025-07-06 161312](https://github.com/user-attachments/assets/e75daad7-8231-42f0-b7ff-892251196705)
![Screenshot 2025-07-06 161330](https://github.com/user-attachments/assets/2c229aa2-220d-40ed-9d6c-7b62e69d5322)
![Screenshot 2025-07-06 161336](https://github.com/user-attachments/assets/3c1a808a-ecb0-4c8a-86d4-e82c2a2462da)
![Screenshot 2025-07-06 161344](https://github.com/user-attachments/assets/ef091a8f-e902-4234-ab0c-9895bec2fc16)
![Screenshot 2025-07-06 161349](https://github.com/user-attachments/assets/075e2b84-4d21-4c67-aa25-355e5be4b05a)
![Screenshot 2025-07-06 161353](https://github.com/user-attachments/assets/330877b5-30ec-4464-a562-ca9614461b31)
![Screenshot 2025-07-06 161406](https://github.com/user-attachments/assets/530be16e-7850-468c-8a10-df92a8c2a771)

<br>

🛠️ Công nghệ sử dụng
Lĩnh vực	Công nghệ
Backend	<a href="https://www.djangoproject.com/"><img src="https://img.shields.io/badge/Django-5.2-092E20?style=flat-square&logo=django" alt="Django"></a> <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10-3776AB?style=flat-square&logo=python" alt="Python"></a>
Database	<a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/PostgreSQL-14-336791?style=flat-square&logo=postgresql" alt="PostgreSQL"></a>
Frontend	<a href="https://getbootstrap.com/"><img src="https://img.shields.io/badge/Bootstrap-4.4-563D7C?style=flat-square&logo=bootstrap" alt="Bootstrap"></a> <a href="#"><img src="https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5" alt="HTML5"></a> <a href="#"><img src="https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3" alt="CSS3"></a> <a href="#"><img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript" alt="JavaScript"></a>
Thanh toán	<a href="https://payos.vn/"><img src="https://img.shields.io/badge/PayOS-VietQR-D42A27?style=flat-square" alt="PayOS"></a>
AI	<a href="https://ai.google.dev/"><img src="https://img.shields.io/badge/Google_Gemini-1.5_Flash-4285F4?style=flat-square&logo=google" alt="Google Gemini"></a>
Deployment	<a href="https://gunicorn.org/"><img src="https://img.shields.io/badge/Gunicorn-499848?style=flat-square&logo=gunicorn" alt="Gunicorn"></a> <a href="#"><img src="https://img.shields.io/badge/Whitenoise-FFFFFF?style=flat-square" alt="Whitenoise"></a>
<br>

🏗️ Cấu trúc Dự án

Dự án được tổ chức theo các ứng dụng (apps) Django để đảm bảo tính module và dễ dàng bảo trì:

mainpage: Xử lý trang chủ và các trang tĩnh.

products: Lõi của dự án, quản lý sản phẩm, giỏ hàng, đơn hàng, thanh toán và đánh giá.

accounts: Chịu trách nhiệm xác thực và quản lý người dùng.

admin(app): Chứa các view dành riêng cho chức năng quản trị (đã được cấu trúc lại để sử dụng chung template với products nhằm giảm trùng lặp).

shop (project root): Chứa file cấu hình chính của dự án (settings.py, urls.py).

templates: Chứa các file HTML được chia sẻ trên toàn bộ dự án.

static: Chứa các file tĩnh như CSS, JavaScript, và hình ảnh.

<br>

🚀 Hướng dẫn Cài đặt & Chạy dự án

Làm theo các bước sau để thiết lập môi trường và chạy dự án trên máy của bạn.

1. Yêu cầu cần có

Python (phiên bản 3.10 trở lên)

PostgreSQL (phiên bản 12 trở lên)

Git

2. Các bước cài đặt

a. Clone repository về máy:

Generated bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
cd YOUR_REPOSITORY_NAME


b. Tạo và kích hoạt môi trường ảo (Virtual Environment):

Generated bash
# Trên macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Trên Windows
python -m venv venv
.\venv\Scripts\activate
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

c. Cài đặt các thư viện cần thiết:

Generated bash
pip install -r requirements.txt
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

d. Thiết lập cơ sở dữ liệu PostgreSQL:

Mở psql hoặc pgAdmin.

Tạo một database mới cho dự án. Ví dụ: shopdb.

Tạo một user mới với password (hoặc sử dụng user có sẵn).

e. Cấu hình biến môi trường:
Tạo một file tên là .env trong thư mục gốc của dự án (cùng cấp với manage.py). Sao chép nội dung dưới đây và điền thông tin của bạn.

Generated ini
# .env.example

# Django Secret Key (có thể giữ nguyên key này cho development)
SECRET_KEY='&5c1wcgzgoighiw1js%$n8otv!_e&1gm*j(dfxzgcp65fttxv2'

# Database Configuration (thay bằng thông tin PostgreSQL của bạn)
DB_NAME='shopdb'
DB_USER='postgres'
DB_PASSWORD='YOUR_DB_PASSWORD'
DB_HOST='localhost'
DB_PORT='5432'

# PayOS API Keys (lấy từ https://dashboard.payos.vn/)
PAYOS_CLIENT_ID='YOUR_PAYOS_CLIENT_ID'
PAYOS_API_KEY='YOUR_PAYOS_API_KEY'
PAYOS_CHECKSUM_KEY='YOUR_PAYOS_CHECKSUM_KEY'

# Google Gemini API Key (lấy từ https://ai.google.dev/)
GEMINI_API_KEY='YOUR_GEMINI_API_KEY'

# Email Configuration (dùng cho tính năng quên mật khẩu)
EMAIL_HOST_USER='your_gmail_address@gmail.com'
EMAIL_HOST_PASSWORD='your_gmail_app_password' # Mật khẩu ứng dụng của Gmail
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Ini
IGNORE_WHEN_COPYING_END

Lưu ý: EMAIL_HOST_PASSWORD là Mật khẩu Ứng dụng (App Password) bạn tạo trong tài khoản Google, không phải mật khẩu đăng nhập thông thường.

f. Chạy Django Migrations:
Lệnh này sẽ tạo các bảng trong cơ sở dữ liệu shopdb dựa trên models của dự án.

Generated bash
python manage.py migrate
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

g. Tạo tài khoản Quản trị viên (Superuser):
Tài khoản này dùng để đăng nhập vào trang quản trị và có toàn quyền.

Generated bash
python manage.py createsuperuser
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Sau đó nhập username, email và password theo hướng dẫn.

h. Chạy Development Server:

Generated bash
python manage.py runserver
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

🎉 Hoàn tất! Mở trình duyệt và truy cập vào http://127.0.0.1:8000/ để xem trang web.

Trang quản trị của Django: http://127.0.0.1:8000/admin/

<br>

🔬 Phân tích sâu các Chức năng cốt lõi
1. Trợ lý AI với Google Gemini (RAG)

Đây là tính năng độc đáo nhất của dự án. Thay vì một chatbot thông thường, hệ thống này thông minh hơn nhờ kiến trúc Retrieval-Augmented Generation:

Retrieval (Truy xuất): Khi người dùng gửi một câu hỏi (ví dụ: "shop có sữa nào cho người già không?"), hàm find_relevant_products trong products/views.py sẽ phân tích câu hỏi, loại bỏ các từ không cần thiết và tìm kiếm trong CSDL các sản phẩm có tên, mô tả, hoặc hãng sản xuất khớp với từ khóa.

Augmentation (Bổ sung): Thông tin của các sản phẩm tìm được (tên, giá, mô tả, tình trạng kho) sẽ được hàm create_product_context_for_gemini định dạng lại thành một "bối cảnh" (context) rõ ràng.

Generation (Tạo sinh): "Bối cảnh" này được gửi kèm với câu hỏi gốc của người dùng đến Google Gemini API. Nhờ có bối cảnh, Gemini có thể đưa ra câu trả lời chính xác, chi tiết và phù hợp với dữ liệu thực tế của cửa hàng, thay vì trả lời một cách chung chung.

2. Luồng thanh toán với PayOS

Hệ thống xử lý thanh toán tự động và an toàn thông qua 3 bước chính:

Tạo link thanh toán: Khi người dùng chọn thanh toán qua PayOS và đặt hàng, hệ thống sẽ gọi đến payos_client.createPaymentLink để tạo một yêu cầu thanh toán với thông tin đơn hàng (mã đơn hàng, số tiền). Người dùng sẽ được chuyển hướng đến checkoutUrl do PayOS cung cấp để thực hiện quét mã VietQR.

Xử lý Webhook: Sau khi người dùng thanh toán thành công, PayOS sẽ gửi một yêu cầu POST đến endpoint /payment/webhook/ của website. View payment_webhook_receiver sẽ xác thực yêu cầu này, kiểm tra trạng thái giao dịch. Nếu thành công (code: '00'), hệ thống sẽ:

Cập nhật trạng thái đơn hàng thành Confirmed.

Trừ số lượng sản phẩm trong kho.

Xóa giỏ hàng của người dùng.

Trang trả về (Return URL): Sau khi hoàn tất thanh toán, PayOS sẽ chuyển hướng người dùng trở lại trang /payment/return/. View payment_return_page sẽ hiển thị thông báo thành công hoặc thất bại cho người dùng và điều hướng họ đến trang chi tiết đơn hàng.

<br>

🤝 Đóng góp

Mọi sự đóng góp để cải thiện dự án đều được hoan nghênh. Vui lòng tuân thủ các bước sau:

Fork dự án này.

Tạo một branch mới cho tính năng của bạn (git checkout -b feature/AmazingFeature).

Commit những thay đổi của bạn (git commit -m 'Add some AmazingFeature').

Push lên branch của bạn (git push origin feature/AmazingFeature).

Mở một Pull Request.

<br>

📜 Giấy phép

Dự án này được cấp phép theo Giấy phép MIT. Xem chi tiết tại file LICENSE.

<br>

