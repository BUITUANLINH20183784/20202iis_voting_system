# Hệ thống bầu cử số

## [Video Demo](https://husteduvn-my.sharepoint.com/:v:/g/personal/linh_bt183784_sis_hust_edu_vn/Ef2_T3c3BBlJvWEsLDR6xdsB1Xuumy3sjlZ40nXpswZNtQ?e=RbD9M9)

## Thông tin nhóm
- Số lượng thành viên: 1
- Danh sách thành viên:

    | Họ và tên     | MSSV     |
    | ------------- | -------- |
    | Bùi Tuấn Linh | 20183784 |
- Tên đề tài: Thiết kế hệ thống bầu cử số

## Hướng dẫn khởi chạy
Yêu cầu cần có:
- [Python 3]()
- Thư viện [Pycryptodome]()

Hệ thống bao gồm 3 bộ phận chính: máy chủ __CLA__, máy chủ __CTF__ và người tham gia bầu cử __Voter__

### CLA
Mở cửa sổ dòng lệnh mới và khởi động CLA:
```bash
$ python CLA.py
```
Chương trình sẽ yêu cầu nhập các cấu hình cơ bản. Tại mỗi bước có thể bỏ trống để sử dụng tham số mặc định.
```bash
$ Key path (./keys):
$ Key name (CLA):
$ Voter list path (./data):
$ Voter list name (auth):
$ Validation list name (validation):
$ Number of voters: 3
$ CTF host (127.0.0.1):
$ CTF port (8888):
$ CTF key name (CTF):
```
Sau khi cấu hình thành công, máy chủ sẽ khởi động (mặc định ở cổng 9999).
```bash
$ Server starting on :9999
```
### CTF
Mở cửa sổ dòng lệnh mới và khởi động CTF:
```bash
$ python CTF.py
```
Chương trình sẽ yêu cầu nhập các cấu hình cơ bản. Tương tự, tại mỗi bước có thể bỏ trống để sử dụng tham số mặc định.
```bash
$ Key path (./keys):
$ Key name (CTF):
$ Data path (./data):
$ Candidate file name (candidate):
$ Result file name (result):
$ Number of voters (3):
$ CLA key name (CLA):
```
Sau khi cấu hình thành công, máy chủ sẽ khởi động (mặc định ở cổng 8888).
```bash
$ Server starting on :8888
```
### Voter
Mở cửa sổ dòng lệnh mới và khởi động Voter:
```bash
$ python Voter.py
```
Tương tự, chương trình sẽ yêu cầu nhập các tham số cấu hình (bỏ trống để sử dụng tham số mặc định).
```bash
$ CLA host (127.0.0.1):
$ CLA port (9999):
$ CLA public key path (./keys/CLA.pub):
$ Candidate list path (./data/candidate):
$ CTF host (127.0.0.1):
$ CTF port (8888):
$ CTF public key path (./keys/CTF.pub):
```
Sau khi khởi động thành công, chương trình sẽ yêu cầu nhập lựa chọn từ người tham gia bầu cử. Có 3 lựa chọn chính: ấn 1 để đăng nhập, ấn 2 để bầu cử và ấn 3 để thoát.
```bash
Enter your choice
1. Authenticate
2. Vote
3. Exit
>
```

Lựa chọn 1 sẽ kết nối đến CLA để yêu cầu xác thực. Ở lựa chọn này người dùng sẽ phải nhập tên và mật khẩu hợp lệ từ danh sách có sẵn (mặc định trong tệp `./data/auth`)
```bash
Enter your choice
1. Authenticate
2. Vote
3. Exit
> 1
Created socket
Connected to CLA at 127.0.0.1:9999
Establishing secure connection
Established
Username: 0
Password: 0
Sent
```
Sau khi xác thực thành công, chương trình sẽ lưu lại số xác thực mà CLA gửi lại.

