import math
import bz2
from collections import Counter

BASE64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

def custom_base64_encode(data_bytes):
    result = ""
    for i in range(0, len(data_bytes), 3):
        chunk = data_bytes[i:i+3]
        val = 0
        for byte in chunk:
            val = (val << 8) | byte
        
        padding = 3 - len(chunk)
        if padding == 2: val <<= 16
        elif padding == 1: val <<= 8
            
        for j in range(3, -1, -1):
            if padding > 0 and j < padding:
                result += "="
            else:
                result += BASE64_ALPHABET[(val >> (j * 6)) & 0x3F]
    return result

def calc_info(text_str):
    if not text_str: return 0
    counts = Counter(text_str)
    entropy = sum(-(c/len(text_str)) * math.log2(c/len(text_str)) for c in counts.values())
    return (entropy * len(text_str)) / 8

files = ['text1.txt', 'text2.txt', 'text3.txt']

for file in files:
    try:
        with open(file, 'rb') as f:
            orig_bytes = f.read()
    except FileNotFoundError:
        continue

    # base64 для оригіналу
    b64_orig = custom_base64_encode(orig_bytes)
    
    # base64 для стисненого файлу (bzip2)
    comp_bytes = bz2.compress(orig_bytes)
    b64_comp = custom_base64_encode(comp_bytes)

    print(f"--- Аналіз Base64 для {file} ---")
    print(f"Розмір оригіналу: {len(orig_bytes)} байт")
    print(f"Розмір Base64 (з оригіналу): {len(b64_orig)} байт")
    print(f"Розмір Base64 (зі стисненого): {len(b64_comp)} байт\n")
    
    print(f"К-сть інф. Base64 (з оригіналу): {calc_info(b64_orig):.2f} байт")
    print(f"К-сть інф. Base64 (зі стисненого): {calc_info(b64_comp):.2f} байт\n")