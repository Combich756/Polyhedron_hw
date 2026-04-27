#!/usr/bin/env -S python3 -B

from time import time
from common.tk_drawer import TkDrawer
from shadow.polyedr import Polyedr


POLYEDR_NAMES = ["ccc", "cube", "box", "king", "cow"]


tk = TkDrawer()
try:
    for name in POLYEDR_NAMES:
        print("=============================================================")
        print(f"Начало работы с полиэдром '{name}'")
        polyedr = Polyedr(f"data/{name}.geom")
        polyedr.print_hidden_edge_projection_sum()
        start_time = time()
        polyedr.draw(tk)
        delta_time = time() - start_time
        print(
            f"Полиэдр '{name}': {delta_time} сек."
        )
        input("Hit 'Return' to continue -> ")
except (EOFError, KeyboardInterrupt):
    print("\nStop")
    tk.close()
