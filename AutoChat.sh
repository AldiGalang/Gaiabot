#!/bin/bash

# Buat dan masuk ke folder Gaiabot
mkdir -p Gaiabot
cd Gaiabot

# Minta input jumlah clone dari user
read -p "Masukkan jumlah repo yang ingin di-clone: " clone_count

# Validasi input harus angka positif
if ! [[ "$clone_count" =~ ^[0-9]+$ ]]; then
    echo "Input harus berupa angka positif!"
    exit 1
fi

# Looping untuk melakukan git clone
for ((i=101; i<101+clone_count; i++)); do
    echo "Cloning gaiabot-$i..."
    git clone https://github.com/AldiGalang/Gaiabot.git "gaiabot-$i"
done

echo "✅ Semua repo telah berhasil di-clone!"

# File input yang berisi API keys dan proxy
api_key_file="../nama.txt"
proxy_file="../proxy.txt"

# Pastikan file nama.txt dan proxy.txt ada
if [[ ! -f "$api_key_file" ]]; then
    echo "❌ File $api_key_file tidak ditemukan!"
    exit 1
fi
if [[ ! -f "$proxy_file" ]]; then
    echo "❌ File $proxy_file tidak ditemukan!"
    exit 1
fi

# Baca semua folder gaiabot-* dalam array
folders=(gaiabot-*)

# Hitung jumlah folder & jumlah baris dalam file
folder_count=${#folders[@]}
api_key_count=$(wc -l < "$api_key_file")
proxy_count=$(wc -l < "$proxy_file")

# Pastikan jumlah baris cukup untuk jumlah folder
if [[ "$api_key_count" -lt "$folder_count" ]]; then
    echo "❌ Jumlah baris di $api_key_file kurang dari jumlah folder gaiabot-*"
    exit 1
fi
if [[ "$proxy_count" -lt "$folder_count" ]]; then
    echo "❌ Jumlah baris di $proxy_file kurang dari jumlah folder gaiabot-*"
    exit 1
fi

echo "📂 Memasukkan API keys dan Proxy ke masing-masing folder gaiabot-*/"

# Loop untuk memasukkan setiap baris ke folder yang sesuai
index=0
while IFS= read -r api_key && IFS= read -r proxy <&3; do
    folder="${folders[$index]}"
    if [[ -d "$folder" ]]; then
        echo "$api_key" > "$folder/file_api_keys.txt"
        echo "$proxy" > "$folder/proxy.txt"
        echo "✅ API Key & Proxy dimasukkan ke $folder"
    fi
    ((index++))
    if [[ $index -ge $folder_count ]]; then
        break
    fi
done < "$api_key_file" 3< "$proxy_file"

echo "✅ Semua API keys dan Proxy telah dimasukkan ke masing-masing folder gaiabot-*"
