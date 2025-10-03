# tools.py
# Các hàm tiện ích hỗ trợ
import subprocess
import shutil
import time
import os


def is_ollama_installed() -> bool:
	"""Kiểm tra xem lệnh `ollama` có trong PATH không."""
	return shutil.which("ollama") is not None


def ollama_status() -> bool:
	"""Truy vấn trạng thái Ollama bằng lệnh `ollama status`.

	Trả về True nếu daemon đang chạy, False nếu không.
	"""
	if not is_ollama_installed():
		return False
	try:
		# Ollama có lệnh status; coi là OK nếu lệnh trả về mã 0.
		res = subprocess.run(["ollama", "status"], capture_output=True, text=True)
		if res.returncode == 0:
			return True
		# Nếu status không thành công, fallback: kiểm tra tiến trình
		return is_ollama_process_running()
	except Exception:
		return is_ollama_process_running()


def is_ollama_process_running() -> bool:
	"""Kiểm tra nếu tiến trình 'ollama' đang chạy (Windows/Unix)."""
	try:
		if os.name == 'nt':
			# Windows: dùng tasklist
			res = subprocess.run(["tasklist"], capture_output=True, text=True)
			return 'ollama.exe' in res.stdout.lower() or 'ollama' in res.stdout.lower()
		else:
			# Unix: dùng ps aux
			res = subprocess.run(["ps", "aux"], capture_output=True, text=True)
			return 'ollama' in res.stdout.lower()
	except Exception:
		return False


def start_ollama_daemon(wait_seconds: int = 2) -> bool:
	"""Khởi động Ollama daemon ở chế độ nền (Windows).

	Trả về True nếu lệnh khởi động đã được gọi thành công.
	"""
	if not is_ollama_installed():
		return False
	try:
		# Trên Windows, khởi chạy Ollama bằng 'ollama serve'
		# Chạy trong một subprocess không chặn; sử dụng creationflags để tách tiến trình
		DETACHED_PROCESS = 0x00000008
		subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
				 stdin=subprocess.DEVNULL, creationflags=DETACHED_PROCESS)
		# Đợi một chút cho daemon khởi động
		time.sleep(wait_seconds)
		# Kiểm tra process hiện có
		return is_ollama_process_running()
	except Exception:
		return False


def ensure_ollama_running(timeout: int = 10) -> bool:
	"""Đảm bảo Ollama daemon đang chạy. Nếu chưa, thử khởi động và chờ cho tới `timeout` giây.

	Trả về True nếu daemon đang chạy hoặc đã khởi động thành công.
	"""
	if not is_ollama_installed():
		return False
	if ollama_status():
		return True

	# Thử khởi động
	started = start_ollama_daemon(wait_seconds=2)
	if not started:
		# Nếu lệnh khởi động không gọi được, trả về False sớm
		return False

	# Poll trạng thái tới khi timeout: thử ollama status, tiến trình, và probe HTTP
	start = time.time()
	while time.time() - start < timeout:
		if ollama_status():
			return True
		if is_ollama_process_running():
			# Thử HTTP probe vào endpoint mặc định của Ollama
			try:
				import urllib.request
				for path in ('/v1', '/v1/models', '/'):
					try:
						url = f"http://127.0.0.1:11434{path}"
						with urllib.request.urlopen(url, timeout=1) as resp:
							if resp.status in (200, 204):
								return True
					except Exception:
						continue
			except Exception:
				pass
		time.sleep(1)
	return False
