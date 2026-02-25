import os
import math
from collections import Counter
import zipfile
import gzip
import bz2
import lzma
import zlib

def calculate_entropy_and_info(text):
    total_chars = len(text)
    if total_chars == 0: return 0, 0, 0
    
    # ймовірності окремих символів P(X)
    char_counts = Counter(text)
    p_x = {char: count / total_chars for char, count in char_counts.items()}
    
    # ентропія H(X)
    h_x = sum(-p * math.log2(p) for p in p_x.values())
    info_single_bytes = (h_x * total_chars) / 8

    if total_chars < 3:
        return h_x, info_single_bytes, info_single_bytes

    # ймовірності біграм P(X,Y) та P(Y|X)
    bigrams = [text[i:i+2] for i in range(total_chars-1)]
    bi_counts = Counter(bigrams)
    p_xy = {bi: count / len(bigrams) for bi, count in bi_counts.items()}
    
    # умовна ентропія H(Y|X)
    h_y_given_x = 0
    for bi, p_xy_val in p_xy.items():
        x = bi[0]
        p_x_val = p_x[x]
        h_y_given_x -= p_xy_val * math.log2(p_xy_val / p_x_val)

    # ймовірності триграм P(X,Y,Z) та P(Z|X,Y)
    trigrams = [text[i:i+3] for i in range(total_chars-2)]
    tri_counts = Counter(trigrams)
    p_xyz = {tri: count / len(trigrams) for tri, count in tri_counts.items()}
    
    # умовна ентропія H(Z|X,Y)
    h_z_given_xy = 0
    for tri, p_xyz_val in p_xyz.items():
        xy = tri[:2]
        p_xy_val = p_xy[xy]
        h_z_given_xy -= p_xyz_val * math.log2(p_xyz_val / p_xy_val)

    # обчислення загальної кількості інформації за формулою з методички:
    # I = H(X1) + H(X2|X1) + sum(H(Xi|Xi-1,Xi-2))
    # оскільки текст є стаціонарним джерелом, сума зводиться до:
    info_tri_bits = h_x + h_y_given_x + (total_chars - 2) * h_z_given_xy
    info_tri_bytes = info_tri_bits / 8
    
    return h_x, info_single_bytes, info_tri_bytes

def compress_and_get_sizes(filename):
    with open(filename, 'rb') as f:
        data = f.read()
        
    sizes = {}
    sizes['original'] = len(data)
    
    # zlib (deflate)
    sizes['zlib'] = len(zlib.compress(data))
    # gzip
    sizes['gzip'] = len(gzip.compress(data))
    # bzip2
    sizes['bzip2'] = len(bz2.compress(data))
    # lzma (xz)
    sizes['lzma'] = len(lzma.compress(data))
    
    # zip
    with zipfile.ZipFile('temp.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(filename, arcname=os.path.basename(filename))
    sizes['zip'] = os.path.getsize('temp.zip')
    os.remove('temp.zip')
    
    return sizes

files = ['text1.txt', 'text2.txt', 'text3.txt']

for file in files:
    if not os.path.exists(file):
        print(f"Файл {file} не знайдено!")
        continue
        
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
        
    entropy, info_single, info_tri = calculate_entropy_and_info(text)
    sizes = compress_and_get_sizes(file)
    
    print(f"--- Аналіз файлу {file} ---")
    print(f"Ентропія алфавіту: {entropy:.4f} біт/символ")
    print(f"Кількість інф. (символи): {info_single:.2f} байт")
    print(f"Кількість інф. (триграми): {info_tri:.2f} байт")
    print(f"Розміри файлів (байт): {sizes}\n")