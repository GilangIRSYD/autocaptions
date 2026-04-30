# Project Specification: Auto-Caption Burn-in System

## 1. Project Overview
Sistem aplikasi web berbasis Streamlit yang memungkinkan pengguna mengunggah video, melakukan transkripsi otomatis menggunakan AI (OpenAI Whisper), dan melakukan proses *burn-in* subtitle secara permanen ke dalam video menggunakan FFmpeg. Sistem dideploy menggunakan Docker dengan dukungan akselerasi hardware NVIDIA (CUDA).

## 2. Tech Stack
- **Frontend/Backend:** Streamlit (Python)
- **AI Model:** OpenAI Whisper (Base Model)
- **Video Engine:** FFmpeg
- **Infrastructure:** Docker & Docker Compose
- **Hardware Target:** Linux Home Server (NVIDIA GeForce 930MX - 2GB VRAM)
- **Deployment:** NVIDIA Container Toolkit (CUDA 11.8)

## 3. System Specifications

### 3.1. User Interface (UI) Features
- Widget pengunggahan file video (mendukung format .mp4, .mov, .avi).
- Indikator status proses (Progress bar/Spinner) untuk Transkripsi dan Encoding.
- Video Player untuk meninjau hasil akhir (Preview).
- Tombol unduh (Download) untuk video hasil proses.

### 3.2. Processing Pipeline
1. **Upload:** Menerima file dan menyimpannya di direktori sementara/volume Docker.
2. **Preprocessing:** Ekstraksi audio dari video menggunakan FFmpeg.
3. **Transcription:** Mengirim audio ke Whisper (running on CUDA) untuk menghasilkan segmen teks dan timestamp.
4. **SRT Generation:** Mengonversi segmen Whisper menjadi file subtitle format `.srt`.
5. **Burn-in (Hardcoding):** Menggabungkan video asli dan file `.srt` menggunakan filter `subtitles` pada FFmpeg.
6. **Cleanup:** (Opsional) Menghapus file sementara untuk menghemat ruang disk pada home server.

---

## 4. Acceptance Criteria (AC)

### AC 1: Video Upload & Compatibility
- **Given:** Pengguna membuka aplikasi di browser.
- **When:** Pengguna memilih file video berformat `.mp4` atau `.mov`.
- **Then:** Sistem harus berhasil menerima file tersebut dan memvalidasi tipe file sebelum masuk ke tahap pemrosesan.

### AC 2: GPU-Accelerated Transcription
- **Given:** File video telah diunggah.
- **When:** Proses transkripsi dimulai.
- **Then:** Sistem harus menggunakan GPU NVIDIA 930MX (CUDA) untuk menjalankan model Whisper 'base'.
- **Validation:** Log aplikasi menunjukkan `device: cuda` dan penggunaan VRAM tidak melebihi 2GB.

### AC 3: Subtitle Burn-in Accuracy
- **Given:** Transkripsi selesai dan file `.srt` telah dibuat.
- **When:** FFmpeg menjalankan perintah encoding.
- **Then:** Subtitle harus menempel secara permanen pada frame video dengan posisi tengah-bawah, mudah dibaca, dan sinkron dengan audio (toleransi delay < 500ms).

### AC 4: Web-Based Preview & Download
- **Given:** Proses burn-in selesai.
- **When:** Video hasil dikonversi.
- **Then:** Pengguna dapat memutar video langsung di web browser dan tombol download berfungsi mengunduh file video yang sudah memiliki subtitle.

### AC 5: Dockerized Deployment
- **Given:** Docker Compose dijalankan di Linux host.
- **When:** Perintah `docker-compose up -d` dieksekusi.
- **Then:** Container harus berjalan dalam mode *detached*, mengenali GPU melalui NVIDIA Container Toolkit, dan aplikasi dapat diakses melalui port 8501 di jaringan lokal.

---

## 5. Constraints & Limitations
- **VRAM Limit:** Maksimal model Whisper yang diizinkan adalah `base` untuk mencegah *Out of Memory* (OOM) pada 930MX.
- **Encoding Speed:** Karena 930MX tidak memiliki NVENC, proses burn-in video akan menggunakan CPU (libx264). Kecepatan proses bergantung pada jumlah core CPU server.
- **Storage:** Pengguna harus memantau volume penyimpanan lokal pada home server jika sering mengolah video berukuran besar.