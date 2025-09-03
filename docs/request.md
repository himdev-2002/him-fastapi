# 📌 HTTP Methods

| Method   | Fungsi                         | Kapan Digunakan                                           | Ciri Khas                                    |
|----------|--------------------------------|----------------------------------------------------------|----------------------------------------------|
| **GET**    | Mengambil data                 | Ambil list data (`/users`), detail data (`/users/1`)      | Read-only, tidak mengubah data               |
| **POST**   | Membuat data baru              | Registrasi user, simpan form ke database                  | Data dikirim di body request                 |
| **PUT**    | Update penuh (replace)         | Edit data (semua field harus dikirim)                     | Menimpa semua field, wajib lengkap           |
| **PATCH**  | Update sebagian (partial)      | Update 1 field saja (misal hanya email user)              | Lebih fleksibel, hanya field yang diubah     |
| **DELETE** | Menghapus data                 | Hapus user (`/users/1`), hapus postingan (`/posts/10`)    | Data dihapus permanen                        |
| **HEAD**   | Ambil hanya header             | Cek status resource, cek ukuran file sebelum download     | Sama dengan GET tapi tanpa body              |
| **OPTIONS**| Cek metode yang tersedia       | Digunakan untuk CORS atau debug endpoint                  | Balikkan daftar method yang didukung server  |