Lựa chọn 2 sẽ kết nối đến CTF để gửi phiếu bầu. Người dùng sẽ cần nhập ID tùy ý để định danh phiếu bầu (bỏ trống để sử dụng ID ngẫu nhiên mặc định) và lựa chọn ứng cử viên của mình từ danh sách (mặc định từ tệp `./data/candidate`). Chương trình sẽ tự động gửi kèm số xác thực từ CLA.
```bash
Enter your choice
1. Authenticate
2. Vote
3. Exit
> 2
Created socket
Connected to CTF at 127.0.0.1:8888
Establishing secure connection
Established
ID (034ffc8f2507072bfa38fae1d7d1eafc):
Candidates:
1
2
Your vote: 1
Sent
```
Sau khi hoàn thành, chọn 3 để thoát, hoặc chọn 1 để đăng nhập người dùng khác.

### Kết quả
Khi mọi người đều đã bầu cử xong, CTF sẽ công bố kết quả bằng việc in ra màn hình và lưu lại (mặc định trong tệp `./data/result`).

### Chương trình phụ trợ
Để tự tạo cặp khóa, sinh ra danh sách người tham gia bầu cử và ứng cử viên, có thể sử dụng chương trình `utils.py`:
```bash
$ python utils.py
```
Sau đó nhập lựa chọn tương ứng và làm theo hướng dẫn.

## Cấu trúc hệ thống
Hệ thống gồm 3 chương trình chính: `CLA.py`, `CTF.py`, `Voter.py`; 1 module `SSock.py`; và 1 chương trình phụ trợ `utils.py`. Ngoài ra có 2 thư mục `data` và `keys` để chứa các tệp dữ liệu phục vụ cho hệ thống.

### Các chương trình chính
Các chương trình `CLA.py` và `CTF.py` chứa các lớp CLA và CTF tương ứng, là các máy chủ CLA và CTF trong mô hình hệ thống bầu cử 2 cơ quan. Các lớp này có 3 phương thức chính:
- `config()` thực hiện cấu hình máy chủ
- `startServer()` thực hiện việc khởi động
- `handle_voter()` tiếp nhận và xử lý yêu cầu của người bầu cử

Chương trình `Voter.py` đóng vai trò là tác nhân người tham gia bầu cử, cho phép người dùng đăng nhập và gửi phiếu bầu. Chương trình có 3 phương thức chính:
- `prompt()` lấy lựa chọn mà người dùng nhập, sau đó gọi các phương thức tương ứng
- `authenticate()` yêu cầu người dùng nhập tên và mật khẩu, sau đó gửi cho CLA yêu cầu xác thực, và lưu lại số xác thực mà CLA gửi
- `vote()` lấy số định danh và lựa chọn bầu cử từ người dùng, sau đó gửi cho CTF kèm với số xác thực mà CLA gửi trước đó.

### Các chương trình và module phụ trợ
`SSock.py` là module hỗ trợ việc tạo kết nối mã hóa, được sử dụng trong các chương trình khác để thực hiện kết nối và truyền tin.

`utils.py` là chương trình phụ trợ giúp tạo cặp khóa, sinh ra danh sách người tham gia bầu cử và danh sách các ứng cử viên.


### Các tệp và thư mục khác
Thư mục `keys` chứa các khóa của CLA và CTF. Các khóa công khai cần phải được biết bởi tất cả những người bầu cử trước khi diễn ra cuộc bầu cử. Các khóa này có thể tạo bằng cách sử dụng chương trình phụ trợ `utils.py`.

Thư mục `data` chứa các dữ liệu cần thiết và kết quả của cuộc bầu cử. Tệp `auth` chứa danh sách tên và mật khẩu băm của các người dùng, được sử dụng bởi CLA. Tệp `candidate` chứa danh sách những người ứng cử. Hai tệp này có thể sinh ra bằng chương trình `utils.py`. Tệp `validate` chứa các số xác thực được CLA lưu lại. Tệp `result` chứa kết quả của cuộc bầu cử được CTF công bố.

Toàn bộ các tệp trong 2 thư mục trên được sử dụng mặc định bởi hệ thống, tuy nhiên khi khởi chạy các chương trình có thể cấu hình để sử dụng các tệp với tên và đường dẫn khác. 