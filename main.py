import os
import sys

print("============================")
print("  APLIKASI GRAFIKA KOMPUTER")
print("============================")
print("1. Mode Transformasi 2D")
print("2. Mode Transformasi 3D")
print("0. Keluar")

choice = input("Pilih mode (0-2): ")

if choice == '1':
    os.system(f"python object2D.py")
elif choice == '2':
    os.system(f"python object3D.py")
elif choice == '0':
    print("Keluar dari aplikasi.")
    sys.exit()
else:
    print("Pilihan tidak valid. Silahkan jalankan ulang.")